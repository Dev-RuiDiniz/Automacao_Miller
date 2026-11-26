# ROADMAP.md — plano de execução da Automação Miller

**Atualizado em:** 26 de novembro de 2026
**Objetivo:** transformar o estado atual em uma operação segura, validada e aceita pelo responsável operacional.

## VPS do cliente — verificada em 21/11/2026

O commit `3cac700` foi instalado em `srv2147368.hstgr.cloud` em uma stack
nova com seis serviços saudáveis. `https://reportai.info` serve a landing
privada com certificado válido. O n8n permanece acessível por túnel SSH.
Foram verificados login, logout, cookie seguro, restrição de rotas internas e
o backup inicial do banco e dos artefatos.

Na verificação de 21/11, o modo Anvisa V8 estava configurado para OpenRouter.
Os quatro workflows estavam importados e inativos, com zero execuções. O
comando `miller-configurar-openrouter` ficou preparado para aplicar a chave e
publicar a entrada V8 e o tratamento de erros. A conta proprietária, a
restauração isolada e a homologação de ponta a ponta permaneciam pendentes. Consulte [ACESSOS.md](ACESSOS.md).

Em 23/11/2026, antes da atualização, a consulta à VPS confirmou o commit
`3cac700`, a chave OpenRouter no renderizador com health HTTP `200` e
zero execuções no n8n.

## Download direto do relatório — 23/11/2026

O commit `b006b7f` foi implantado e verificado na VPS do cliente. A migração
`006` foi aplicada, os workflows de processamento e de erros foram vinculados
à credencial PostgreSQL e estão publicados, e o webhook de entrada está
registrado. O workflow atualizado conclui documento e tentativa após registrar
o PDF para download autenticado pelo painel.

Em 23/11, o upload autenticado foi liberado para a simulação do cliente,
prevista para 24/11. O n8n registrou zero execuções na verificação do acesso.
A homologação de ponta a ponta e a reconciliação seguem pendentes. O
reprocessamento continua suspenso no Caddy.
O n8n opera continuamente na VPS e a conta proprietária será cadastrada no
primeiro uso administrativo do editor por túnel SSH. Consulte [DEPLOY.md](DEPLOY.md).

## Rodada extra de releitura — 24/11/2026

O teste do cliente em 24/11 chegou ao limite de releituras do Anvisa V8. O
quarto pedido combinou páginas já solicitadas com páginas ainda não solicitadas
para releitura no ciclo. A correção na branch `hotfix/rodada-extra-de-releitura`
permite atender uma vez as páginas ainda não solicitadas e exige avanço
validado para prosseguir. A retomada foi verificada com migração explícita
de um checkpoint sintético da identidade anterior.
A VPS não foi consultada durante esta atualização de código.
A implantação na VPS e a retomada do documento do cliente permanecem pendentes.

## Leitura em um minuto

**26/11/2026 — Luna opcional.** Modo em até duas chamadas em revisão,
com o Terra como padrão. O ensaio isolado com 228 páginas sintéticas
validou quatro fichas de referência, incluindo atos de fronteira.
A implantação e a homologação com documentos autorizados seguem pendentes.
O protocolo existente conserva o checkpoint dos 26 lotes e deve retomar no Terra.

**25/11/2026 — Retenção de páginas de releitura.** A tentativa 2 na VPS do
cliente parou após a página 17 sair da janela, com 12 lotes concluídos no
checkpoint migrado. O ajuste local mantém as releituras do ciclo na janela
enquanto couberem e permite migrar o checkpoint de `0894805`. Implantação,
migração do checkpoint real e retomada seguem pendentes.

A homologação ainda está incompleta. Na VPS de testes, a verificação de
27/10/2026 encontrou o commit `29a6b4b` com o v2 híbrido publicado. Um PDF
sintético chegou a `aguardando_envio`, com qualidade reprovada por omitir a
sequência concessão/cancelamento e sugerir renovação após o cancelamento. Em
16/11, as PRs #5 e #3 foram integradas ao `main`. A VPS do cliente recebeu
essa versão em 21/11.

**Na VPS, não envie documentos reais pelo v2 híbrido nem declare o projeto
concluído antes de fechar os itens P0 e P1 e obter o aceite operacional.**
Os testes locais Anvisa V8 de novembro tiveram autorizações próprias,
registradas abaixo, e não homologam o v2 da VPS. Em 15/11 a stack local foi
parada a pedido do usuário, com 1.003 fichas preservadas para retomada;
a conclusão real de ponta a ponta continua pendente.

## Estado verificado

### Repositório

- Em 27/10/2026, o checkout `/opt/automacao-miller` da VPS de testes estava no commit `29a6b4b`. É uma fotografia histórica.
- Em 16/11/2026, a PR #5 foi mesclada por squash no commit `2aabff7`, trazendo a opção Anvisa V8/OpenRouter e a retomada otimizada por checkpoints. A PR #3 foi atualizada sobre essa base e mesclada com o guia local. O commit `3cac700` foi a primeira versão instalada na VPS do cliente. Em 23/11, foi substituído por `b006b7f`.
- A PR #3 documenta o teste local com Ollama em `docs/TESTE_LOCAL.md`, com a landing limitada a `127.0.0.1:8085` e os workflows de envio e reconciliação inativos. A stack completa local com V8/OpenRouter tem guia separado em `deploy/full-local/README.md`.
- O export versionado do workflow permanece inativo no Git; o workflow v2 publicado no n8n foi verificado separadamente.
- A suíte local passou em 27/10/2026: 94 testes aprovados e dois avisos de depreciação do evento `on_event` do FastAPI. O teste ponta a ponta da VPS está descrito abaixo.
- A descrição da PR #3 registra 75 testes Python, configuração Compose válida e seis serviços locais saudáveis na validação feita à época. Não repeti a suíte nem o upload ponta a ponta em 16/11; nenhum e-mail foi enviado nesta integração.
- Os exports JSON no Git são modelos versionados e ficam inativos. Eles não provam se um workflow está ativo no n8n.

### Guia local com Ollama — PR #3

A PR #3 foi integrada em 16/11/2026. O guia explica como iniciar a stack local,
enviar um PDF textual de teste, conferir Markdown/PDF e baixar o relatório
após a conclusão. O override publica a landing apenas em `127.0.0.1:8085`. A
reconciliação ficam inativos. O roteiro cobre o caminho local com Ollama, não o
modo Anvisa V8/OpenRouter nem a stack da VPS. Os 75 testes e health checks são
resultados históricos informados pela PR, não foram executados novamente nesta
integração.

### Validação local antes do merge no GitHub — 15/11/2026 (histórico)

Conflitos locais entre `main` (`29a6b4b`) e a branch `feature/performance-test`
(`eaf90bd`) resolvidos, preservando o V8, seus checkpoints e o histórico das
duas branches. O contexto determinístico foi integrado ao ramo Ollama do v1;
o v2 híbrido continua em export separado. RF-22 e RF-23 identificam seus
requisitos sem colidir com RF-20 (conversão local) e RF-21 (retomada).

Validação atual: 415 testes Python no contêiner e 15 contratos dependentes de
Node executados no host, total de 430 testes distintos; os 32 contratos do
host e as duas suítes JavaScript passaram. Compose, JSON, links locais e
Gitleaks aprovados. Não houve implantação, reinício da stack pausada, chamada
de IA, processamento de documento real ou push. Pendências operacionais
anteriores permanecem.

### Integração Anvisa V8 com OpenRouter

**Estado em 16/11/2026:** a opção foi integrada à `main` pela PR #5, no commit
`2aabff7`. Ela continua sem implantação confirmada na VPS. O usuário informou
o aceite do PDF revisado pelo cliente. O
[V8 autossuficiente](prompts/chatgpt-anvisa-pdf-v8-autossuficiente.txt) foi
preservado byte a byte e é usado pelo Terra para analisar o Markdown paginado.
A aplicação gera o PDF com índice e fichas e guarda os controles no ZIP privado.

O teste local autorizado foi pausado em 15/11. O último checkpoint validado
preserva 159 de 198 páginas fechadas e 1.003 fichas, mas não há relatório final
homologado. A retomada depende de reiniciar a stack local e confirmar
**Reprocessar** no mesmo protocolo; não se deve enviar outra cópia do PDF.
Créditos, chave e estado atual da stack não foram consultados em 16/11.

**Teste real iniciado em 12/11/2026 às 11h49 (Brasília):** após autorização
explícita do usuário, confirmada a retomada com a prévia `análise do Markdown
salvo`. Criada a tentativa 4, execução n8n 20, na etapa `analise_markdown`.
Na consulta inicial, documento e tentativa estavam em processamento, com a
execução n8n em `running`. A tentativa terminou em erro às 11h55. Também consta
a tentativa 5, execução 22, das 13h42 às 13h44, encerrada pelo mesmo motivo.

**Histórico — bloqueio no contrato dos registros compactos:** o V8 permite
`justificativa` para excluídos e representações duplicadas, mas o validador
exigia `justificativa_destino` para todos os eventos. Os quatro retornos
preservados das tentativas 4 e 5 têm oito excluídos com `justificativa` válida
e sem `justificativa_destino`. A falha ocorria antes da conferência de evidências.
Uma adaptação somente em memória do nome do campo fez esses quatro blocos
passarem na validação, com 61 a 63 evidências literais conferidas por resposta.
Isso identifica uma incompatibilidade da aplicação com o V8, sem homologar
os demais blocos ou o relatório completo.

**Concluído em 12/11/2026 — compatibilidade e mensagens:** compactos aceitam
`justificativa` e mantêm compatibilidade com `justificativa_destino`, sem
reescrever os registros. Incluídos e pendentes continuam com ficha completa.
Falhas de estrutura agora identificam campo, valor recebido e condição esperada
no diagnóstico privado e na chamada de correção. Mensagem e descrição do n8n
são preservadas juntas; referências `ANV8D-...` são classificadas como validação.
Os registros históricos anteriores não foram reescritos.

Passaram 161 testes Python e 14 testes da interface. Os quatro retornos reais
passaram na validação corrigida sem adaptação ou edição dos dados, com 61 a 63
evidências literais por resposta. Três casos sintéticos no n8n, com IA simulada,
verificaram compacto aceito, correção direcionada e segunda rejeição com motivo
e referência preservados no banco. Renderizador e workflow de erros aplicados
na stack local, com os seis serviços saudáveis. Mantidos Terra e V8 aprovado;
nenhuma chamada de IA externa ou nova tentativa real foi iniciada. Permanece
pendente validar o processamento completo do documento real em nova retomada
autorizada; o teste dos blocos preservados não homologa o relatório inteiro.

**Resultado real apurado em 12/11/2026 — tentativa 6:** execução 28, iniciada
às 14h59 e encerrada em erro às 15h23 de Brasília (aproximadamente 24m07s).
A execução superou uma rejeição literal no bloco 6–10 e chegou ao bloco
111–115. A IA devolveu cobertura parcial: inicialmente a página 115 ficou
pendente; após a correção, ficaram pendentes as páginas 114 e 115. Os retornos
declaram itens de suplementos/medicamentos ainda não individualizados e
inventários não concluídos. A interrupção por cobertura incompleta preserva
a regra de não gerar relatório final parcial.

**Histórico — limitação apurada na tentativa 6:** a aplicação repetia o bloco
completo uma vez e não persistia os lotes aceitos ou continuava grupos pendentes.
A IA atribuiu a parcialidade a limite de resposta; o limite técnico efetivo do
provedor não foi comprovado. A investigação dessa tentativa não alterou código.

**Concluído em 12/11/2026 — análise incremental e checkpoints:** lotes densos
são reduzidos por páginas-alvo inteiras. Respostas parciais continuam em grupos
de eventos completos, com IDs, valores e evidências preservados. Cobertura e
inventário permanecem pendentes até o fechamento. Lotes concluídos e registros
validados de lotes pendentes são salvos no volume privado, com identidade da
fonte/modelo/instruções/código, gravação atômica, digest, revalidação e bloqueio
de concorrência. Falta/corrupção de estado conhecido interrompe antes da IA.
Há limites de chamadas, contexto, tempo e respostas sem progresso. O PDF final
continua dependendo de todos os lotes fechados e validados.

Passaram 182 testes Python e 14 testes da interface. A integração sintética no
n8n comprovou um lote e dois eventos salvos antes de falha, persistência após
recriar o contêiner, retomada com apenas uma nova chamada simulada e consulta
final sem nova chamada de IA. Fonte densa foi dividida em quatro lotes menores.
Os dois retornos parciais reais foram conferidos sem rede: 11/13 registros e
62/86 evidências válidas para continuação, mantendo a cobertura pendente.
Isso não homologa a conclusão do documento real. Nenhuma nova tentativa real
ou chamada ao OpenRouter foi iniciada nesta implementação.

O progresso em memória das seis tentativas anteriores não pode ser recuperado
retroativamente; o novo salvamento vale para as próximas execuções. A retomada
continua pelo mesmo botão e pelo Markdown salvo, recuperando automaticamente
o checkpoint interno compatível quando existir.

**Novo bloqueio apurado em 12/11/2026 — tentativa 7:** execução 38, das
16h19m38s às 16h22m32s de Brasília, encerrada por HTTP 402 do OpenRouter.
Antes da recusa, o lote 6–7 produziu uma evidência do inventário que não existe
literalmente na página 7; a chamada corretiva recebeu o erro de créditos.
Não foi uma nova interrupção por cobertura parcial. Os seis serviços estavam
saudáveis na investigação.

