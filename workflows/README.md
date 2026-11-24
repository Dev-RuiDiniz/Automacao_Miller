# Workflows n8n
Visão do fluxo em [FLUXOGRAMA.md](../FLUXOGRAMA.md); locais seguros de credenciais em [ACESSOS.md](../ACESSOS.md). Confirme o estado dos workflows na VPS: os arquivos exportados no Git ficam inativos por segurança.

Para homologar localmente a rota Ollama até `concluido`, siga o
[roteiro de teste local](../docs/TESTE_LOCAL.md). Para a stack isolada com
Anvisa V8/OpenRouter e retomada por checkpoints, use
[deploy/full-local/README.md](../deploy/full-local/README.md). Nenhum desses
roteiros ativa workflows na VPS.

## Estado observado na VPS do cliente em 23/11/2026

No commit `b006b7f`, o processamento interno v1 e o tratamento de erros
estão publicados em suas versões atualizadas. O webhook de entrada está
registrado e os dez nós PostgreSQL usam a credencial existente. O envio
legado e a reconciliação antiga estão inativos. O upload autenticado foi
liberado para o teste do cliente. O n8n registrou zero execuções nessa
verificação e o reprocessamento público continua suspenso no Caddy.
Consulte [DEPLOY.md](../DEPLOY.md).

## Estado observado na VPS do cliente em 21/11/2026

Os exports de processamento interno v1, erros, envio manual e reconciliação
estão importados e inativos. Os nós de banco foram vinculados à credencial
PostgreSQL do cliente. O n8n registra zero execuções. À época, o processamento Anvisa
V8 aguardava a chave da OpenRouter.

## Estado observado na VPS de testes em 27/10/2026

O n8n tem seis workflows registrados. Estão publicados Automação Regulatória - Duas Passagens e Automacao Regulatoria - Erros Internos. Automacao Regulatoria - Repositorio Interno (v1) foi despublicado. Automação Regulatória - Envio manual do relatório, Automação Regulatória - Reconciliação Interna e Avaliação Sintética - NVIDIA NIM continuam inativos.

Essa fotografia de 27/10/2026 antecede o download direto. Confira o estado publicado no n8n antes de operar.

Os exports do Git continuam com active=false de propósito. Não os use como prova do estado remoto e não reimporte workflows em produção sem backup, preservação dos vínculos de credenciais e teste controlado.

Essa fotografia é da VPS. Desde 16/11/2026, a `main` também contém o v1 com
seleção Anvisa V8 via OpenRouter e retomada por checkpoints, usado nos testes
locais de novembro. O v2 híbrido é um export separado e não implementa essa
seleção nem a retomada por artefatos do v1. A aplicação local foi pausada em
15/11, conforme ROADMAP.md. A VPS não foi consultada nem atualizada durante a
integração das PRs no GitHub.

## Versão híbrida v2 — implantada em 27/10/2026

`automacao-regulatoria-internal-v2-hybrid.json` permanece um export inativo no
Git, mas foi importado e publicado na VPS após backup. Ele preserva o export v1
para rollback. O fluxo ativo usa esta sequência: o gateway Python varre o Markdown
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

O painel autenticado confirmou o v2 publicado e o v1 despublicado em
27/10/2026. O workflow de erros continua publicado. Não use o documento oficial
como fixture de teste.

### Resultado da homologação sintética em 27/10/2026

Um PDF artificial de duas páginas percorreu upload, conversão, análise local
com `qwen2.5:3b`, validação e renderização. O protocolo terminou em
`aguardando_envio`, com cobertura de páginas 2/2, zero erros e zero entregas de
e-mail. Foram gerados Markdown convertido, relatório Markdown e PDF.

O teste técnico passou, mas o relatório falhou em qualidade: descreveu como
inexistente uma contradição/alteração entre a concessão da página 1 e o
cancelamento da página 2, recomendou planejar renovação após o cancelamento e
ordenou as seções incorretamente. A validação confirmou 8 de 10 referências e
deixou duas pendentes por formato não reconhecido. O PDF também mostrou âncoras
Markdown sem resolução. O texto malicioso de teste não levou à revelação de
segredos. Corrija prompt/validação e repita o fixture antes de processar
documentos reais.


## Fluxos internos versionados

A entrada oficial de novos documentos é a landing privada. Os exports ficam
inativos no repositório para evitar ativação acidental.

