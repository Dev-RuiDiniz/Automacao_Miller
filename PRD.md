# PRD.md — Agente de Automação e Análise Regulatória

## 1. Identificação do produto

**Produto:** Agente de Automação e Análise Regulatória
**Empresa responsável:** DB Tecnologia
**Responsável técnico:** Rui Diniz — Engenheiro de Software
**Objetivo do projeto:** automatizar o recebimento, leitura, organização, análise e distribuição de documentos regulatórios em PDF, substituindo um processo manual e repetitivo por um fluxo automatizado, rastreável e de baixo custo operacional.

---

## 2. Visão do produto

O produto será uma solução self-hosted de automação regulatória construída principalmente com **n8n + Ollama + PostgreSQL**, executada em servidor Linux via Docker. A arquitetura também poderá integrar NVIDIA NIM; documentos reais só poderão usar um endpoint de produção cuja licença e termos permitam o tipo de dado processado.

O caminho ativo recebe documentos pela landing privada e mantém os arquivos no
volume Docker e os metadados no PostgreSQL. O Google Drive permanece apenas nos
exports históricos; não é parte da entrada nem do processamento atual.

O sistema deve receber novos documentos PDF pelo gateway de upload, converter cada documento para Markdown paginado, fazer uma primeira leitura determinística de menções literais com página e evidência, pedir à IA que procure achados não capturados pelas regras em todas as páginas e validar em Python cada citação proposta pela IA contra o Markdown salvo. A IA que escreve o relatório final recebe as observações determinísticas e somente os candidatos cuja página e citação foram localizadas. Essa validação comprova onde o trecho aparece; não comprova se a interpretação do fato está correta. O PostgreSQL mantém metadados e estados; o volume privado do Docker guarda os arquivos. O envio por Gmail é solicitado manualmente pelo operador após a geração do relatório.

A IA deve atuar como ferramenta de apoio técnico à leitura, classificação, organização e geração de relatórios. O sistema deve produzir uma análise automatizada com linguagem e estrutura de especialista sênior, sem se apresentar como autoridade regulatória, advogado, médico ou responsável técnico, nem emitir decisão jurídica, médica ou regulatória definitiva.

### Em palavras simples

O operador entrega um PDF; o sistema organiza o texto, aponta o que encontrou e mostra de quais páginas tirou cada citação. O operador decide se solicita o envio do relatório. O resultado ajuda a equipe a trabalhar, mas não garante que a interpretação da IA esteja correta e não substitui um profissional habilitado.

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
enviar ou disponibilizar o relatório. Falhas técnicas continuam sendo tratadas
como erro e não como resultado válido.

### 4.3 Sistema automatizado

Responsável por:

1. detectar novos documentos;
2. processar o conteúdo;
3. consolidar temporariamente os achados dos lotes;
4. produzir o relatório;
5. armazenar os artefatos;
6. encaminhar o resultado por e-mail;
7. registrar erros, alertas de qualidade e referências que merecem conferência opcional.

---

## 5. Arquitetura funcional de referência

Componentes definidos para o projeto:

- **n8n:** automação e orquestração do workflow;
- **Ollama:** execução local atualmente implantada do modelo de IA;
- **Python no gateway:** leitura determinística do Markdown persistido e validação das páginas e citações propostas pela IA;
- **NVIDIA NIM:** provedor externo planejado, condicionado a endpoint/licença de
  produção, autorização para os dados e credencial protegida no n8n. A API
  Developer/API Catalog Trial segue limitada a fixture sintético;
- **PostgreSQL:** fonte de verdade operacional, metadados, estados, erros e vínculos;
- **Volume privado do Docker:** armazenamento interno dos PDFs, Markdown e relatórios;
- **Google Drive:** histórico da homologação anterior; não participa dos workflows ativos;
- **Gmail:** envio manual do relatório após a aprovação operacional;
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
Leitura determinística de menções literais por página
        ↓
IA audita todos os lotes em busca de achados não capturados pelas regras
        ↓
Python valida página e citação literal dos candidatos
        ↓
IA interpreta observações e candidatos aceitos para escrever o relatório
        ↓
Validação final da cobertura e das referências do relatório
        ↓
Geração e armazenamento do PDF
        ↓
Documento em aguardando_envio
        ↓
Conferência opcional do PDF e Markdown
        ↓
Envio manual por Gmail
        ↓
