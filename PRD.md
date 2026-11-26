# PRD.md — Agente de Automação e Análise Regulatória

## 1. Identificação do produto

**Produto:** Agente de Automação e Análise Regulatória
**Empresa responsável:** DB Tecnologia
**Responsável técnico:** Rui Diniz — Engenheiro de Software
**Objetivo do projeto:** automatizar o recebimento, leitura, organização, análise e distribuição de documentos regulatórios em PDF, substituindo um processo manual e repetitivo por um fluxo automatizado, rastreável e de baixo custo operacional.

---

## 2. Visão do produto

O produto será uma solução self-hosted de automação regulatória construída principalmente com **n8n + Ollama + PostgreSQL**, executada em servidor Linux via Docker. O Ollama é o caminho local padrão. O relatório Anvisa V8 usa GPT-6 Luna por padrão quando o OpenRouter é selecionado. O provedor só pode receber Markdown autorizado após revisão dos termos e da privacidade aplicáveis, sem fallback automático. A integração NVIDIA NIM de produção permanece condicionada a endpoint/licença que permita o tipo de dado processado.

O caminho ativo recebe documentos pela landing privada e mantém os arquivos no
volume Docker e os metadados no PostgreSQL. O Google Drive permanece apenas nos
exports históricos; não é parte da entrada nem do processamento atual.

O sistema deve receber novos documentos PDF pelo gateway de upload, converter cada documento para Markdown paginado, analisar todas as páginas em lotes e gerar um relatório técnico em Markdown e PDF. O PostgreSQL mantém os metadados e os estados; o volume privado do Docker guarda os arquivos. O painel autenticado libera o download do PDF assim que o workflow conclui o processamento e armazena o arquivo. O sistema confere automaticamente cobertura de páginas e referências literais; a revisão humana permanece opcional e uma referência pendente não bloqueia a conclusão operacional.

A IA deve atuar como ferramenta de apoio técnico à leitura, classificação, organização e geração de relatórios. O sistema deve produzir uma análise automatizada com linguagem e estrutura de especialista sênior, sem se apresentar como autoridade regulatória, advogado, médico ou responsável técnico, nem emitir decisão jurídica, médica ou regulatória definitiva.

---

## 3. Problema que o produto resolve

O processo atual depende de leitura, identificação, consolidação e distribuição manual de informações regulatórias.

O produto deverá reduzir:

- trabalho operacional repetitivo;
- tempo gasto na leitura inicial de documentos;
- risco de perda de informações durante o processamento manual;
- dependência de APIs de IA cobradas por token;
- dificuldade de rastrear quais documentos foram processados;
- inconsistência na estrutura dos relatórios gerados.

---

## 4. Usuários e atores

### 4.1 Usuário operacional

Responsável por enviar documentos pela landing privada e consultar os resultados gerados.

### 4.2 Equipe de conferência opcional

Pode conferir o relatório, as páginas e as evidências quando a equipe desejar:

- ambiguidade ou contradição;
- informação não comprovada;
- referências de página ou evidência pendentes;
- falha parcial de extração ou análise.

Essa conferência é um recurso operacional e não é pré-requisito para gerar,
utilizar o relatório. Falhas técnicas continuam sendo tratadas
como erro e não como resultado válido.

### 4.3 Sistema automatizado

Responsável por:

1. detectar novos documentos;
2. processar o conteúdo;
3. consolidar temporariamente os achados dos lotes;
4. produzir o relatório;
5. armazenar os artefatos;
6. disponibilizar o PDF do relatório no painel autenticado;
7. registrar erros, alertas de qualidade e referências que merecem conferência opcional.

---

## 5. Arquitetura funcional de referência

Componentes definidos para o projeto:

- **n8n:** automação e orquestração do workflow;
- **Ollama:** execução local padrão do modelo de IA;
- **OpenRouter + GPT-6.1 Terra:** opção explícita para o relatório Anvisa V8,
  usando apenas Markdown autorizado e a chave protegida no servidor;
- **NVIDIA NIM API Trial:** provedor externo limitado a avaliações com conteúdo
  sintético, usando credencial protegida no n8n;
- **Python no gateway:** contexto determinístico do RF-22 e validação de
  candidatos no workflow híbrido v2, conforme RF-23;
- **NVIDIA NIM de produção:** integração planejada, ainda não implementada,
  condicionada a endpoint/licença e termos que permitam os dados autorizados;
- **PostgreSQL:** fonte de verdade operacional, metadados, estados, erros e vínculos;
- **Volume privado do Docker:** armazenamento interno dos PDFs, Markdown e relatórios;
- **Google Drive:** histórico da homologação anterior; não participa dos workflows ativos;
- **Docker:** empacotamento e implantação dos serviços;
- **VPS Linux:** hospedagem do ambiente.
- **Landing/API de upload:** entrada privada, protocolo, status e download controlado do relatório.

Infraestrutura de referência apresentada na proposta:

- 2 vCPU;
- 8 GB de RAM;
- 100 GB NVMe;
- Linux;
- modelo de IA leve e quantizado compatível com os recursos disponíveis.

---

## 6. Fluxo principal do produto

```text
PDF recebido pelo gateway de upload
        ↓
Persistência no volume privado e registro no PostgreSQL
        ↓
Conversão para Markdown com marcadores de página
        ↓
Análise de todas as páginas em lotes
        ↓
Achados JSON temporários consolidados
        ↓
Relatório Markdown e validação de páginas/evidências
        ↓
Geração e armazenamento do PDF
        ↓
Documento concluído, com download do PDF e conferência opcional no painel
```

O JSON usado em cada lote é temporário: ele ajuda a consolidar os achados, mas
não é salvo nem exibido como análise final. Os artefatos analíticos do caminho
atual são o relatório Markdown e sua versão PDF.

No modo Anvisa V8, os lotes e grupos validados também são salvos como controle
privado de retomada, conforme RF-04 e RF-21. Esse controle não é uma análise
JSON publicada no painel nem um artefato `analysis_json`.

Quando o documento for enviado pela landing, o gateway persiste atomicamente o
arquivo no volume privado, gera um protocolo e registra o documento no
PostgreSQL antes de encaminhar a execução ao webhook interno do n8n. A landing
é a única origem oficial de novos documentos. Os exports antigos com Google
Drive permanecem somente para auditoria e rollback.

O volume `automacao_miller_artifacts_data` é montado em `/data/artifacts` no
gateway e no n8n. Os arquivos usam chaves relativas organizadas por SHA-256 em
`objects/ab/cd/<sha256>/`, enquanto o PostgreSQL registra metadados, estados,
tentativas, erros e vínculos de artefatos nas tabelas `documents`, `artifacts`,
`processing_attempts` e `workflow_errors`. Estruturas de análise JSON mantidas
para compatibilidade com registros ou workflows antigos não são produzidas no
caminho atual.

---

## 7. Requisitos funcionais

### RF-01 — Recebimento de entrada

O sistema deve receber PDFs exclusivamente pelo gateway privado da landing,
validar o conteúdo, persistir o arquivo no volume interno e registrar um
documento elegível no PostgreSQL. O Google Drive não é uma entrada ativa.

O modo local de conversão do RF-20 é uma ferramenta separada para testes
manuais; não é uma entrada operacional de documentos e não cria protocolo.

### RF-02 — Leitura de PDF

O sistema deve ler os PDFs suportados para produzir o artefato Markdown intermediário. Falhas de leitura devem ser classificadas como erro técnico.

### RF-03 — Conversão obrigatória para Markdown

