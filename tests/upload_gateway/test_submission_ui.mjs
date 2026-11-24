import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const script = fs.readFileSync(new URL('../../infra/upload_gateway/static/submission.js', import.meta.url), 'utf8');
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#039;'}[c]));
const attempt = (number, stage, status = 'em_processamento') => ({attempt_number: number, current_stage: stage,
  status, started_at: `2026-11-12T01:0${number}:00Z`});

async function screen({ dispatchError = false, previewError = false, queryToken = '' } = {}) {
  const elements = new Map(), timers = new Map(), documentEvents = {}, windowEvents = {};
  let timerId = 0, failRead = false, readGate = null, dispatchGate = null;
  const data = {
    submission: {submission_id: 'sintetico', filename: 'sintetico.pdf', status: 'erro',
      current_stage: 'analise_markdown', updated_at: '2026-11-12T01:01:00Z'},
    artifacts: [], report_available: false,
    attempts: [attempt(1, 'analise_markdown', 'erro')], errors: [], reviews: [],
  };
  const element = (selector) => {
    if (!elements.has(selector)) {
      const classes = new Set(['hidden']);
      let html = '';
      elements.set(selector, { disabled: false, value: '', textContent: '', open: false, htmlWrites: 0,
        get innerHTML() { return html; }, set innerHTML(value) { html = value; this.htmlWrites++; },
        handlers: {}, addEventListener(event, handler) { this.handlers[event] = handler; },
        classList: { add: (c) => classes.add(c), remove: (c) => classes.delete(c),
          contains: (c) => classes.has(c),
          toggle(c, force) { const add = force ?? !classes.has(c); add ? classes.add(c) : classes.delete(c); return add; } },
        removeAttribute(name) { delete this[name]; },
        showModal() { this.open = true; }, close() { this.open = false; }, scrollIntoView() {} });
    }
    return elements.get(selector);
  };
  const calls = [];
  const tabs = ['report', 'markdown', 'json'].map(name => Object.assign(element('.tab-' + name), {dataset: {tab: name}}));
  ['#review-notes', '#corrected-json'].forEach(element);
  const document = {hidden: false, querySelector: element, querySelectorAll: selector => selector === '.tab' ? tabs : [],
    addEventListener(event, fn) { documentEvents[event] = fn; }};
  const context = {
    location: { pathname: '/submissions/sintetico/view' }, queryToken,
    document, window: {addEventListener(event, fn) { windowEvents[event] = fn; }},
    formatDate: String, formatBytes: String, statusLabel: String, escapeHtml,
    encodeURIComponent, apiHeaders: () => ({}),
    setTimeout(fn, ms) { const key = ++timerId; timers.set(key, {fn, ms}); return key; },
    clearTimeout: key => timers.delete(key),
    fetch: async url => { calls.push({path: url, artifact: true}); return {ok: true, text: async () => 'Markdown sintético'}; },
    api: async (path, options = {}) => {
      calls.push({ path, options });
      if (path.endsWith('/reprocess')) {
        if (dispatchGate) await dispatchGate;
        if (dispatchError) throw Error('Não foi possível iniciar a retomada.');
        data.submission.status = 'recebido'; data.submission.current_stage = 'retomada_solicitada';
        data.submission.updated_at = '2026-11-12T01:02:00Z';
        return { resumed_from: { stage: 'analysis', label: 'análise do Markdown salvo' } };
      }
      if (path.endsWith('/resume')) {
        if (previewError) throw Error('Markdown salvo indisponível.');
        return { stage: 'analysis', label: 'análise do Markdown salvo' };
      }
      if (readGate) await readGate;
      if (failRead) throw Error('Sem conexão');
      return JSON.parse(JSON.stringify(data));
    },
  };
  await vm.runInNewContext(script, context);
  return {elements, calls, timers, context, document, documentEvents, windowEvents, data,
    failRead: value => { failRead = value; }, readGate: value => { readGate = value; },
    dispatchGate: value => { dispatchGate = value; },
    async tick() {
      assert.equal(timers.size, 1);
      const [key, timer] = [...timers][0]; timers.delete(key);
      assert.equal(timer.ms, 5000); await timer.fn();
    },
    async settle() { await context.refresh(); },
  };
}

