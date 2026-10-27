# Workflows n8n
Visão do fluxo em [FLUXOGRAMA.md](../FLUXOGRAMA.md); locais seguros de credenciais em [ACESSOS.md](../ACESSOS.md). Confirme o estado dos workflows na VPS: os arquivos exportados no Git ficam inativos por segurança.

## Estado observado na VPS em 26/10/2026

O n8n tinha cinco workflows registrados. Estavam ativos somente Automação Regulatória - Repositório Interno e Automação Regulatória - Erros Internos. Automação Regulatória - Envio manual do relatório, Automação Regulatória - Reconciliação Interna e Avaliação Sintética - NVIDIA NIM estavam inativos.

Por isso, um relatório pode chegar a aguardando_envio, mas a solicitação de envio não está operacional até que o workflow de Gmail seja publicado, configurado e testado. A reconciliação também não recupera documentos ou entregas parados enquanto estiver inativa. Este estado é uma fotografia da consulta; confira novamente no n8n antes de operar.

Os exports do Git continuam com active=false de propósito. Não os use como prova do estado remoto e não reimporte workflows em produção sem backup, preservação dos vínculos de credenciais e teste controlado.

## Versão híbrida v2 — trabalho local de 27/10/2026

`automacao-regulatoria-internal-v2-hybrid.json` é um export novo e inativo. Ele
preserva o v1 e propõe esta sequência: o gateway Python varre o Markdown
persistido e registra observações literais; a IA audita cada lote à procura de
lacunas; Python confere a página, o lote e a citação de cada candidato; e a IA
redige o relatório usando somente os candidatos aceitos e as observações. O
prompt da auditoria está em `prompts/regulatory-gap-audit-v1.md`, com contrato
em `prompts/regulatory-gap-audit-v1.schema.json`.

A rota autenticada
`POST /internal/submissions/{id}/validate-ai-audit` relê o Markdown salvo e
faz essa conferência. Ela só verifica localização de evidência; não prova que a
conclusão proposta pela IA está correta. Candidatos rejeitados ficam pendentes e
fora do prompt de síntese. A versão continua usando IA em todos os lotes e para
interpretar o relatório.

Este export ainda não foi importado nem ativado na VPS. A última consulta
remota, em 26/10/2026, mostrava o v1 ativo. Antes de implantação, faça backup,
revise diff e credenciais, teste com fixture sintético e homologue em ambiente
controlado. Não use o documento oficial como fixture de teste.


## Fluxo ativo

A origem oficial de novos documentos é a landing privada. Os exports ficam
inativos no repositório para evitar ativação acidental. Na homologação local,
importe os workflows de processamento e de erro interno, associe a credencial
PostgreSQL aos dois e ative ambos. Mantenha o envio por e-mail e a reconciliação
inativos no teste ponta a ponta:

1. `automacao-regulatoria-internal-v1.json` — recebe o protocolo, reivindica o
   documento no PostgreSQL, lê o PDF do volume, converte, analisa, grava os
   artefatos e deixa o documento em `aguardando_envio`, com alertas de qualidade
   e referências para conferência opcional;
2. `automacao-regulatoria-send-report-v1.json` — recebe a solicitação manual do
   painel, reivindica a entrega, lê o relatório do volume, envia pelo Gmail e
   marca `concluido` somente após sucesso;
3. `automacao-regulatoria-reconcile-v1.json` — recupera documentos presos em
   processamento e entregas de e-mail paradas e as despacha ao workflow correto;
4. `automacao-regulatoria-internal-error-v1.json` — registra categoria, etapa,
   execução, tentativa e mensagem no PostgreSQL.

Os exports `automacao-regulatoria-v1.json`, `automacao-regulatoria-intake-v1.json`,
`automacao-regulatoria-completion-v1.json` e
`automacao-regulatoria-error-v1.json` são históricos da homologação com Google
Drive. Permanecem versionados e inativos para auditoria e rollback, sem serem
parte do fluxo ativo.

## Repositório interno

O gateway e o n8n compartilham `/data/artifacts`, proveniente do volume Docker
`automacao_miller_artifacts_data`. A organização é determinística por SHA-256:

```text
/data/artifacts/objects/ab/cd/<sha256>/
  original.pdf
  markdown-v1.md
  report-v1.md
  report-v1.pdf
```