A consulta de metadados mostrou limite mensal da chave de US$ 10, uso acumulado
de US$ 9,848618745 e restante de US$ 0,151381255. A conta tinha US$ 20 em
créditos totais e o mesmo uso acumulado, saldo de US$ 10,151381255. Esses valores
não medem o custo isolado desta tentativa. O teto solicitado de 48 mil tokens
de saída corresponde a até US$ 0,24 somente de saída no preço público consultado,
antes da entrada. O orçamento da chave é o principal indício do bloqueio;
o corpo da resposta 402 foi descartado pelo transporte, impedindo confirmar
retroativamente seu subtipo/reserva. Revisar esse limite antes da retomada e
preservar metadados seguros de erros HTTP em ajuste futuro de observabilidade.

O checkpoint da tentativa 7 foi revalidado sem rede, contra o Markdown original:
três lotes concluídos, páginas 1–5, oito registros e 82 referências literais
válidas. A identidade continua compatível; a próxima análise pode reutilizar
esses lotes e começar pelos alvos 6–7. O lote rejeitado não foi promovido a
concluído. Não houve nova chamada de IA, reprocessamento ou mudança de limite
nesta investigação. A homologação das 198 páginas permanece pendente.

**Bloqueio atual apurado em 12/11/2026 — tentativa 8:** após o usuário aumentar
o limite mensal da chave para US$ 100, a consulta confirmou US$ 90,151381255
de margem nesse limite. Essa margem é diferente do saldo da conta. A execução
40 foi iniciada às 16h59m14s e terminou às 17h43m11s de Brasília por
`conferencia_integridade_pendente` no bloco 113–115. Os seis serviços estavam
saudáveis. O erro final desta tentativa é de validação, sem HTTP 402 registrado.

A IA devolveu 26 registros: inicialmente 11 fichas estavam com revisão técnica
pendente; a correção concluiu a conferência de uma ficha, deixando outras dez
pendentes. Os motivos declarados incluem conferência inversa da fonte para a
ficha, pesquisa de ocorrências e revisão da continuação de anexo ainda não
executadas. As páginas 114–115 e dois inventários também permaneceram pendentes.
O estado de análise da página 113 foi declarado concluído apesar da conferência
pendente de uma de suas fichas; esse estado isolado não comprova conclusão.

**Histórico — limitação identificada na tentativa 8:** a continuação intermediária aceitava pendências na
cobertura e no inventário, mas valida todas as fichas como concluídas antes de
atingir a continuação/salvamento. Uma ficha com integridade pendente rejeita o
grupo completo. A única correção recebe a primeira falha e pode resolver apenas
ela, deixando as demais para uma nova rejeição. O limite de quatro eventos é
enviado somente após uma resposta parcial aceita; ele não estava presente na
primeira chamada nem na correção desse lote. Os alvos somavam 30.609 caracteres,
abaixo do limiar de 32 mil, por isso permaneceram agrupados, mesmo gerando 26
registros. Não foi comprovado limite técnico do provedor.

Encaminhamento registrado na investigação: solicitar grupos pequenos desde a primeira resposta; separar
eventos integralmente validados dos itens que precisam de revisão; persistir
os grupos completos e continuar a conferência dos pendentes, preservando IDs,
fonte e evidências. A correção deve informar todas as pendências conhecidas do
grupo. Manter a validação final estrita e não trocar o estado para `revisada`
sem fazer a conferência. Preservar os lotes existentes: como a identidade inclui
o código, qualquer migração de checkpoint para uma implementação nova precisa
ser explícita e revalidada, sem reinício silencioso ou relaxamento da identidade.

Reprodução sem rede da orquestração com as duas respostas guardadas confirmou
duas chamadas simuladas, rejeição na segunda e nenhum registro salvo do lote
113–115. Quinze registros iniciais e 16 corretivos passaram individualmente;
isso não homologa o lote ou a revisão semântica. O checkpoint existente foi
revalidado contra o Markdown: 59 lotes concluídos, páginas 1–112, 143 registros
e 1.612 referências literais válidas. O próximo alvo permanece 113–115. Não houve
alteração funcional, nova tentativa ou chamada externa de IA na investigação.

**Concluído em 12/11/2026 — grupos desde o início e revisão incremental:** o
renderizador solicita até quatro eventos desde a primeira chamada e nas
correções. Eventos completos são salvos separadamente de fichas ainda em
revisão. A continuação prioriza essas fichas, com IDs e evidências preservados
e versões anteriores em histórico privado. Eventos concluídos são imutáveis.
Pendências explícitas mantêm o trabalho aberto mesmo com rótulo `revisada`,
sem alterar esse rótulo ou apagar notas por conveniência. Correções recebem
as falhas conhecidas dos registros do grupo conjuntamente. A validação final
continua estrita; não há PDF com ficha ou inventário tecnicamente pendente.

Passaram 194 testes Python no contêiner e os dez testes de contrato que exigem
Node.js no host, totalizando 204. O arquivo de testes JavaScript da tela passou.
Integração n8n com IA simulada confirmou fichas completas e duas revisões salvas
antes de falha, persistência após recriar o contêiner e retomada com uma única
chamada para fechar as duas revisões. PDF/ZIP mantiveram os quatro IDs e suas
evidências; nova consulta à análise completa fez zero chamadas. Caso denso
também passou. Recursos sintéticos removidos ao final.

As duas respostas reais do bloco 113–115 foram reproduzidas sem rede em cópia
temporária: 16 fichas completas e dez ainda em revisão ficaram salvas, mantendo
os 59 lotes anteriores. Isso não conclui as revisões nem homologa o documento.
Somente os 59 lotes concluídos do checkpoint operacional foram migrados para
a identidade nova, por ferramenta explícita com backup, bloqueio, revalidação,
origem registrada e estado anterior intacto; respostas diagnósticas parciais
não foram importadas no estado operacional.

Atualizado somente o renderizador local e conferidos os fontes instalados,
Terra, V8 aprovado, permissões privadas e seis serviços saudáveis. Workflows
mantiveram suas versões ativas. Preservadas as páginas 1–112, 143 registros e
1.612 referências literais verificadas. A prévia do botão continua `análise
do Markdown salvo`; a próxima retomada começa nos alvos 113–115. O documento
continua em erro com oito tentativas até nova confirmação do operador.
Nenhuma nova tentativa real, chamada externa de IA ou alteração na VPS foi feita.

**Histórico — bloqueio apurado em 12/11/2026 na tentativa 9:** execução 54, das
19h58m42s às 20h03m43s de Brasília, encerrada por limite interno de tamanho da
fonte/continuidade. Ao buscar outras ocorrências dos identificadores de quatro
fichas em revisão, o contexto acumulado passou a abranger as 198 páginas. O
pacote reconstruído tem 2.251.331 bytes, acima do teto de 480.000 bytes do
orquestrador. Essa proteção dispara antes da próxima chamada ao OpenRouter;
não demonstra recusa do provedor ou esgotamento de tokens/créditos.

O contexto ampliado foi salvo antes de verificar seu tamanho. Como já existe
continuidade, o fluxo não divide o lote nem reduz essa janela automaticamente,
para não descartar trabalho. O mesmo checkpoint reproduz o erro antes de nova
chamada de IA. A revalidação confirmou identidade/digest/fonte e todos os
registros: permanecem 59 lotes concluídos, páginas 1–112, 143 registros e
1.612 referências literais; no lote 113–115 foram salvos mais quatro registros
completos e quatro em revisão, com 142 referências literais no conjunto parcial.
Os seis serviços estavam saudáveis.

**Ajuste definido na investigação:** busca local de ocorrências no Markdown e recuperação de
contexto relevante em janelas limitadas, conferindo o orçamento antes de
persistir/enviar uma expansão. Preservar também a solicitação de pesquisa que
ainda falta cumprir; não eliminar páginas ou declarar busca integral feita
sem executá-la. Recuperar o estado atual por migração/revalidação explícita,
mantendo lotes, IDs, evidências e revisões guardados. Não remover contexto
manualmente do arquivo para simular revisão concluída.

Recomendação operacional: corrigir a ampliação de contexto e retomar o mesmo
protocolo, preservando o progresso. Não há corrupção demonstrada que justifique
recomeçar a análise pela página 1; reinício não corrige essa limitação e refaz
trabalho válido. Nenhuma tentativa foi reiniciada, nem código/configuração
alterados nesta investigação. A homologação completa continua pendente.

**Concluído em 12/11/2026 — contexto em janelas e recuperação da tentativa 9:**
busca literal local no Markdown, páginas com ocorrências e fila de contexto
solicitado/entregue. Pacotes de até 480.000 bytes UTF-8 incluem continuidade e
correção, sem cortar páginas. Entregar contexto não equivale a conferi-lo; o
lote permanece aberto enquanto restarem páginas na fila. Respostas rejeitadas
mantêm a janela necessária à retomada e limites de saída conservam os pedidos
aceitos. Mantidos Terra, V8 e verificações literais.

Passaram 211 testes Python no contêiner e dez contratos com Node.js no host,
totalizando 221; o módulo JavaScript da interface também passou. Integração
n8n com IA simulada confirmou falha, persistência após recriar o contêiner,
retomada, entrega das 30 páginas pedidas e geração do PDF/ZIP, com maior pacote
de 453.489 bytes. Recursos sintéticos removidos. Na cópia privada da tentativa
9, sem rede, três janelas avançaram sem o antigo bloqueio; pacotes de até
479.732 bytes preservaram lotes, registros e revisões. Essa prova técnica não
substitui a revisão semântica do documento real.

Atualizado apenas o renderizador local e migrado explicitamente o checkpoint
do formato 2 para o 3, após backup, bloqueio e revalidação integral. O original
permanece intacto. Conservados 59 lotes concluídos, páginas 1–112, 143 registros
e, no lote 113–115, quatro completos e quatro em revisão. As 198 páginas do
contexto antigo ficaram solicitadas, sem presumir entrega ou revisão. Fontes
instalados, permissões privadas, V8, Terra e seis serviços saudáveis conferidos;
workflows mantiveram suas versões. A prévia confirma `análise do Markdown salvo`.

O documento continua em erro com nove tentativas até nova confirmação em
**Reprocessar**; não é necessário reenviar o PDF nem recomeçar pela página 1.
A homologação completa das 198 páginas permanece pendente da próxima execução
real. Nenhuma chamada externa de IA, consumo adicional de créditos ou mudança
na VPS foi realizada nesta implementação.

**Histórico — bloqueio apurado em 12/11/2026 na tentativa 10:** execução 69, das
20h55m07s às 21h08m09s de Brasília, encerrada com `limite de novos pedidos de
contexto do lote atingido; fila preservada`. É outra proteção local: a tentativa
9 excedia o tamanho do pacote; a 10 atingiu o teto de três novos pedidos de
contexto por lote. O contador também inclui novos grupos de buscas literais,
mesmo quando suas ocorrências já estão em páginas entregues, e não reinicia
após salvar progresso dos grupos de eventos. O quarto pedido novo interrompe
antes de gravar a proposta; os pedidos anteriormente aceitos permanecem salvos.
O corpo desse pedido real rejeitado não foi registrado como diagnóstico.

A recuperação em janelas avançou: as 198 páginas constam como entregues, sem
atestar revisão semântica, e há 43 buscas locais preservadas. O checkpoint
continua com 59 lotes concluídos, páginas 1–112 e 143 registros. No lote
113–115 há agora 24 registros completos, zero fichas em revisão e quatro
versões históricas; o lote ainda está aberto. Revalidação offline confirmou
fonte, identidade, digest, evidências e preservação dos lotes e IDs anteriores.
A próxima janela 111–117 tem 203.514 bytes, abaixo de 480.000. A exceção atual
foi reproduzida no quarto pedido sintético, em memória e sem rede.

**Ajuste definido na investigação:** distinguir buscas locais e ampliações de páginas, considerar
o avanço dos grupos no controle de repetição e persistir o pedido pendente que
provoca a interrupção. Manter limites de tamanho, chamadas, prazo e buscas,
sem permitir repetição indefinida. Testar mais de três grupos de buscas no
mesmo lote com progresso preservado, além de pedidos repetidos sem progresso.
Os testes anteriores de janelas/retomada não cobriam essa sequência real.
Não há motivo demonstrado para descartar o progresso e recomeçar pela página 1.
Documento parado em erro com dez tentativas, sem relatório final; seis serviços
saudáveis. Nesta investigação não houve alteração funcional, reprocessamento,
chamada externa de IA, consumo adicional de créditos ou mudança na VPS.

**Concluído em 12/11/2026 — buscas separadas e limite renovado por progresso:**
buscas literais não consomem o orçamento de ampliações explícitas de páginas.
São admitidas até três ampliações com páginas inéditas por
`contexto_necessario` desde o último avanço validado dos grupos. Novos registros,
fichas concluídas e avanço de cobertura/inventário reabrem esse orçamento;
entrega de páginas, buscas e repetição de grupo idêntico não o reabrem. O
pedido que atinge o limite é salvo após conferir o orçamento da janela, antes
da interrupção, para não se perder na retomada. Mantidos limites de 480.000
bytes, 32 chamadas por lote/execução, prazo, 16 termos por pedido, 256 por lote
e rejeição de repetições sem trabalho novo.