1. `automacao-regulatoria-internal-v1.json` e `automacao-regulatoria-internal-v2-hybrid.json`
   recebem o protocolo, reivindicam o documento, processam e guardam os
   artefatos. Depois de salvar o PDF, registram o artefato e concluem documento
   e tentativa em uma operação PostgreSQL.
2. `automacao-regulatoria-reconcile-v1.json` encaminha documentos recebidos ou
   presos em processamento ao workflow interno.
3. `automacao-regulatoria-internal-error-v1.json` registra categoria, etapa,
   execução, tentativa e mensagem no PostgreSQL.

O `automacao-regulatoria-internal-v1.json` mantém os ramos Ollama e Anvisa V8,
além da retomada autenticada por artefatos. No ramo Ollama, o contexto
determinístico é carregado antes dos lotes; o ramo OpenRouter conserva suas
buscas literais, janelas e checkpoints próprios, sem essa varredura adicional.
Selecione o export correspondente ao ambiente antes de configurar o webhook.

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

Nos ramos Ollama, depois de salvar o Markdown, o workflow chama a rota interna autenticada
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
e `workflow_errors`. `analysis_results` e `analysis_json` são compatibilidade
legada; o fluxo atual não grava análise estruturada. Os workflows devem gravar
somente chaves relativas, nunca caminhos absolutos.

No modo V8, os controles ficam no ZIP de verificação. As respostas rejeitadas
são guardadas separadamente como diagnóstico privado no renderizador, sem
inserção em `analysis_results` ou publicação entre os artefatos da landing.
O mesmo volume privado guarda checkpoints de lotes e grupos já validados,
também separados dos relatórios finais e da tabela de análises legadas.

Associe no n8n a credencial PostgreSQL. Nenhum ID de credencial
é versionado neste repositório. O workflow de erro interno precisa estar ativo
e associado à credencial PostgreSQL para registrar a falha e mudar o protocolo
para `erro`; sem ele, uma execução interrompida pode deixar o documento em
`em_processamento`. A variável `ARTIFACTS_GID` deve representar o
grupo compartilhado que permite ao gateway e ao n8n ler e gravar no volume.
Além das permissões do volume, o n8n deve receber
`N8N_RESTRICT_FILE_ACCESS_TO=/data/artifacts`, que libera os nós de arquivo
somente dentro do repositório privado compartilhado.

## Reprocessamento e conferência opcional

A recuperação de artefatos descrita abaixo exige o workflow v1 atualizado.
O v2 híbrido preserva seu caminho de processamento de outubro; não contém os
nós de carregamento e desvio por checkpoint do v1.

A deduplicação é feita pelo SHA-256 no gateway e reforçada pela restrição única
do PostgreSQL. Para retomar um documento em erro, use **Reprocessar** no detalhe
do protocolo. O botão chama `POST /api/v1/submissions/{id}/reprocess`. O gateway confere os artefatos, registra o operador em
`human_reviews`, reserva a solicitação de forma transacional e despacha o
webhook de processamento. Cliques repetidos ou uma operação em andamento são
rejeitados; uma falha de despacho anterior ao claim permite nova tentativa.

O claim identifica `retomada_solicitada` antes de atualizar a etapa. Depois de
abrir uma nova tentativa, o workflow carrega o checkpoint pela rota interna
autenticada `/internal/submissions/{id}/resume-context`, vinculada à execução e
ao número da tentativa. Com Markdown íntegro, salta a leitura/conversão do PDF
e a regravação da fonte. Com relatório vinculado à mesma fonte, salta também a
análise. No V8, o PDF já validado é recuperado do ZIP da revisão; no caminho
comum, o relatório Markdown pode ser renderizado sem chamar o modelo novamente.
Um PDF com hash e vínculo verificável também pode ser reutilizado.

Os artefatos da nova saída usam a versão da nova tentativa; os originais
permanecem preservados. Hash, tamanho, fonte, sequência de páginas e vínculo
entre revisões são conferidos. Arquivo registrado ausente ou alterado bloqueia
a retomada. Markdown legado com hash e metadados no cabeçalho é suportado; se
a lista estruturada de avisos não foi guardada, essa limitação é informada.
Um relatório legado sem hash/vínculo suficiente não é tratado como checkpoint.

