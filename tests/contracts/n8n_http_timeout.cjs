// Executar dentro da imagem n8n, sem rede externa, recebendo o export por stdin.
const fs = require('fs');
const http = require('http');
const assert = require('assert/strict');
const { HttpRequestV2 } = require('/usr/local/lib/node_modules/n8n/node_modules/n8n-nodes-base/dist/nodes/HttpRequest/V2/HttpRequestV2.node.js');
const base = '/usr/local/lib/node_modules/n8n/node_modules/n8n-core/dist/execution-engine/node-execution-context/utils/';
require(base + 'request-helper-functions.js');
const { proxyRequestToAxios } = require(base + 'request-helpers/legacy-request-adapter.js');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const workflow = Array.isArray(input) ? input[0] : input;
const exported = workflow.nodes.find(node => node.name === 'OpenRouter - Analyze and render V8');
const evaluate = (expression, names, values) => new Function(...names, 'return (' + expression.slice(3, -2) + ')')(...values);
const timeout = evaluate(exported.parameters.options.timeout, ['$env'], [{ OPENROUTER_TIMEOUT_SECONDS: '0' }]);
assert.equal(exported.typeVersion, 2);
assert.equal(timeout, 0);
const source = {submission_id:'protocolo-sintetico',source_filename:'sintetico.pdf',attempt_number:1,
  markdown:'## Página 1\nDocumento sintético.\n',metadata:{page_count:1,markdown_sha256:'hash-ficticio'},warnings:[]};
const body = evaluate(exported.parameters.bodyParametersJson, ['$', '$execution'], [() => ({first: () => ({json:source})}), {id:'execucao-sintetica'}]);
const headers = evaluate(exported.parameters.headerParametersJson, ['$env'], [{INTERNAL_API_TOKEN:'token-ficticio'}]);
const seenTimeouts = [];
const nativeSetTimeout = http.ClientRequest.prototype.setTimeout;
http.ClientRequest.prototype.setTimeout = function(value, ...args) {
  seenTimeouts.push(value);
  return nativeSetTimeout.call(this, value, ...args);
};
let desiredStatus = 200;
let received;
const server = http.createServer((req, res) => {
  let content = '';
  req.on('data', chunk => {content += chunk;});
  req.on('end', () => {
    received = {headers:req.headers,body:JSON.parse(content)};
    setTimeout(() => {
      res.statusCode = desiredStatus;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify(desiredStatus === 200 ? {sintetico:true} : {detail:'IA: falha sintética preservada.'}));
    }, 150);
  });
});

async function execute(timeoutValue) {
  const parameters = {...exported.parameters,url:'http://127.0.0.1:'+server.address().port,
    bodyParametersJson:body,headerParametersJson:headers,options:{...exported.parameters.options,timeout:timeoutValue}};
  const node = {...exported,parameters};
  const context = {
    getNode:() => node,getInputData:() => [{json:{sintetico:true}}],
    getNodeParameter:(name,index,fallback) => name.split('.').reduce((value,key) => value?.[key],parameters) ?? fallback,
    continueOnFail:() => false,sendMessageToUI:() => {},
    helpers:{request:options => {
      assert.equal(options.timeout,timeoutValue);
      return proxyRequestToAxios({id:'teste-local'}, {},node,options);
    }},
  };
  return new HttpRequestV2({}).execute.call(context);
}

(async () => {
  await new Promise(resolve => server.listen(0,'127.0.0.1',resolve));
  try {
    const success = await execute(timeout);
    assert.equal(success[0][0].json.statusCode,200);
    assert.equal(success[0][0].json.body.sintetico,true);
    assert.equal(received.headers['x-internal-token'],'token-ficticio');
    assert.deepEqual(received.body,{markdown:source.markdown,page_count:1,markdown_sha256:'hash-ficticio',
      source_filename:source.source_filename,warnings:[],diagnostic_context:{submission_id:source.submission_id,attempt_number:1,execution_id:'execucao-sintetica'}});
    desiredStatus = 502;
    const failure = await execute(timeout);
    assert.equal(failure[0][0].json.statusCode,502);
    assert.equal(failure[0][0].json.body.detail,'IA: falha sintética preservada.');
    assert(seenTimeouts.length > 0 && seenTimeouts.every(value => value === 0));
    const prepare = workflow.nodes.find(node => node.name === 'OpenRouter - Prepare verification bundle').parameters.jsCode;
    const AsyncFunction = Object.getPrototypeOf(async function() {}).constructor;
    await assert.rejects(new AsyncFunction('$json',prepare)(failure[0][0].json),/falha sintética preservada/);
    desiredStatus = 200;
    await assert.rejects(execute(30),/aborted|timeout|timed out/i);
    console.log(JSON.stringify({timeout_zero:true,success_status:200,error_status:502,
      body_and_header_preserved:true,error_detail_preserved:true,finite_call_timeout:true,external_calls:0}));
  } finally {
    server.close();
    http.ClientRequest.prototype.setTimeout = nativeSetTimeout;
  }
})().catch(error => {console.error(error.message);process.exitCode = 1;server.close();});