Todo PDF elegível deve ser convertido para uma representação Markdown organizada antes de qualquer extração estruturada ou chamada ao provedor de IA selecionado. O Markdown deve conter metadados do documento, SHA-256, contagem de páginas, versão do conversor e um marcador `## Página N` para cada página. Falha de conversão, PDF corrompido ou ausência de camada textual deve interromper a análise e gerar erro técnico explícito. Possíveis tabelas devem ser preservadas quando detectáveis, com aviso de layout quando a geometria não puder ser reconstruída com segurança; OCR não faz parte desta etapa.

Nos layouts suportados, a sequência deve acompanhar a leitura visual: cada
coluna antes da seguinte, respeitando cabeçalhos, regiões de largura inteira,
tabelas e continuações entre páginas. A ordem interna dos objetos do PDF não
é, por si só, evidência dessa sequência. A reorganização não deve inventar ou
apagar conteúdo. Limitação detectada de ordem espacial deve produzir aviso
identificado como nota da ferramenta, inclusive no Markdown da página; não
pode ser apresentada como ausência de informação. Mudança de conversor gera
novo artefato/hash e exige nova validação, preservando a fonte anterior para auditoria.

### RF-04 — Análise por IA

A análise local usa Ollama. A configuração `ANVISA_REPORT_PROVIDER=openrouter`
seleciona o Anvisa V8, com GPT-6 Luna (`openai/gpt-6-luna`) fixado no Compose.
Ambos usam o [V8 autossuficiente](prompts/chatgpt-anvisa-pdf-v8-autossuficiente.txt)
inalterado. O Markdown paginado persistido é a única fonte documental em ambos
os caminhos. No modo OpenRouter não são enviados o PDF bruto, o protocolo, o
nome do arquivo ou credenciais no conteúdo da solicitação. A integração usa
blocos de páginas, permite recuperar contexto e valida cobertura, evidências
literais e reconciliação dos registros. Saída incompleta ou inválida bloqueia
o relatório V8. A aplicação produz PDF com índice inicial clicável, resumo,
fichas e pendências, bem como Markdown de consulta e ZIP interno da mesma
revisão contendo PDF, JSONL, cobertura e verificação. A aprovação humana de um
PDF anterior não homologa novas respostas do modelo ou da API.

Incluídos e pendentes usam a ficha completa com `justificativa_destino`.
Excluídos e representações duplicadas podem usar o registro compacto do V8,
com `justificativa`; para compatibilidade, nesses compactos também é aceita
`justificativa_destino`. Toda justificativa fornecida deve ser texto não vazio.
Se ambas as chaves existirem, preservar seus valores sem escolher, copiar ou
sobrescrever uma delas. Essa compatibilidade não dispensa páginas válidas,
evidências literais e reconciliação do inventário.

Se uma evidência V8 falhar, registrar em armazenamento privado o bloco enviado,
a resposta rejeitada, o ID do registro, o caminho do campo, a página, o trecho
e o motivo específico, vinculados ao hash da fonte, protocolo, tentativa e
execução. A chamada de correção deve receber esse diagnóstico e a resposta
anterior, mantendo o limite de uma correção por grupo de resposta. Diferenças apenas de
espaços ou quebras continuam rejeitadas pela conferência literal. O histórico
exibe somente página, motivo e referência de diagnóstico; os detalhes
documentais ficam disponíveis ao operador do ambiente, sem endpoint público.
Os identificadores internos não são enviados ao provedor. Falha ao preservar
o diagnóstico interrompe a análise como erro de armazenamento.

Falhas de estrutura também devem identificar o campo (JSON Pointer), o ID do
registro quando aplicável, o valor recebido e a condição esperada no diagnóstico
privado enviado à correção. O resumo público não deve expor esses valores. Ao
registrar falhas, o workflow de erros deve preservar mensagem e descrição do
n8n, sem repetir textos idênticos. Referências de diagnóstico V8 identificam
erros de validação; o nome do último nó não deve substituir a causa conhecida.

Blocos densos devem ser reduzidos por páginas-alvo sem cortar o texto das
páginas ou unidades documentais. Uma resposta parcial deve continuar em grupos
de eventos completos, preservando os IDs, valores e evidências dos registros
já validados. O inventário e a cobertura são acumulados; páginas e unidades
pendentes não são promovidas a concluídas apenas para satisfazer o validador.
Iniciar cada lote com até oito eventos entre novos e revisões. Após respostas
compactas aceitas com progresso, permitir grupos de 12 e depois 16, até esse
máximo conferido no servidor. Respostas com incluídos/pendentes e revisões de
fichas completas permanecem em até oito eventos, podendo usar menos quando
extensas. O limite é de transporte, sem resumir ou dividir fichas/eventos.
Fichas com revisão ainda aberta devem ser guardadas separadamente dos eventos completos, após validar sua estrutura,
páginas e evidências literais. Priorizar a revisão dessas fichas antes de
extrair novas unidades. Preservar seus IDs e evidências; dados acrescentados
ou corrigidos pela releitura ficam auditáveis pelas versões anteriores no
checkpoint privado. Eventos já concluídos permanecem imutáveis.

Desde a primeira continuação, enviar as fichas concluídas somente por um
índice de todos esses eventos, com IDs, categorias, destinos, páginas, hashes
e referências curtas confirmadas. As fichas completas permanecem intactas no
checkpoint e são reunidas pelo aplicativo no resultado final. Campo ausente
do índice não representa ausência na fonte ou na ficha; o índice não é
evidência nem substitui a conferência documental. Continuar rejeitando
alteração de ficha concluída, duplicação e perda de IDs do inventário.

O transporte admite inventário incremental: a IA devolve somente campos,
blocos e unidades novos ou alterados, vinculados ao hash da base integral.
IDs locais de transporte de blocos/unidades são estáveis e distintos dos
identificadores documentais. Campos omitidos preservam seus valores; não
excluir unidades, IDs reservados ou evidências anteriores. Rejeitar bases
divergentes, IDs desconhecidos, duplicados e substituição integral disfarçada.
O inventário continua derivado da leitura da fonte, não das fichas. O servidor
consolida o inventário completo antes de validar cobertura e reconciliação.
A representação integral anterior permanece aceita, com as mesmas validações,
para compatibilidade; não aceitar as duas representações na mesma resposta.

No delta do inventário, aceitar `adicionar_evidencias` no bloco ou unidade.
O servidor conserva as evidências anteriores integralmente e em sua ordem,
acrescentando somente objetos novos, sem duplicar objetos idênticos. Para
compatibilidade, `campos.evidencias` nesse delta tem a mesma semântica aditiva;
lista vazia não exclui evidências. Não combinar as duas formas no mesmo objeto.
Quando somente acrescentar evidências, `campos` pode ser omitido. Rejeitar
listas ou objetos malformados e manter a conferência literal, de páginas e
escopo após expandir e consolidar. Essa união não se aplica a outros arrays,
IDs ou fichas completas; os demais controles de imutabilidade, revisão e
reconciliação permanecem. Não completar informações por suposição.

No delta do inventário, ao refinar explicitamente `limites` de um bloco ou unidade,
enviar o objeto completo, conservando as chaves e a estrutura das referências existentes.
O servidor mantém os limites novos recebidos e guarda na lista `evidencias`
do mesmo bloco/unidade os objetos exatos das evidências anteriores deslocadas
dos limites, preservando ordem e atributos e sem duplicar objetos idênticos
já presentes. Não inferir limites nem substituir valores por normalização.
Limite existente apagado ou malformado continua inválido.
As citações antigas e novas passam pelas mesmas validações de literalidade,
páginas e escopo; conservar ambas não comprova revisão nem resolve divergências
automaticamente. Evidências removidas de outros campos continuam rejeitadas,
com campo anterior e objeto exato ausente no diagnóstico privado enviado à
única correção. Conferir também o orçamento do inventário consolidado, sem
descartar evidências para caber no limite.