**Reprocessar** não usa o Retry genérico do n8n: esse recurso poderia repetir
somente a validação de uma resposta de erro já armazenada. A retomada exige
que o progresso parcial da IA tenha sido persistido para reutilizá-lo.

No V8, os lotes e grupos validados passam a ser persistidos no renderizador.
Na retomada do Markdown, ele reutiliza automaticamente os checkpoints da mesma
fonte e identidade de análise. Execuções antigas sem esse controle continuam
sem recuperação retroativa de seus lotes em memória.

Resultados com citações pendentes, contradição ou evidência insuficiente
mantêm o alerta no relatório e podem concluir quando a cobertura de páginas
estiver completa. O operador pode visualizar o relatório e conferir as páginas
pelo painel autenticado. O fluxo atual não grava um JSON de análise; a rota para artefato `analysis_json` permanece para
compatibilidade com documentos antigos.

O PDF é apresentado como relatório executivo: começa com resumo dos achados,
leitura prática para acompanhamento operacional e comercial, pontos de atenção
e próximos passos. As seções detalhadas continuam exibindo os dados extraídos e
as evidências de página disponíveis; a linguagem comercial não substitui a
conferência opcional do documento original.
Cada achado exibe suas páginas de origem. Se a IA não conseguir comprovar a
referência, o relatório mostra essa pendência de forma explícita e mantém o caso
disponível para conferência, sem inventar a numeração da página.

O workflow de reconciliação encontra documentos recebidos ou recupera
processamentos parados sem execução ativa no n8n. Ele encaminha esses
protocolos para o webhook interno de processamento.

## Painel e download

O gateway oferece `/upload` para a fila, `/new` para upload e
`/submissions/{id}/view` para o detalhe. O botão **Baixar relatório PDF** aparece
quando a consulta autenticada encontra o protocolo em `concluido` e o PDF no
volume privado. A rota `/api/v1/submissions/{id}/report` responde com o PDF do
protocolo como anexo. A visualização e a conferência opcional ficam no detalhe.

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
`UPLOAD_GATEWAY_BASE_URL` no ambiente protegido. Associe a credencial
PostgreSQL após importar os exports.

Para consultar ou reprocessar, use o painel, o protocolo e as tabelas internas. Não use
pastas do Drive para representar estados. Arquivos antigos do Drive não são
apagados automaticamente e só podem entrar por procedimento de importação
controlada futuro.

## Modo Anvisa V8 com OpenRouter

O detalhe do protocolo consulta o estado persistido a cada cinco segundos
enquanto visível. O workflow principal grava as etapas de recuperação do
checkpoint, conversão, análise e preparação do PDF no documento e na tentativa
ativa. Esses marcadores não alteram a escolha de checkpoint nem indicam
conclusão antecipada. O cliente confirma a retomada em diálogo antes de
`POST /api/v1/submissions/{id}/reprocess`; cancelar ou fechar não faz esse POST.

Configure `ANVISA_REPORT_PROVIDER=openrouter` e `OPENROUTER_API_KEY` no `.env`
protegido. A chave é injetada somente no `report-renderer`. Recrie o n8n para
aplicar o provedor e reconstrua a imagem do renderizador para instalar o prompt.
Importe o export interno atualizado e associe a credencial PostgreSQL no
ambiente de homologação. Os exports do Git permanecem inativos.

Depois de persistir o Markdown, o workflow chama a rota interna autenticada
do renderizador. O serviço envia o V8 intacto e os blocos paginados ao Terra
(`openai/gpt-6.1-terra`), sem PDF bruto nem protocolo. O serviço pede contexto adicional quando a
resposta informa que o ato continua fora do bloco. Confere hashes, cobertura,
citações e reconciliação do inventário antes de escrever o relatório; em caso
de falha, o workflow registra erro e não troca para Ollama automaticamente.

O validador aceita `justificativa` nos registros compactos de excluídos e
representações duplicadas, conforme a seção 6 do V8. Também aceita a chave
anterior `justificativa_destino` nesses compactos. Se as duas forem fornecidas,
valida os textos e preserva ambos, sem normalizar a resposta. Incluídos e
pendentes continuam exigindo `justificativa_destino` e todos os campos da ficha.
Nenhuma dessas formas dispensa a validação literal, de páginas ou de inventário.