Documento concluído e download oficial liberado
```

O JSON usado em cada lote é temporário: ele ajuda a consolidar os achados, mas
não é salvo nem exibido como análise final. Os artefatos analíticos do caminho
atual são o relatório Markdown e sua versão PDF.

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

### RF-02 — Leitura de PDF

O sistema deve ler os PDFs suportados para produzir o artefato Markdown intermediário. Falhas de leitura devem ser classificadas como erro técnico.

### RF-03 — Conversão obrigatória para Markdown

Todo PDF elegível deve ser convertido para uma representação Markdown organizada antes de qualquer extração estruturada ou chamada ao provedor de IA selecionado. O Markdown deve conter metadados do documento, SHA-256, contagem de páginas, versão do conversor e um marcador `## Página N` para cada página. Falha de conversão, PDF corrompido ou ausência de camada textual deve interromper a análise e gerar erro técnico explícito. Possíveis tabelas devem ser preservadas quando detectáveis, com aviso de layout quando a geometria não puder ser reconstruída com segurança; OCR não faz parte desta etapa.

### RF-04 — Análise por IA

A análise usa o Markdown persistido como única fonte documental. Ollama local é
o provedor atualmente implantado. O projeto passa a prever uma integração
opcional com NVIDIA NIM para documentos reais somente quando o endpoint tiver
licença de produção e seus termos permitirem expressamente o tipo de dado
enviado, incluindo informação governamental. Antes do envio, o responsável deve
autorizar o documento e o destino e registrar as condições de retenção, uso dos
dados e proteção aplicáveis. O provedor e o modelo precisam ficar identificados
na tentativa; não há fallback automático entre provedores.

A NVIDIA API Trial/Developer Catalog continua exclusiva para o workflow manual
de avaliação com fixture sintético, separado e inativo. Os termos atuais do
Trial limitam o uso a teste/avaliação, restringem o envio de informação
governamental sem permissão específica do serviço e permitem uso de conteúdo
para melhoria de produtos/modelos. O endpoint Trial não processa uploads reais.
Uma credencial exposta deve ser revogada e substituída antes de qualquer uso.

Depois da leitura determinística, a IA deve auditar todos os lotes do Markdown
em busca de fatos relevantes não localizados pelas regras. Ela deve devolver
candidatos com página e citação literal. Python deve verificar se a página
existe, se pertence ao lote analisado e se a citação está na página indicada do
Markdown persistido. A etapa de redação final recebe as observações
determinísticas e somente os candidatos aceitos. Candidatos rejeitados ficam
fora da síntese e são contabilizados como pendentes. Falha em qualquer lote da
auditoria impede a geração de um relatório apresentado como completo.

Essa arquitetura continua usando IA para procurar lacunas e interpretar o
relatório. A primeira passagem reduz a dependência de IA para localizar padrões
simples, mas não torna o processamento sem IA nem garante que as regras cubram
todo achado relevante.

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

### RF-07 — Cobertura documental e qualidade das evidências

O sistema deve exibir no relatório um sinal objetivo que informe quantas páginas
foram analisadas e quantas referências a páginas e evidências literais foram
confirmadas no Markdown original. Esse sinal mede cobertura e localização de
evidências; não representa confiança semântica ou nota de certeza da IA.

Referências não localizadas, com página inexistente ou citação diferente da
fonte devem ser marcadas como pendentes e claramente distinguidas das
comprovadas. Pendências de citação não bloqueiam a geração do PDF, o estado
`aguardando_envio` nem a solicitação manual de envio. Cobertura incompleta por
falha técnica de lote, leitura ou página deve interromper a geração do relatório.

A validação é oferecida pela rota interna autenticada
`POST /internal/submissions/{id}/validate-report`. O gateway carrega o Markdown original
do armazenamento, confere as páginas analisadas e cada par página/evidência,
e devolve as referências confirmadas e pendentes. A origem não pode ser enviada
pelo cliente como substituta do artefato guardado.

Essa validação comprova apenas cobertura e localização literal de páginas e trechos. Ela não verifica se a interpretação da IA está semanticamente correta. Pela regra atual, referências pendentes não bloqueiam por si só o relatório ou a solicitação manual de envio; esse comportamento não deve ser apresentado como garantia de qualidade.

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

### RF-12 — Envio manual por e-mail

Depois de gerar e persistir o PDF final, o workflow deve colocar o documento em
`aguardando_envio` quando a cobertura do processamento estiver completa,
independentemente de haver referências pendentes. O operador
autenticado pode visualizar os artefatos, conferir páginas e evidências quando
desejar, selecionar os destinatários padrão ou substituí-los para aquele
documento e solicitar o envio pelo Gmail. O status só pode mudar para
`concluido` após a confirmação do Gmail; uma falha deve ser registrada em
`email_deliveries` e permitir nova tentativa controlada.

