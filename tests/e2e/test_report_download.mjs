import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash, pbkdf2Sync, randomBytes } from 'node:crypto';
import { chmodSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { after, before, test } from 'node:test';
import { fileURLToPath } from 'node:url';

const { chromium } = createRequire(import.meta.url)('playwright');
const root = fileURLToPath(new URL('../../', import.meta.url));
const setup = mkdtempSync(join(tmpdir(), 'miller-e2e-'));
const nonce = randomBytes(6).toString('hex');
const project = `miller-e2e-${nonce}`;
const secret = () => randomBytes(24).toString('hex');
const password = secret();
const salt = randomBytes(16);
const iterations = 310_000;
const passwordHash = pbkdf2Sync(password, salt, iterations, 32, 'sha256').toString('base64url');
const envFile = join(setup, '.env');
const env = {
  ...process.env,
  POSTGRES_USER: 'n8n', POSTGRES_DB: 'n8n', POSTGRES_PASSWORD: secret(),
  N8N_ENCRYPTION_KEY: secret(), N8N_INSTANCE_OWNER_MANAGED_BY_ENV: 'false',
  INTERNAL_API_TOKEN: secret(), LANDING_ACCESS_TOKEN: secret(), AUTH_SESSION_SECRET: secret(),
  LANDING_USERNAME: 'operador-e2e',
  LANDING_PASSWORD_HASH: `pbkdf2_sha256$${iterations}$${salt.toString('base64url')}$${passwordHash}`,
  SESSION_COOKIE_SECURE: 'false', ANVISA_REPORT_PROVIDER: 'ollama', OLLAMA_MODEL: 'sintetico',
  ARTIFACT_VOLUME_NAME: `${project}-artifacts`, ARTIFACT_STORAGE_DIR: '/data/artifacts',
  ARTIFACTS_GID: '10002', N8N_RESTRICT_FILE_ACCESS_TO: '/data/artifacts',
  N8N_SUBMISSION_WEBHOOK_URL: 'http://n8n:5678/webhook/automacao-regulatoria-internal',
  UPLOAD_GATEWAY_BASE_URL: 'http://upload-gateway:8085',
  PDF_CONVERTER_BASE_URL: 'http://pdf-converter:8080', WORKFLOW_TIMEOUT_SECONDS: '40',
  MILLER_E2E_SETUP_DIR: setup,
};
let browser;
let baseUrl;

function compose(...args) {
  return execFileSync('docker', [
    'compose', '--env-file', envFile, '-p', project,
    '-f', 'docker-compose.yml', '-f', 'tests/e2e/compose.yml', ...args,
  ], { cwd: root, env, encoding: 'utf8', stdio: ['ignore', 'pipe', 'inherit'], timeout: 180_000 });
}

function prepareWorkflows() {
  chmodSync(setup, 0o755);
  writeFileSync(envFile, '', { mode: 0o600 });
  const credential = { id: 'miller-e2e-postgres', name: 'PostgreSQL sintético', type: 'postgres', data: {
    host: 'postgres', port: 5432, database: env.POSTGRES_DB, user: env.POSTGRES_USER, password: env.POSTGRES_PASSWORD,
  } };
  writeFileSync(join(setup, 'credentials.json'), JSON.stringify([credential]));
  const workflows = ['internal-error-v1', 'internal-v1'].map(suffix => {
    const path = join(root, 'workflows', `automacao-regulatoria-${suffix}.json`);
    const workflow = JSON.parse(readFileSync(path, 'utf8'));
    for (const node of workflow.nodes.filter(node => node.type === 'n8n-nodes-base.postgres')) {
      node.credentials = { postgres: { id: credential.id, name: credential.name } };
    }
    return workflow;
  });
  writeFileSync(join(setup, 'workflows.json'), JSON.stringify(workflows));
}

before(async () => {
  prepareWorkflows();
  const images = [
    ['pdf-converter', env.MILLER_E2E_CONVERTER_IMAGE],
    ['report-renderer', env.MILLER_E2E_RENDERER_IMAGE],
    ['upload-gateway', env.MILLER_E2E_GATEWAY_IMAGE],
  ];
  const servicesToBuild = images.filter(([, image]) => !image).map(([service]) => service);
  if (servicesToBuild.length) compose('build', ...servicesToBuild);
  compose('up', '-d', '--wait', 'postgres');
  compose('run', '--rm', '--no-deps', '--entrypoint', 'sh', 'n8n', '-ec', [
    'n8n import:credentials --input=/fixtures/credentials.json',
    'n8n import:workflow --input=/fixtures/workflows.json',
    'n8n publish:workflow --id=automacao-reg-error-handler',
    'n8n publish:workflow --id=automacao-regulatoria-internal',
  ].join('\n'));
  compose('up', '-d', '--no-build', '--wait', '--wait-timeout', '90');
  const address = compose('port', 'upload-gateway', '8085').trim();
  assert.match(address, /^127\.0\.0\.1:[1-9]\d*$/, 'O gateway de teste deve publicar uma porta temporária local.');
  baseUrl = `http://${address}`;
  browser = await chromium.launch();
});

after(async () => {
  try {
    await browser?.close();
    compose('down', '--volumes', '--remove-orphans');
  } finally {
    rmSync(setup, { recursive: true, force: true });
  }
});

function sourcePdf(text) {
  const stream = `BT /F1 14 Tf 50 700 Td (${text}) Tj ET\n`;
  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    `<< /Length ${stream.length} >>\nstream\n${stream}endstream`,
  ];
  let pdf = '%PDF-1.4\n';
  const offsets = objects.map((object, index) => {
    const offset = pdf.length;
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
    return offset;
  });
  const xref = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (const offset of offsets) pdf += `${String(offset).padStart(10, '0')} 00000 n \n`;
  return Buffer.from(`${pdf}trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`);
}