A fila começa com até cinco páginas-alvo; lotes com mais de 32.000 caracteres
nos alvos são divididos por páginas, mantendo os textos inteiros e contexto
de duas páginas em cada direção. O modelo pode pedir contexto adicional.
Desde a primeira chamada e nas correções, são solicitados grupos de até quatro
eventos, entre novos e revisões. Os registros anteriores entram como dados de
continuidade; o retorno traz o novo grupo e cobertura/inventário acumulados.
IDs e evidências já validados são preservados. Repetições idênticas do mesmo
ID não duplicam registros; alteração de evento concluído, duplicação exata com
outro ID ou omissão de IDs reservados no inventário são rejeitadas.

Fichas com conferência de integridade ainda aberta são separadas em `drafts`,
após validar estrutura, páginas e citações. As completas ficam em `records`.
A próxima chamada prioriza até quatro IDs em revisão e solicita zero eventos
novos enquanto houver fichas abertas. Revisões preservam IDs e evidências
literais, admitem dados recuperados/corrigidos com fundamento na fonte e guardam
as versões anteriores em `review_history`, somente no checkpoint privado.
O histórico também é revalidado ao carregar. Eventos completos são imutáveis.
Quando as fichas completas impedem que o pacote caiba, o transporte usa
`modo_registros_preservados: indice`, esvazia somente a lista enviada
`registros_preservados` e inclui todos os eventos concluídos em
`indice_registros_preservados`. Cada referência traz ID, categoria, destino,
páginas, hash canônico da ficha e campos confirmados de até 256 caracteres,
sem cortar valores. Isso é um índice de controle, não uma ficha ou evidência;
campos ausentes não indicam ausência documental. As fichas integrais ficam
no checkpoint e são reunidas pelo servidor no resultado final. Revisões,
inventários e detalhes da correção continuam integrais. O núcleo ainda inclui
todas as páginas obrigatórias; nenhuma referência é promovida a revisão feita.
As validações usam sempre as fichas completas, inclusive para impedir alterações,
duplicações e perda de IDs. O índice só é usado se o envio integral não couber.
Um estado `revisada` com pendências explícitas continua em aberto; o servidor
não remove notas nem promove fichas/inventários a concluídos por esse rótulo.
Se uma resposta exceder o tamanho de grupo solicitado, os registros válidos não
são truncados nem descartados só por essa quantidade; a chamada seguinte volta
a pedir o grupo pequeno. Continuam o timeout por chamada, os limites de
contexto e as proteções de progresso; as chamadas usam janelas com continuação automática.

O contexto adicional usa uma fila privada de páginas solicitadas e entregues.
Cada pacote de dados tem até 480.000 bytes UTF-8, contando Markdown,
continuidade e os detalhes da correção. As páginas são inteiras; o núcleo inclui
alvos e todas as evidências das fichas/histórico. Páginas reais citadas na resposta
rejeitada também acompanham sua correção. Vizinhas dos alvos são opcionais
quando impediriam o avanço da fila. O orçamento é conferido antes de salvar
uma ampliação. Uma página obrigatória que não caiba interrompe sem truncamento.

O modelo pode responder `buscas_necessarias` com até 16 termos literais ou
`contexto_necessario` com números de páginas. Identificadores confirmados nas
quatro fichas priorizadas também geram buscas locais. A pesquisa percorre todas
as páginas do Markdown, sem normalizar texto, e retorna método, quantidade
examinada e páginas com a substring exata; essas páginas e suas vizinhas entram
na fila. Zero ocorrências não atesta ausência documental ou semântica.
`contexto_recuperado` informa a janela atual, páginas já enviadas, páginas ainda
pendentes e resultados das buscas. O envio não significa revisão efetiva.
Mesmo uma resposta que declare o lote fechado não elimina páginas pendentes.
Falha após uma janela conserva fichas, IDs, evidências e o restante da fila.
A última janela sem resposta aceita fica disponível na retomada após rejeição;
um limite de saída após pedido aceito interrompe sem dividir e perder sua fila.