Evidências idênticas podem ser transmitidas uma vez e reutilizadas por
referências locais à chamada. Não resumir, normalizar ou truncar os trechos.
Rejeitar referências desconhecidas, redefinições e encadeamentos; verificar
literalmente as evidências novas e limitar a amplificação antes de expandir.
Expandir os objetos antes de aplicar os validadores V8 existentes. Fichas em
revisão, inventário, diagnóstico e resposta rejeitada continuam disponíveis
integralmente por essa representação reversível, assim como as páginas
obrigatórias. Preservar no diagnóstico a resposta de transporte original e
seu dicionário para auditoria; referências rejeitadas não podem adquirir outro
significado na chamada de correção. Usar grupos adaptativos conservadores. Permitir até
dois lotes operacionais independentes por análise em chamadas concorrentes;
a continuação e a correção dentro de um mesmo lote permanecem sequenciais.
O limite concorrente é de duas chamadas ao provedor em voo, não de dois lotes
com trabalho iniciado. Um lote em espera de retentativa ou com chamada
bloqueada por contexto sobreposto conserva seu gerador, progresso, pacote e
orçamentos. Uma vaga livre pode atender outro lote independente dos lotes já
iniciados; nenhuma chamada em voo é interrompida ou deixa de contar no limite.
Priorizar a retomada de lotes iniciados quando estiverem elegíveis. Esperas
de retentativa consideram o tempo já transcorrido durante o trabalho dos
demais lotes, sem renovar tentativas. Não iniciar nova chamada após falha
persistente e manter as regras de drenagem e armazenamento abaixo.
Na saída, a IA pode compartilhar valores integrais e exatamente idênticos de
campos das fichas em `campos_compartilhados`, usando referências locais
`$campo` explícitas em cada campo. Aplicável a ato, dispositivo, decisão,
objeto, composição, entidades, processos, petições, apresentações, ressalvas,
relações e campos adicionais. IDs, destino, categoria, páginas da ficha,
justificativa e conferência de integridade permanecem individuais. A
referência substitui o valor completo, sem herança, união ou sobrescrita;
diferenças e evidências são preservadas. O dicionário vale somente para a
resposta atual e não admite encadeamento, referência desconhecida ou mistura
de referência e atributos. Conferir a amplificação antes de copiar e
reconstruir cada ficha integralmente antes de validar, revisar, persistir ou
gerar os artefatos. Valores inline continuam aceitos. O diagnóstico conserva
a resposta de transporte original; a correção recebe valores resolvidos e
referências inválidas identificadas sem permitir sua vinculação a outro valor.

Aumentar apenas após grupo aceito com avanço, preenchido com registros
compactos curtos, apoiado em métricas reais de saída e duração. Entrega de contexto,
respostas rejeitadas, sem avanço ou sem métricas não justificam crescimento.
Respostas extensas, lentas ou completas reduzem/conservam o próximo grupo;
após redução ou correção, aguardar dois sucessos antes de crescer novamente.
Guardar a política por lote no checkpoint e revalidá-la antes de retomada.
Uma divisão em alvos menores conserva a política aprendida. Não inventar
medidas ao migrar versões anteriores: elas recomeçam em oito.

Retentativa de transporte repete exatamente o pacote e não muda o tamanho.
Uma correção mantém o limite do grupo rejeitado e seu orçamento único. Saída
truncada pode reduzir o próximo pedido pelos tamanhos 16/12/8/4/2/1, sem
usar dados incompletos, dispensar conferência ou renovar outros orçamentos.
Na correção, truncamento continua erro explícito para preservar o grupo.
Não contornar um limite de contexto cortando páginas ou dados obrigatórios.
Unidades restantes permanecem no inventário pendente. O documento só encerra
com todas as páginas e reconciliações concluídas.

Um único coordenador deve validar e persistir as mudanças dos lotes, mantendo
o bloqueio exclusivo do checkpoint para toda a análise. Somente o I/O do
provedor pode ocorrer em threads. Um lote não altera o estado de outro; cada
evento pertence ao recorte onde começa sua unidade e páginas compartilhadas
servem apenas como contexto. Conferir conflitos globais antes de aceitar
registros e manter leitura de páginas inteiras, buscas e revisão inversa.
Janelas, evidências, páginas de unidades conhecidas e pedidos de contexto
sobrepostos exigem chamadas sequenciais. Uma ampliação pode suspender o
paralelismo do lote até a chamada sobreposta terminar; não presume revisão
ou independência semântica apenas pela separação das páginas.

Lotes podem terminar fora da ordem de leitura. Preservar sua partição completa,
sem lacunas nem sobreposição de alvos, e gravar/restaurar listas ordenadas por
página. Uma retomada revalida também esses resultados e não refaz lotes já
fechados. O resultado final deve estar em ordem documental e só pode ser
montado quando todos os lotes e reconciliações terminarem. Nenhum lote pode
sobrescrever o progresso salvo por outro.

Após falha persistente, não despachar novas chamadas. Aguardar as já em voo,
validar e guardar as respostas aproveitáveis antes de retornar o erro. Se o
armazenamento ficar incerto, impedir novas promoções. Retentativas, correções,
buscas, ampliações e falta de progresso continuam com seus orçamentos por
lote, sem renovação por outra resposta terminar. Conferir o prazo opcional
novamente no despacho de chamadas que aguardaram dependências; o padrão
continua sem prazo global. Amostras internas podem ter orçamento explícito
por lote, em cópias privadas; esse orçamento não é recebido pela rota
operacional, não gera relatório parcial e não altera limites da aplicação.

Recuperar contexto adicional em janelas de páginas inteiras, com pacote de
dados de até 480.000 bytes UTF-8, incluindo continuidade, diagnóstico e resposta
anterior na correção. Manter as páginas-alvo e as evidências das fichas e do
histórico; na correção, incluir também as páginas reais citadas pelo grupo
rejeitado. Conferir o orçamento antes de persistir uma ampliação. Guardar
separadamente páginas solicitadas, entregues e ainda pendentes; solicitar o
documento integral não deve obrigar seu envio numa única chamada. A entrega
de uma janela não comprova sua revisão nem permite eliminar o restante da fila.
Uma resposta rejeitada deve manter sua janela disponível na próxima retomada;
um limite de saída não deve descartar pedidos de contexto já aceitos.

Separar entrega histórica da presença na chamada atual. Uma página já
entregue e ausente da janela pode ser explicitamente reenfileirada para
releitura, sem apagar o histórico. Guardar fila e contador no checkpoint,
com até três pedidos ordinários que acrescentem releituras desde o último
avanço documental validado. Um quarto pedido admite uma única rodada extra
quando inclui páginas já entregues, ausentes da janela e ainda não solicitadas
para releitura no ciclo. Enfileirar somente essas páginas adicionais e manter
a fila anterior. A cada nova janela, conservar as páginas já relidas no ciclo
enquanto couberem.
Priorizar o núcleo obrigatório e a fila de entregas pendentes antes dessas
releituras e reservar as páginas vizinhas opcionais para o espaço restante.
A retenção termina com avanço documental validado e não renova o contador.
Durante a rodada extra, atender a fila aceita em janelas
inteiras e bloquear novos pedidos de contexto até haver avanço validado.
Após entregar a fila, exigir avanço ou conclusão validada do lote. Entregar
páginas, trocar a janela técnica, retentar transporte ou retomar manualmente
não renova esse contador nem os demais orçamentos. Avanço validado libera o
orçamento próprio de releitura,
conservando páginas ainda pendentes. Releituras não consomem o limite de
ampliações para páginas novas nem autorizam encerrar revisão automaticamente.