O sufixo `v1` no exemplo representa a primeira tentativa; novas tentativas
recebem sua própria versão. O workflow atual não grava `analysis-vN.json`.

Depois de salvar o Markdown, o workflow chama a rota interna autenticada
`POST /internal/submissions/{id}/deterministic-context`. O gateway relê o
artefato salvo, registra menções literais de uma lista de termos e identificadores
de processo conhecidos, e relaciona identificadores iguais encontrados em
páginas diferentes. Esses dados são pistas com página e trecho, não uma
classificação de status ou prova de que duas ocorrências sejam o mesmo ato. A
síntese recebe vínculos associados aos achados; o relatório lista as menções e
ocorrências relacionadas para conferência. A etapa não exige embeddings nem
ativa o serviço legado `rag-service`.

O PostgreSQL é a fonte de verdade. As tabelas operacionais incluem
`documents`, `artifacts`, `processing_attempts`, `human_reviews`,
`workflow_errors`, `report_recipients`, `document_recipients` e
`email_deliveries`. `analysis_results` e `analysis_json` são compatibilidade
legada; o fluxo atual não grava análise estruturada. Os workflows devem gravar
somente chaves relativas, nunca caminhos absolutos.

Associe no n8n apenas as credenciais PostgreSQL e Gmail. Nenhum ID de credencial
é versionado neste repositório. O workflow de erro interno precisa estar ativo
e associado à credencial PostgreSQL para registrar a falha e mudar o protocolo
para `erro`; sem ele, uma execução interrompida pode deixar o documento em
`em_processamento`. A variável `ARTIFACTS_GID` deve representar o
grupo compartilhado que permite ao gateway e ao n8n ler e gravar no volume.
Além das permissões do volume, o n8n deve receber
`N8N_RESTRICT_FILE_ACCESS_TO=/data/artifacts`, que libera os nós de arquivo
somente dentro do repositório privado compartilhado.

## Reprocessamento e conferência opcional

A deduplicação é feita pelo SHA-256 no gateway e reforçada pela restrição única
do PostgreSQL. Para autorizar reprocessamento, registre a decisão em
`human_reviews`, mantenha o PDF no volume e devolva o documento ao estado
`recebido`; o workflow de reconciliação fará o despacho pelo webhook interno.

Resultados com citações pendentes, contradição ou evidência insuficiente
seguem em `aguardando_envio` com o alerta preservado no relatório, desde que
a cobertura de páginas esteja completa. O download oficial só é
liberado quando o PostgreSQL indicar `concluido`. O operador pode visualizar o
PDF e o Markdown pelo painel autenticado e confirmar as páginas quando desejar,
mas essa conferência não é obrigatória para solicitar o envio. O fluxo atual não
grava um JSON de análise; a rota para artefato `analysis_json` permanece para
compatibilidade com documentos antigos.

O PDF é apresentado como relatório executivo: começa com resumo dos achados,
leitura prática para acompanhamento operacional e comercial, pontos de atenção
e próximos passos. As seções detalhadas continuam exibindo os dados extraídos e
as evidências de página disponíveis; a linguagem comercial não substitui a
conferência opcional do documento original.
Cada achado exibe suas páginas de origem. Se a IA não conseguir comprovar a
referência, o relatório mostra essa pendência de forma explícita e mantém o caso
disponível para conferência, sem inventar a numeração da página.

O workflow de reconciliação diferencia tarefas de documentos e entregas de
e-mail. Quando uma entrega fica em `enviando` por mais de 15 minutos e não há
uma execução n8n ativa, a reconciliação volta seu estado para `solicitado`,
carrega `delivery_id` e `submission_id` e chama o workflow
`automacao-regulatoria-send-report`. Documentos recebidos ou recuperados de uma
execução parada continuam sendo enviados ao workflow interno de processamento.
Assim, a retomada do e-mail não inicia novamente a análise do PDF.

## Painel e envio manual

O gateway oferece `/upload` para a fila, `/new` para upload,
`/submissions/{id}/view` para o detalhe e `/settings/recipients` para a lista
de destinatários. As APIs autenticadas mantêm os destinatários padrão e o
snapshot específico de cada envio no PostgreSQL. O workflow de envio recebe
`submission_id` e `delivery_id`; não consulta pastas do Drive e não usa
`REPORT_RECIPIENTS` como fonte operacional.

