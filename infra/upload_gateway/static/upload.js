const maxBytes = 100 * 1024 * 1024;
const dz = document.querySelector('#dropzone'), fi = document.querySelector('#file');
const send = document.querySelector('#send'), filename = document.querySelector('#filename');
const message = document.querySelector('#message'), statusBox = document.querySelector('#status');
const openProtocol = document.querySelector('#open-protocol');
let selected = null, protocol = null, duplicate = false, generation = 0, pollTimer = null;

function show(element, text, kind = 'info') {
  element.className = 'notice ' + kind;
  element.textContent = text;
}

function stopTracking() {
  generation++;
  if (pollTimer !== null) clearTimeout(pollTimer);
  pollTimer = null;
}

function choose(file) {
  stopTracking();
  selected = null;
  send.disabled = true;
  filename.textContent = '';
  statusBox.className = 'notice info hidden';
  openProtocol.classList.add('hidden');
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
    return show(message, 'Selecione um arquivo PDF.', 'error');
  }
  if (file.size > maxBytes) return show(message, 'O arquivo excede o limite de 100 MB.', 'error');
  selected = file;
  filename.textContent = `${file.name} · ${formatBytes(file.size)}`;
  send.disabled = false;
  message.className = 'notice hidden';
}

dz.onclick = () => fi.click();
dz.onkeydown = event => {
  if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); fi.click(); }
};
fi.onchange = () => choose(fi.files[0]);
['dragenter', 'dragover'].forEach(type => dz.addEventListener(type, event => {
  event.preventDefault(); dz.classList.add('active');
}));
['dragleave', 'drop'].forEach(type => dz.addEventListener(type, event => {
  event.preventDefault(); dz.classList.remove('active');
}));
dz.ondrop = event => choose(event.dataTransfer.files[0]);

send.onclick = async () => {
  if (!selected || send.disabled) return;
  stopTracking();
  const current = generation;
  send.disabled = true;
  show(message, 'Enviando e registrando o documento...');
  const body = new FormData();
  body.append('file', selected);
  try {
    const data = await api('/api/v1/submissions', {method: 'POST', body});
    if (current !== generation) return;
    protocol = data.submission_id;
    duplicate = data.duplicate === true;
    show(message, duplicate
      ? `Este PDF já foi enviado. O protocolo ${protocol} foi recuperado; nenhum novo processamento foi iniciado.`
      : `Protocolo ${protocol} registrado.`, duplicate ? 'info' : 'success');
    openProtocol.href = '/submissions/' + encodeURIComponent(protocol) + '/view'
      + (queryToken ? '?token=' + encodeURIComponent(queryToken) : '');
    openProtocol.textContent = duplicate ? 'Abrir protocolo existente' : 'Acompanhar processamento';
    openProtocol.classList.remove('hidden');
    await poll(current);
  } catch (error) {
    if (current !== generation) return;
    show(message, error.message, 'error');
    send.disabled = false;
  }
};

async function poll(current) {
  try {
    const data = await api('/api/v1/submissions/' + encodeURIComponent(protocol));
    if (current !== generation) return;
    const prefix = duplicate ? 'Status do protocolo existente' : 'Status';
    show(statusBox, `${prefix}: ${statusLabel(data.status)}${data.message ? ' · ' + data.message : ''}`);
    if (['concluido', 'erro', 'aguardando_revisao'].includes(data.status)) return;
    pollTimer = setTimeout(() => poll(current), 4000);
  } catch (_) {
    if (current === generation) pollTimer = setTimeout(() => poll(current), 5000);
  }
}

window.addEventListener('pagehide', stopTracking);