Passaram 219 testes Python no contêiner e dez contratos com Node.js no host,
totalizando 229, além do módulo JavaScript da interface. Casos novos cobrem
seis grupos de buscas no mesmo lote, pesquisas sem consumir ampliações,
renovação após progresso, preservação do quarto pedido de páginas, rejeição
de repetição, limite total de chamadas e migração íntegra do formato 3.
Integração n8n com IA simulada superou quatro grupos de buscas, salvou progresso
antes de falha, retomou após recriar o contêiner e gerou PDF/ZIP com seis grupos
e sete registros. O lote concluído foi reutilizado sem IA. Recursos temporários
removidos. Na cópia privada do checkpoint real, quatro buscas novas passaram
sem o bloqueio anterior, com todos os registros preservados e pacotes de até
204.090 bytes. Isso não conclui a análise semântica do documento real.

Atualizado apenas o renderizador local e migrado explicitamente o checkpoint
da implementação conhecida do formato 3 para a nova identidade, mantendo o
mesmo formato e preservando o original. Conservados 59 lotes, páginas 1–112,
143 registros e, no lote 113–115, 24 completos, quatro versões históricas,
43 buscas e o controle de entrega das 198 páginas. Conferidos fontes, identidade,
Terra, V8, permissões privadas e seis serviços saudáveis. Workflows inalterados;
prévia autenticada confirma `análise do Markdown salvo`.

O documento permanece em erro com dez tentativas, aguardando confirmação em
**Reprocessar** no mesmo protocolo. Não é necessário reenviar o PDF ou refazer
as 112 páginas concluídas. Nenhuma nova execução real, chamada externa de IA,
consumo adicional de créditos ou mudança na VPS foi realizada nesta entrega.

**Bloqueio apurado em 12/11/2026 — tentativa 11:** execução 74, das
21h29m49s às 22h18m47s de Brasília, encerrada com HTTP 402 do OpenRouter.
Documento em erro, sem análise principal ativa. É uma recusa do provedor
relacionada à autorização de créditos, distinta dos limites locais anteriores.
Consulta somente de metadados: conta com US$ 20 em créditos totais e
US$ 19,512259845 de uso acumulado, saldo de US$ 0,487740155. A chave mantém
limite mensal de US$ 100 e US$ 80,487740155 de margem. Esses valores não são
o custo isolado da tentativa. O saldo baixo é o principal indício do bloqueio;
o corpo/metadata da resposta 402 foi descartado pelo transporte, impedindo
confirmar seu subtipo ou valor de reserva. Verificar/repor saldo da conta
antes da retomada; aumentar apenas o limite mensal não adiciona créditos.
Nenhuma recarga, mudança de limite ou nova execução foi feita na investigação.

**Histórico — bloqueio apurado em 14/11/2026 — tentativa 12:** execução 76, das
14h18m14s às 14h41m40s de Brasília, encerrada porque a continuidade do lote
116–117 ultrapassou o limite local de 480.000 bytes. As 70 fichas completas
desse lote ocupam 449.218 bytes e são reenviadas integralmente a cada chamada.
Com inventário e controle de contexto, o pacote já tem 486.330 bytes sem
nenhuma página; com as páginas obrigatórias 116 e 117, chega a 511.269 bytes.
O limite de quatro eventos por resposta não limita o crescimento da entrada.
A divisão por páginas considera o texto inicial e não é reaplicada quando
o lote já tem continuidade, deixando a retomada bloqueada no mesmo estado.

Reprodução offline com a imagem instalada e parser original, sem rede e com
volumes somente para leitura, confirmou a mesma exceção antes de qualquer
chamada de IA. Hash do Markdown, digest e revalidação integral do checkpoint
passaram; o arquivo permaneceu inalterado. Preservados 60 lotes completos,
páginas 1–115, 180 registros desses lotes e 70 fichas completas do lote ainda
pendente. Nenhuma análise principal ativa na consulta. O nome do último nó,
`OpenRouter - Prepare verification bundle`, apenas propaga o erro recebido do
renderizador; a falha ocorre na montagem do contexto antes de gerar PDF/ZIP.

**Próximo passo registrado na investigação:** corrigir o crescimento da continuidade reenviada em lotes
densos, preservando fichas integrais, IDs, evidências e inventários no controle
privado. Validar a estratégia com limite de pacote e retomada antes de outra
tentativa real; repetir o botão com a implementação atual reproduz a falha.
Não houve alteração funcional, chamada externa de IA, edição/migração do
checkpoint, nova tentativa ou mudança na VPS durante esta investigação.

**Concluído em 14/11/2026 — continuidade densa e retomada local:** mediante
autorização do usuário, o renderizador passa a usar um índice de todos os
eventos concluídos quando o envio das fichas completas não cabe. O índice
preserva IDs, categorias, destinos, páginas, hash e referências confirmadas;
as fichas integrais continuam no checkpoint e no resultado final. Revisões,
inventários, diagnóstico, resposta rejeitada e páginas obrigatórias não são
reduzidos. Mantidos o teto de 480.000 bytes e as validações de imutabilidade,
duplicação, evidências e cobertura. O V8 e o modelo Terra permanecem os mesmos;
as instruções adicionais de transporte explicam o índice.

Passaram 228 testes Python no contêiner isolado e os dez contratos com Node.js
no host, totalizando 238, além do teste da interface. A API sintética gerou PDF
e ZIP contendo as fichas completas após a retomada por índice. Na cópia privada
do estado real, a janela caiu de 511.269 bytes mínimos para 186.088 bytes com
as vizinhas 114–119; preservados lotes, fichas e continuidade. A retomada
simulada e a repetição da migração passaram sem chamar IA externa.

Preservados backup protegido e imagem anterior. Atualizado somente o
renderizador local; migrado explicitamente o estado para a nova identidade,
com comparação integral dos lotes completos e pendentes contra a origem.
Mantidos 60 lotes, páginas 1–115, 180 registros concluídos e 70 fichas do lote
116–117. Conferidos hashes instalados, V8, permissões 600/700 e seis serviços
saudáveis. A prévia autenticada continua `análise do Markdown salvo`.
Próximo passo: o operador retomar pelo mesmo protocolo para validar a análise
real; a simulação não homologa o relatório integral de 198 páginas. Nenhuma
nova tentativa real foi iniciada nesta correção; VPS e workflows inalterados.

**Histórico — bloqueio apurado em 14/11/2026 — tentativa 13:** execução 78,
das 15h08m21s às 16h39m29s de Brasília, encerrada com `tempo total excedido;
o progresso validado foi preservado no checkpoint`. O renderizador e o n8n
estão configurados com `OPENROUTER_TIMEOUT_SECONDS=5400`. Esse orçamento de
90 minutos vale para a análise inteira daquela tentativa, incluindo todos os
lotes e grupos restantes; não é renovado pelo avanço de fichas. O HTTP do nó
OpenRouter aguarda 5.520 segundos, portanto a mensagem veio da guarda de
prazo do renderizador, propagada pelo nó de preparação do ZIP.

O lote 116–117 concluiu com 102 registros. Permanecem salvos 61 lotes completos,
páginas 1–117 e 282 registros; no lote 118–120 há mais 76 fichas completas,
sem ficha em revisão. O último salvamento foi às 16h39m28s. A tentativa
preservou 108 registros adicionais em relação ao estado migrado antes dela.
Hash da fonte, digest e revalidação integral do checkpoint passaram. A próxima
janela, páginas 116–122, tem 458.570 bytes, dentro do teto de 480.000.

A reprodução offline confirmou que prazo expirado produz a mesma mensagem
antes da IA. Com prazo novo, o estado chega ao próximo grupo dos alvos
118–120, sem repetir os lotes concluídos. Volumes somente para leitura,
checkpoint inalterado e zero chamadas externas. Os seis serviços estavam
saudáveis e nenhuma análise principal estava ativa na consulta.

**Próximo passo registrado na investigação:** retomar o mesmo protocolo para continuar o progresso salvo.
Para reduzir interrupções manuais em análises longas, avaliar continuação
controlada entre etapas com orçamento de tempo, preservando limites totais e
checkpoint. Aumentar o orçamento de uma tentativa é uma opção de configuração,
mas não substitui a definição dessa política operacional. Nenhuma configuração,
código, workflow ou tentativa real foi alterado nesta investigação.

**Concluído em 14/11/2026 — meta de 90 minutos sem prazo global:** o usuário
esclareceu que 90 minutos é uma meta desejada, não uma regra de interrupção.
PRD corrigido e `OPENROUTER_TIMEOUT_SECONDS=0` aplicado ao renderizador e ao
n8n locais. A análise passa a continuar além desse tempo; permanecem timeout
de 360 segundos por chamada e os limites de grupos, contexto, buscas,
validação e ausência de progresso. Um prazo global positivo continua sendo
uma configuração opcional explícita, sem usar a meta como padrão.

Atualizado somente o nó HTTP `OpenRouter - Analyze and render V8` para a
versão 2 instalada, que respeita zero numérico. O nó 4.2 substituía esse valor
por cinco minutos, e a string zero provoca timeout imediato no transporte.
Teste no nó e transporte reais validou espera sem prazo, corpo e header
interno preservados, HTTP 200/502, propagação do detalhe e timeout positivo.
Conexões, demais nós, configurações e referências de credenciais permaneceram
idênticos ao export implantado anterior. Workflow republicado no mesmo ID e
verificado ativo na nova revisão após recriar o n8n.

Passaram 251 testes Python, contando os 13 contratos com Node.js executados
no host, além dos testes JavaScript da interface e do HTTP n8n real.
Relógio simulado avançou por cinco horas sem cortar a análise; os limites por
chamada e contra ciclos continuaram funcionando. Na cópia privada do estado
real, migração e retomada atravessaram duas horas simuladas, conservando
61 lotes, páginas 1–117, 282 registros e 76 fichas do lote 118–120.

Preservados banco, configuração, workflow, checkpoints e imagem anteriores em
backup protegido. Migrado explicitamente o checkpoint operacional e aplicados
renderizador/n8n locais, com seis serviços saudáveis, configuração zero nos
dois serviços, origem intacta e prévia `análise do Markdown salvo`. Documento
permanece em erro com 13 tentativas, aguardando o operador retomar pelo mesmo
protocolo. Nenhuma nova análise real, chamada externa de IA ou alteração na
VPS foi realizada; o documento integral continua pendente de homologação.

**Concluído em 14/11/2026 — continuação e retentativas automáticas:** a pedido
do usuário, 32 chamadas deixam de encerrar o lote e passam a delimitar uma
janela técnica. O renderizador recarrega e revalida o checkpoint e continua
automaticamente na mesma tentativa, mantendo bloqueio, correção aberta,
ausência de progresso, buscas e ampliações. O diagnóstico mantém a contagem
acumulada de chamadas; os metadados finais informam continuações automáticas
e retentativas de transporte daquela execução.

Timeout/conexão e HTTP 408, 429, 500, 502, 503 e 504 têm até três tentativas
da mesma chamada, com esperas de 5 e 15 segundos e revalidação antes de
repetir. Erros de crédito/autorização, saída inválida e validação continuam
explícitos. A troca de janela não renova o orçamento das retentativas. Falha
persistente após três tentativas preserva o progresso e termina com motivo.
Mantidos prazo global zero, timeout individual de 360 segundos, V8 e Terra.

Passaram 270 testes Python no contêiner e os 13 contratos dependentes de
Node.js no host, total de 283; os 30 contratos completos passaram no host.
Também passaram a interface e o contrato HTTP real do n8n. Casos verificam
36 chamadas no mesmo lote, checkpoint íntegro, retry com o mesmo pacote,
conservação de lotes concluídos, falha persistente e posterior retomada,
correção única através de janelas, falta de progresso, buscas/ampliações sem
renovação indevida e bloqueio de checkpoint corrompido antes de outra chamada.

Na cópia privada do estado real, migrados 61 lotes e 76 fichas pendentes;
timeout simulado, retry e duas trocas de janela passaram com pacotes iguais
de 458.570 bytes, sem IA externa ou alteração da origem. Backup preservado;
atualizado somente o renderizador local e migrado explicitamente o checkpoint
operacional. Conferidos códigos, digest, fonte anterior idêntica ao backup,
permissões 600/700, seis serviços saudáveis e prévia de retomada HTTP 200.
Workflow, n8n e configuração permaneceram iguais. O operador pode retomar o
mesmo protocolo; nenhuma nova tentativa real foi iniciada nesta correção.

**Diagnóstico de desempenho em 14/11/2026 — execução 80:** consultas somente
de leitura durante a tentativa 14 indicam gargalo na sequência de chamadas
OpenRouter, com fichas pequenas por grupo e repetição de contexto/inventário.
O processo do renderizador acumulou 56,75 segundos de CPU em 7.190 segundos
de vida, média de 0,79% de um núcleo; memória observada de aproximadamente
79 MiB em 512 MiB disponíveis. Essas medidas não indicam saturação local de
CPU/RAM na análise em curso. Conversão e renderização final não eram a etapa ativa.