Pesquisar identificadores literalmente no Markdown integral e informar método,
quantidade de páginas examinadas e páginas com ocorrências. Priorizar essas
páginas e suas vizinhas, inclusive para identificadores confirmados nas fichas
em revisão. Zero ocorrências de uma substring exata não comprova ausência
documental ou semântica. Preservar os pedidos pendentes após falha e retomada,
sem declarar buscas ou conferências não realizadas. Se nem uma página inteira
com a continuidade obrigatória couber, interromper com progresso preservado.

Busca conhecida reutiliza o resultado local salvo, sem nova varredura da
fonte. Quando solicitada, reenfileirar suas páginas encontradas e vizinhas
ausentes da chamada; não repetir as já atendidas no mesmo ciclo de releitura
ao avançar pelas janelas de uma fila. Pedido explícito de página ausente
permanece sujeito ao orçamento próprio de releitura. Listas vazias nos campos
opcionais de pedido não são solicitações: validar as fichas recebidas na
mesma resposta, exigindo os campos obrigatórios e mantendo a correção única.

Buscas literais locais não consomem o limite de ampliações explícitas de
páginas. Permitir até três pedidos que acrescentem páginas por
`contexto_necessario` desde o último avanço validado do grupo. Novos registros,
fichas concluídas ou avanço de cobertura/inventário reabrem esse orçamento;
repetir achados, entregar contexto ou executar buscas não comprovam esse avanço.
Conferir o tamanho e salvar o novo pedido antes de interromper por esse limite,
preservando as páginas ainda pendentes na retomada. Buscas locais continuam
limitadas a 16 termos por pedido e 256 termos por lote, com janelas técnicas
de chamadas e timeout individual. Repetição sem nova busca, releitura admitida
ou página pendente deve interromper. Páginas presentes na chamada não devem
ser reenviadas apenas porque foram pedidas novamente.

Antes de rejeitar um pedido de contexto, guardar em diagnóstico privado a
resposta de transporte, o pedido, a janela efetivamente enviada, os estados
anterior/proposto do contexto, motivo específico e vínculo à tentativa e à
execução. Erros desse contrato são de validação de contexto, com referência
ANV8D no histórico; o detalhe documental não é público. Falha de preservação
é erro de armazenamento. O diagnóstico não adiciona chamadas ou gravações
em respostas normais aceitas nem amplia o orçamento de correção.

Pendências explícitas mantêm uma ficha ou inventário em aberto mesmo se o
estado declarado pelo modelo disser `revisada`; preservar essa declaração
sem interpretá-la como sucesso nem apagar a pendência automaticamente. A
validação final continua exigindo revisão concluída e ausência de pendências
técnicas. Uma busca literal bem-sucedida não substitui a conferência inversa.
Cada grupo admite uma correção estrutural/literal, informando conjuntamente
as falhas conhecidas dos registros daquele grupo. As chamadas são organizadas
em janelas técnicas de até 32 solicitações por lote. Ao completar uma janela,
recarregar e revalidar o checkpoint salvo e continuar automaticamente o mesmo
lote, na mesma tentativa do documento, sem intervenção no painel. Manter o
bloqueio de concorrência e os estados de correção, ausência de progresso,
buscas e ampliações; a troca de janela não renova esses orçamentos nem promove
páginas ou inventários a concluídos. Os diagnósticos mantêm a contagem total
de chamadas do lote, inclusive quando houver várias janelas.

Falhas de conexão, timeout individual e HTTP 408, 429, 500, 502, 503 ou 504
admitem até três tentativas da mesma chamada: a inicial e duas novas, com
esperas de 5 e 15 segundos. Revalidar o checkpoint antes de repetir e manter
o mesmo pacote, incluindo diagnóstico e resposta anterior se for correção.
Uma retentativa de transporte não concede nova correção estrutural/literal
nem deve refazer lotes concluídos. Falha persistente após três tentativas
termina em erro explícito com progresso preservado. Erros de crédito ou
autorização, saída inválida, armazenamento e validação não entram nesse retry.

Permanecem limites de contexto, buscas, ampliações e timeout por chamada;
duas respostas consecutivas sem progresso interrompem a continuação
preservando o checkpoint. O PDF final V8 só pode
ser gerado após todas as páginas e inventários estarem efetivamente fechados
e as verificações mecânicas passarem.

Os checkpoints privados devem guardar lotes concluídos e registros já
validados de lotes pendentes. Sua identidade inclui protocolo, hash do Markdown,
modelo, prompt, instruções e implementação da análise. A retomada revalida o
conteúdo contra a mesma fonte antes de reutilizá-lo. Escritas devem ser
atômicas e sincronizadas; análises simultâneas da mesma identidade são
bloqueadas. Corrupção ou ausência de um estado previamente registrado
interrompe a análise com erro de armazenamento antes de nova chamada de IA.
Mudança de identidade usa um estado separado e preserva o anterior.
Uma migração entre implementações conhecidas exige ação explícita do operador,
backup, análise parada, mesma fonte/protocolo/modelo/V8, bloqueio das duas
identidades e revalidação integral do estado. Registrar a origem na nova
identidade, manter o original e não sobrescrever outro progresso no destino.
Não há migração automática nem seleção de checkpoint pela interface pública.

O endpoint gratuito de trial da NVIDIA
pode ser chamado somente pelo workflow manual de avaliação, separado e inativo,
com fixture sintético sem dados reais. Esse workflow exige credencial protegida
no n8n e valida estrutura, página e evidência do fixture; não processa uploads
nem substitui a análise no fluxo real. Não há fallback automático entre
provedores. A habilitação do OpenRouter exige autorização para o material
enviado e revisão dos termos e da privacidade antes do uso operacional.

### RF-05 — Identificação regulatória

A análise deve ser capaz de identificar, quando presentes no documento:

- status regulatório;
- medicamentos;
- suplementos alimentares;
- ensaios clínicos;
- exigências;
- pendências.

Para o relatório regulatório, deve organizar, quando presentes:

- medicamentos deferidos/registrados;
- medicamentos indeferidos;
- suplementos deferidos/aprovados;
- suplementos indeferidos;
- estudos clínicos deferidos;
- estudos clínicos indeferidos;
- outros atos regulatórios, incluindo cancelamentos.

### RF-06 — Consolidação temporária dos achados

O workflow pode usar JSON temporário por lote para consolidar achados, páginas
e evidências. Esse JSON não é um artefato final: a saída persistida do MVP é o
relatório Markdown e seu PDF. A prioridade executiva do relatório representa a
prioridade das ações, não uma medida de confiança ou certeza semântica da IA.

No modo V8, o ZIP de verificação contém os controles da revisão. Respostas
rejeitadas também são preservadas separadamente como diagnóstico privado
previsto em RF-04, assim como os checkpoints dos lotes e grupos validados;
não são relatórios finais nem registros de `analysis_results`.

### RF-07 — Cobertura documental e qualidade das evidências

O sistema deve exibir no relatório um sinal objetivo que informe quantas páginas
foram analisadas e quantas referências a páginas e evidências literais foram
confirmadas no Markdown original. Esse sinal mede cobertura e localização de
evidências; não representa confiança semântica ou nota de certeza da IA.

Referências não localizadas, com página inexistente ou citação diferente da
fonte devem ser marcadas como pendentes e claramente distinguidas das
comprovadas. Pendências de citação não bloqueiam a geração do PDF nem a conclusão do processamento. Cobertura incompleta por
falha técnica de lote, leitura ou página deve interromper a geração do relatório.

A validação é oferecida pela rota interna autenticada
`POST /internal/submissions/{id}/validate-report`. O gateway carrega o Markdown original
do armazenamento, confere as páginas analisadas e cada par página/evidência,
e devolve as referências confirmadas e pendentes. A origem não pode ser enviada
pelo cliente como substituta do artefato guardado.