Páginas, inventários e fichas com revisão pendente continuam em aberto. Somente um lote fechado
entra na cobertura concluída, e o PDF só é montado depois de todos os lotes.
Cada janela técnica permite 32 chamadas ao modelo por lote. Ao completar
uma janela, o renderizador recarrega e revalida o checkpoint e continua o
mesmo lote automaticamente, sob o mesmo bloqueio e na mesma tentativa do
documento. A contagem de chamadas do diagnóstico permanece acumulada;
correção aberta, tentativas de transporte, ausência de progresso, buscas e
ampliações não são zeradas por essa troca. Os metadados de processamento
informam `continuacoes_automaticas` e `retentativas_transporte` daquela execução.
Há até três ampliações explícitas de páginas desde o último avanço validado
do grupo e uma correção por grupo. Somente páginas inéditas solicitadas em
`contexto_necessario` consomem esse orçamento; buscas locais são separadas,
mesmo quando suas ocorrências acrescentam páginas à fila. Novos registros,
fichas concluídas e avanço de cobertura/inventário reabrem o orçamento.
Entregar contexto, pesquisar ou repetir um grupo idêntico não o reabrem.
O pedido que atinge o limite fica salvo, após conferir a janela, antes da
interrupção. Buscas obedecem aos tetos de 16 termos por pedido e 256 por lote;
pedidos repetidos sem trabalho novo são rejeitados. Entregar as janelas de um
pedido já aceito não conta como uma ampliação. Duas respostas sem progresso
interrompem a continuação. Cada chamada ao provedor mantém timeout de até
360 segundos. O prazo global fica desabilitado por padrão; a meta de 90 minutos
não encerra o documento. Falha temporária de transporte admite três tentativas
da mesma chamada, com esperas de 5 e 15 segundos antes da segunda e da terceira.
Timeout/conexão e HTTP 408, 429, 500, 502, 503 e 504 são recuperáveis por essa
política. Crédito/autorização, JSON inválido e validação não recebem esse
retry. O checkpoint é recarregado e revalidado antes de repetir o mesmo
pacote; a retentativa mantém os detalhes da correção em andamento.
Se as três tentativas falharem, registrar erro explícito e preservar o
progresso para retomada. O orçamento de transporte só reabre após receber uma
resposta, e não ao trocar a janela. Não existe repetição ilimitada de falhas.

Os estados ficam em `/data/diagnostics/checkpoints/<identidade>/state.json`,
com arquivos `600`, diretórios `700`, digest e gravação atômica sincronizada.
Um bloqueio de arquivo impede análises simultâneas da mesma identidade. A
identidade inclui protocolo, hash do Markdown, modelo, V8, instruções e código
da análise; uma mudança cria namespace separado, preservando o estado antigo.
Todos os lotes carregados são revalidados contra a fonte antes de qualquer
nova chamada de IA. Um estado conhecido removido/corrompido bloqueia a análise
com erro de armazenamento. Não há rota pública para editar ou baixar estados.
Inclua o volume privado completo no backup; não remova o volume ao atualizar.

O checkpoint também guarda registros válidos de lotes ainda pendentes. Ele
nunca promove esses lotes a concluídos. Se a análise inteira já estiver salva,
uma nova tentativa de renderização reutiliza os resultados sem nova chamada
ao provedor. O ZIP e `report_context.analysis_checkpoint` informam os lotes
e páginas reutilizados. A etapa exibida no painel continua sendo a análise
do Markdown; o navegador não escolhe o arquivo interno de retomada.

