const id = location.pathname.split('/').filter(Boolean)[1];
const endpoint = '/api/v1/submissions/' + encodeURIComponent(id);
const urlToken = queryToken ? '?token=' + encodeURIComponent(queryToken) : '';
const el = selector => document.querySelector(selector);
const retry = el('#retry'), retryEmail = el('#retry-email');
const send = el('#send'), sendConfirm = el('#send-confirm');
const dialog = el('#resume-dialog'), confirmResume = el('#resume-confirm');
const cancelResume = el('#resume-cancel');
let detail = null, recipients = [], activeTab = 'report', viewerKey = null, viewerRequest = 0;
let preview = null, previewKey = null, resuming = false, refreshing = null;
let pollTimer = null, stopped = false;

const stageNames = {
  recebido: 'Aguardando início do processamento',
  retomada_solicitada: 'Retomada solicitada',
  documento_reivindicado: 'Iniciando processamento',
  recuperando_checkpoint: 'Recuperando o último ponto salvo',
  convertendo_pdf: 'Convertendo PDF para Markdown',
  markdown_persistido: 'Markdown salvo',
  analise_markdown: 'Analisando Markdown e gerando relatório',
  relatorio_markdown_persistido: 'Relatório Markdown salvo',
  preparando_pdf: 'Preparando e salvando PDF do relatório',
  relatorio_pronto: 'Relatório pronto para envio',
};
const stageLabel = value => stageNames[value] || value || 'Etapa não informada';
const toggle = (element, visible) => element.classList.toggle('hidden', !visible);
function notice(text, kind = 'info') {
  el('#flash').className = 'notice ' + kind;
  el('#flash').textContent = text;
}
function artifact(type) {
  return (detail?.artifacts || []).filter(x => x.artifact_type === type)
    .sort((a, b) => Number(b.version || 0) - Number(a.version || 0))[0];
}
function latestAttempt() {
  return [...(detail.attempts || [])].sort((a, b) => b.attempt_number - a.attempt_number)[0];
}
function renderMeta() {
  const s = detail.submission;
  el('#title').textContent = s.submission_id;
  el('#subtitle').textContent = s.filename;
  el('#meta').innerHTML = [
    ['Status', `<span class="status ${escapeHtml(s.status)}">${escapeHtml(statusLabel(s.status))}</span>`],
    ['Etapa atual', escapeHtml(stageLabel(s.current_stage))],
    ['Tamanho', formatBytes(s.size_bytes)], ['Hash SHA-256', escapeHtml(s.sha256)],
    ['Criado em', formatDate(s.created_at)], ['Atualizado em', formatDate(s.updated_at)],
    ['Mensagem', escapeHtml(s.message || 'Sem mensagem')],
  ].map(([a, b]) => `<div><dl><dt>${a}</dt><dd>${b}</dd></dl></div>`).join('');
  const attempt = latestAttempt();
  el('#progress').innerHTML = `<strong>${escapeHtml(statusLabel(s.status))}</strong>
    <p>${s.status === 'erro' ? 'Interrompido em' : 'Etapa atual'}:
    ${escapeHtml(stageLabel(s.current_stage))}</p>
    ${attempt ? `<span class="muted small">Tentativa ${Number(attempt.attempt_number)}</span>` : ''}`;
}
function events(items) {
  return items.map(x => `<div class="event"><time>${formatDate(x.date)}</time><p>
    <strong>${escapeHtml(x.title)}</strong><br>${escapeHtml(x.text || '')}</p></div>`).join('');
}
function renderHistory() {
  const items = [
    ...(detail.attempts || []).map(x => ({date: x.started_at,
      title: `Tentativa ${x.attempt_number} · ${stageLabel(x.current_stage)}`,
      text: x.error_message || statusLabel(x.status)})),
    ...(detail.errors || []).map(x => ({date: x.created_at,
      title: `${x.error_category || 'Erro'} · ${stageLabel(x.current_stage)}`, text: x.error_message})),
  ].sort((a, b) => new Date(b.date) - new Date(a.date));
  el('#history').innerHTML = items.length ? events(items) : '<p class="muted small">Nenhuma tentativa registrada.</p>';
  el('#timeline').innerHTML = events([
    {date: detail.submission.created_at, title: 'Documento recebido', text: detail.submission.filename},
    ...(detail.reviews || []).map(x => ({date: x.reviewed_at, title: `Revisão · ${x.decision}`, text: x.notes})),
  ]);
}
function renderDeliveries() {
  el('#deliveries').innerHTML = detail.deliveries?.length ? events(detail.deliveries.map(x => ({
    date: x.requested_at, title: `Envio ${statusLabel(x.status)}`,
    text: (x.recipient_emails || []).join(', ') + (x.error_message ? '\n' + x.error_message : ''),
  }))) : '<p class="muted small">Nenhum envio solicitado.</p>';
}
async function showTab(name) {
  activeTab = name;
  document.querySelectorAll('.tab').forEach(x => x.classList.toggle('active', x.dataset.tab === name));
  const a = artifact(name === 'report' ? 'report_pdf' : name === 'markdown' ? 'markdown' : 'analysis_json');
  const key = JSON.stringify([name, a?.artifact_id, a?.version, a?.sha256, a?.storage_key]);
  if (key === viewerKey) return;
  viewerKey = key;
  const request = ++viewerRequest, viewer = el('#viewer');
  if (!a) {
    viewer.innerHTML = '<div class="empty">Este artefato ainda não foi gerado.</div>';
    return;
  }
  const link = `${endpoint}/artifacts/${a.artifact_type}?disposition=inline${queryToken ? '&token=' + encodeURIComponent(queryToken) : ''}`;
  if (name === 'report') {
    viewer.innerHTML = `<iframe title="Visualização do relatório" src="${escapeHtml(link)}"></iframe>`;
    return;
  }
  try {
    const response = await fetch(link, {credentials: 'same-origin', headers: apiHeaders(), cache: 'no-store'});
    if (!response.ok) throw new Error('Não foi possível carregar o artefato.');
    let text = await response.text();
    if (request !== viewerRequest) return;
    if (name === 'json') { try { text = JSON.stringify(JSON.parse(text), null, 2); } catch (_) {} }
    viewer.innerHTML = name === 'markdown' ? `<div class="markdown">${escapeHtml(text)}</div>` : `<pre>${escapeHtml(text)}</pre>`;
  } catch (e) {
    if (request !== viewerRequest) return;
    viewerKey = null;
    viewer.innerHTML = `<div class="empty">${escapeHtml(e.message)}</div>`;
  }
}
function renderRecipients() {
  el('#recipient-list').innerHTML = recipients.length ? recipients.map(x => `<label class="check">
    <input type="checkbox" value="${escapeHtml(x.email)}" ${x.active ? 'checked' : 'disabled'}>
    ${escapeHtml(x.label || x.email)} <span class="muted small">${escapeHtml(x.email)}</span></label>`).join('')
    : '<p class="muted small">Nenhum destinatário padrão ativo.</p>';
}
async function renderActions() {
  const s = detail.submission;
  toggle(send, s.status === 'aguardando_envio');
  if (s.status !== 'aguardando_envio') toggle(sendConfirm, false);
  toggle(el('#review-panel'), ['aguardando_revisao', 'aguardando_envio'].includes(s.status));
  toggle(el('#download'), s.status === 'concluido');
  if (s.status === 'concluido') el('#download').href = endpoint + '/report' + urlToken;
  const latestDelivery = [...(detail.deliveries || [])].sort((a, b) => new Date(b.requested_at) - new Date(a.requested_at))[0];
  const emailFailure = s.status === 'erro' && latestDelivery?.status === 'falhou' && artifact('report_pdf');
  const canResume = s.status === 'erro' && !emailFailure;
  toggle(retryEmail, emailFailure);
  toggle(retry, canResume);
  if (!canResume) {
    preview = null; previewKey = null;
    retry.disabled = true; confirmResume.disabled = true;
    if (dialog.open) dialog.close();
    return;
  }
  const key = s.updated_at;
  if (previewKey !== key || !preview) {
    preview = null;
    retry.disabled = true; confirmResume.disabled = true;
    try {
      preview = await api(endpoint + '/resume', {cache: 'no-store'});
      previewKey = key;
    } catch (e) {
      retry.title = e.message;
      el('#resume-error').textContent = e.message;
      return;
    }
  }
  retry.title = 'Continuar a partir de ' + preview.label;
  el('#resume-stage').textContent = preview.label;
  retry.disabled = resuming; confirmResume.disabled = resuming;
}
async function refresh() {
  if (refreshing) return refreshing;
  refreshing = (async () => {
    try {
      detail = await api(endpoint, {cache: 'no-store'});
      renderMeta(); renderHistory(); renderDeliveries();
      await renderActions();
      void showTab(activeTab);
      el('#sync-status').textContent = 'Atualização automática · conferido em ' + formatDate(new Date().toISOString());
      return true;
    } catch (_) {
      el('#sync-status').textContent = 'Não foi possível atualizar agora. Exibindo os últimos dados recebidos; uma nova consulta será feita automaticamente.';
      return false;
    }
  })();
  try { return await refreshing; } finally { refreshing = null; }
}
function schedulePoll() {
  clearTimeout(pollTimer);
  if (!stopped && !document.hidden) pollTimer = setTimeout(async () => {
    if (stopped || document.hidden) return;
    await refresh();
    schedulePoll();
  }, 5000);
}
function openResumeDialog() {
  if (resuming || !preview || detail.submission.status !== 'erro') return;
  el('#resume-error').textContent = '';
  if (!dialog.open) dialog.showModal();
}
async function resumeProcessing() {
  if (resuming || !dialog.open || !preview || detail.submission.status !== 'erro') return;
  resuming = true;
  retry.disabled = true; confirmResume.disabled = true; cancelResume.disabled = true;
  confirmResume.textContent = 'Solicitando...';
  el('#resume-error').textContent = '';
  try {
    const result = await api(endpoint + '/reprocess', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'});
    dialog.close(); preview = null; previewKey = null;
    notice('Retomada solicitada a partir de ' + result.resumed_from.label + '.', 'success');
    // Uma consulta anterior ao despacho não deve substituir o estado da retomada.
    if (refreshing) await refreshing;
    await refresh();
  } catch (e) {
    el('#resume-error').textContent = e.message;
    notice(e.message, 'error');
  } finally {
    resuming = false; cancelResume.disabled = false;
    confirmResume.textContent = 'Confirmar reprocessamento';
    retry.disabled = !preview; confirmResume.disabled = !preview;
    schedulePoll();
  }
}
function selectedEmails() {
  const values = [...el('#recipient-list').querySelectorAll('input:checked')].map(x => x.value);
  const extra = el('#custom-emails').value.split(',').map(x => x.trim().toLowerCase()).filter(Boolean);
  return [...new Set([...values, ...extra])];
}
async function requestSend(path = endpoint + '/send-report') {
  const emails = selectedEmails();
  if (!emails.length) return notice('Selecione ou informe ao menos um destinatário.', 'error');
  sendConfirm.disabled = true; retryEmail.disabled = true;
  try {
    await api(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({recipients: emails})});
    notice('Envio solicitado. O relatório será liberado após a confirmação do Gmail.', 'success');
    await refresh();
  } catch (e) { notice(e.message, 'error'); }
  finally { sendConfirm.disabled = false; retryEmail.disabled = false; }
}
async function review(decision) {
  const notes = el('#review-notes').value.trim();
  if (!notes) return notice('Informe as observações da conferência.', 'error');
  let corrected_payload;
  const raw = el('#corrected-json')?.value.trim();
  if (raw) {
    try { corrected_payload = JSON.parse(raw); }
    catch (_) { return notice('O JSON corrigido não é válido.', 'error'); }
  }
  try {
    await api(endpoint + '/review', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({decision, notes, corrected_payload})});
    notice('Conferência registrada.', 'success');
    await refresh();
  } catch (e) { notice(e.message, 'error'); }
}
retry.addEventListener('click', openResumeDialog);
confirmResume.addEventListener('click', resumeProcessing);
cancelResume.addEventListener('click', () => { if (!resuming) dialog.close(); });
dialog.addEventListener('cancel', event => { if (resuming) event.preventDefault(); });
dialog.addEventListener('click', event => { if (event.target === dialog && !resuming) dialog.close(); });
send.addEventListener('click', () => sendConfirm.classList.toggle('hidden'));
sendConfirm.addEventListener('click', () => requestSend());
retryEmail.addEventListener('click', () => requestSend(endpoint + '/retry-email'));
document.querySelectorAll('.tab').forEach(x => x.addEventListener('click', () => showTab(x.dataset.tab)));
el('#approve').addEventListener('click', () => review('liberar_envio'));
el('#reprocess').addEventListener('click', () => review('reprocessar'));
document.addEventListener('visibilitychange', () => {
  clearTimeout(pollTimer);
  if (!document.hidden && !stopped) void refresh().finally(schedulePoll);
});
window.addEventListener('pagehide', () => { stopped = true; clearTimeout(pollTimer); });
window.addEventListener('pageshow', event => {
  if (event.persisted) { stopped = false; void refresh().finally(schedulePoll); }
});
async function load() {
  await refresh();
  try {
    recipients = (await api('/api/v1/settings/report-recipients')).items || [];
    renderRecipients();
  } catch (e) { notice(e.message, 'error'); }
  schedulePoll();
}
load();