Essa validação comprova apenas cobertura e localização literal de páginas e trechos. Ela não verifica se a interpretação da IA está semanticamente correta. Pela regra atual, referências pendentes não bloqueiam por si só a conclusão do processamento; esse comportamento não deve ser apresentado como garantia de qualidade.

### RF-08 — Conferência humana opcional

Ambiguidade, contradição, informação não comprovada ou referência pendente
devem ser sinalizadas no relatório, com as páginas disponíveis e suas
limitações. A equipe pode conferir esses pontos pelo painel, mas a revisão
humana não é obrigatória para concluir o processamento.

### RF-09 — Geração de relatório

O sistema deve gerar automaticamente um relatório padronizado com base nos dados processados.

### RF-10 — Geração de PDF

O relatório final deve ser convertido para PDF.

### RF-11 — Armazenamento

Os artefatos definidos pelo workflow, incluindo o Markdown intermediário e o
relatório associados ao PDF de origem, devem ser salvos no volume privado do
Docker. O PostgreSQL deve registrar o tipo, caminho interno, hash, tamanho e
vínculo de cada artefato.

### RF-12 — Conclusão e download do PDF

Quando o processamento obrigatório terminar e o PDF final estiver armazenado,
o workflow deve registrar o artefato e concluir o documento e a tentativa no
PostgreSQL. O detalhe do protocolo deve exibir o botão **Baixar relatório PDF**
automaticamente ao detectar a conclusão, quando o arquivo estiver disponível.
A conferência das referências continua opcional.

### RF-13 — Tratamento de erros

O workflow deve possuir tratamento básico de erros para evitar que falhas silenciosas sejam consideradas processamento concluído. Falha na conversão PDF → Markdown deve interromper a extração e encaminhar o documento para erro. Alertas de qualidade, citações pendentes ou ausência de evidência devem ser
registrados no relatório técnico e não podem ser confundidos com falha técnica.

### RF-14 — Rastreabilidade

Cada documento deve possuir estado de processamento identificável, permitindo distinguir minimamente:

- recebido;
- em processamento;
- concluído;
- com erro.

`aguardando_revisao` pode existir apenas como estado legado ou de compatibilidade;
o fluxo atual não depende dele para concluir o relatório.

### RF-15 — Painel operacional autenticado

O sistema deve oferecer login por sessão, painel de fila com busca, filtros,
indicadores, detalhes do protocolo, linha do tempo, tentativas, erros, conferência
opcional. O detalhe deve permitir visualizar o relatório PDF e baixar o arquivo
após a conclusão. Registros antigos podem manter um
artefato JSON por compatibilidade; o fluxo atual não o gera.

Enquanto o detalhe do protocolo estiver aberto, a interface deve atualizar
automaticamente o andamento, a etapa atual, as tentativas e os erros, incluindo
o conteúdo de `#history`, sem exigir atualização manual da página. Novas etapas,
falhas e a conclusão devem aparecer conforme forem registradas pelo fluxo,
inclusive após uma retomada. A exibição deve refletir o estado persistido,
sem antecipar sucesso nem perder o histórico das tentativas anteriores.
As consultas automáticas não devem apagar observações em edição
ou a aba de visualização selecionada. Falha na consulta deve ser identificada
como problema de atualização da tela, preservando o último estado recebido.

### RF-16 — Gateway de upload

O gateway deve validar o conteúdo do arquivo, calcular SHA-256, impedir
duplicidade acidental, persistir o upload em volume controlado e encaminhar o
protocolo ao n8n sem expor credenciais de integrações ao navegador.

### RF-17 — Download e visualização controlados

O download do relatório exige acesso autenticado, documento em `concluido` e
arquivo presente no volume privado. A visualização também exige acesso
validado. O servidor resolve o arquivo pelo protocolo e limita o acesso ao
volume de artefatos.

### RF-19 — Acesso por usuário e senha

A landing deve oferecer uma página de acesso com usuário e senha antes da tela
de upload. As credenciais devem ser configuradas somente no ambiente autorizado;
a senha deve ser armazenada como hash e a autenticação deve criar uma sessão
segura em cookie. O acesso legado por token privado pode permanecer disponível
para compatibilidade operacional, mas não deve expor o token na interface de
login.

### RF-20 — Gerar somente Markdown em testes locais

O operador pode iniciar uma interface de conversão independente em
`127.0.0.1:18080`, enviar um PDF textual de até 100 MiB e baixar o Markdown
completo em UTF-8. Esse modo reutiliza o conversor versionado, preserva os
marcadores de página e o corpo extraído, informa SHA-256 do PDF e do Markdown,
versões e avisos, e não executa OCR ou análise regulatória.

O exportador deve manter os avisos também no arquivo baixado, antes das
páginas e identificados como notas da ferramenta, não como texto do PDF.
Metadados devem ser escapados; conteúdo documental deve ser exibido como texto,
sem executar HTML ou instruções. Texto não extraível, falha parcial e problemas
visíveis na extração não podem ser apresentados como ausência de informação.

Esse modo não chama n8n, Ollama ou APIs externas, não usa PostgreSQL/credenciais,
não persiste documentos no volume operacional e não altera estados ou regras
de download do relatório final. Não possui autenticação e deve permanecer
restrito ao loopback, sem proxy, túnel ou exposição pública. Não deve registrar
corpo de documento em logs; arquivos temporários de upload devem ser fechados.

O download é uma fonte para teste manual, não um relatório final ou documento
processado com sucesso no fluxo principal. Compartilhar o arquivo em qualquer
serviço externo depende de autorização para aquele conteúdo e de conferência
dos avisos e da fonte. A aplicação não faz esse compartilhamento. A integração
futura com a API OpenAI e a escolha de modelo não fazem parte desta entrega.

Aceite específico: upload/conversão/download funcionando no navegador; hashes
e páginas verificáveis; avisos presentes no arquivo; erro de entrada não gera
download; nenhuma chamada de IA ou dependência da stack operacional.

---

### RF-21 — Retomar processamento pelo último artefato íntegro

Para documentos em `erro`, o botão **Reprocessar** deve solicitar uma nova
tentativa do mesmo protocolo, com registro do operador e preservação das
tentativas, erros e versões anteriores.

Ao clicar em **Reprocessar**, a interface deve abrir uma tela de confirmação
perguntando se o cliente deseja retomar o processamento a partir do último
ponto salvo, com as ações **Cancelar** e **Confirmar reprocessamento**.
Somente a confirmação explícita deve disparar a solicitação de retomada.
Cancelar ou fechar a confirmação não deve iniciar uma tentativa nem alterar
o estado do documento.

O servidor identifica o último ponto de recuperação verificável no armazenamento:

- Sem Markdown persistido: retomar pela conversão do PDF original íntegro.
- Com Markdown paginado íntegro: reutilizar sua versão, hash, páginas e avisos;
  continuar na análise, sem converter o PDF novamente.
- Com relatório Markdown validado e vinculado à fonte: continuar na geração ou
  persistência do PDF, sem nova análise. No V8, recuperar o PDF do ZIP íntegro
  da mesma revisão; não renderizar o V8 como relatório genérico.
- Com PDF íntegro e vinculado ao relatório: reutilizá-lo na finalização.

A escolha de etapa, arquivos e versões ocorre no servidor. Caminhos enviados
pelo navegador não podem selecionar outra fonte. Ausência, corrupção ou
divergência de um checkpoint registrado deve produzir erro explícito;
relatórios sem vínculo verificável não são reutilizados. Um relatório anterior
a uma nova conversão não substitui a análise dessa nova tentativa.

Solicitações simultâneas não podem iniciar duas tentativas. O documento só
passa a `concluido` depois da persistência dos artefatos obrigatórios.
A retomada abrange artefatos
persistidos; resultados parciais internos da IA que não foram salvos não são
checkpoints e precisam ser refeitos a partir do Markdown.