test('primeiro clique abre confirmação e cancelar não despacha', async () => {
  const {elements, calls} = await screen();
  await elements.get('#retry').handlers.click();
  assert.equal(elements.get('#resume-dialog').open, true);
  assert.match(elements.get('#resume-stage').textContent, /Markdown salvo/);
  assert.equal(calls.some(c => c.path.endsWith('/reprocess')), false);
  await elements.get('#resume-cancel').handlers.click();
  assert.equal(elements.get('#resume-dialog').open, false);
  assert.equal(calls.some(c => c.path.endsWith('/reprocess')), false);
});

test('fechar por Escape ou pelo fundo não solicita retomada', async () => {
  const {elements, calls} = await screen();
  const dialog = elements.get('#resume-dialog');
  for (const action of ['cancel', 'click']) {
    await elements.get('#retry').handlers.click();
    let prevented = false;
    dialog.handlers[action]({target: dialog, preventDefault() { prevented = true; }});
    if (action === 'cancel' && !prevented) dialog.close();
    assert.equal(dialog.open, false);
  }
  assert.equal(calls.some(c => c.path.endsWith('/reprocess')), false);
});

test('somente confirmar solicita retomada', async () => {
  const { elements, calls } = await screen();
  assert.equal(elements.get('#retry').classList.contains('hidden'), false);
  await elements.get('#retry').handlers.click();
  await elements.get('#resume-confirm').handlers.click();
  assert.equal(calls.filter(c => c.path.endsWith('/reprocess')).length, 1);
  assert.match(elements.get('#flash').textContent, /Markdown salvo/);
  assert.equal(elements.get('#retry').classList.contains('hidden'), true);
});

test('falha de despacho mantém confirmação com erro e permite tentar novamente', async () => {
  const { elements } = await screen({ dispatchError: true });
  await elements.get('#retry').handlers.click();
  await elements.get('#resume-confirm').handlers.click();
  assert.equal(elements.get('#resume-dialog').open, true);
  assert.equal(elements.get('#resume-confirm').disabled, false);
  assert.equal(elements.get('#retry').disabled, false);
  assert.match(elements.get('#flash').textContent, /Não foi possível/);
});

test('dois cliques na confirmação despacham somente uma solicitação', async () => {
  const s = await screen();
  let release;
  s.dispatchGate(new Promise(resolve => { release = resolve; }));
  await s.elements.get('#retry').handlers.click();
  const first = s.elements.get('#resume-confirm').handlers.click();
  await s.elements.get('#resume-confirm').handlers.click();
  assert.equal(s.elements.get('#resume-confirm').disabled, true);
  assert.equal(s.calls.filter(c => c.path.endsWith('/reprocess')).length, 1);
  release(); await first;
});

test('polling mostra conversão, análise, PDF, erro e conclusão sem perder tentativas', async () => {
  const s = await screen();
  for (const [stage, label] of [['convertendo_pdf', 'Convertendo PDF'], ['analise_markdown', 'Analisando Markdown'], ['preparando_pdf', 'Preparando e salvando PDF']]) {
    s.data.submission.status = 'em_processamento'; s.data.submission.current_stage = stage;
    s.data.attempts = [attempt(1, 'analise_markdown', 'erro'), attempt(2, stage)];
    await s.tick();
    assert.match(s.elements.get('#progress').innerHTML, new RegExp(label));
    assert.match(s.elements.get('#history').innerHTML, /Tentativa 1/);
    assert.match(s.elements.get('#history').innerHTML, /Tentativa 2/);
  }
  s.data.submission.status = 'erro'; s.data.submission.updated_at = '2026-11-12T01:03:00Z';
  s.data.errors = [{created_at: '2026-11-12T01:03:00Z', current_stage: 'preparando_pdf', error_message: '<Erro sintético>'}];
  await s.tick();
  assert.match(s.elements.get('#progress').innerHTML, /Interrompido em/);
  assert.match(s.elements.get('#history').innerHTML, /&lt;Erro sintético&gt;/);
  const download = s.elements.get('#download');
  assert.equal(download.classList.contains('hidden'), true);
  s.data.submission.status = 'concluido'; s.data.submission.current_stage = 'relatorio_pronto';
  s.data.report_available = true;
  await s.tick();
  assert.match(s.elements.get('#progress').innerHTML, /Relatório pronto para download/);
  assert.equal(download.classList.contains('hidden'), false);
  assert.equal(download.href, '/api/v1/submissions/sintetico/report');
  assert.equal(s.calls.some(c => c.options?.method === 'POST'), false);
});

