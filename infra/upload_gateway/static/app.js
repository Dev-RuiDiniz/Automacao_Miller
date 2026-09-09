const queryToken = new URLSearchParams(location.search).get('token') || '';
const apiHeaders = () => queryToken ? {'X-Landing-Token': queryToken} : {};
const api = async (url, options = {}) => { const headers={...apiHeaders(),...(options.headers||{})}; const response=await fetch(url,{...options,headers,credentials:'same-origin'}); let data=null; try{data=await response.json()}catch(_){} if(!response.ok)throw new Error(data?.detail||'Não foi possível concluir a operação.'); return data; };
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[char]));
const statusLabel = value => ({recebido:'Recebido',processando:'Processando',aguardando_revisao:'Aguardando revisão',aguardando_envio:'Aguardando envio',concluido:'Concluído',erro:'Erro'}[value] || value);
const formatDate = value => value ? new Intl.DateTimeFormat('pt-BR',{dateStyle:'short',timeStyle:'short'}).format(new Date(value)) : '—';
const formatBytes = value => { const n=Number(value||0); if(!n)return '—'; const units=['B','KB','MB','GB']; const i=Math.min(Math.floor(Math.log(n)/Math.log(1024)),3); return `${(n/1024**i).toFixed(i?1:0)} ${units[i]}`; };
async function logout(){await fetch('/auth/logout',{method:'POST',credentials:'same-origin'});location.assign('/');}
document.querySelectorAll('[data-logout]').forEach(button=>button.addEventListener('click',logout));
if (queryToken) document.querySelectorAll('a[href^="/"]').forEach(link => {
  const url = new URL(link.href, location.origin);
  if (!url.searchParams.has('token')) { url.searchParams.set('token', queryToken); link.href = url.pathname + url.search; }
});