No V8, quando houver checkpoint privado compatível, a mesma retomada a partir
do Markdown reutiliza os lotes concluídos e continua as unidades pendentes.
O navegador continua sem escolher arquivos ou lotes. Falha posterior na
renderização pode reutilizar toda a análise já concluída. Execuções anteriores
à implantação desse controle, sem lotes guardados, não têm recuperação
retroativa de seu progresso em memória.

### RF-22 — Contexto determinístico rastreável

Depois de persistir o Markdown paginado, o gateway deve relê-lo do armazenamento
privado e procurar um conjunto versionado de termos regulatórios literais e
formatos conhecidos de identificador de processo. Cada ocorrência deve manter
página, termo/identificador e trecho extraído. Um identificador exatamente igual
encontrado em mais de uma página deve formar um vínculo entre essas ocorrências.

Essa leitura é determinística: não classifica o resultado do ato, não decide
que duas ocorrências são o mesmo evento e não substitui a análise do documento.
Além de identificadores e termos regulatórios, o conjunto versionado pode
localizar datas e durações em formatos conhecidos, sempre mantendo a linha
original como evidência. O relatório deve apresentar as observações e os
vínculos entre páginas como pistas para conferência, preservar cada página e
explicitar que a repetição de um identificador não prova igualdade de status.
A varredura usa somente o Markdown persistido; ausência de um termo da lista
de regras não prova que o documento não contenha um achado relevante.

### RF-23 — Auditoria de lacunas e validação em Python

No workflow híbrido v2, a IA deve revisar todas as páginas em lotes para propor
fatos que não estejam
representados nas observações determinísticas. Cada candidato precisa trazer
fato, categoria, página e trecho literal. O gateway deve aceitar o candidato
para a síntese somente se a página existir, pertencer ao lote de origem e
contiver o trecho citado. Candidato sem evidência válida fica pendente e não
entra no prompt do relatório final. Essa validação mecânica não confirma a
correção semântica do fato nem substitui a conferência profissional.

---

## 8. Regras de negócio

### RN-01 — IA é apoio, não decisão final

Nenhuma resposta do modelo deve ser apresentada como parecer jurídico, médico ou regulatório definitivo.

### RN-02 — Não inventar informação ausente

Se o documento não fornecer evidência suficiente para determinada conclusão, o
sistema deve registrar a ausência de evidência, explicitar a limitação e
apresentar as páginas disponíveis para conferência opcional.

### RN-03 — Ambiguidade deve ser explicitada

Quando houver ambiguidade ou conteúdo contraditório, o fluxo deve preservar
as versões conflitantes e suas referências. O sinal de cobertura e evidência
não mede a certeza semântica da IA. A conferência humana pode ocorrer depois,
mas não é um gate obrigatório.

### RN-04 — Fonte primária é o documento processado

As conclusões produzidas devem estar vinculadas ao conteúdo extraído do PDF recebido.

### RN-05 — Falha de processamento não equivale a ausência de dado

Problemas de leitura, parsing, conversão ou IA devem ser classificados como erro técnico, e não como “informação não encontrada”.

### RN-06 — Processamento concluído exige artefato final

Um processamento só pode ser marcado como concluído quando as etapas obrigatórias do fluxo tiverem sido executadas com sucesso e o relatório final tiver sido gerado, armazenado e vinculado ao protocolo.

### RN-07 — Idempotência

O mesmo arquivo não deve gerar processamentos duplicados de forma não
intencional. O gateway deve deduplicar pelo SHA-256 e o workflow deve usar a
reivindicação transacional do PostgreSQL para impedir execuções concorrentes.

Ao reenviar um PDF já cadastrado, a API deve identificar explicitamente que
retornou o protocolo existente. A tela de upload deve informar que nenhum
processamento novo foi iniciado e oferecer acesso ao detalhe desse protocolo.
Seu status e mensagem anteriores são preservados e identificados como dados
do protocolo existente; não apresentar o cancelamento antigo como falha do
novo envio. Reenvio não autoriza retomada nem reinício; **Reprocessar** segue
a confirmação e a recuperação definidas no RF-21.

### RN-08 — Registro de falhas

Erros relevantes devem possuir registro suficiente para diagnóstico, incluindo etapa, documento, horário e mensagem de erro quando disponível.

### RN-09 — Credenciais fora do código

Credenciais do Google, n8n, servidor ou qualquer outro serviço não podem ser mantidas em código-fonte versionado.

### RN-10 — Modelo substituível

O desenho deve permitir troca futura do modelo Ollama sem necessidade de reconstrução completa do workflow.

### RN-11 — Markdown como fonte intermediária oficial

Depois da conversão, o Markdown persistido é a única fonte documental permitida para a extração estruturada e para a análise por IA. O PDF bruto permanece como fonte primária de auditoria, mas não deve ser enviado diretamente ao Ollama.

### RN-12 — Status regulatório preservado

O sistema deve diferenciar, no mínimo, `deferido`, `indeferido`, `cancelado` e `outro`. Um ato cancelado não pode ser incluído automaticamente como indeferido.

### RN-13 — Acesso privado da landing

As rotas de upload, consulta e download devem exigir o token do link privado.
Rotas internas de arquivo e atualização de status devem exigir token separado
e permanecer disponíveis somente na rede interna do Docker/VPS.

### RN-14 — Download condicionado

O relatório só pode ser liberado pela landing quando o processamento estiver
`concluido` e o arquivo estiver dentro do volume de artefatos permitido.

### RN-15 — Sessão de acesso

A sessão da landing deve usar cookie `HttpOnly`, `SameSite=Lax`, prazo de
expiração configurável e assinatura baseada em segredo do ambiente. O logout
deve invalidar o cookie local. Usuário, hash da senha, segredo de sessão e
tokens não podem ser versionados.

### RN-16 — Conteúdo documental não confiável

Texto extraído do documento e achados dele derivados são dados de origem, não
instruções para o modelo. Prompts devem instruir explicitamente o modelo a não
obedecer a comandos embutidos no documento, não acessar ferramentas e não
alterar as regras da análise. A rota externa não deve transmitir identificadores
internos do protocolo que não sejam necessários ao provedor. O resultado segue
sujeito à validação de estrutura, cobertura e evidências do workflow.

### RN-17 — Menções determinísticas não são decisões

Termos e identificadores localizados por regras devem ser exibidos com o trecho
e a página de origem. A regra só confirma a ocorrência literal. Não pode inferir
deferimento, indeferimento, cancelamento, identidade de atos ou consequência
regulatória a partir de uma palavra ou de um identificador repetido.

### RN-18 — Candidatos da IA no fluxo híbrido precisam de citação verificável

Nenhum candidato proposto pela IA pode entrar na síntese final sem passar pela
validação Python da página e do trecho literal contra o Markdown persistido.
Essa checagem atesta apenas a localização da citação, não a verdade ou a
interpretação do candidato. Itens rejeitados permanecem identificados como
pendentes e não podem ser reaproveitados na redação final.

---

## 9. Requisitos não funcionais

### RNF-01 — Implantação

O ambiente deve ser executável em servidor Linux utilizando Docker.

### RNF-02 — Privacidade operacional

A análise local ocorre por Ollama. No modo OpenRouter autorizado, o Markdown
paginado é a única fonte documental enviada ao modelo Anvisa V8. A
chave não passa pelo navegador nem pelo n8n; fica no ambiente do serviço que
chama a API. A avaliação com a
API Trial gratuita da NVIDIA usa apenas um texto artificial fixo, sem documento
real, identificador interno ou dado pessoal. O workflow de avaliação é manual,
separado e inativo por padrão; sua credencial fica somente no armazenamento
protegido do n8n. O endpoint de trial não pode ser usado para processar o PDF
governamental recebido.