### RF-13 — Tratamento de erros

O workflow deve possuir tratamento básico de erros para evitar que falhas silenciosas sejam consideradas processamento concluído. Falha na conversão PDF → Markdown deve interromper a extração e encaminhar o documento para erro. Alertas de qualidade, citações pendentes ou ausência de evidência devem ser
registrados no relatório técnico e não podem ser confundidos com falha técnica.

### RF-14 — Rastreabilidade

Cada documento deve possuir estado de processamento identificável, permitindo distinguir minimamente:

- recebido;
- em processamento;
- aguardando envio;
- concluído;
- com erro.

`aguardando_revisao` pode existir apenas como estado legado ou de compatibilidade;
o fluxo atual não depende dele para concluir o relatório.

### RF-15 — Painel operacional autenticado

O sistema deve oferecer login por sessão, painel de fila com busca, filtros,
indicadores, detalhes do protocolo, linha do tempo, tentativas, erros, conferência
opcional e configuração de destinatários. O detalhe deve permitir visualizar o
relatório PDF e seu Markdown antes do envio. Registros antigos podem manter um
artefato JSON por compatibilidade; o fluxo atual não o gera.

### RF-16 — Gateway de upload

O gateway deve validar o conteúdo do arquivo, calcular SHA-256, impedir
duplicidade acidental, persistir o upload em volume controlado e encaminhar o
protocolo ao n8n sem expor credenciais de integrações ao navegador.

### RF-17 — Download e visualização controlados

As visualizações autenticadas podem ocorrer enquanto o documento aguarda envio
ou possui um registro legado de revisão. O download oficial do relatório deve
responder somente quando o documento estiver em `concluido`; nenhuma chave
absoluta ou caminho do volume pode ser exposto ao navegador.

### RF-18 — Destinatários e auditoria de entrega

O sistema deve manter destinatários padrão ativos ou inativos, destinatários
específicos por documento e um snapshot de cada solicitação de envio, com
status, execução, tentativa, erro, responsável e datas.

### RF-19 — Acesso por usuário e senha

A landing deve oferecer uma página de acesso com usuário e senha antes da tela
de upload. As credenciais devem ser configuradas somente no ambiente autorizado;
a senha deve ser armazenada como hash e a autenticação deve criar uma sessão
segura em cookie. O acesso legado por token privado pode permanecer disponível
para compatibilidade operacional, mas não deve expor o token na interface de
login.

### RF-20 — Contexto determinístico rastreável

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

### RF-21 — Auditoria de lacunas e validação em Python

A IA deve revisar todas as páginas em lotes para propor fatos que não estejam
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

Um processamento só pode ser marcado como concluído quando as etapas obrigatórias do fluxo tiverem sido executadas com sucesso e o relatório final tiver sido gerado.

### RN-07 — Idempotência

O mesmo arquivo não deve gerar processamentos duplicados de forma não
intencional. O gateway deve deduplicar pelo SHA-256 e o workflow deve usar a
reivindicação transacional do PostgreSQL para impedir execuções concorrentes.

### RN-08 — Registro de falhas

Erros relevantes devem possuir registro suficiente para diagnóstico, incluindo etapa, documento, horário e mensagem de erro quando disponível.

### RN-09 — Credenciais fora do código

Credenciais do Google, Gmail, n8n, servidor ou qualquer outro serviço não podem ser mantidas em código-fonte versionado.

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

### RN-18 — Candidatos da IA precisam de citação verificável

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

A análise local por Ollama permanece disponível. Uma integração NVIDIA para
documentos reais depende de licença/assinatura de produção e de termos que
permitam o dado governamental específico; a autorização do usuário, por si só,
não substitui essa permissão. Antes da integração, confirme retenção, uso para
treinamento/melhoria, controles de acesso e localização do processamento. A API
Trial gratuita usa somente fixture artificial e nunca recebe documentos,
identificadores internos ou dados pessoais/governamentais sem permissão expressa
do endpoint. Credenciais devem ficar no cofre n8n, nunca no export ou Git.

### RNF-03 — Manutenibilidade

Workflows, prompts, configurações e documentação devem ser organizados de forma que possam ser atualizados sem perda de rastreabilidade.

### RNF-04 — Observabilidade mínima

Falhas de integração, extração, análise e envio precisam ser identificáveis.

### RNF-05 — Recuperação