Consultados somente metadados de duas gerações já encerradas e vinculadas a
diagnósticos desta tentativa. Uma retornou quatro fichas: 76.061 tokens nativos
de entrada, 10.485 de saída e `generation_time=117423`; a outra retornou somente
controles de inventário: 29.483 de entrada, 3.258 de saída e `generation_time=37542`.
Os intervalos entre criação na API e salvamento local foram aproximadamente
118 e 38 segundos. São amostras de respostas rejeitadas, não uma média de
todas as chamadas. Na primeira, o JSON compacto continha 16.968 bytes de
fichas e mais 10.096 bytes de inventário acumulado.

Próximo trabalho proposto: medir cada chamada aceita, reduzir repetição de
fichas/inventários no transporte com consolidação e validação no servidor e
avaliar paralelismo apenas entre unidades independentes. Validar preservação
de evidências, cobertura e reconciliação antes de implantar qualquer otimização.
O ritmo por página varia muito: a execução avançou de 122 para 130 páginas
durante as consultas recentes; a projeção linear anterior de 27 horas tem
baixa confiança. Nenhuma otimização, alteração de modelo, prompt, limite,
workflow, checkpoint ou serviço foi aplicada durante a análise em andamento.

**Execução local interrompida a pedido do usuário em 14/11/2026:** cancelada
a tentativa 14, execução n8n 80, às 19h42m02s de Brasília. Encerrado também o
trabalho do renderizador para impedir continuidade da requisição síncrona.
O checkpoint foi revalidado sem rede, com volumes somente para leitura:
130 páginas concluídas, 477 registros nos lotes completos e 20 fichas
completas do lote 131–132. Último salvamento às 19h41m32s.

Documento e tentativa foram retirados de `em_processamento` e registrados
como interrupção manual, com motivo e auditoria, mantendo o mesmo protocolo
e 14 tentativas. Serviço de renderização disponibilizado novamente sem
retomar a análise. Nenhuma execução principal ativa na conferência. O
progresso permanece disponível para futura retomada autorizada; otimizações
de desempenho propostas continuam pendentes de implementação e validação.

**Proposta medida em 14/11/2026 — reduzir repetição no transporte:** simulações
somente em memória, sem IA e com volumes somente para leitura, compararam
fichas completas com índice para o mesmo texto documental. No lote parado
131–132, com 20 fichas, o JSON de dados caiu de 112.630 para 99.070 bytes
(12%). No lote já fechado 121–122, usando suas 36 fichas finais na simulação,
caiu de 266.459 para 134.692 bytes (49,5%). A segunda comparação não reconstrói
a chamada histórica; mede apenas as representações do estado final existente.

Em uma resposta diagnóstica com quatro fichas, compartilhar 11 objetos de
evidência repetidos reduziu o JSON de 27.557 para 25.096 bytes (8,9%), com
expansão estrutural idêntica ao original. A resposta original era rejeitada;
isso comprova apenas serialização sem perda, não qualidade da análise. O
inventário acumulado ocupava 10.096 bytes, indicando espaço para protocolo
de alterações incrementais consolidado e validado no servidor. Os ganhos
em bytes não equivalem a ganhos medidos de tokens ou duração e não se somam.

Primeira fase proposta: índice de fichas concluídas desde a primeira
continuação, inventário incremental com IDs/versões estáveis e medição de
tempo/tokens por chamada. Evidências compartilhadas e grupos adaptativos
podem ser avaliados depois; paralelismo exige unidades independentes e
reconciliação final. Manter fichas, evidências, inventários e versões completos
no checkpoint e expandir o transporte antes das validações existentes.
Comparar blocos densos e leves sob as mesmas condições antes de afirmar prazo
de conclusão. As quatro horas anteriores foram informadas pelo usuário;
a projeção de 22–27 horas não constitui medição comparável de uma execução
completa. Nenhuma otimização ou retomada real foi aplicada nessa avaliação.

**Histórico de 14/11/2026 — primeiras reduções de transporte, com grupos de quatro:**
índice de fichas concluídas desde o início, alterações incrementais do
inventário consolidadas no servidor e evidências compartilhadas sem perda.
Mantidos validação V8 integral, fonte, fichas imutáveis, grupos de quatro,
sequência única e prazo global zero. Grupos adaptativos e paralelismo adiados.
Passaram 292 testes no contêiner, os 13 contratos dependentes de Node no host
(305 testes Python distintos) e a interface JavaScript. Em teste sintético
real, uma chamada OpenRouter levou 16,121 segundos, com deltas e referências;
PDF e ZIP validados. Essa amostra não permite estimar as 198 páginas reais.

Preservados backup e origem; migrados integralmente os 130 alvos concluídos,
477 registros e 20 fichas pendentes para a identidade final, sem iniciar
retomada. Seis serviços saudáveis. Na comparação local do lote parado 131–132,
o pacote de dados passou de 112.630 para 101.682 bytes (9,72% menor), com as
mesmas páginas; é redução em bytes, não duração medida.

**Amostra real concluída em 14/11/2026 — após autorização específica:** o
usuário confirmou o envio do documento e derivados ao OpenRouter. Feitas
seis chamadas em cópia privada do checkpoint, com os originais somente para
leitura. Duração total de 150,226 segundos; média de 22,454 segundos por chamada
(14,690–26,013). Cinco respostas aceitas acrescentaram 20 fichas excluídas,
sem fechar o lote 131–132. Uma resposta foi rejeitada por remover evidência
de unidade já salva e a única correção permitida resolveu a falha. Ritmo
observado com retrabalho e instrumentação: 7,511 segundos por ficha nova.

No agregado das seis chamadas, o JSON de dados enviado foi 13,01% menor que
as representações integrais equivalentes. Nas cinco respostas aceitas, o
JSON de saída foi 83,24% menor que o resultado equivalente após expansão de
evidências e consolidação do inventário. São comparações em bytes da mesma
amostra; não demonstram redução de tempo nessas proporções nem constituem
benchmark de duração contra a implementação anterior.

Para as 68 páginas ainda abertas na origem, dois cenários condicionais:
40,3 minutos usando a média histórica de 3,669 fichas/página nas 66 páginas
posteriores ao lote atual; 7,05 horas usando a densidade de 50 unidades/página
do lote amostrado. Ambos supõem uma ficha por unidade, 80 unidades ainda sem
ficha na origem do lote atual e custo de ficha igual ao das exclusões desta
amostra. Não são intervalo de confiança, prazo ou limite: densidade futura,
fichas completas, contexto adicional e correções podem mudar muito o tempo.
Não há base para uma previsão única nem para prometer quatro horas no total.

A amostra produziu 20 fichas adicionais somente na cópia; não foram incorporadas
ao checkpoint operacional. A origem permanece com 130 páginas concluídas,
477 registros de lotes completos e 20 fichas do lote pendente, execução 80
cancelada. Nenhuma retomada automática. Grupos adaptativos e paralelismo
continuam adiados; o documento integral ainda precisa ser homologado.

**Histórico de 14/11/2026 — grupos de oito ainda sequenciais e evidências aditivas:**
a pedido do usuário, máximo de oito conferido no servidor e união ordenada
que preserva as evidências anteriores. Mantidos fichas imutáveis, validação
literal, cobertura, reconciliação, prazo global zero e sequência única.
Paralelismo continua por último. Passaram 306 testes no contêiner e os 13
contratos com Node no host, total de 319 testes Python distintos; interface
JavaScript aprovada. A resposta anterior rejeitada por perda de evidência
foi reproduzida sem rede e passou com todas as anteriores preservadas.

O mesmo fixture sintético concluiu em uma chamada de 14,872 segundos, com
PDF e ZIP validados. Repetida a amostra real no mesmo checkpoint inicial e
páginas 131–132, em volume privado separado: seis chamadas, seis respostas
aceitas, 48 fichas novas excluídas, nenhuma correção e 230,256 segundos no
total. Média de 35,979 segundos por chamada, agora com oito fichas cada;
4,797 segundos por ficha incluindo instrumentação. Antes: 20 fichas em
150,226 segundos, com uma correção e 7,511 segundos por ficha. Nesta comparação,
o tempo por ficha caiu 36,14% e a vazão subiu de 7,988 para 12,508 por minuto.
É uma observação de duas amostras do mesmo início, não ensaio controlado de
latência para todo o documento ou de cada ajuste isoladamente.

No mesmo cenário denso anterior — 80 fichas ainda faltantes no lote atual da
origem e 66 páginas seguintes com 50 unidades/página — a projeção passa de
7,05 para 4,50 horas adicionais, usando 3.380 × 4,797 segundos. É referência
condicional do restante a partir do progresso salvo, sem prazo máximo ou
interrupção automática. A amostra só contém excluídos de um lote que não
fechou; densidade futura, fichas completas e correções podem mudar a duração.
A comparação não comprova duração total de quatro horas desde o começo.

Implantado somente o renderizador e migrado explicitamente o checkpoint
operacional, com backup e origem intacta: 130 páginas fechadas, 477 registros
e 20 fichas do lote aberto. Seis serviços saudáveis. As 48 fichas do benchmark
ficaram só na cópia; execução 80 continua cancelada, sem nova tentativa,
retomada automática, envio, alteração no workflow, configuração, commit ou push.
Documento integral ainda pendente de homologação.

**Histórico de 14/11/2026 — paralelismo com grupos fixos de oito:** até dois
lotes operacionais sem sobreposição de contexto por análise, mantendo oito
fichas por chamada, continuações sequenciais e um único escritor do checkpoint.
Janelas, evidências, unidades conhecidas e pedidos de contexto sobrepostos
serializam os despachos. Lotes podem concluir fora de ordem; o checkpoint
preserva a partição e a montagem final espera todos. Falha persistente impede
novas chamadas e drena as já em voo; falha de armazenamento impede promoções.
Prazo global permanece zero. Passaram 315 testes no contêiner e 13 contratos
com Node no host, total de 328 testes Python distintos, além da interface.

Comparadas duas amostras nos mesmos lotes 131–132 e 138–140 e estado inicial,
com até três chamadas por lote, sem disputar a API entre os modos. Controle
sequencial: quatro chamadas aceitas, 32 fichas novas, 230,487 segundos, três
páginas fechadas. Paralelo: seis chamadas aceitas, 48 fichas novas, 165,819
segundos, duas simultâneas observadas, nenhum lote fechado. Sem correções
ou falhas persistentes nos dois modos. O fixture sintético também passou,
com uma chamada de 10,574 segundos e PDF/ZIP conferidos.

A IA variou quantidade de fichas e fechamento dos lotes; as saídas não são
finais equivalentes. Não atribuir toda diferença ao paralelismo nem afirmar
redução controlada de duração do documento. A medição paralela observada foi
3,455 segundos por ficha (17,368 por minuto). Mantendo a hipótese densa
anterior de 3.380 fichas ainda necessárias na origem, a projeção é de 3,243
horas adicionais, cerca de 3h15, com baixa confiança. Essa hipótese não mede
a densidade futura e não é prazo máximo, limite ou garantia; a variabilidade
de granularidade/refechamento exige comparação antes da homologação integral.

Somente o renderizador local foi atualizado, com backup, migração explícita
e origem íntegra: 130 páginas, 477 registros fechados e 20 fichas do lote
aberto na operação. As duas amostras ficaram em cópias privadas separadas e
foram revalidadas. Execução 80 continua cancelada, sem nova tentativa, envio,
alteração de workflow, configuração, commit, push ou VPS. Seis serviços
saudáveis. Documento integral permanece pendente de homologação.

**Implementado localmente em 14/11/2026 — grupos adaptativos:** autorizado
somente o item 1. Iniciar em oito, crescer 12/16 após compactos aceitos com
métricas e reduzir/conservar diante de respostas extensas, completas ou limite
de saída. Política por lote preservada na retomada e em alvos divididos,
com correções e transporte mantendo seus orçamentos. Fichas completas ficam
em até oito; nenhuma validação ou fonte é reduzida. Passaram 332 testes no
contêiner e 13 contratos com Node no host (345 testes distintos), além da
interface. Fixture real no OpenRouter: uma chamada de 13,595 segundos,
13,707 segundos com validação/PDF/ZIP. Não estima a duração do documento real.

Somente o renderizador atualizado; backup e migração explícita preservam
130 páginas, 477 registros e 20 fichas no lote aberto. Origem intacta e
sem política/medição inventada. Paralelismo anterior permanece; fila dinâmica
e campos comuns (itens 2 e 3) continuam para depois da avaliação.

**Comparação real concluída em 14/11/2026:** após autorização explícita para
até 24 chamadas (12 por modo), usadas 16 em cópias separadas do mesmo estado
inicial. O controle fixo fechou o lote 131–132 em 344,491 segundos e dez
chamadas; o adaptativo, em 318,723 segundos e seis chamadas. Ganho observado
de 7,48% no tempo total, 40% menos chamadas e 40,98% menos tokens de entrada
(511.354 → 301.819). O adaptativo recebeu grupos de 8/12/16/16/16/12 fichas.

Ambos acrescentaram 80 fichas, concluíram as mesmas 100 unidades/IDs por
unidade e passaram na validação de fonte, estrutura, inventário e evidências,
sem correções. Todas as 497 fichas anteriores ficaram intactas. As novas
redações não são integralmente idênticas; não houve revisão semântica
independente. Amostra restrita a duas páginas com excluídos e uma chamada por
vez: não mede o ganho com fichas completas ou dois lotes simultâneos. Houve
um intervalo de 50,336 segundos entre chamadas adaptativas, fora do tempo de
API e não perfilado, incluído no total observado. Não revisar a projeção do
documento inteiro por simples aplicação desse percentual.