## Documentos extensos

No workflow v1, as páginas do Markdown convertido são analisadas em lotes de até
6.000 caracteres. Cada lote preserva os números das páginas; páginas muito
longas são divididas por parágrafo e, se necessário, por trechos menores. Os
resultados dos lotes são combinados e duplicatas são removidas. Se qualquer
lote falhar ou a contagem de páginas não corresponder ao PDF, o processamento
falha e não cria um relatório parcial. O Markdown integral permanece guardado
no volume e relacionado ao documento no PostgreSQL. A leitura por regras é
executada sobre esse Markdown salvo antes da análise. O v1 envia todos os lotes
diretamente para extração por IA.

No v2 híbrido local, a IA também percorre todos os lotes, mas para procurar
lacunas nas observações do Python. Cada sugestão retorna página e trecho. O
gateway valida essas citações no Markdown persistido antes da síntese final.
Isso reduz o que a síntese precisa considerar, mas não reduz a auditoria a
apenas páginas ambíguas e não elimina chamadas de IA.

O nó `Loop Over Items` envia um lote por vez ao Ollama e espera cada resposta
antes de continuar. Sem essa sequência, o n8n pode iniciar centenas de chamadas
simultâneas e exceder a memória do modelo. Essa proteção reduz picos de memória,
mas aumenta o tempo de processamento de documentos extensos. A análise de cada
lote usa contexto de 4.096 tokens; mantenha `OLLAMA_NUM_PARALLEL=1` no ambiente
local de pouca memória.

`PDF_CONVERTER_TIMEOUT_SECONDS` é configurado em segundos. O workflow converte
essa unidade para milissegundos, como exige o nó HTTP do n8n. O padrão é 300
segundos (300.000 milissegundos). A conversão não é repetida automaticamente:
repetir uma conversão demorada pode sobrecarregar o serviço; falhas são
registradas pelo workflow de erro e exigem reprocessamento explícito.

## Operação

Configure `LANDING_ACCESS_TOKEN`, `INTERNAL_API_TOKEN`,
`N8N_INTERNAL_PROCESSING_WEBHOOK_URL`, `ARTIFACT_STORAGE_DIR` e
`UPLOAD_GATEWAY_BASE_URL` no ambiente protegido. Gmail e PostgreSQL devem ser
associados após a importação dos exports.

Para consultar ou reprocessar, use o painel, o protocolo e as tabelas internas. Não use
pastas do Drive para representar estados. Arquivos antigos do Drive não são
apagados automaticamente e só podem entrar por procedimento de importação
controlada futuro.

## Validação atual de citações e RAG legado

**Nota de vigência:** a seção abaixo descreve a capacidade legada de RAG,
que não é chamada pelo caminho atual. O workflow atual usa JSON temporário em
cada lote para organizar os achados, mas não persiste esse JSON nem cria
`quality_checks`.

A validação usada atualmente é feita pelo gateway na rota interna
`POST /internal/submissions/{id}/validate-report`. Ela abre o Markdown original e
compara cada página e evidência literal do relatório. Retorna a cobertura, as
referências confirmadas e as pendentes. Citações pendentes são marcadas no
relatório e não bloqueiam a entrega; páginas não cobertas interrompem a
geração para impedir relatório parcial.

A capacidade legada de RAG funciona assim: depois de persistir o Markdown, o workflow chama o serviço interno
`RAG_SERVICE_BASE_URL` para indexar chunks por página, executar busca híbrida e
registrar os chunks recuperados. O contexto enviado ao Ollama contém o marcador
`## Página N`, o protocolo e a instrução de copiar evidência curta.

O nó `RAG - Validate citations` confere o resultado contra os chunks do mesmo
documento, incluindo páginas existentes, trecho literal normalizado, status
permitido e classificação de dispositivos. O resultado segue com avisos e
limitações quando houver falha de qualidade, sem bloquear a disponibilização do
relatório quando não houver falha técnica.