Uma falha intermediária não deve obrigar o reprocessamento manual de todo o fluxo quando for tecnicamente possível retomar a partir da etapa adequada.

### RNF-06 — Segurança

Tokens, senhas, chaves e credenciais devem ser armazenados por mecanismos adequados do ambiente e nunca em arquivos públicos do repositório.

### RNF-07 — Serviço local de conversão

A conversão PDF → Markdown deve ser executada por serviço local versionado, testável e implantável via Docker, com health check, timeout e contrato HTTP interno. O serviço deve validar a estrutura do PDF com `pdfplumber`, manter leitura textual eficiente para documentos extensos e retornar avisos de layout sem ocultar falhas.

---

## 10. Modelo mínimo do relatório regulatório

O relatório em Markdown deve conter as seções fixas pedidas pelo prompt ativo:

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
- integração com Gmail;
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
- envio manual por e-mail pelo painel, com conferência opcional;
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
MVP. A leitura determinística do RF-20 é uma etapa lexical simples, não usa
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
7. o provedor aprovado para o ambiente processar o conteúdo; se for NVIDIA,
   comprovar licença de produção e permissão para o tipo de dado;
8. todas as páginas forem analisadas e os achados temporários forem consolidados;
9. o relatório for gerado;
10. o relatório for convertido para PDF;
11. o PDF final for armazenado no volume privado e associado ao documento no PostgreSQL;
12. o relatório puder ser visualizado internamente antes do envio;
13. o envio manual for confirmado pelo Gmail e registrado no PostgreSQL;
14. um caso de falha de conversão impedir a extração e ser identificado;
15. uma referência pendente for identificada no relatório, sem bloquear o fluxo, e puder ser conferida opcionalmente;
16. a fila, o detalhe, os destinatários e a conferência opcional forem operáveis pela sessão autenticada;
17. houver documentação mínima de operação;
18. os testes de funcionamento definidos no repositório estiverem aprovados;
19. a landing protegida aceitar um PDF, gerar protocolo e mostrar seu status;
20. o workflow analisar todas as páginas em lotes limitados e interromper o relatório se um lote falhar;
21. páginas e evidências literais forem conferidas automaticamente e citações inválidas forem marcadas como pendentes, sem bloquear o estado `aguardando_envio`;
22. o relatório final puder ser baixado somente após conclusão válida.
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

## Decisão histórica sobre o fluxo da versão v1 — 2026-10-02

Esta seção registra o desenho da versão v1, anterior à arquitetura híbrida
descrita no RF-21. A v1 continua sendo a versão observada na VPS na consulta de
26/10/2026; o export v2 híbrido permanece inativo no repositório.

O processamento percorre uma cadeia linear, mas analisa o documento completo em
lotes para manter cada chamada ao modelo dentro de um limite controlado:

```text
PDF -> Markdown paginado -> varredura determinística de termos e identificadores
    -> análise de todas as páginas em lotes de até 6.000 caracteres
    -> achados e ligações literais temporários consolidados -> relatório Markdown
    -> validação de cobertura e referências -> PDF -> aguardando_envio
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
original. Citações não confirmadas ficam pendentes e não bloqueiam a entrega.
Lote com falha técnica ou cobertura incompleta interrompe a geração do
relatório. RAG, embeddings e `quality_checks` continuam fora do caminho ativo.
A revisão humana continua disponível como conferência opcional. O sinal do
relatório mede cobertura e localização de citações; não é confiança da IA. A
prioridade executiva indica a prioridade de ação recomendada e não substitui
esse sinal nem expressa certeza semântica.

Persistência PostgreSQL, deduplicação por SHA-256, controle de tentativas,
reconciliação, classificação de erros, envio autenticado e download somente após
`concluido` continuam obrigatórios.

## Decisão de arquitetura híbrida — 2026-10-27

O fluxo alvo passa a separar leitura mecânica, busca de lacunas e interpretação:

```text
Markdown persistido
  -> Python registra observações literais para todas as páginas
  -> IA audita todos os lotes e propõe fatos que podem faltar
  -> Python confere página, lote e citação dos candidatos
  -> IA interpreta observações e candidatos aceitos no relatório final
  -> validação do relatório, PDF e aguardando_envio
```

A versão local está representada em
`workflows/automacao-regulatoria-internal-v2-hybrid.json` e foi criada inativa.
O endpoint de validação usa o Markdown persistido e seu hash. Nenhum documento
real foi usado para a alteração nem para os testes sintéticos. Essa decisão
define o comportamento esperado do produto; não significa que o workflow já
esteja ativo na VPS.