Origem e conteúdo operacional preservados, incluindo a proveniência da
migração. Execução 80 cancelada, nenhuma principal ativa e seis serviços
saudáveis. Não houve retomada, incorporação das amostras, envio ou alteração
adicional de código/configuração. Fila dinâmica e campos comuns seguem
adiados; permanece pendente a homologação do documento integral.

**Concluído localmente em 14/11/2026 — melhor ocupação das duas vagas:**
autorizado somente o item 2. Lotes suspensos conservam gerador, contexto e
orçamentos, sem reservar uma das duas chamadas em voo; outro lote independente
pode avançar. Retomadas elegíveis têm prioridade, retry considera o tempo já
transcorrido e sobreposições continuam serializadas. Mantidos escritor único,
drenagem após falha persistente, grupos adaptativos e prazo global zero.

Passaram 72 testes direcionados e a suíte oficial: 336 no contêiner, com 13
contratos dependentes de Node pulados ali e aprovados no host, totalizando
349 testes Python distintos. Os 30 contratos no host e a interface também
passaram. Novos casos cobrem terceiro lote durante retry/contexto, pacote
idêntico, máximo dois, orçamento sem renovação e migração da política adaptativa.

Fixture real: uma chamada de 16,423 segundos e 16,581 com validação/PDF/ZIP.
Amostra real em três lotes independentes, teto de seis chamadas e duas por
lote: usadas cinco em 230,939 segundos, quatro respostas aceitas e uma de
contexto. Acrescentadas 22 fichas (20 excluídas e duas incluídas); média de
10,497 segundos por ficha nova. Concorrência máxima dois e ocupação observada
de 63,23% das duas vagas. A restrição de lotes/orçamento da própria amostra
deixou somente um lote elegível ao fim; não é o limite da operação real.
Não houve retentativa. A ocupação durante esperas foi comprovada nos testes,
sem comparação real antes/depois que isole seu ganho no tempo total.

Projeções condicionais do ponto operacional salvo, sem incorporar a cópia:
aproximadamente 56 minutos adicionais se as 66 páginas após o lote atual
repetirem 477/130 fichas por página (80 + 66 × 477/130 ≈ 322 fichas restantes);
aproximadamente 9h51 se repetirem 50 fichas por página (3.380 restantes).
Ambas usam os 10,497 segundos por ficha da amostra, incluindo contexto e
instrumentação. Não são intervalo de confiança, limite, ganho contra as 3h15
anteriores ou previsão confirmada. A amostra é pequena, mistura tipos de
trabalho e variou a granularidade: o lote 138–140 declarou fechamento sem
fichas, com oito unidades inventariadas; 146–147 continua parcial com duas
incluídas e nove unidades conhecidas. Homologação semântica permanece pendente.

Implantado somente o renderizador, com backup e migração explícita da versão
adaptativa. Origem intacta e 130 páginas, 477 registros fechados e 20 fichas
no lote aberto preservados; execução 80 cancelada, nenhuma principal ativa
e seis serviços saudáveis. Campos comuns (item 3) continuam adiados.

**Implementado em 15/11/2026 — campos comuns (ponto 3):** retomada autorizada
após reinício da máquina, com dispensa explícita de karpathy-guidelines
somente nesta tarefa. Valores integrais idênticos podem ser declarados uma
vez na resposta e referenciados por campo. O servidor reconstrói as fichas
antes das validações existentes, sem herança nem união; preserva diferenças,
IDs e evidências. Dicionário local, referências inválidas/encadeadas,
amplificação, correção única, revisão e retomada estão cobertos. A migração
reconhece a implementação anterior da fila por seus hashes exatos.

Validação local: 357 testes no contêiner (355 na suíte oficial e dois casos
adicionais de revisão/PDF/ZIP), mais 13 contratos com Node aprovados no host,
totalizando 370 testes Python distintos. Os 30 contratos completos e a
interface JavaScript passaram no host. Nenhum teste usou o provedor externo.

Aplicado somente ao renderizador local, com imagem anterior e cópia privada
do volume preservadas. Migração explícita revalidou e conservou integralmente
67 lotes fechados (páginas 1–130), 477 registros desses lotes e 20 fichas do
lote aberto, além de contexto, inventários e políticas. Arquivo de origem
intacto e novo checkpoint com permissão 600. V8 e Terra preservados, saúde
HTTP 200 e seis serviços saudáveis. Consultas somente leitura confirmaram
dois documentos e 15 tentativas em erro, sem execução n8n ativa. Nenhuma
retomada, nova tentativa, envio ou alteração na VPS foi iniciada.

**Histórico — medição inicialmente bloqueada:** preparados os mesmos recortes da medição anterior,
em cópia privada e com teto de uma chamada sintética e cinco documentais.
A revisão automática rejeitou o envio desse Markdown ao OpenRouter por não
reconhecer autorização verificável nesta conversa, inclusive após localizar
a autorização anterior. Nenhuma chamada executada nessa etapa. A autorização
foi solicitada e posteriormente concedida nesta conversa, conforme medição abaixo.
Os 10,497 segundos por ficha e os cenários de 56 minutos/9h51 restantes
continuam resultados históricos de 14/11, sem validar o ganho do ponto 3.

**Medição limitada concluída em 15/11/2026:** o usuário autorizou somente
algumas chamadas e reservou a execução completa para a aplicação. Realizadas
seis chamadas ao OpenRouter: uma sintética, sua correção e quatro documentais,
em cópia privada; nenhuma chamada adicional depois desse teto. A primeira
sintética usou formato de delta inválido e foi corrigida na chamada seguinte,
com PDF/ZIP conferidos. Para manter o teto, retirado o recorte 138–140:
duas chamadas em 131–132 e duas em 146–147, máximo duas simultâneas.

Janela entre a primeira requisição documental e a última resposta: 188,387 s
(3min08s), incluindo intervalos internos e excluindo preparação, sintético e
auditoria final. Média das quatro requisições: 65,608 s. Duas respostas foram
aceitas (oito e 12 excluídos), uma solicitou contexto e uma foi rejeitada.
Na cópia, 497 → 517 fichas completas, sem rascunhos e com 130 páginas fechadas.
Média da janela por ficha nova válida: 9,419 s; 170.626 tokens de entrada e
23.132 de saída informados nas quatro chamadas. O inventário continua parcial.

A resposta com contexto continha duas incluídas, que não foram promovidas.
A última também trouxe duas incluídas, mas usou `$campo` dentro de
`campos_adicionais/validade_certificacao`, fora dos campos integrais permitidos.
O validador rejeitou a referência; o limite da amostra encerrou antes de
solicitar a correção, sem nova chamada. Houve dez definições e 20 referências
a campos nas duas respostas, sem ficha completa incluída validada nesta
amostra. Não demonstra ganho do ponto 3 nem regressão controlada: falta um
controle equivalente e o recorte difere do teste anterior.

Cenário provisório com densidade histórica: 80 + 66 × 477/130 ≈ 322 fichas
equivalentes restantes × 9,419 s ≈ **50min35s adicionais**. Para aproximadamente
819 fichas totais, análise desde o início ≈ 2h09; somando somente a conversão
histórica de 674,18 s, ≈ **2h20 antes da finalização/envio**. Não é medição do
documento inteiro nem prazo garantido. A densidade de 50 fichas/página nas
66 páginas futuras projetaria cerca de 8h51 restantes. Correções, fichas
completas e contexto tornam a confiança baixa; não tratar os cenários como
intervalo de confiança ou usar o sintético para projetar o documento real.

Reprodução sem rede das quatro respostas gerou exatamente os mesmos lotes e
pendências da cópia, com os motivos e estados preservados. Fonte, digest,
evidências e todas as 497 fichas anteriores revalidados; checkpoint operacional
byte a byte intacto. Permanecem dois documentos e 15 tentativas em erro,
sem execução n8n ativa e com seis serviços saudáveis. Nenhum resultado da
amostra foi incorporado à operação. Sem mudança de código, configuração,
workflow, VPS, nova tentativa ou envio; implementação local do ponto 3
permanece instalada. A validação integral pela aplicação ainda está pendente.

**Histórico — bloqueio apurado em 15/11/2026, tentativa 15, execução 81:** retomada real
iniciada às 18h30m52s e encerrada às 18h48m51s de Brasília, cerca de 18 minutos.
Erro final `delta_evidencia_removida`, diagnóstico
`ANV8D-20d7ce87c913470da59a2e165943403a`, no bloco B4 do lote 144–145.
Ocorreu na sexta chamada do lote, já corretiva. O nó de preparação do ZIP
apenas propagou a rejeição da análise; não é falha demonstrada de geração PDF.

Reprodução sem rede confirmou que a resposta substituiu a evidência de
`limites.fim`, página 144, de 78 por 109 bytes. Ambas existem literalmente
na fonte, e a nova contém a antiga. A base do delta confere e o início foi
mantido. Contudo, o objeto de evidência anterior não aparece mais no bloco:
o transporte substitui `limites` e exige preservar todos os objetos anteriores.
Não houve acréscimo em `adicionar_evidencias`. A proteção contra remoção
rejeitou a resposta; a única correção do grupo já havia sido usada.
Manter em memória a evidência antiga por essa lista aditiva fez a fusão do
inventário passar, conservando o limite novo. Essa prova não homologa os
demais campos da resposta nem constitui correção aplicada.

Há também retrabalho do ponto 3: referências `$campo` foram emitidas em
subcampos de petição/CNPJ, fora dos campos integrais permitidos. O erro
imediatamente anterior do lote 144–145 foi desse tipo; a correção removeu
essa barreira, mas introduziu a troca de evidência descrita acima. Definir
explicitamente como refinar limites mantendo evidências anteriores e melhorar
o diagnóstico da evidência removida; manter validação literal e correção única.
A falha final não é HTTP 402, timeout ou interrupção manual.

Checkpoint revalidado sem rede: 73 lotes fechados, 141 páginas concluídas e
728 fichas nesses lotes; sete fichas completas no lote aberto 144–145,
total de 735 salvas. A contagem de 141 páginas não significa prefixo contínuo:
136–137 ainda estão pendentes, embora haja lotes fechados até a página 143.
Os seis serviços estavam saudáveis na investigação. Não houve nova chamada,
tentativa, alteração de código, correção de registros ou implantação. A análise
completa e o PDF continuam pendentes; retomar sem ajustar o contrato pode
repetir o problema. Detalhes e hipótese testada registrados no LOG.

**Corrigido e aplicado localmente em 15/11/2026 — evidências dos limites:**
autorizado o ajuste do tratamento. Ao receber limites completos refinados, o
servidor conserva citações anteriores deslocadas na lista de evidências do
mesmo bloco/unidade, mantendo os limites novos e todos os atributos antigos.
Não duplica objetos idênticos, apaga limites, normaliza trechos ou conclui
revisões. As validações de fonte, páginas, escopo e IDs permanecem. Remoções
fora de limites continuam inválidas e o diagnóstico agora identifica campo
anterior e objeto ausente. A correção continua única por grupo.

A resposta original que encerrou a tentativa 15 passou sem edição dos dados
na reprodução offline: quatro fichas recebidas, 11 no conjunto do lote e
211 ocorrências de evidências literais conferidas. O lote ainda é parcial,
conforme os dados, e esse resultado não foi incorporado à operação. Os
58 testes iniciais direcionados passaram. A suíte oficial final passou com
382 testes no contêiner e 13 contratos com Node conferidos no host, totalizando
395 testes Python distintos. Os 30 contratos completos e as duas suítes
JavaScript também passaram. Adicionado caso de limites diferentes mantendo
ambas as evidências e a revisão pendente, sem resolução automática.

Imagem anterior e volume privado preservados; aplicado somente o renderizador
local. Migração explícita para identidade nova manteve todos os dados,
inventários, filas, revisões e políticas: 73 lotes, 141 páginas fechadas e
735 fichas salvas, com origem intacta e novo arquivo 600. V8 e Terra
preservados, serviço HTTP 200 e reprodução da falha conferida na imagem final.
Permanecem dois documentos e 16 tentativas em erro, sem execução n8n ativa.
Nenhuma chamada externa, retomada ou nova tentativa foi iniciada. O operador
pode usar **Reprocessar** para continuar pelo progresso salvo; a conclusão
integral do documento e o PDF seguem pendentes dessa execução.

**Histórico — bloqueio de contexto na tentativa 16, execução 83, em 15/11/2026:**
das 19h07m33s às 19h30m19s de Brasília, 22min46s. Erro terminal:
`pedido de contexto sem nova busca ou página pendente`. O lote 144–145 agora
está concluído; a falha anterior de evidências não se repetiu como causa final.
Os seis serviços estavam saudáveis e o erro não indica crédito ou timeout.