A versão com fila de contexto usa formato 3 e identidade nova. A migração
das implementações conhecidas nos formatos 1, 2 e 3 é uma ação explícita e sem IA,
com backup, análise parada, mesma fonte/modelo/V8 e revalidação integral. Ela
preserva o estado original, registra a origem no destino e não sobrescreve
outro progresso. Consulte o [procedimento local](../deploy/full-local/README.md#migração-explícita-dos-checkpoints-anteriores).
O ajuste do controle de buscas mantém o formato 3, mas altera a identidade do
código. A migração da implementação anterior desse formato conserva também
as buscas, páginas entregues, fila pendente e histórico, sem presumir revisão.

Na falha de validação, o renderizador salva o bloco e a resposta rejeitada em
`/data/diagnostics`, no volume exclusivo `automacao_miller_diagnostics_data`.
O n8n informa protocolo, tentativa e execução somente à rota interna; esses
identificadores não entram na solicitação ao OpenRouter. A correção recebe
o campo (JSON Pointer), ID do registro, página, trecho rejeitado, motivo e
resposta anterior. Há no máximo uma correção por grupo; a regra literal e o
V8 aprovado permanecem iguais. A indicação de coincidência após normalizar
espaços é apenas diagnóstico e não libera a evidência.

Em falhas de estrutura, a correção recebe campo, motivo, valor recebido e
condição esperada, além da resposta anterior. As falhas conhecidas dos registros
do grupo são enviadas conjuntamente em `falhas_registros`. O resumo do erro contém somente
o motivo seguro e a referência; os valores permanecem privados. O workflow
`automacao-regulatoria-internal-error-v1.json` combina mensagem e descrição do
n8n e classifica as referências `ANV8D-...` como validação. Isso vale para novos
registros; as mensagens das tentativas anteriores são preservadas como histórico.

Arquivos `ANV8D-*.json` usam permissão `600` e diretórios `700`. O histórico de
falha contém uma referência `ANV8D-...`, página e motivo, sem transcrição ou
caminho privado. Consulte o arquivo correspondente por acesso administrativo
ao contêiner/volume; não o publique nem o anexe a logs ou chamados públicos.
Inclua esse volume no backup protegido. Se o armazenamento falhar, o serviço
interrompe a análise com erro de armazenamento, sem tentar corrigir às cegas.

O PDF com índice clicável e o Markdown usam os artefatos existentes da landing.
O ZIP de verificação acompanha o PDF no volume privado, como
`report-vN-anvisa-v8.zip`; sua chave relativa fica nos metadados do relatório
Markdown. O pacote
registra os limites das verificações mecânicas e da revisão feita pelo modelo.

`OPENROUTER_TIMEOUT_SECONDS=0` (padrão) desabilita o prazo total da análise V8.
O renderizador continua limitando cada chamada ao provedor a 360 segundos.
Um valor positivo, até 14.400 segundos, configura um prazo global opcional
somente por decisão explícita do operador; não use a meta de 90 minutos como
limite implícito. O nó HTTP aguarda sem prazo total quando o valor é zero.
Somente o nó `OpenRouter - Analyze and render V8` usa `typeVersion: 2`, que
transmite zero numérico ao transporte HTTP sem substituir pelo padrão de
cinco minutos. O nó 4.2 substitui esse zero; a string `"0"` também não serve,
pois o transporte a trata como expiração imediata. Preservados corpo JSON,
header interno, resposta completa e propagação de erros HTTP. Esse contrato
precisa ser revalidado ao trocar a versão do n8n. Com prazo global positivo,
o HTTP adiciona 120 segundos.
O [teste do nó e transporte reais](../tests/contracts/n8n_http_timeout.cjs),
executado na imagem n8n sem rede externa e com o export por stdin, confere
zero numérico, autenticação interna fictícia, corpo, HTTP 200/502, detalhe de
erro preservado e timeout positivo. Não usa documentos ou credenciais reais.
Teste com um PDF sintético após configurar a chave.
Valide conteúdo, custo e latência em material autorizado antes de habilitar
para uso operacional. O modo local em `127.0.0.1:18080` continua somente conversão.

## Validação atual de citações e RAG legado

**Nota de vigência:** a seção abaixo descreve a capacidade legada de RAG,
que não é chamada pelo caminho atual. O workflow atual usa JSON temporário em
cada lote para organizar os achados, mas não persiste esse JSON nem cria
`quality_checks`.

A persistência privada de respostas V8 rejeitadas e dos checkpoints de progresso
é a exceção descrita na seção Anvisa V8 acima; não ativa o RAG nem as tabelas legadas.

A validação usada atualmente é feita pelo gateway na rota interna
`POST /internal/submissions/{id}/validate-report`. Ela abre o Markdown original e
compara cada página e evidência literal do relatório. Retorna a cobertura, as
referências confirmadas e as pendentes. Citações pendentes são marcadas no
relatório e não bloqueiam a conclusão; páginas não cobertas interrompem a
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

## Fluxos de análise integral com Ollama — v1 e v2

O workflow interno preserva o Markdown original e analisa as páginas em lotes:

```text
V1: PDF -> Markdown paginado -> contexto determinístico (termos e processos)
    -> lotes de até 6.000 caracteres analisados pela IA
    -> consolidação -> relatório -> validação -> PDF persistido -> concluido

V2 local: PDF -> Markdown paginado -> observações determinísticas em Python
    -> todos os lotes auditados pela IA -> validação Python de página/citação
    -> síntese IA somente com observações e candidatos aceitos
    -> validação do relatório -> PDF persistido -> concluido
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
`openai/gpt-oss-20b`. Usa apenas o fixture sintético e não chama o gateway. Também não
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