A futura integração NVIDIA de produção depende das condições de licença,
privacidade e autorização registradas no LOG.md em 26/10/2026; o Trial
continua exclusivo para fixture sintético. Essa integração não é habilitada
pela seleção de provedor do Anvisa V8.

### RNF-03 — Manutenibilidade

Workflows, prompts, configurações e documentação devem ser organizados de forma que possam ser atualizados sem perda de rastreabilidade.

### RNF-04 — Observabilidade mínima

Falhas de integração, extração, análise e armazenamento precisam ser identificáveis.

### RNF-05 — Recuperação

Uma falha intermediária não deve obrigar o reprocessamento manual de todo o fluxo quando for tecnicamente possível retomar a partir da etapa adequada.

O RF-21 define a retomada autenticada pelo painel, com validação de integridade,
reserva exclusiva da tentativa e auditoria. O ajuste de um limite externo não
reinicia automaticamente uma execução encerrada com erro.

### RNF-06 — Segurança

Tokens, senhas, chaves e credenciais devem ser armazenados por mecanismos adequados do ambiente e nunca em arquivos públicos do repositório.

### RNF-07 — Serviço local de conversão

A conversão PDF → Markdown deve ser executada por serviço local versionado, testável e implantável via Docker, com health check, timeout e contrato HTTP interno. O serviço deve validar a estrutura do PDF com `pdfplumber`, manter leitura textual eficiente para documentos extensos e retornar avisos de layout sem ocultar falhas.

### RNF-08 — Meta de desempenho sem interrupção por duração total

O prazo de 90 minutos é uma meta operacional de desempenho, não um limite de
execução ou regra para encerrar a análise. Ultrapassar essa duração não deve
interromper um documento que continua avançando. No caminho V8, o prazo global
fica desabilitado por padrão no renderizador e na espera HTTP do n8n.
Permanecem timeout por chamada ao provedor, contexto/buscas, detecção de
ausência de progresso, integridade e persistência dos checkpoints. Completar
32 chamadas no lote aciona continuação automática; timeout ou falha temporária
aciona as tentativas controladas do RF-04. Erros persistentes e violações das
demais proteções continuam exigindo erro explícito com progresso preservado.

---

## 10. Modelo mínimo do relatório regulatório

O relatório V8 usa o título e a ordem definidos no prompt aprovado: índice
de assunto/página de origem, resumo, fichas por categoria e pendências. As
seções abaixo continuam válidas para o relatório executivo do Ollama:

1. resumo executivo;
2. respostas às perguntas de negócio;
3. escopo e identificação do documento;
4. achados regulatórios;
5. impacto de mercado e comercial;
6. plano de ação recomendado;
7. riscos, contradições e pontos de atenção;
8. limitações e informações não comprovadas;
9. referências de páginas.

Para facilitar a leitura por equipes operacionais e comerciais, o relatório
também deve começar com um resumo executivo em linguagem clara, apresentar os
achados traduzidos em implicações práticas de acompanhamento e indicar próximos
passos. A redação pode explicar possíveis impactos em cadastro, registros,
processos, prazos e comunicação interna, mas não deve criar impacto financeiro,
jurídico ou regulatório que não esteja evidenciado no documento. O resumo deve
preservar o sinal de cobertura/evidência, os alertas e as limitações encontradas.
Cada achado exibido deve informar as páginas de origem. Quando a página não
puder ser comprovada, o relatório deve indicar explicitamente que a referência
está pendente, sem preencher a página por inferência, e permitir conferência
opcional pela equipe.

Para estudos clínicos, o produto relacionado deve ser classificado como medicamento, suplemento, dispositivo, outro ou não identificado. O sistema não pode converter um dispositivo em medicamento ou suplemento por inferência.

Quando uma categoria não possuir registros, o relatório deve informar que nenhum registro foi localizado no recorte analisado. Isso não pode ser usado para ocultar uma falha técnica de conversão, extração ou análise.

---

## 11. Escopo incluído

O projeto contempla:

- preparação do servidor;
- instalação do Docker;
- instalação e configuração do n8n;
- instalação e configuração do Ollama;
- modelo inicial;
- repositório interno em volume privado do Docker;
- persistência operacional em PostgreSQL;
- desenvolvimento do workflow;
- desenvolvimento dos prompts;
- serviço local de conversão PDF → Markdown;
- consolidação temporária dos achados de cada lote;
- processamento de PDFs;
- conversão para Markdown;
- persistência do Markdown e das evidências;
- leitura determinística de termos e identificadores com rastreabilidade por página;
- análise por IA;
- geração de relatórios;
- conversão para PDF;
- armazenamento automático;
- download do PDF pelo painel, com conferência opcional;
- tratamento básico de erros;
- recurso opcional de conferência humana;
- testes;
- ajustes finais;
- documentação básica de operação.

---

## 12. Fora do escopo inicial

Não fazem parte do escopo inicial:

- contratação da VPS;
- domínio;
- mensalidades de terceiros;
- OCR comercial pago;
- revisão jurídica;
- responsabilidade técnica regulatória;
- painel administrativo personalizado;
- aplicativo mobile;
- treinamento de pesos dentro da VPS de homologação;
- integrações não descritas no escopo;
- mudanças substanciais de escopo após aprovação.

Qualquer item fora desta lista de requisitos deve ser tratado como alteração de escopo e registrado no `LOG.md` antes da implementação.

RAG, embeddings, `quality_checks`, análise JSON persistida e nota de confiança
semântica da IA não fazem parte do caminho ativo nem dos critérios de aceite do
MVP. A leitura determinística do RF-22 é uma etapa lexical simples, não usa
embeddings nem é RAG. Código, tabelas e exports relacionados a RAG ou a esquemas
JSON históricos permanecem como capacidade opcional/legada e não são chamados
pelo workflow atual. A prioridade executiva continua no relatório porque orienta
a ordem das ações sugeridas; ela não representa confiança da IA.

### Regras de qualidade e evidência

- Cada achado precisa informar `paginas_origem` e `evidencia` literal do Markdown.
- A página e o trecho precisam pertencer ao documento atual e ser auditáveis.
- Os únicos status são `deferido`, `indeferido`, `cancelado` e `outro`.
- Cancelamento não é indeferimento; dispositivo não é medicamento ou suplemento por inferência.
- Falha técnica interrompe a etapa e é registrada. Falha de qualidade gera
  relatório técnico com aviso, limitação e referências disponíveis; não bloqueia
  o processamento quando não houver falha técnica.
- Nenhum resultado com citação inválida pode ser apresentado como evidência
  comprovada; o relatório deve marcar a referência como pendente, sem impedir a
  conclusão operacional.

---

## 13. Critérios de aceite

O MVP poderá ser considerado entregue quando:

1. o ambiente estiver instalado e executando no servidor definido;
2. o gateway conseguir receber um PDF de teste e registrar o documento no PostgreSQL;
3. o PDF for convertido obrigatoriamente para Markdown;
4. o Markdown possuir metadados, hash e marcadores de página;
5. o Markdown for persistido e associado ao PDF de origem;
6. a análise usar somente o Markdown paginado persistido como fonte documental;
7. o provedor configurado processar o conteúdo; na opção OpenRouter, usar
   Terra, o V8 aprovado e apenas o Markdown documental autorizado; uma futura
   opção NVIDIA exige licença de produção e permissão para o tipo de dado;
