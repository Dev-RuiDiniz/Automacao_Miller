import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const script = fs.readFileSync(new URL('../../infra/upload_gateway/static/upload.js', import.meta.url), 'utf8');

function screen({duplicate = false, status = 'erro', message = '', token = ''} = {}) {
  const nodes = new Map(), calls = [], timers = [], handlers = {};
  let readGate = null;
  const element = selector => {
    if (!nodes.has(selector)) {
      const node = {className: 'hidden', disabled: false, textContent: '', files: [],
        addEventListener() {}, click() {}};
      node.classList = {
        add(name) { node.className = [...new Set([...node.className.split(' '), name])].join(' '); },
        remove(name) { node.className = node.className.split(' ').filter(c => c !== name).join(' '); },
        contains(name) { return node.className.split(' ').includes(name); },
      };
      nodes.set(selector, node);
    }
    return nodes.get(selector);
  };
  const data = {submission_id: 'protocolo-sintetico', duplicate, status, message};
  const context = {document: {querySelector: element}, window: {addEventListener(name, fn) { handlers[name] = fn; }},
    queryToken: token, formatBytes: String, statusLabel: value => value === 'erro' ? 'Erro' : value,
    encodeURIComponent, FormData: class { append() {} },
    setTimeout(fn, ms) { timers.push({fn, ms}); return timers.length; }, clearTimeout() {},
    api: async (path, options = {}) => {
      calls.push({path, options});
      if (options.method !== 'POST' && readGate) await readGate;
      return {...data};
    },
  };
  vm.runInNewContext(script, context);
  return {nodes, calls, timers, handlers, data, context,
    choose(file = {name: 'sintetico.pdf', size: 10}) { context.choose(file); },
    readGate(value) { readGate = value; },
    send() { return nodes.get('#send').onclick(); }};
}

test('PDF já interrompido identifica protocolo existente e não solicita reprocessamento', async () => {
  const s = screen({duplicate: true, message: 'Processamento interrompido a pedido do usuário; progresso salvo preservado.', token: 'token-ficticio'});
  s.choose(); await s.send();
  assert.match(s.nodes.get('#message').textContent, /já foi enviado.*nenhum novo processamento/);
  assert.equal(s.nodes.get('#message').className, 'notice info');
  assert.match(s.nodes.get('#status').textContent, /^Status do protocolo existente: Erro/);
  assert.match(s.nodes.get('#status').textContent, /progresso salvo preservado/);
  assert.equal(s.nodes.get('#open-protocol').href, '/submissions/protocolo-sintetico/view?token=token-ficticio');
  assert.equal(s.nodes.get('#open-protocol').textContent, 'Abrir protocolo existente');
  assert.equal(s.calls.filter(c => c.options.method === 'POST').length, 1);
  assert.equal(s.calls.some(c => c.path.includes('/reprocess')), false);
  assert.equal(s.timers.length, 0);
});

test('upload novo mantém confirmação de registro e acompanhamento', async () => {
  const s = screen({status: 'processando'});
  s.choose(); await s.send();
  assert.equal(s.nodes.get('#message').className, 'notice success');
  assert.match(s.nodes.get('#message').textContent, /registrado/);
  assert.equal(s.nodes.get('#open-protocol').textContent, 'Acompanhar processamento');
  assert.equal(s.nodes.get('#status').textContent, 'Status: processando');
  assert.equal(s.timers[0].ms, 4000);
});

test('selecionar outro PDF impede status atrasado do protocolo anterior', async () => {
  const s = screen({duplicate: true, message: 'Cancelamento antigo.'});
  let release;
  s.readGate(new Promise(resolve => { release = resolve; }));
  s.choose(); const pending = s.send();
  await Promise.resolve(); await Promise.resolve();
  s.choose({name: 'outro.pdf', size: 20});
  release(); await pending;
  assert.equal(s.nodes.get('#status').classList.contains('hidden'), true);
  assert.equal(s.nodes.get('#open-protocol').classList.contains('hidden'), true);
  assert.equal(s.nodes.get('#send').disabled, false);
});