Causa imediata confirmada em `context_window.request`: um retorno com chave
de contexto/busca entra nesse caminho antes da validação de fichas; se não
adicionar páginas solicitadas ou termos novos e a fila pendente estiver vazia,
interrompe. A proteção também rejeita releitura de página historicamente
entregue que não está disponível na janela atual. O estado do lote 151–152
tem 14 páginas solicitadas/entregues, nenhuma pendente e somente oito na
última janela; seis já entregues estão ausentes dessa chamada. Reconstruir o
pacote mantém essa ausência. Reprodução sem rede confirmou o mesmo erro para
essa releitura, uma busca vazia e uma busca conhecida repetida.

**Limite da apuração:** o retorno final de contexto não foi guardado. Esse
ramo fica fora do diagnóstico de validação de registros. A condição de parada
está confirmada; não há base para afirmar qual das variantes ocorreu no
retorno real, quais páginas/termos foram pedidos ou se havia fichas no mesmo
retorno. O estado sugere o lote 151–152 como origem, sem payload final que
comprove a solicitação exata. A lacuna entre entrega histórica e presença na
janela está demonstrada, não equivale à reprodução exata desse retorno.

Encaminhamento: distinguir presença atual de entrega histórica, tratar
campos de pedido vazios e releitura controlada mantendo proteção contra loops,
e guardar pedido/resposta/janela/estado antes de interromper. Não simplesmente
remover a proteção, promover revisão ou aumentar chamadas. A categoria
`infraestrutura` também está incorreta para esse caso: o n8n separou o erro
em mensagem e descrição `IA`, sem o prefixo `IA:` reconhecido pelo classificador.

Checkpoint revalidado: 75 lotes, páginas 1–145 concluídas, 771 fichas nesses
lotes e 36 completas no lote aberto 161–162, total 807, zero rascunhos.
Nenhuma resposta/citação foi editada e o arquivo permaneceu intacto. Há dois
documentos e 17 tentativas em erro, sem execução n8n ativa na consulta final.
Sem alteração funcional, implantação, nova chamada ou retomada nesta análise.

**Quatro pontos corrigidos e aplicados localmente em 15/11/2026:** autorizados com
preservação do desempenho. Contexto distingue entrega histórica de janela
atual, com releitura controlada e cache da busca conhecida. Listas vazias
não desviam fichas válidas. Repetições sem conteúdo ausente continuam bloqueadas;
até três pedidos de releitura por avanço documental ficam persistidos,
sem renovar outros orçamentos. Pedidos rejeitados guardam resposta, janela e
contexto em diagnóstico ANV8D; a classificação existente reconhece validação,
sem mudança de workflow. Mantidos dois envios simultâneos e grupos adaptativos.

Suíte final: 400 testes no contêiner e 13 contratos com Node conferidos no host,
413 testes Python distintos. Os 30 contratos e as duas suítes JavaScript
passaram. Benchmark controlado antes/depois, 15 repetições por versão:
12 chamadas simuladas, 25 gravações, máximo dois envios simultâneos e mesmas
100 fichas válidas em ambos. Mediana local 352,551 → 346,199 ms;
bytes das mensagens 669.667 → 669.643. Sem regressão observada nesse ensaio;
intervalos se sobrepõem, portanto não atribuir ganho firme nem garantir o
tempo total da API real, que não foi chamada nesta validação.

No estado real revalidado, uma releitura construída para a página 146 ausente
da janela do lote 151–152 foi atendida: pacote de sete páginas/87.092 bytes,
contra oito/97.242 no pacote anterior. História e 807 fichas intactas; repetição
de página já presente continuou bloqueada. Não é a resposta real perdida da
tentativa 16. Imagem anterior e cópia privada do volume preservadas. Migração
explícita manteve integralmente as 807 fichas, inventários, filas, buscas,
revisões e políticas; não inventou releituras anteriores. Origem intacta,
novo checkpoint 600 e V8 original conferidos. Aplicado somente ao renderizador
local, com seis serviços saudáveis. Não havia execução ativa antes da troca;
permanecem dois documentos e 17 tentativas em erro, sem nova execução.
Retomada do documento continua pela confirmação do operador em Reprocessar.

**Pausado a pedido do usuário em 15/11/2026, às 21h02 (Brasília):** a retomada
pela aplicação criou a tentativa 17, execução 85, iniciada às 20h09.
A execução foi cancelada no n8n e o renderizador interrompido; documento e
tentativa receberam `erro`, categoria `cancelamento_manual`, com mensagem
de progresso preservado. Os seis serviços da stack local estão parados,
com volumes mantidos. O checkpoint final foi revalidado contra o Markdown:
84 lotes e 159 de 198 páginas fechados, 977 fichas em lotes fechados e
26 completas em lotes abertos, total de 1.003, sem rascunhos. Cópia privada
em `miller-paused-progress-20261115`; arquivo de estado conferido byte a byte.
Próximo passo: subir a stack e confirmar Reprocessar no mesmo protocolo.
Ainda falta concluir as páginas restantes e validar o PDF final; a execução
interrompida não fornece uma média medida de ponta a ponta.

**Estado atual — retorno ao Terra em 12/11/2026:** a pedido do usuário,
restaurado GPT-6.1 Terra (`openai/gpt-6.1-terra`) somente no renderizador local,
com o mesmo V8 e as mesmas validações. Onze testes do renderizador passaram.
Uma página sintética pela API real respondeu HTTP 200 em 6,84 segundos, com
modelo, cobertura, PDF e ZIP conferidos. O teste sintético não homologa o
documento real nem demonstra correção da falha de evidência anterior.

A tentativa real com Sol começou às 00h31 e terminou em erro às 01h21 de
12/11/2026: evidência literal não localizada na página indicada. Permaneceram
preservados o PDF original, o Markdown e três tentativas, sem relatório final.
A troca de volta não iniciou outra tentativa. Próximo passo: confirmar a
retomada no mesmo protocolo para testar o Terra a partir do Markdown salvo.
A VPS não foi alterada.

**Diagnóstico da falha de evidência em 12/11/2026:** no protocolo investigado,
essa mensagem corresponde a uma única tentativa; a tela a apresenta na
tentativa e no registro de erro da mesma execução. O hash do Markdown confere
com o artefato registrado e seus 198 marcadores de página estão em sequência.
O validador faz busca textual exata; uma mudança apenas de quebra de linha
para espaço reproduziu a rejeição em caso sintético. A mensagem também agrupa
página com tipo inválido, página fora do conjunto permitido e citação vazia.
Não foi possível identificar o campo/citação real rejeitado: naquela execução,
o renderizador devolveu somente a mensagem genérica e não guardou o bloco/resposta.

**Concluído — diagnóstico e correção direcionada em 12/11/2026:** cada rejeição
de validação passa a guardar o bloco e a resposta em volume exclusivo privado,
com campo, ID do registro, página, trecho, motivo, hash da fonte e identificação
da tentativa/execução. A única chamada de correção recebe esses detalhes e a
resposta anterior; diferenças de espaços continuam rejeitadas. O histórico de
falha recebe página, motivo e referência segura. Falha de persistência encerra
como erro de armazenamento. O V8 aprovado e o Terra foram preservados.

Passaram 123 testes Python e 14 testes da interface. Dois casos sintéticos com
IA simulada pelo n8n local verificaram correção aceita (HTTP 200), segunda
rejeição (HTTP 422), associação à execução, privacidade e persistência após
recriar o contêiner. Renderizador e workflow aplicados na stack local, com os
seis serviços saudáveis. Não houve chamada externa nem nova tentativa real;
esses testes não homologam a análise do documento real. A resposta antiga
descartada continua indisponível. A VPS não foi alterada.

**Pendente — apresentação do histórico:** diferenciar no painel a tentativa
do registro de erro associado à mesma execução. A duplicação visual não foi
alterada nesta entrega.

**Histórico — primeira troca em 12/11/2026:** por solicitação do usuário, o modelo foi trocado
de Terra para GPT-6.1 Sol (`openai/gpt-6.1-sol`) e aplicado somente ao
renderizador da stack local. Onze testes do renderizador passaram, incluindo
identidade do modelo e recusa de resposta identificada como Terra. Uma análise
real pelo OpenRouter com uma página sintética respondeu HTTP 200 em cerca de
13 segundos, com PDF e ZIP íntegros e cobertura da página conferida.

O prompt V8 permaneceu com o hash aprovado. A troca não iniciou nova tentativa
do documento real e não altera o resultado das tentativas anteriores. Próximo
passo: conferir tempo, custo e conteúdo na retomada de material autorizado.
O teste sintético não homologa a análise do documento real. A VPS não foi
atualizada.

### Stack completa local

**Estado em 11/11/2026:** os seis serviços da stack `miller-full-local`
foram iniciados e ficaram saudáveis. O
[complemento local](deploy/full-local/README.md) publica a landing em
`127.0.0.1:18085` e o n8n em `127.0.0.1:25678`, com volumes próprios.
Login da landing, painel e prontidão do n8n responderam HTTP 200.
Os quatro workflows internos foram importados; processamento e erros foram
publicados, com credencial PostgreSQL local. Envio e reconciliação ficaram
inativos. Os acessos gerados estão somente no arquivo local protegido.

Validação atual: Compose válido, 15 testes de contrato de implantação aprovados
e upload de PDF artificial inválido com HTTP 202, seguido de estado `erro`,
uma tentativa e um registro de falha no banco. Essa falha HTTP do conversor
foi classificada como `infraestrutura`; a classificação precisa ser ajustada
e conferida antes de considerar o cenário de conversão plenamente homologado.

Naquele ponto da preparação, ainda faltava enviar um PDF sintético válido e
conferir a análise pelo OpenRouter. A chave estava configurada somente no
renderizador; Gmail OAuth e entrega manual local permaneciam pendentes. O
serviço Ollama estava saudável, sem modelo baixado nesse volume, pois o provedor
selecionado era OpenRouter. As tentativas posteriores estão registradas abaixo;
este parágrafo é histórico, não a próxima ação atual.

**Teste posterior em 11/11/2026:** o usuário enviou um PDF pela landing local.
A execução 3 converteu e persistiu o Markdown, chamou a análise V8 e encerrou
em `erro` após o OpenRouter retornar HTTP 402. Não houve relatório Markdown,
PDF final ou envio. Os seis serviços permaneceram saudáveis. A consulta
somente de metadados da chave confirmou um orçamento mensal com pouco limite
restante; o saldo global da conta e a origem detalhada do bloqueio não foram
confirmados. É necessário revisar crédito/orçamento no OpenRouter antes de
novo teste controlado. O erro de IA foi classificado como `infraestrutura`,
reforçando a pendência de classificação descrita acima. Não houve reexecução
automática; PDF e Markdown permaneceram preservados.

**Estado final conhecido em 15/11/2026:** a stack local foi pausada a pedido do
usuário. Os seis serviços foram parados sem remover volumes. O checkpoint privado
foi revalidado contra o Markdown e preserva 159/198 páginas fechadas e 1.003
fichas; não existe relatório final homologado. A aplicação não foi reiniciada
nem o checkpoint retomado durante a integração das PRs em 16/11.

### Reenvio de PDF já cadastrado

**Corrigido localmente em 15/11/2026:** o reenvio do PDF autorizado retornava
o mesmo protocolo e a mensagem de cancelamento de 14/11, sem nova tentativa.
A tela anunciava protocolo registrado e mostrava o erro antigo sem identificar
o reenvio. A API agora informa `duplicate`; a tela explica que nenhum novo
processamento foi iniciado, distingue o status do protocolo existente e
oferece acesso ao detalhe. Mensagem, arquivos e histórico são preservados.
Trocar o arquivo cancela o acompanhamento anterior para impedir resposta
atrasada na seleção nova. Não criar protocolo fictício se a consulta de um
duplicado falhar. Deduplicação e confirmação da retomada permanecem.

Validação atual: 62 testes de upload/contratos no contêiner e 13 contratos
dependentes de Node no host, totalizando 75 testes Python distintos; os 30
contratos completos e as duas suítes JavaScript da interface passaram.
Aplicado somente ao gateway local. Reenvio real do mesmo PDF pela API local
retornou HTTP 200 e `duplicate:true`, com protocolo, histórico e PDF íntegros,
sem nova tentativa ou chamada externa. Permanecem seis serviços saudáveis,
dois documentos e 15 tentativas em erro, sem execução n8n ativa.

O início integral do mesmo PDF não é uma ação disponível na interface atual:
**Reprocessar** usa o último checkpoint íntegro. A correção não implementa
reinício total nem inicia processamento em nome do operador.

### Retomada pelo botão Reprocessar

**Estado em 11/11/2026:** implementada a retomada autenticada pelo último
artefato íntegro registrado, conforme RF-21. O botão de processamento foi
separado da tentativa de e-mail. O servidor valida o checkpoint, registra a
autorização, bloqueia solicitações concorrentes e abre uma nova tentativa do
mesmo protocolo. Markdown salvo evita reconversão; relatório vinculado à fonte
evita nova análise. No V8, o PDF da mesma revisão é recuperado do ZIP verificado.
Checkpoints ausentes ou divergentes bloqueiam a retomada.

Validação: suíte ativa com 104 testes Python aprovados e três testes JavaScript
da tela aprovados. Em workflow n8n sintético separado, a falha de análise foi
retomada sem reconversão; a falha posterior ao relatório reutilizou o PDF sem
nova análise. Solicitações simultâneas resultaram em um despacho e um conflito,
com histórico e versões preservados. Caminho comum de renderização e retomada
de PDF também exercitado sem chamadas de IA.