8. todas as páginas forem analisadas e os achados temporários forem consolidados;
9. o relatório for gerado;
10. o relatório for convertido para PDF;
11. o PDF final for armazenado no volume privado e associado ao documento no PostgreSQL;
12. o relatório puder ser visualizado no detalhe autenticado do protocolo;
13. documento e tentativa forem concluídos no PostgreSQL após o registro do PDF persistido;
14. um caso de falha de conversão impedir a extração e ser identificado;
15. uma referência pendente for identificada no relatório, sem bloquear o fluxo, e puder ser conferida opcionalmente;
16. a fila, o detalhe e a conferência opcional forem operáveis pela sessão autenticada;
17. houver documentação mínima de operação;
18. os testes de funcionamento definidos no repositório estiverem aprovados;
19. a landing protegida aceitar um PDF, gerar protocolo e mostrar seu status;
20. o workflow analisar todas as páginas em lotes limitados e interromper o relatório se um lote falhar;
21. páginas e evidências literais forem conferidas automaticamente e citações inválidas forem marcadas como pendentes, sem bloquear a conclusão do processamento;
22. o relatório final puder ser baixado somente após conclusão válida.

Os critérios 23–24 aplicam-se ao contexto determinístico dos ramos Ollama;
os critérios 25–29, à auditoria do workflow híbrido v2. O modo Anvisa V8
mantém as validações específicas do RF-04.

23. um identificador repetido em páginas diferentes preservar todas as ocorrências e seus trechos, sem unir status ou atos por inferência;
24. marcadores de página ausentes ou fora de ordem forem rejeitados pela leitura determinística, e as menções encontradas aparecerem no relatório como localizações literais, não decisões.
25. a primeira passagem Python processar todas as páginas do Markdown salvo e registrar a versão do conjunto de regras;
26. a IA auditar todos os lotes e a falta de resposta de qualquer lote impedir um relatório apresentado como completo;
27. candidatos com evidência inexistente, página errada ou página fora do lote forem excluídos da síntese e contabilizados como pendentes;
28. a síntese final receber apenas candidatos aceitos pelo validador Python e as observações determinísticas;
29. observações de datas e durações preservarem a evidência original e não inferirem o efeito jurídico ou regulatório do texto.

---

## 14. Princípios de evolução

Toda evolução do produto deve preservar:

- rastreabilidade;
- conferência humana opcional para casos duvidosos;
- separação entre conteúdo original e interpretação da IA;
- possibilidade de troca do modelo;
- documentação atualizada;
- compatibilidade com a infraestrutura aprovada, salvo mudança registrada;
- segurança de credenciais;
- controle de alterações por Git.

---

## 15. Fonte de verdade

Para governança do desenvolvimento:

1. `PRD.md` define **o que o produto deve fazer**;
2. `AGENTS.md` define **como agentes e desenvolvedores devem trabalhar no repositório**;
3. `ROADMAP.md` define **em que fase o projeto está e o que falta**;
4. `LOG.md` registra **decisões, alterações, incidentes e memória operacional**.

Em caso de conflito entre implementação e documentação, a divergência deve ser registrada e resolvida antes de considerar a tarefa concluída.

O README.md apresenta a visão comercial e o uso; FLUXOGRAMA.md ilustra as etapas; ACESSOS.md informa onde configurar credenciais sem armazenar seus valores. Esses documentos complementam, mas não alteram, os requisitos deste PRD.

## Corpus oficial do DOU

O sistema pode importar, em staging protegido, edições completas do DOU
obtidas pelo INLABS da Imprensa Nacional. Cada edição deve permanecer como
documento independente, com data, seção, edição, URL e SHA-256. O corpus pode
servir a uma futura capacidade opcional de RAG e à fila de candidatos, mas não
é consultado pelo fluxo de análise atual. Nenhum documento bruto entra
automaticamente no treinamento supervisionado. Apenas análises corrigidas e
aprovadas em revisão humana podem formar exemplos de treinamento.

## Fluxo operacional com Ollama v1 — decisão de 2026-10-02

Esta seção descreve o ramo Ollama do v1, que mantém a opção Anvisa V8 em
ramo separado. O v2 híbrido tem export próprio e aplica o RF-23. A fotografia
da VPS de 27/10/2026 e os testes locais de novembro são estados distintos.

O processamento percorre uma cadeia linear, mas analisa o documento completo em
lotes para manter cada chamada ao modelo dentro de um limite controlado:

```text
PDF -> Markdown paginado -> varredura determinística de termos e identificadores
    -> análise de todas as páginas em lotes de até 6.000 caracteres
    -> achados e ligações literais temporários consolidados -> relatório Markdown
    -> validação de cobertura e referências -> PDF persistido -> concluido -> download no painel
```

O relatório Markdown é o resultado técnico principal; o PDF é a apresentação
final. O contrato ativo `regulatory-extraction-v6-full-document-batched-deterministic-context`
analisa todas as páginas, preserva as referências, recebe ligações literais de
identificadores entre páginas e usa as nove perguntas de negócio, com foco em
impacto, prioridade, plano de ação, limitações e referências de página. O prompt
instrui o modelo a tratar texto e evidências do PDF como dados não confiáveis e
ignorar comandos embutidos. A saída JSON dos lotes é temporária; ela é
consolidada e não substitui o Markdown nem é salva como análise estruturada do
documento.

O gateway confere a cobertura e cada citação do relatório contra o Markdown
original. Citações não confirmadas ficam pendentes e não bloqueiam a conclusão.
Lote com falha técnica ou cobertura incompleta interrompe a geração do
relatório. RAG, embeddings e `quality_checks` continuam fora do caminho ativo.
A revisão humana continua disponível como conferência opcional. O sinal do
relatório mede cobertura e localização de citações; não é confiança da IA. A
prioridade executiva indica a prioridade de ação recomendada e não substitui
esse sinal nem expressa certeza semântica.

Persistência PostgreSQL, deduplicação por SHA-256, controle de tentativas,
reconciliação, classificação de erros e download autenticado somente após
`concluido` continuam obrigatórios.

## Modelo Anvisa V8 no OpenRouter

No provedor OpenRouter, a stack Docker do sistema usa somente GPT-6 Luna.
O Markdown paginado é dividido em duas faixas contíguas,
com até duas páginas de sobreposição por lado. A página de início da unidade
determina a parte responsável pela ficha. Um documento de uma página exige uma
chamada. O índice de ocorrências literais orienta a leitura sem decidir
pertinência ou situação regulatória.

O modelo retorna JSON estruturado com todo o contrato V8, incluindo justificativa
nas fichas completas, IDs no inventário e observações de cobertura de até
96 caracteres. O renderizador valida cobertura e citações por parte e só gera
um PDF e um pacote de verificação quando todas as partes passam. Uma falha
encerra a tentativa sem chamada extra. O modo Luna não reutiliza nem migra
checkpoints Terra. Esses checkpoints permanecem guardados para auditoria.

## Decisão de arquitetura híbrida — 2026-10-27

O fluxo alvo passa a separar leitura mecânica, busca de lacunas e interpretação:

```text
Markdown persistido
  -> Python registra observações literais para todas as páginas
  -> IA audita todos os lotes e propõe fatos que podem faltar
  -> Python confere página, lote e citação dos candidatos
  -> IA interpreta observações e candidatos aceitos no relatório final
  -> validação do relatório, PDF persistido e conclusão
```

A implementação está representada em
`workflows/automacao-regulatoria-internal-v2-hybrid.json` e foi criada inativa.
O endpoint de validação usa o Markdown persistido e seu hash. Nenhum documento
real foi usado para a alteração nem para os testes sintéticos. Essa decisão
aplica-se ao workflow híbrido v2; não substitui o contrato
Anvisa V8. O registro de 27/10/2026 no LOG.md confirma a publicação do v2 na
VPS e a reprovação de qualidade do ensaio sintético. Isso não homologa o V8
local nem comprova o estado atual da VPS.