test('atualização preserva formulário, aba e artefato inalterado', async () => {
  const s = await screen();
  s.data.artifacts = [{artifact_type: 'markdown', artifact_id: 1, version: 1, sha256: 'abc'}];
  await s.tick(); await s.elements.get('.tab-markdown').handlers.click();
  const writes = s.elements.get('#viewer').htmlWrites;
  s.elements.get('#review-notes').value = 'Observação em edição';
  s.elements.get('#corrected-json').value = '{"teste":true}';
  await s.tick();
  assert.equal(s.elements.get('#review-notes').value, 'Observação em edição');
  assert.equal(s.elements.get('#corrected-json').value, '{"teste":true}');
  assert.equal(s.elements.get('#viewer').htmlWrites, writes);
  assert.equal(s.elements.get('.tab-markdown').classList.contains('active'), true);
  assert.match(s.calls.find(c => c.artifact).path, /\/markdown\?disposition=inline$/);
});

test('PDF final aparece automaticamente e não é recarregado sem alteração', async () => {
  const s = await screen();
  s.data.artifacts = [{artifact_type: 'report_pdf', artifact_id: 2, version: 2, sha256: 'abc'}];
  await s.tick();
  assert.match(s.elements.get('#viewer').innerHTML, /\/report_pdf\?disposition=inline/);
  const writes = s.elements.get('#viewer').htmlWrites; await s.tick();
  assert.equal(s.elements.get('#viewer').htmlWrites, writes);
});

test('falha de consulta preserva último estado e polling se recupera', async () => {
  const s = await screen();
  const history = s.elements.get('#history').innerHTML;
  s.failRead(true); await s.tick();
  assert.match(s.elements.get('#sync-status').textContent, /últimos dados/);
  assert.equal(s.elements.get('#history').innerHTML, history);
  s.failRead(false); s.data.submission.current_stage = 'convertendo_pdf'; await s.tick();
  assert.match(s.elements.get('#progress').innerHTML, /Convertendo PDF/);
  assert.match(s.elements.get('#sync-status').textContent, /conferido em/);
});

test('polling pausa em aba oculta e ao sair, retomando ao voltar', async () => {
  const s = await screen();
  s.document.hidden = true; s.documentEvents.visibilitychange(); assert.equal(s.timers.size, 0);
  s.document.hidden = false; s.documentEvents.visibilitychange(); await s.settle();
  assert.equal(s.timers.size, 1);
  s.windowEvents.pagehide(); assert.equal(s.timers.size, 0);
  s.windowEvents.pageshow({persisted: true}); await s.settle(); assert.equal(s.timers.size, 1);
});

test('consultas simultâneas compartilham uma requisição', async () => {
  const s = await screen();
  let release; s.readGate(new Promise(resolve => { release = resolve; }));
  const count = s.calls.length;
  const first = s.context.refresh(), second = s.context.refresh(); assert.equal(s.calls.length, count + 1);
  release(); await Promise.all([first, second]);
});

test('retomada em outro cliente fecha confirmação e bloqueia despacho antigo', async () => {
  const s = await screen();
  await s.elements.get('#retry').handlers.click();
  s.data.submission.status = 'em_processamento'; s.data.submission.current_stage = 'recuperando_checkpoint'; await s.tick();
  assert.equal(s.elements.get('#resume-dialog').open, false);
  await s.elements.get('#resume-confirm').handlers.click();
  assert.equal(s.calls.some(c => c.path.endsWith('/reprocess')), false);
});

test('checkpoint indisponível impede abrir confirmação e despachar', async () => {
  const s = await screen({previewError: true});
  assert.equal(s.elements.get('#retry').disabled, true); await s.elements.get('#retry').handlers.click();
  assert.equal(s.elements.get('#resume-dialog').open, false);
  assert.equal(s.calls.some(c => c.path.endsWith('/reprocess')), false);
});

test('download exige arquivo disponível e preserva o acesso por token', async () => {
  const s = await screen({queryToken: 'teste + pdf'});
  const download = s.elements.get('#download');
  s.data.submission.status = 'concluido';
  await s.tick();
  assert.equal(download.classList.contains('hidden'), true);
  assert.equal(download.href, undefined);
  s.data.report_available = true;
  await s.tick();
  assert.equal(download.classList.contains('hidden'), false);
  assert.equal(download.href, '/api/v1/submissions/sintetico/report?token=teste%20%2B%20pdf');
  s.data.report_available = false;
  await s.tick();
  assert.equal(download.classList.contains('hidden'), true);
  assert.equal(download.href, undefined);
});