Aplicada somente à stack local, com export anterior preservado, credenciais
mantidas e workflow publicado. A prévia do protocolo real reconheceu o Markdown
legado como checkpoint de análise, sem iniciar nova execução. O próximo passo
do operador é atualizar a página e clicar em **Reprocessar** após corrigir a
causa externa. Naquela implantação, a retomada de lotes internos de IA ainda
não estava implementada; lotes não persistidos reiniciavam a partir do Markdown.
A VPS não foi atualizada e Gmail permanece fora desta validação.

**Concluído em 12/11/2026 — confirmação antes da retomada:** o clique em
**Reprocessar** abre um diálogo com o ponto de retomada, **Cancelar** e
**Confirmar reprocessamento**, conforme RF-21. Somente confirmar despacha a
solicitação; cancelar, Escape ou fechar o diálogo não iniciam tentativa.
Cliques repetidos são bloqueados durante o despacho. Aplicado à stack local.

### Atualização automática do andamento no detalhe do protocolo

**Implementado em 12/11/2026:** a tela consulta o detalhe a cada cinco segundos
enquanto visível, exibe a etapa persistida e atualiza tentativas, erros, envios
e disponibilidade dos artefatos, conforme RF-15. Preserva destinatários,
observações e aba selecionada; não recarrega um PDF inalterado. Pausa as
consultas em aba oculta e ao sair. Falha de consulta preserva os dados e mostra
aviso de atualização, sem classificar o processamento como erro.

A API expõe `current_stage` já armazenado no banco. O workflow registra
recuperação do checkpoint, conversão, análise e preparação do PDF, vinculadas
à tentativa ativa. Não há percentual estimado nem acompanhamento dos lotes
internos da IA durante uma chamada. Export anterior e configuração implantada
foram preservados; a versão local com os marcadores foi publicada.

Validação: 107 testes Python e 14 testes JavaScript aprovados. Na cópia n8n
sintética, a primeira análise falhou e a retomada usou o Markdown salvo:
uma conversão, duas análises simuladas e documento em `aguardando_envio`, com
histórico preservado e novos nós de etapa executados. O n8n manteve a segunda
execução marcada `running`, embora o último nó tivesse sucesso e não houvesse
execução ativa para interromper; registrar/investigar essa inconsistência de
infraestrutura separadamente. Logs também mostraram erro no processamento
de estatísticas. A inspeção visual ficou pendente por indisponibilidade do
acesso ao navegador. A VPS não foi alterada e o documento real não foi
reprocessado.

### Teste local — Gerar somente Markdown

**Estado:** modo implementado em 29/10/2026, separado da stack operacional.

Interface local com upload/conversão/download em `127.0.0.1:18080`, sem IA,
banco, n8n, credencial ou `.env`. Reutiliza o conversor, preserva o corpo
paginado, metadados e avisos no arquivo. Não é relatório final nem alteração
da landing/VPS. Instruções em [infra/pdf_converter/README.md](infra/pdf_converter/README.md).

Validação histórica de 29/10: 115 testes Python e 21 testes JavaScript aprovados; build e
Compose local válidos; upload, conversão e download conferidos no navegador
com PDF público de uma página. Teste HTTP da versão final com PDF público de
100 páginas: 200, sequência 1–100, hashes conferidos, aproximadamente 49,45 s
somente conversão/exportação local. Não mede relatório, IA ou meta de 90 minutos.

Validação de 31/10 do conversor `0.4.0`: 129 testes Python e 21 JavaScript
aprovados. O PDF autorizado de 198 páginas foi convertido pelo endpoint local
com HTTP 200 em 674,18 s (11 min 14 s), gerando 2.173.841 bytes de Markdown,
marcadores 1–198 e hashes conferidos. Foram mantidos 89 avisos de tabelas
(86 possíveis tabelas em texto e três tabelas estruturadas), sem páginas sem
texto ou fallback de leitura. Regeneração em `output/markdown/`, artefatos locais
não versionados. Esse tempo é da conversão nesta máquina, não da VPS ou da IA.

Próximo passo do operador: gerar `.md` dos PDFs autorizados, conferir avisos e
conteúdo com o original e testar prompts manualmente. Integração futura com a
API OpenAI, escolha de modelo, qualidade regulatória e tempo final não foram
validados nesta entrega e não são ativados por este modo.

### Histórico do teste manual — V8 autossuficiente, somente prompt + Markdown

**Estado em 01/11/2026:** usuário esclareceu que o teste deve começar com
somente dois arquivos. Criado o [prompt V8 autossuficiente](prompts/chatgpt-anvisa-pdf-v8-autossuficiente.txt),
consolidando as instruções completas e as correções gerais, sem depender de V7,
relatórios, ZIP, checkpoint ou histórico anterior. O guia de envio foi
atualizado. Naquela data a execução e o aceite ainda estavam pendentes.

Próximo passo: em conversa nova, anexar somente o prompt autossuficiente e o
mesmo Markdown gerado pela aplicação. A análise parte do zero; PDF, JSONL,
cobertura e verificação são saídas a gerar, não requisitos de entrada.
Solicitar o ZIP final para auditoria. Não alterar a aplicação nem reconverter
o documento. O prompt não inclui empresas, páginas-alvo, contagens ou hash
fixo desta edição; as regressões continuam externas à geração.

Esta edição já orientou ajustes: resultado positivo não comprova generalização.
Validação do modelo, documento independente, aceite do cliente e integração
de IA/API permanecem pendentes. Complemento anterior preservado abaixo.

### Histórico do teste manual — V8 complementar à V7

**Estado em 01/11/2026:** V8 preparada a pedido do usuário para corrigir a
entrega V7 `v7-cp027-20261101` na mesma conversa. Ainda não executada nem
homologada. Arquivos históricos: `chatgpt-anvisa-pdf-v8.txt` e
`LEIA_ME-chatgpt-anvisa-v8-complementar-historico.txt`, arquivados localmente.
V7 preservada como base. Este complemento foi substituído, para o próximo
teste, pela versão autossuficiente descrita acima.

A rodada V7 com o Markdown corrigido produziu 710 fichas e PDF de 414 páginas,
declarando as 198 páginas concluídas. A auditoria de 01/11 confirmou os 710
links e a transposição dos valores examinados, mas encontrou nove unidades
farmacêuticas omitidas na continuação da RE 2.175, fonte página 146. Também
identificou artigos de vigência ausentes, campo de escopo incoerente,
ambiguidade de inclusão, 34 observações de cobertura desatualizadas e hash
do PDF divergente da verificação. Portanto, a entrega não foi aprovada como
completa. As falhas demonstradas não exigem regenerar o Markdown.

Procedimento histórico do complemento: anexar o V8 na mesma conversa, conferir acesso ao prompt V7,
Markdown e pacote cp027 e executar a revisão corretiva. Reconferir unidades
e continuações da fonte contra os registros, corrigir estados e gerar os
quatro arquivos cumulativos V8 em nova revisão, mantendo os originais.
Não reutilizar checkpoints de outra fonte. A V8 contém localizadores dos
erros conhecidos desta edição; um reparo bem-sucedido não prova generalização.

Alterações desta etapa limitadas a prompt e documentação. Aplicação, conversor,
contrato operacional, n8n, VPS e Markdown permanecem inalterados. Validação
do novo pacote, aceite do cliente, teste em documento independente e futura
integração de IA/API permanecem pendentes.

### Histórico do teste manual — Prompt Anvisa V7 e conversor

**Estado em 31/10/2026:** V7 executada pelo usuário e auditada; não aprovada
como entrega final. O PDF recebido tem 39 páginas e 81 fichas incluídas; a
cobertura continua parcial. A auditoria encontrou associação indevida dos
suplementos das páginas 114/115 à RE 2.140, em vez da RE 2.143. O Markdown da
aplicação já trazia os atos fora da ordem visual; é defeito da fonte intermediária,
não algo a corrigir silenciosamente por suposição no prompt.

Decisão autorizada: corrigir a ordenação no conversor compartilhado e regenerar
o Markdown do mesmo PDF pela aplicação local. A versão `0.4.0` lê regiões e
colunas pela geometria, preserva tabelas detectadas e explicita limitações de
ordem. Não há regras por empresa/ato nem edição manual do documento.
V6, V7, PDF original e Markdown anterior são preservados. A VPS não foi alterada.
Antes de implantar o conversor no fluxo operacional, medir o custo da leitura
geométrica no servidor e revisar `PDF_CONVERTER_TIMEOUT_SECONDS` (padrão de
300 segundos no export); o teste local não ajusta nem valida esse timeout.

Próximo passo definido em 31/10 (histórico, sucedido pela etapa V8 acima):
abrir uma conversa nova no ChatGPT e anexar o **novo
Markdown gerado com o conversor 0.4.0** e o mesmo
`chatgpt-anvisa-pdf-v7.txt`, sem alterar o prompt (cópia histórica local).
Não reutilizar checkpoints ligados ao hash antigo nem fornecer relatórios
anteriores ou o guia de regressões como fonte da geração. Guardar PDF, JSONL,
cobertura e verificação da mesma revisão para conferir conteúdo e omissões.
Mensagem de início/continuação e regressões externas ao prompt em
`LEIA_ME-chatgpt-anvisa-v7.txt` (cópia histórica local).

O prompt prioriza interpretação pela IA, com código apenas como apoio local,
e não exige desenvolver outro parser/testes na execução. Nenhuma integração,
troca de modelo ou mudança do prompt ativo foi feita. Testes do conversor não
homologam a extração por IA. Aceite do cliente, teste
em documento separado e contrato de integração permanecem pendentes.

### Experimento local — Correção da entrega manual V5 (referência)

**Estado em 31/10/2026:** scripts da entrega manual corrigidos em cópia isolada,
sem integração na aplicação. O ZIP original e o Markdown autorizado foram
preservados. O pacote reproduzível e o novo PDF ficam em `output/pdf/`, como
artefatos locais não versionados; não devem ser incluídos em commit.

Validação deste experimento: 144 testes aprovados, G1–G8 sem falhas, 710 fichas
incluídas, 310 apresentações preservadas e 710 links internos reconciliados.
O PDF tem 304 páginas; 13 páginas críticas foram inspecionadas visualmente,
sem cortes ou sobreposições nas amostras. A auditoria e os hashes acompanham
o pacote. Isso não homologa individualmente os 710 eventos.

Próximo passo: revisão e aceite do cliente, confrontando o original, as tabelas
com avisos nas páginas-fonte 122/123, as correções e as exclusões. O extrator
continua específico dos formatos desta edição do DOU; outros documentos
exigem validação separada. O tempo local parte do Markdown e não mede a meta
operacional de 90 minutos. Não houve mudança de prompt ativo, modelo, API,
n8n, Docker ou VPS; integração futura depende de nova decisão.

### VPS de testes — fotografia verificada em 27/10/2026

Verificação por SSH, gateway e painel autenticado do n8n em 27/10/2026:

- O projeto Automação Miller tem 6 containers saudáveis: n8n 2.30.5, PostgreSQL, Ollama 0.32.1, conversor PDF, renderizador PDF e gateway.
- O n8n escuta apenas em 127.0.0.1:25678. Use túnel SSH para abrir o painel.
- O gateway publica a porta apenas dentro da rede Docker. Não foi encontrado listener HTTP/HTTPS na VPS; a landing ainda não tem uma entrada pública verificada.
- Estão publicados o workflow v2 `Automação Regulatória - Duas Passagens` e o workflow de erros internos. O v1 está despublicado. Envio manual, reconciliação e avaliação sintética NVIDIA permanecem inativos.
- O proprietário do n8n foi criado pelo responsável, que concluiu o login no painel. A senha não foi registrada neste repositório; o local onde o responsável a guardou não foi verificado.
- O banco tem 10 documentos: 4 em `aguardando_envio` e 6 em `erro`. Um dos quatro aguardando envio é o fixture sintético desta homologação; os outros três já existiam. Não houve envio de e-mail.
- Os seis containers do Miller estavam saudáveis na verificação, incluindo n8n 2.30.5, PostgreSQL, Ollama 0.32.1, conversor PDF, renderizador PDF e gateway.
- A segunda tentativa autorizada para o PDF extenso foi interrompida quando o usuário escolheu avaliar o uso da NVIDIA API. O n8n registrou a execução 16 como erro em `Ollama - Analyze each batch`; o Ollama foi reativado e está saudável. PDF original, Markdown v1 e artefatos anteriores foram preservados. Não foi gerado relatório v2 nem enviado e-mail.
- Não há credencial NVIDIA configurada na VPS. O único workflow NVIDIA é a avaliação sintética, inativa e sem credencial. O usuário autorizou planejar NVIDIA NIM como provedor externo para documentos reais, mas a implementação depende de endpoint e licença de produção cujos termos permitam expressamente informação governamental. A chave enviada pelo chat está comprometida e não pode ser usada. Não transmitir o PDF real ao Developer/API Catalog Trial; a licença da conta NVIDIA não foi verificada.
- A senha administrativa root foi exposta anteriormente e sua rotação continua pendente. A chave de API NVIDIA exposta também precisa ser revogada.
- Em 27/10 foi criado backup protegido do PostgreSQL, do volume de artefatos e dos cinco workflows existentes antes da importação. A restauração isolada e uma cópia fora da VPS ainda não foram testadas.
- A VPS tem 2 vCPU e 7,8 GiB de RAM. Na consulta havia 6,2 GiB disponíveis, 330 MiB de swap em uso e 64 GiB livres em disco. Ela é compartilhada com o projeto Ideia Saúde Agent Test, que mantém 5 containers. O container de interface desse projeto usava 92% do próprio limite de 256 MiB; isso não causou pressão de memória geral na fotografia consultada, mas reforça a necessidade de acompanhar carga antes de processar PDFs longos.
- As antigas stacks BRANDRIOT Socialsuite e Supabase Socialsuite foram removidas em 26/10/2026. Não aparecem mais no inventário Docker consultado.