async function submitPdf(page, text) {
  await page.goto(baseUrl);
  await page.getByLabel('Usuário').fill(env.LANDING_USERNAME);
  await page.getByLabel('Senha').fill(password);
  await page.getByRole('button', { name: 'Acessar documentos' }).click();
  await page.waitForURL('**/upload');
  await page.goto(`${baseUrl}/new`);
  const original = sourcePdf(text);
  await page.locator('#file').setInputFiles({ name: 'sintetico.pdf', mimeType: 'application/pdf', buffer: original });
  const submitted = page.waitForResponse(response => response.url().endsWith('/api/v1/submissions') && response.request().method() === 'POST');
  await page.locator('#send').click();
  const response = await submitted;
  assert.equal(response.status(), 202);
  const { submission_id: id } = await response.json();
  await page.locator('#open-protocol').click();
  await page.waitForURL(`**/submissions/${id}/view`);
  return { id, original, endpoint: `${baseUrl}/api/v1/submissions/${id}` };
}

test('protocolo em processamento libera o PDF final no mesmo painel ao concluir', async () => {
  const page = await browser.newPage({ acceptDownloads: true });
  try {
    const { id, original, endpoint } = await submitPdf(page, 'ATO REGULATORIO SINTETICO');
    await page.locator('#progress').getByText('Processando', { exact: true }).waitFor();
    assert.equal(await page.locator('#download').isVisible(), false);
    assert.equal((await page.request.get(`${endpoint}/report`)).status(), 409);

    compose('exec', '-T', 'ollama', 'touch', '/tmp/liberar-analise');
    const button = page.getByRole('link', { name: 'Baixar relatório PDF' });
    await button.waitFor({ state: 'visible', timeout: 45_000 });
    assert.match(await page.locator('#progress').innerText(), /Concluído/);
    const downloaded = page.waitForEvent('download', {
      predicate: download => download.url() === `${endpoint}/report`,
    });
    await button.click();
    const file = await downloaded;
    assert.equal(file.suggestedFilename(), `relatorio-${id}.pdf`);
    const pdf = readFileSync(await file.path());
    assert.equal(pdf.subarray(0, 5).toString(), '%PDF-');
    assert.notDeepEqual(pdf, original);
    const detail = await (await page.request.get(endpoint)).json();
    const artifact = detail.artifacts.find(item => item.artifact_type === 'report_pdf');
    assert.equal(artifact.size_bytes, pdf.length);
    assert.equal(artifact.sha256, createHash('sha256').update(pdf).digest('hex'));
    assert.equal(detail.attempts[0].status, 'concluido');
    assert.equal((await fetch(`${endpoint}/report`)).status, 403);
  } finally {
    await page.close();
  }
});

test('falha na análise mantém o download do relatório indisponível', async () => {
  const page = await browser.newPage();
  try {
    const { endpoint } = await submitPdf(page, 'FALHA SINTETICA');
    await page.locator('#progress').getByText('Erro', { exact: true }).waitFor({ timeout: 45_000 });
    assert.equal(await page.locator('#download').isVisible(), false);
    assert.equal((await page.request.get(`${endpoint}/report`)).status(), 409);
    const detail = await (await page.request.get(endpoint)).json();
    assert.equal(detail.report_available, false);
    assert.equal(detail.errors[0].error_category, 'validação');
  } finally {
    await page.close();
  }
});