O contrato histórico de análise estruturada é o `regulatory-extraction-v3`. O
contrato ativo é o `regulatory-extraction-v6-full-document-batched-deterministic-context`, orientado
a inteligência regulatória e impacto de mercado. O relatório responde a nove perguntas:
o que aconteceu; quem é afetado; qual é o status regulatório; qual é o impacto
direto no negócio; qual é o impacto potencial de mercado; se existe urgência ou
prazo; o que a empresa deve fazer agora; o que ainda não foi comprovado; e qual
é a prioridade executiva. O Ollama retorna Markdown com seções obrigatórias,
plano de ação e referências de páginas. Respostas e ações usam listas com
marcadores para manter a leitura do PDF clara. A análise não é parecer
regulatório definitivo e a conferência humana é opcional.

Para reconstruir a base de embeddings, execute a indexação somente para os
Markdowns já persistidos e mantenha os workflows antigos do Drive inativos.

## Fluxo de análise integral no v1 e proposta do v2

O workflow interno preserva o Markdown original e analisa as páginas em lotes:

```text
V1: PDF -> Markdown paginado -> contexto determinístico (termos e processos)
    -> lotes de até 6.000 caracteres analisados pela IA
    -> consolidação -> relatório -> validação -> PDF -> aguardando_envio

V2 local: PDF -> Markdown paginado -> observações determinísticas em Python
    -> todos os lotes auditados pela IA -> validação Python de página/citação
    -> síntese IA somente com observações e candidatos aceitos
    -> validação do relatório -> PDF -> aguardando_envio
```

O artefato `report_markdown` é preservado junto do `report_pdf`. O prompt
`regulatory-extraction-v6.md` define a extração estruturada e a consolidação,
inclui as pistas determinísticas entre páginas e orienta o modelo a ignorar
instruções embutidas no conteúdo do PDF.
O JSON de cada lote é temporário e não é persistido como análise do documento.
RAG, embeddings e `quality_checks` continuam fora do caminho ativo. O envio, a
reconciliação, o tratamento de erros e o download oficial seguem sem alterações.

## Avaliação sintética da API NVIDIA

`nvidia-synthetic-api-eval-v1.json` é um workflow manual, inativo e isolado do
upload. Ele envia somente o fixture artificial
`tests/fixtures/synthetic-regulatory-sample.md` ao endpoint
`https://integrate.api.nvidia.com/v1/chat/completions`, usando o modelo
`openai/gpt-oss-20b`. Não lê arquivos, não chama o gateway nem o Gmail e não
altera o workflow de documentos reais. O resultado passa por validação JSON e
conferência literal da página/evidência contra o próprio fixture; a latência e
os tokens reportados pela API são exibidos na saída.

Para executar:

1. Crie no n8n uma credencial `HTTP Header Auth` com o cabeçalho `Authorization`
   e valor `Bearer <chave NVIDIA>`. Não coloque a chave no export, no `.env`, nos
   logs ou no chat.
2. Importe o export inativo e selecione a credencial no nó
   `NVIDIA - Analyze synthetic fixture`.
3. Execute manualmente o workflow e confira `latency_ms`, uso de tokens,
   quantidade de achados e validação da evidência.
4. Mantenha o workflow inativo ao terminar. A execução não usa nem representa o
   PDF recebido: mede uma requisição curta com texto artificial e não prova o
   tempo ou a precisão do processamento real de 142 páginas.

A NVIDIA API Catalog/Developer é um endpoint de prototipação e teste, com
limites/créditos dependentes da conta. Os termos do Trial restringem informação
governamental, confidencial, pessoal, financeira ou de saúde sem permissão
expressa do serviço e permitem o uso de conteúdo para melhoria de produtos e
modelos, além de logs de segurança. Não envie PDF real a esse endpoint.

O projeto passa a prever um workflow separado para NVIDIA NIM de produção,
condicionado a licença/assinatura apropriada e a termos que permitam
expressamente o tipo de dado. Esse workflow ainda não foi implementado nem
configurado. Faça primeiro o teste sintético, guarde a credencial de produção
somente no cofre do n8n e registre provedor/modelo em cada tentativa. A chave
enviada no chat está comprometida e deve ser revogada; não foi instalada no
n8n.

Fontes: [termos oficiais da NVIDIA API Trial](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf) e [FAQ oficial do NVIDIA NIM](https://docs.api.nvidia.com/nim/docs/product).