### Limitação de qualidade observada

O teste sintético ponta a ponta de 27/10 usou um PDF artificial de duas páginas com o mesmo processo, uma concessão na página 1, cancelamento na página 2 e uma frase de injeção de prompt. A conversão cobriu 2/2 páginas; a IA não revelou segredo nem seguiu a frase maliciosa. O gateway encerrou a tentativa sem erros em `aguardando_envio`, gerou Markdown e PDF e registrou zero entregas de e-mail.

A validação independente do relatório confirmou 8 de 10 referências; duas ficaram pendentes por formato não reconhecido. A síntese também declarou que não havia contradição, omitiu a mudança de concessão para cancelamento e recomendou preparar renovação após o cancelamento. A ordem das seções saiu incorreta e o PDF mostrou âncoras Markdown sem resolução. Portanto, o teste técnico passou, mas o relatório não está aprovado para uso real. Corrigir a síntese/validação e repetir este fixture antes de processar documentos reais.

A cobertura de páginas e a localização literal das citações são checagens mecânicas. Elas não garantem que a interpretação da IA esteja correta.

## Base já existente no repositório

- Entrada privada de PDFs, protocolo, hash SHA-256 e bloqueio de duplicidade.
- Armazenamento privado de PDFs e relatórios; metadados e estados no PostgreSQL.
- Conversão PDF para Markdown com marcador de página. Não há OCR.
- Análise integral por lotes sequenciais de até 6.000 caracteres.
- Geração de relatório Markdown e PDF.
- Conferência mecânica de cobertura e citações.
- Painel, conferência opcional e download autenticado do PDF concluído.
- Exports separados para processamento, reconciliação, erro e avaliação sintética.
- Scripts de backup e migração no repositório.

Esses itens descrevem a base versionada. O estado da VPS e dos workflows ativos
é uma fotografia separada, indicada acima; exports no Git ficam inativos e não
confirmam o estado implantado.

## Incremento de contexto determinístico — testado localmente

O gateway agora relê o Markdown persistido, confere seu SHA-256 e localiza um
conjunto fixo de termos regulatórios e formatos conhecidos de número de
processo. Ele mantém página e trecho de cada ocorrência e liga números
exatamente iguais encontrados em páginas diferentes. O relatório lista essas
menções sem classificá-las como decisões; a síntese recebe os vínculos como
pistas e deve preservar contradições.

Registro histórico da versão v1 em 26/10: o workflow usava o prompt v6, que
declara texto e evidências do PDF como dados não confiáveis e instrui o modelo a
ignorar comandos embutidos. A IA analisava todos os lotes e a primeira passagem
determinística era apenas contexto adicional. A lista de termos era limitada e
não garantia cobertura semântica.

### Homologação local e documentos de referência

1. Usar cópias autorizadas de documentos de referência.
2. Começar com um PDF textual curto e confirmar protocolo, Markdown e relatório.
3. Conferir se as páginas aparecem em sequência e se os fatos citados estão no trecho correto.
4. Concluir a validação do PDF longo de 142 páginas citado acima, sem iniciar duplicata.
5. Conferir o relatório com o responsável operacional; a revisão humana é uma conferência opcional do produto, mas o aceite dos testes do projeto continua necessário.
6. No modo Ollama, manter a análise local. No modo Anvisa V8, usar o OpenRouter somente com Markdown autorizado e após o teste sintético da integração.

Esse incremento da versão v1 foi testado localmente com fixture sintético e 89
testes em 26/10/2026. Ele não havia sido implantado na VPS na consulta daquela
data. Os exports do repositório permanecem `active=false`.

## Nova arquitetura híbrida — 27/10/2026

Foi implementada no checkout local uma versão v2 inativa com duas passagens:

1. Python lê todo o Markdown já persistido e localiza identificadores, termos,
   datas e durações em formatos conhecidos, preservando página e linha de
   evidência. O resultado registra a versão do conjunto de regras.
2. A IA audita todos os lotes à procura de fatos relevantes que não aparecem
   nas observações determinísticas e propõe candidatos com página e citação.
3. O gateway Python valida a página, o lote de origem e a existência exata do
   trecho citado no Markdown. Candidatos inválidos ficam pendentes e não entram
   na síntese.
4. A IA interpreta as observações e somente os candidatos aceitos para redigir
   o relatório final.

O código do gateway, o export
`workflows/automacao-regulatoria-internal-v2-hybrid.json`, o prompt e o schema
estão no repositório. Isso não significa que a IA foi removida: ela continua
auditando todos os lotes e interpreta o relatório. A checagem do Python confirma
somente a localização da citação, não a correção semântica do candidato.

**Situação em 27/10:** o export v2 está no commit `a5e036c`, foi importado e
publicado na VPS após backup. O v1 está despublicado; o handler de erros segue
ativo. A homologação sintética terminou tecnicamente, mas encontrou falhas de
interpretação e formatação descritas no estado verificado. Não reprocessar o PDF
oficial até corrigir e repetir a homologação.

**Validação em 27/10:** `python -m pytest -q` — 94 testes aprovados, com dois
avisos de depreciação do FastAPI; Compose validado localmente e na VPS. O teste
sintético da VPS usou Ollama local `qwen2.5:3b`, uma execução, 2 páginas e
terminou em `aguardando_envio`. Nenhum PDF real foi processado e nenhum e-mail
foi enviado.

## Plano de execução

### P0 — fechar segurança e recuperação

1. **Rotacionar o acesso root da VPS.**
   Responsável: administrador do servidor. Mantenha primeiro o acesso por chave SSH validado, troque a senha exposta e guarde o novo valor no cofre aprovado. Não envie a senha pelo chat.

2. **Confirmar a guarda da senha do proprietário do n8n.**
   Responsável: administrador do n8n. A conta foi criada e o login foi verificado em 27/10. Confirme que a senha definida está guardada no cofre aprovado. Depois reconfirme a credencial PostgreSQL.

3. **Publicar a landing de forma segura.**
   Responsáveis: administrador da VPS e responsável técnico. Defina domínio e proxy HTTPS aprovado, publique somente o gateway, confirme firewall e cookie seguro e teste login/logout. Mantenha a porta 25678 do n8n presa ao loopback. Não exponha o gateway ou o n8n diretamente sem proteção.

4. **Testar restauração do backup e manter cópia fora da VPS.**
   Responsável: administrador da VPS. O backup protegido do banco, volume de artefatos e workflows foi criado em 27/10. Copie-o para outro local, confira os hashes e restaure em ambiente isolado. A cópia na própria VPS não protege contra perda total do servidor.

5. **Regularizar os acessos a provedores externos.**
   Responsável: administrador das contas de IA. Revogue a chave NVIDIA exposta e confirme a situação da chave exposta anteriormente; a API Trial permanece restrita ao fixture sintético. Antes de retomar o V8 local, confira a chave e o orçamento do OpenRouter no ambiente protegido, revise os termos aplicáveis ao documento e confirme a autorização do destino. A chave fica somente no `.env` protegido do `report-renderer`, nunca no Git, workflow ou navegador. Para documentos reais via NVIDIA, exija licença de produção e permissão expressa para os dados.

6. **Corrigir as falhas semânticas e estruturais do relatório híbrido.**
   Responsável: responsável técnico e responsável pelo produto. O teste sintético de 27/10 não preservou a sequência concessão/cancelamento, recomendou renovação após o cancelamento, marcou duas referências como pendentes por formato e ordenou as seções incorretamente. Ajuste prompt e validação, inclua testes de regressão e repita o teste antes de qualquer PDF real. O PRD atual permite que referências pendentes não bloqueiem a conclusão do relatório; a equipe ainda deve decidir se essa regra é aceitável.

### P1 — fazer o caminho operacional funcionar de ponta a ponta

7. **Triar os documentos operacionais preexistentes.**
   Responsáveis: operador e responsável técnico. Examine os três documentos que já aguardavam envio e os seis em erro antes do fixture sintético. Descubra a causa de cada erro, preserve histórico e não reinicie documentos automaticamente. Não conte o novo fixture sintético como documento operacional. A tentativa anterior do PDF extenso continua sem nova execução nesta homologação.

8. **Homologar o download direto e a reconciliação.**
   Responsável: administrador do n8n. A migração 006, a publicação dos workflows atualizados e o vínculo PostgreSQL foram verificados em 23/11 na VPS do cliente. Valide uma falha controlada e use um PDF sintético autorizado para confirmar a conclusão da tentativa e o download no painel. Atualize a reconciliação e publique-a depois de verificar que evita execuções repetidas.

9. **Manter a proteção contra comandos embutidos e ampliar os casos de regressão.**
   Responsável: responsável técnico. O fixture de 27/10 continha um pedido para revelar uma chave; o relatório não o seguiu. Esse resultado cobre somente um caso sintético e não garante resistência geral. Preserve este teste e repita-o após qualquer mudança de prompt ou modelo.

10. **Repetir a homologação ponta a ponta após corrigir o relatório.**
    Responsáveis: responsável técnico e operador. A primeira execução sintética completou upload, conversão, análise e geração dos artefatos, mas falhou em critérios semânticos e estruturais. Repita o fixture de duas páginas e só aprove quando o relatório descrever concessão e cancelamento na ordem correta, não recomendar renovação incompatível, citar as evidências sem pendências indevidas e respeitar a ordem das seções. Confirme o status `concluido` e o download autenticado do PDF gerado.

11. **Executar a matriz de falhas e retomada.**
    Responsáveis: responsável técnico e operador. Teste PDF inválido/sem texto, falha do conversor, falha de lote Ollama, falha de validação, renderização, armazenamento, duplicidade, reenvio e recuperação de processo parado. Confirme que erro não vira “informação ausente”, que tentativa repetida não duplica trabalho e que o download do PDF exige conclusão e sessão válida.

12. **Homologar os caminhos com documentos autorizados.**
    Responsáveis: responsável técnico, operador e representante indicado pelo cliente. No v2 da VPS, repetir primeiro o fixture sintético após corrigir as falhas de interpretação e estrutura; depois avaliar o PDF de 142 páginas em janela autorizada, sem duplicar protocolo. No V8 local, retomar o documento de 198 páginas pelo mesmo protocolo e checkpoint, após conferência dos acessos e confirmação de **Reprocessar**. Em ambos, conferir cobertura, fatos, evidências, duração e qualidade; registrar aceite e limitações. O V8 ainda não tem relatório final homologado.

### P2 — melhorar segurança e desempenho depois da estabilidade

13. **Medir o desempenho com carga controlada.**
    O modelo qwen2.5:3b executa em CPU numa VPS compartilhada de 2 vCPU. A segunda tentativa do PDF de 142 páginas foi interrompida após cerca de 26 minutos, ainda na análise por lotes. O V8 implementa grupos adaptativos e até duas chamadas concorrentes para lotes independentes; a branch registra benchmark controlado sem regressão, mas o relatório real completo ainda não foi concluído. Meça tempo e RAM em PDFs curtos e longos e confirme duração, custo e qualidade em ponta a ponta. Depois de aprovar endpoint NVIDIA de produção, compare primeiro com fixture sintético. Não envie documento real à API Trial nem aumente o paralelismo além do limite implementado sem medição.

14. **Reduzir exposição da landing.**
    Avalie remover o token legado aceito por URL, adicionar limitação de tentativas no login e no upload, proteção CSRF e níveis de acesso quando houver necessidade operacional. Preserve o túnel local do n8n.

15. **Definir operação contínua.**
    Aprovar retenção de PDFs, política de backup, alerta de falha, responsável
    por conferir pendências e tempo de resposta. RAG, treinamento e coleta DOU
    continuam opcionais e fora do caminho ativo.

### Limites de escopo preservados

- Google Drive: integração histórica; não recebe novos documentos.
- RAG, embeddings e quality_checks: capacidade opcional/legada, não usada no fluxo atual.
- JSON de cada lote: não é relatório final; no V8, o progresso validado é persistido em checkpoint privado, sem `analysis_json` público.
- NVIDIA Trial: somente teste manual com fixture sintético; nunca documento real.
- OCR pago, app mobile, fine-tuning e modelo proprietário: fora do escopo aprovado.

## Critério de entrada em produção

Só avançar quando todos os itens P0 estiverem decididos, os itens P1 críticos passarem em ambiente controlado, o backup puder ser restaurado, os acessos estiverem protegidos e o responsável operacional aceitar por escrito a qualidade e as limitações do relatório.

## Como manter este arquivo

Marque uma tarefa como concluída somente com evidência. Ao verificar estado remoto, registre a data e a origem da confirmação. Registre decisões e incidentes no LOG.md sem incluir senhas, tokens, dados pessoais ou conteúdo de documentos reais.
