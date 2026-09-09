# LOG.md — Registro e Memória do Projeto

## 1. Objetivo

Este arquivo é a memória operacional e técnica do projeto **Agente de Automação e Análise Regulatória**.

Deve ser utilizado por agentes de IA e desenvolvedores para compreender:

- contexto do projeto;
- decisões tomadas;
- alterações de escopo;
- mudanças de arquitetura;
- incidentes;
- testes importantes;
- pendências;
- restrições;
- histórico de evolução.

O `LOG.md` é append-only por princípio: registros anteriores não devem ser apagados apenas porque uma decisão mudou.

---

## 2. Como registrar

Usar o formato:

```text
## AAAA-MM-DD — Título

Tipo:
Status:
Contexto:
Decisão/Ação:
Arquivos/Componentes afetados:
Testes:
Pendências:
Impacto:
```

Tipos sugeridos:

- `DECISAO`
- `ARQUITETURA`
- `ESCOPO`
- `IMPLEMENTACAO`
- `TESTE`
- `BUG`
- `INCIDENTE`
- `INFRA`
- `PROMPT`
- `MODELO`
- `DOCUMENTACAO`
- `BLOQUEIO`
- `ENTREGA`

---

## 3. Contexto consolidado do projeto

### Produto

Solução automatizada para processamento e análise de documentos regulatórios em PDF.

### Objetivo

Substituir processo manual e repetitivo por fluxo automatizado, rastreável e de baixo custo operacional.

### Stack definida

- n8n;
- Ollama;
- Google Drive;
- Gmail;
- Docker;
- Linux em VPS.

### Arquitetura aprovada para evolução

- PostgreSQL como fonte de verdade operacional;
- volume privado do Docker para PDFs, Markdown e relatórios;
- Google Drive apenas para importação temporária durante a transição;
- Gmail para envio;
- n8n para orquestração;
- Ollama para análise local.

Essa arquitetura ainda não está implementada nos workflows versionados. A
homologação vigente registrada nos eventos históricos continua usando o Drive.

### Fluxo de referência

```text
Google Drive
→ PDF
→ conversão obrigatória para Markdown
→ persistência do Markdown
→ extração estruturada
→ Ollama
→ dados estruturados
→ relatório
→ PDF
→ Google Drive
→ Gmail
```

### Capacidades previstas

- monitoramento automático de PDFs;
- extração de conteúdo;
- conversão para Markdown;
- análise por IA;
- identificação de status regulatório;
- identificação de medicamentos;
- identificação de suplementos alimentares;
- identificação de ensaios clínicos;
- identificação de exigências e pendências;
- dados estruturados;
- controle de confiança;
- revisão humana;
- geração de relatório;
- geração de PDF;
- armazenamento;
- envio automático;
- tratamento básico de erros.

### Limites importantes

A IA é ferramenta de apoio e não substitui profissional habilitado em questões jurídicas, médicas ou regulatórias.

Casos com baixa confiança, informação contraditória ou evidência insuficiente devem poder ser direcionados à revisão humana.

### Fora do escopo inicial

- OCR comercial pago;
- revisão jurídica;
- responsabilidade técnica regulatória;
- painel administrativo;
- aplicativo mobile;
- fine-tuning;
- treinamento de modelo proprietário;
- integrações não descritas;
- mudanças substanciais após aprovação.

---

## 4. Registro inicial

## 2026-08-11 — Proposta comercial de referência

**Tipo:** ESCOPO  
**Status:** BASELINE

**Contexto:**  
Foi estabelecida a proposta comercial para criação de um Agente de Automação e Análise Regulatória utilizando n8n e Ollama.

**Decisão/Ação:**  
Adotar como arquitetura inicial:

- n8n para orquestração;
- Ollama para IA local;
- Google Drive para entrada e armazenamento;
- Gmail para envio;
- Docker para implantação;
- VPS Linux para hospedagem.

**Arquivos/Componentes afetados:**  
Baseline geral do projeto.

**Testes:**  
Ainda não aplicável.

**Pendências:**  

- acessos;
- arquivos de exemplo;
- implantação;
- integrações;
- workflow;
- testes.

**Impacto:**  
Define o escopo funcional e técnico inicial.

---

## 2026-08-11 — Infraestrutura de referência

**Tipo:** INFRA  
**Status:** BASELINE

**Contexto:**  
Foi indicada infraestrutura de baixo custo para o MVP.

**Decisão/Ação:**  
Usar como referência inicial:

- 2 vCPU;
- 8 GB RAM;
- 100 GB NVMe;
- Linux;
- modelo Ollama leve e quantizado.

**Arquivos/Componentes afetados:**  
Docker, n8n, Ollama.

**Testes:**  
Será necessário medir consumo real de CPU/RAM durante a fase de implantação.

**Pendências:**  
Confirmar VPS efetivamente contratada.

**Impacto:**  
O modelo de IA e os limites de processamento devem respeitar os recursos do servidor.

---

## 2026-08-11 — Política de IA

**Tipo:** DECISAO  
**Status:** BASELINE

**Contexto:**  
A solução processará documentos potencialmente sensíveis e regulatórios.

**Decisão/Ação:**  

- executar IA localmente via Ollama;
- não tratar saída da IA como parecer definitivo;
- sinalizar baixa confiança;
- encaminhar ambiguidades para revisão humana;
- evitar dependência de cobrança por token no escopo inicial.

**Arquivos/Componentes afetados:**  
Prompts, workflow, relatórios, validações.

**Testes:**  
Criar casos com baixa evidência e conteúdo contraditório.

**Pendências:**  
Definir o modelo inicial e a métrica/regra prática de confiança.

**Impacto:**  
A arquitetura deve preservar supervisão humana.

---

## 2026-08-11 — Escopo de integração

**Tipo:** ESCOPO  
**Status:** BASELINE

**Contexto:**  
Foram definidas as integrações do MVP.

**Decisão/Ação:**  
O MVP contempla somente:

- Google Drive;
- Gmail;
- n8n;
- Ollama.

Integrações adicionais exigem avaliação e registro de mudança de escopo.

**Arquivos/Componentes afetados:**  
Workflow e credenciais.

**Testes:**  
Testar upload/download no Drive e envio pelo Gmail.

**Pendências:**  
Receber acessos autorizados.

**Impacto:**  
Evita expansão silenciosa de escopo.

---

## 2026-08-11 — Limitação de OCR

**Tipo:** ESCOPO  
**Status:** BASELINE

**Contexto:**  
PDFs escaneados podem não possuir texto extraível.

**Decisão/Ação:**  
OCR comercial pago não faz parte do escopo inicial.

O sistema deve diferenciar:

- documento sem informação;
- documento cuja extração falhou;
- documento que exige OCR.

**Arquivos/Componentes afetados:**  
Etapa de extração e tratamento de erro.

**Testes:**  
Adicionar PDF escaneado ao conjunto de validação.

**Pendências:**  
Definir comportamento operacional para documento sem texto extraível.

**Impacto:**  
Pode gerar encaminhamento manual ou necessidade de orçamento adicional.

---

## 2026-08-25 — Criação da governança do repositório

**Tipo:** DOCUMENTACAO  
**Status:** CONCLUIDO

**Contexto:**  
Foi solicitada a criação dos quatro arquivos de governança para orientar o projeto e qualquer agente atuando no repositório.

**Decisão/Ação:**  
Criados:

- `PRD.md`;
- `AGENTS.md`;
- `ROADMAP.md`;
- `LOG.md`.

**Arquivos/Componentes afetados:**  
Documentação raiz do repositório.

**Testes:**  
Revisão cruzada entre escopo, regras, roadmap e memória.

**Pendências:**  

- versionar os arquivos no repositório;
- confirmar estrutura real do repositório;
- confirmar status de infraestrutura e acessos;
- atualizar este log conforme a execução começar.

**Impacto:**  
O projeto passa a ter uma fonte explícita de requisitos, processo de desenvolvimento, acompanhamento e memória.

---

## 2026-08-25 — README comercial e versionamento inicial

**Tipo:** DOCUMENTACAO  
**Status:** CONCLUIDO

**Contexto:**  
Foi solicitada uma apresentação comercial e descritiva do produto para clientes e usuários, além do primeiro versionamento da documentação na branch estável.

**Decisão/Ação:**  
Criado um README com proposta de valor, fluxo operacional, públicos, recursos, segurança, limites da IA, escopo inicial, requisitos de implantação e próximos passos. Confirmado o uso da branch `main` como versão estável e do repositório remoto oficial `origin`.

**Arquivos/Componentes afetados:**  
`README.md`, `PRD.md`, `ROADMAP.md`, `LOG.md`, `AGENTS.md` e plano de execução em `docs/superpowers/plans/`.

**Testes:**  
Revisão de consistência do README contra o PRD, revisão do diff e verificação de ausência de credenciais ou tokens nos arquivos da entrega. Não há testes automatizados aplicáveis a esta alteração exclusivamente documental.

**Pendências:**  
Configuração da infraestrutura, integrações, arquivos PDF de referência, definição do modelo Ollama, testes ponta a ponta e demais itens do roadmap permanecem em aberto.

**Impacto:**  
A documentação inicial passa a apresentar o produto para o público externo e a registrar a governança necessária para a evolução segura do projeto.

---

## 2026-08-25 — Fechamento da preparação interna da Fase 0

**Tipo:** DOCUMENTACAO  
**Status:** PREPARAÇÃO INTERNA CONCLUÍDA

**Contexto:**  
Foi executado o plano de fechamento da preparação interna do repositório, sem iniciar infraestrutura, integrações externas ou processamento de documentos.

**Decisão/Ação:**  
Criados o `.gitignore`, o `.env.example` seguro, a estrutura inicial de diretórios e os checklists de acessos, responsáveis e documentos de referência. Os bloqueios externos permaneceram pendentes e foram explicitamente preservados no roadmap.

**Arquivos/Componentes afetados:**  
`.gitignore`, `.env.example`, `docs/checklists/`, `infra/`, `workflows/`, `prompts/`, `scripts/`, `tests/fixtures/`, `ROADMAP.md` e `LOG.md`.

**Testes:**  
Validação de placeholders no `.env.example`, verificação planejada de arquivos ignorados, revisão de referências Markdown e busca por padrões de credenciais. Não foram executados testes de infraestrutura ou integração, pois permanecem fora desta frente.

**Pendências:**  
Confirmar VPS, acessos Google Drive/Gmail, PDFs autorizados, destinatários, responsáveis pela validação e demais itens dos bloqueios `EXT-001` a `EXT-005`.

**Impacto:**  
O repositório possui uma base segura e organizada para iniciar a Fase 1 quando os acessos e insumos externos forem disponibilizados, sem criar dados ou credenciais fictícias.

---

## 2026-08-25 — Camada obrigatória PDF para Markdown

**Tipo:** ARQUITETURA
**Status:** IMPLEMENTADO PARCIALMENTE

**Contexto:**
Foi definida a regra de que nenhum PDF deve seguir para extração estruturada ou Ollama sem passar primeiro por uma conversão local e determinística para Markdown. O PDF de referência recebido é um Diário Oficial da União de 128 páginas, contendo atos da Anvisa e conteúdos não relacionados ao recorte regulatório solicitado.

**Decisão/Ação:**
Criado o serviço local `infra/pdf_converter` com API interna, validação estrutural por `pdfplumber`, extração textual eficiente, metadados por hash, marcadores `## Página N`, tratamento explícito de PDFs inválidos/sem camada textual e imagem Docker. Criados o contrato do gate n8n, o contrato/schema de extração regulatória e a documentação de status `deferido`, `indeferido`, `cancelado` e `outro`.

**Arquivos/Componentes afetados:**
`infra/pdf_converter/`, `tests/pdf_converter/`, `workflows/pdf-to-markdown-gate.md`, `prompts/regulatory-extraction-v1.md`, `prompts/regulatory-extraction.schema.json`, `.env.example`, `PRD.md`, `ROADMAP.md` e `docs/checklists/matriz-documentos-referencia.md`.

**Testes:**
Testes unitários e de API do conversor passaram para PDF textual, PDF inválido, PDF sem camada textual, health check e contrato de conversão. A validação ponta a ponta com Google Drive, n8n, Ollama e o PDF de 128 páginas ainda está pendente.

**Pendências:**
Implantar o container na VPS, integrar o gate no workflow n8n, persistir o Markdown no Drive, executar a validação completa do PDF de referência e conectar a extração estruturada ao Ollama.

**Impacto:**
A extração passa a ter um artefato intermediário auditável e uma barreira técnica contra análise direta do PDF bruto, preservando páginas e distinguindo erro técnico de ausência de informação.

**Referência:**
`2026_08_24_ASSINADO_do1.pdf`, 128 páginas, SHA-256 `3AD26053AF9898A8BFA7DE5AE3A409313AB9230ED28079F1794C82238797E9B6`. O arquivo não será versionado no repositório.

## 2026-08-25 — Desempenho e preservação de layout do conversor

**Tipo:** IMPLEMENTAÇÃO / DESEMPENHO
**Status:** VALIDADO LOCALMENTE

**Contexto:**
A reconstrução geométrica de tabelas e o modo `layout=True` do `pdfplumber` tornaram a conversão do DOU de 128 páginas impraticável.

**Decisão/Ação:**
O conversor foi versionado como `0.3.0`. O texto passou a ser extraído em ordem por palavra com `pypdf`, mantendo `pdfplumber` na abertura e validação estrutural do documento. Possíveis tabelas são detectadas por padrão textual, preservadas em bloco Markdown e acompanhadas de aviso quando a geometria não é reconstruída.

**Arquivos afetados:**
`infra/pdf_converter/converter.py`, `infra/pdf_converter/app.py`, `infra/pdf_converter/README.md`, `workflows/pdf-to-markdown-gate.md`, `.env.example`, `PRD.md` e `tests/pdf_converter/test_converter.py`.

**Testes:**
`python -m pytest -q` passou com 7 testes. Após o gate de tabelas estruturadas, o PDF de referência foi convertido localmente em 66,30 s, com 128 páginas, 128 marcadores, Markdown não vazio, um bloco de tabela estruturada e SHA-256 conferido. Os recortes das páginas 71–75 e 79 preservaram os atos de alimentos, medicamentos, indeferimentos, cancelamentos e o conteúdo de ensaio clínico; a validação da extração estruturada e do workflow integrado permanece pendente.

**Pendências:**
Implantar o container na VPS, integrar o gate no workflow n8n, persistir o Markdown no Drive e executar os cenários estruturados contra fixture sanitizada/autorizada.

**Impacto:**
A camada obrigatória mantém desempenho previsível em DOU extensos sem transformar avisos de layout em dados silenciosamente reconstruídos.

---

## 2026-08-25 — Confirmação de documentos e responsável de validação

**Tipo:** GOVERNANÇA
**Status:** CONCLUÍDO

**Contexto:**
Os documentos PDF de referência foram enviados e o responsável pela validação foi informado como Miller.

**Decisão/Ação:**
Os itens de confirmação da Fase 0 foram concluídos. O bloqueio `EXT-004` passou para `DONE`, os documentos foram mantidos fora do Git e Miller foi registrado como responsável pela validação técnica, revisão humana e aprovação dos resultados.

**Arquivos afetados:**
`ROADMAP.md`, `docs/checklists/acessos-e-responsaveis.md` e `docs/checklists/matriz-documentos-referencia.md`.

**Testes:**
Revisão de consistência dos checklists e conferência do vínculo com o PDF de referência já registrado.

**Pendências:**
A validação técnica dos cenários do PDF continua prevista na Fase 10; esta atualização confirma apenas o recebimento dos documentos e a responsabilidade.

**Impacto:**
A governança da Fase 0 passa a registrar os insumos e o responsável sem versionar o PDF original.

---

## 5. Pendências abertas

| ID | Pendência | Tipo | Prioridade | Status |
|---|---|---|---|---|
| P-001 | Confirmar VPS | INFRA | Alta | Aberta |
| P-002 | Receber credenciais do Google Drive | BLOQUEIO | Alta | Aberta |
| P-003 | Receber credenciais Gmail | BLOQUEIO | Alta | Aberta |
| P-004 | Validar PDF de referência recebido | TESTE | Alta | Em andamento |
| P-005 | Selecionar modelo Ollama inicial | MODELO | Alta | Aberta |
| P-006 | Definir estrutura final da saída da IA | PROMPT | Alta | Concluída |
| P-007 | Definir regra operacional de confiança | DECISAO | Alta | Aberta |
| P-008 | Definir template do relatório | IMPLEMENTACAO | Média | Aberta |
| P-009 | Definir destinatários dos e-mails | ESCOPO | Média | Aberta |
| P-010 | Definir comportamento para PDF escaneado | DECISAO | Média | Concluída |

---

## 6. Decisões que ainda precisam ser fechadas

### D-001 — Modelo Ollama

Registrar:

- nome;
- tag/versão;
- quantização;
- memória consumida;
- tempo médio;
- motivo da escolha.

### D-002 — Confiança

Definir como um resultado será classificado em:

- aceitável;
- baixa confiança;
- inconclusivo;
- erro técnico.

### D-003 — Estrutura das pastas do Drive

Definir pastas para:

- entrada;
- processamento;
- concluídos;
- revisão;
- erros;
- relatórios.

### D-004 — Idempotência

Definir mecanismo para impedir processamento duplicado.

Possibilidades:

- ID do arquivo no Google Drive;
- hash do conteúdo;
- registro de execução persistente.

### D-005 — Política de retry

Definir quantas tentativas serão realizadas para erros transitórios.

### D-006 — Retenção

A proposta não define política de retenção. Não presumir exclusão automática de documentos sem aprovação.

---

## 7. Registro de incidentes

Usar esta seção quando houver falha em produção ou homologação.

Template:

```text
## AAAA-MM-DD — INC-XXX — título

Tipo: INCIDENTE
Severidade:
Início:
Fim:
Componente:
Sintoma:
Causa:
Correção:
Prevenção:
Dados afetados:
Necessita reprocessamento:
```

---

## 8. Registro de mudanças de prompt

Toda mudança relevante do prompt deve registrar:

- data;
- versão;
- motivo;
- comportamento esperado;
- documentos usados no teste;
- diferenças observadas;
- decisão de manter ou reverter.

Template:

```text
## AAAA-MM-DD — PROMPT vX

Tipo: PROMPT
Motivo:
Mudança:
Dataset de teste:
Resultado:
Riscos:
Decisão:
```

---

## 9. Registro de mudança de modelo

Template:

```text
## AAAA-MM-DD — MODELO

Tipo: MODELO
Modelo anterior:
Modelo novo:
Motivo:
RAM:
CPU:
Tempo médio:
Qualidade observada:
Testes executados:
Decisão:
```

---

## 2026-08-26 — Implementacao da stack de homologacao

**Tipo:** IMPLEMENTACAO / INFRAESTRUTURA
**Status:** IMPLEMENTADO E IMPLANTADO NA VPS DE HOMOLOGACAO; INTEGRACOES GOOGLE PENDENTES

**Contexto:**
A VPS propria foi auditada antes da implantacao. O ambiente possui Debian 13,
2 vCPU, 8 GB de RAM, 4 GB de swap, 99 GB de disco com aproximadamente 65 GB
livres, Docker 29.5.2 e Docker Compose 5.1.4. Ja existem os projetos Docker
`atendimento` e `rtk-renata`, com dois n8n ativos; eles nao devem ser alterados.

**Decisao/Acao:**
Criada a branch `feat/vps-staging-deployment`. Implementada stack isolada com
n8n 2.30.5, PostgreSQL 15.18, Ollama 0.32.1, conversor PDF→Markdown e
renderizador local de relatorios PDF. O modelo inicial definido e
`qwen2.5:3b`, sujeito a benchmark de memoria e tempo na VPS. Adicionados
controle de duplicidade por ID+SHA-256, tabela de rastreabilidade, retry de
chamadas HTTP, workflow principal versionado e workflow separado de erros.

**Arquivos afetados:**
`docker-compose.yml`, `deploy/`, `infra/report_renderer/`,
`infra/regulatory_analysis/`, `workflows/`, `prompts/`, `.env.example`,
`tests/`, `README.md`, `ROADMAP.md` e `docs/checklists/acessos-e-responsaveis.md`.

**Testes:**
`python -m pytest -q` passou com 16 testes. Os dois exports n8n e o YAML do
Compose foram validados localmente. A stack remota iniciou com todos os cinco
servicos saudaveis; o endpoint interno do Ollama respondeu via n8n com
`qwen2.5:3b` em aproximadamente 61 segundos no primeiro carregamento.

**Pendencias:**
Configurar credenciais Google Drive/Gmail dentro do n8n, preencher IDs de
pastas e destinatarios, ativar o workflow principal e executar os cenarios da
matriz. Os workflows foram importados com sucesso apos a criacao do usuario
proprietario no n8n.

**Impacto:**
O repositorio passa a conter uma base executavel e isolada para homologacao,
sem reutilizar volumes, portas publicas ou credenciais dos projetos existentes.

## 2026-08-26 — Auditoria e implantacao da VPS de homologacao

**Tipo:** AUDITORIA / INFRAESTRUTURA / MODELO
**Status:** CONCLUIDO COM PENDENCIAS DE INTEGRACAO

**Contexto:**
A auditoria confirmou Debian 13.6, kernel 6.12.85, 2 vCPU, 7.8 GiB de RAM,
4 GiB de swap, aproximadamente 65 GiB livres, Docker 29.5.2 e Compose 5.1.4.
Os projetos `atendimento` e `rtk-renata` permaneceram sem alteracao.

**Decisao/Acao:**
A stack foi instalada em `/opt/automacao-miller` com volumes e rede proprios,
n8n publicado somente em `127.0.0.1:25678`. O PostgreSQL, Ollama, conversor e
renderizador nao possuem portas publicadas. O modelo `qwen2.5:3b` foi baixado,
carregado e validado pelo endpoint HTTP interno a partir do container n8n.
As portas UFW 3000, 5432, 8000 e 8080 foram removidas somente apos confirmacao
de que nao havia listener nessas portas; SSH, HTTP, HTTPS e portas dos projetos
existentes foram preservados.

**Testes:**
`docker compose config --quiet`, `docker compose ps`, health checks dos cinco
servicos, readiness do n8n, health checks do conversor/renderizador, existencia
das tabelas de rastreabilidade e inferencia HTTP do Ollama.

**Pendencias:**
Credenciais Google, IDs das pastas, destinatarios, ativacao dos workflows e
testes ponta a ponta continuam pendentes. A senha root usada nesta
sessao foi exposta no contexto da tarefa e deve ser rotacionada imediatamente;
o acesso root por senha nao deve ser desativado antes de validar uma chave SSH
alternativa.

**Impacto:**
A homologacao possui infraestrutura operacional e isolada, mas ainda nao pode
ser considerada aceita ponta a ponta sem Drive/Gmail autorizados.

## 2026-08-26 — Configuracao inicial do n8n

**Tipo:** CONFIGURACAO / ACESSO
**Status:** CONCLUIDO

**Contexto:**
O n8n novo exigiu a configuracao inicial de proprietario antes de aceitar a
importacao por CLI.

**Decisao/Acao:**
Foi criada uma conta proprietaria administrativa fora do repositorio. O login
foi testado pelo tunel SSH, e os workflows principal e de erros foram
importados e mantidos inativos. O acesso deve ser entregue por canal seguro;
nenhuma senha foi registrada no Git.

**Testes:**
Login HTTP 200 pelo tunel, listagem autenticada dos dois workflows com
`active=false` e confirmacao dos IDs versionados.

**Pendencias:**
Associar credenciais OAuth do Google, configurar IDs das pastas e destinatarios
e somente depois ativar o workflow principal.

**Impacto:**
O painel esta acessivel localmente e pronto para configuracao autorizada das
integracoes, sem exposicao publica da porta 25678.

## 2026-08-26 — Estrutura do Drive de homologação

**Tipo:** INTEGRACAO / CONFIGURACAO
**Status:** PASTAS CRIADAS; AUTORIZACAO OAUTH PENDENTE

**Contexto:**
Foi solicitada a preparação do Drive pessoal para o primeiro teste do MVP.

**Decisão/Ação:**
Criada a pasta principal `Automacao Miller - Homologacao` e as subpastas
Entrada, Processamento, Concluídos, Revisão, Erros, Markdown e Relatórios.
Os IDs foram gravados somente no `.env` protegido da VPS em
`/opt/automacao-miller`; nenhum ID ou segredo foi incluído no Git. O destinatário
de teste foi configurado como `rui.pdiniz@gmail.com`, e as credenciais Google
foram associadas aos nós correspondentes do workflow principal.

**Testes:**
Listagem do Drive confirmou as sete subpastas. O `.env` remoto permaneceu com
permissão 600 e o n8n reiniciou saudável após a configuração.

**Pendências:**
Concluir o consentimento OAuth no n8n, configurar a credencial PostgreSQL,
validar os nós Google e executar o primeiro processamento real.

**Impacto:**
O ambiente de homologação está com a estrutura de armazenamento preparada,
sem ativar o workflow antes da autorização e validação das integrações.

## 10. Regra para o próximo agente

Antes de iniciar qualquer tarefa:

1. ler este arquivo até o final;
2. conferir pendências abertas;
3. conferir decisões ainda não fechadas;
4. consultar `ROADMAP.md`;
5. confirmar requisito no `PRD.md`;
6. seguir `AGENTS.md`;
7. ao terminar, atualizar esta memória.

O agente não deve presumir que uma decisão ainda aberta já foi tomada.

## 2026-09-06 — Landing privada e gateway de upload

**Tipo:** ARQUITETURA / IMPLEMENTAÇÃO
**Status:** IMPLEMENTADO LOCALMENTE; HOMOLOGAÇÃO PENDENTE

**Contexto:**
Foi solicitada uma entrada por navegador para envio de PDFs, acompanhamento por
protocolo e download do relatório final, preservando o n8n como orquestrador.

**Decisão/Ação:**
Criados uma landing responsiva, um gateway FastAPI com tokens separado para
acesso externo e interno, persistência PostgreSQL/volume, idempotência por
SHA-256, endpoints de status/download e workflows n8n de intake e reconciliação.
O Gmail permanece obrigatório além do download na landing.

**Arquivos/Componentes afetados:**
`infra/upload_gateway/`, `tests/upload_gateway/`, `docker-compose.yml`,
`.env.example`, `workflows/automacao-regulatoria-intake-v1.json`,
`workflows/automacao-regulatoria-completion-v1.json`, `PRD.md`, `ROADMAP.md` e
`workflows/README.md`.

**Testes:**
`python -m pytest -q` passou com 22 testes. A validação Docker, importação dos
workflows no n8n, configuração de tokens/Caddy e teste ponta a ponta permanecem
pendentes.

**Pendências:**
Preservar a alteração local existente no Compose da VPS, configurar segredos no
ambiente autorizado, importar/associar credenciais nos workflows e executar os
cenários de Drive, Ollama, relatório e Gmail.

**Impacto:**
A entrada passa a ser assíncrona e rastreável, sem expor credenciais internas;
o PDF original continua no Drive e o relatório só é baixado após status
`concluido`.

## 2026-08-26 - Fechamento do MVP na homologacao

Data: 2026-08-26
Tipo: INTEGRACAO / VALIDACAO / SEGURANCA
Contexto: OAuth do Google, pastas do Drive, credencial PostgreSQL e workflow
de erros estavam configurados na VPS de homologacao.
Decisao/Acao: Corrigidos os parametros de compatibilidade do n8n 2.30.5 para
busca, movimentacao e upload no Drive, multipart do conversor e anexo Gmail.
O fluxo passou a persistir o Markdown antes da IA, reanexar o PDF do renderer
antes do Gmail e decidir o estado somente depois do envio.
Arquivos afetados: workflow principal, compose, contrato de implantacao e
documentacao operacional.
Testes: pytest local com 16 testes; PDF simples concluido com Markdown,
relatorio e e-mail PDF; DOU 2026_08_24_ASSINADO_do1.pdf convertido com 128
paginas e marcadores das paginas 71-75 e 79 conferidos. O DOU gerou relatorio
e e-mail com anexo, mas ficou aguardando_revisao por baixa confianca. O banco
registrou artefatos e nao houve erros persistidos em workflow_errors.
Pendencias: revisao humana do DOU, simulacao dos erros externos, retomada
apos falha, melhoria de inferencia para documentos extensos e rotacao da
senha root exposta.
Impacto: Homologacao funcional para o PDF simples e segura para o DOU,
sem marcar conclusao quando a evidencia/regra de confianca nao permite.

## 2026-08-26 - Verificacao final da stack

Data: 2026-08-26
Tipo: TESTE / OPERACAO
Contexto: Foram feitas novas execucoes depois dos ajustes de roteamento,
escopo de paginas e associacao de credenciais no n8n.
Decisao/Acao: Mantido o DOU em Revisao, com Markdown integral, relatorio PDF
e e-mail com anexo. O PDF simples concluido foi restaurado em Concluidos.
Testes: Execucao final do DOU com confidence_status baixa_confianca,
status aguardando_revisao e movimentacao para Revisao. Duplicidade final
com documento concluido retornou ignored_duplicate sem chamar Ollama.
docker compose ps mostrou os cinco servicos saudaveis; n8n permaneceu
local-only e o workflow ativo com errorWorkflow associado. O healthz do n8n
respondeu; conversor e renderer estavam saudaveis pelo Docker healthcheck.
Pendencias: Os testes de falha externa e retomada ainda precisam de ambiente
controlado. A revisao do DOU continua humana por politica de seguranca.
Impacto: O criterio de nao concluir antes do envio foi preservado; o DOU nao
foi falsamente aceito como classificacao regulatoria definitiva.

## 2026-09-08 — Acesso da landing por usuário e senha

**Tipo:** SEGURANÇA / IMPLEMENTAÇÃO
**Status:** IMPLEMENTADO LOCALMENTE; CONFIGURAÇÃO DA VPS PENDENTE

**Contexto:**
Foi solicitada uma página de acesso para a landing de homologação, que até
então dependia apenas do token privado no link.

**Decisão/Ação:**
Adicionar login por usuário e senha com hash PBKDF2, sessão assinada em cookie
`HttpOnly`, expiração configurável e logout. O token privado existente será
mantido para compatibilidade operacional e testes automatizados. Nenhuma
credencial real será criada ou versionada pelo repositório.

**Arquivos afetados:**
`infra/upload_gateway/`, `tests/upload_gateway/test_api.py`, `.env.example`,
`docker-compose.yml`, `deploy/README.md`, `workflows/README.md`, `PRD.md` e
`ROADMAP.md`.

**Testes:**
Serão executados casos de login válido, credencial inválida, sessão protegida,
logout, expiração e compatibilidade com o token legado.

**Pendências:**
Configurar usuário, hash da senha, segredo de sessão e cookie seguro no `.env`
da VPS; reconstruir o gateway; testar login, upload, acompanhamento e download
pela landing.

**Impacto:**
A interface não dependerá mais de credenciais na URL para o uso normal, sem
remover o mecanismo legado antes da validação completa da homologação.

## 2026-09-08 — Ativação do acesso da landing na VPS

**Tipo:** DEPLOY / SEGURANÇA / TESTE
**Status:** CONCLUÍDO; FLUXO DE DOCUMENTO PENDENTE

**Contexto:**
Após a implementação do login, foram geradas credenciais aleatórias de
homologação e solicitada a ativação no servidor para permitir o teste da
interface.

**Decisão/Ação:**
Preservado o `.env` anterior em backup restrito, configurados usuário, hash
PBKDF2, segredo de sessão, tokens de integração e cookie seguro, atualizado o
checkout da VPS para `de93fb9` e reconstruído o gateway. O hash foi protegido
com aspas simples no `.env` porque contém `$`.

**Arquivos/Componentes afetados:**
`.env` protegido da VPS, backup `.env.before-auth-20260908`, gateway de upload,
n8n e stack Docker de homologação. As credenciais de teste foram salvas apenas
na Área de Trabalho local e no ambiente protegido do servidor.

**Testes:**
HTTPS: login `200`, upload protegido com sessão `200`, logout `200` e acesso
posterior sem sessão `403`. Landing sem sessão retorna a página de login; n8n
retorna readiness `200`; todos os seis serviços permanecem saudáveis.

**Pendências:**
Enviar um PDF autorizado pela landing e validar protocolo, processamento,
relatório, download e os cenários de falha/retomada.

**Impacto:**
A landing agora possui acesso operacional por usuário e senha em HTTPS, sem
expor a senha ou o hash no Git.

## 2026-09-09 — Decisão pelo repositório interno

**Tipo:** ARQUITETURA / DECISÃO DE ESCOPO
**Status:** APROVADO; IMPLEMENTAÇÃO PENDENTE

**Contexto:**
Foi avaliado se o Google Drive deveria continuar sendo responsável pela
organização dos PDFs, Markdown e relatórios. A stack já possui PostgreSQL para
metadados e um volume privado compartilhado entre o gateway e o n8n.

**Decisão/Ação:**
Adotar PostgreSQL como fonte de verdade operacional e volume privado do Docker
como repositório interno dos arquivos. O Google Drive deixa de ser o
armazenamento oficial e poderá permanecer apenas como integração de importação
durante a transição. Os workflows deverão deixar de usar pastas do Drive como
representação principal de estado.

**Arquivos afetados:**
`PRD.md`, `ROADMAP.md`, `LOG.md` e, na próxima implementação, o esquema
PostgreSQL, o gateway, os volumes e os workflows n8n.

**Testes:**
Não aplicável à decisão documental. A implementação deverá validar caso feliz,
duplicidade, falhas intermediárias, retomada, revisão humana e download.

**Pendências:**
Criar o modelo de documentos e artefatos, migrar a persistência dos arquivos,
adaptar os workflows e definir backup conjunto do banco e do volume.

**Impacto:**
O sistema passará a ter uma fonte interna e consultável para organização,
status, auditoria e recuperação, reduzindo a dependência operacional do
Google Drive.

## 2026-09-09 — Implementação do repositório interno landing-only

**Tipo:** ARQUITETURA / IMPLEMENTAÇÃO / MIGRAÇÃO
**Status:** IMPLEMENTADO NO REPOSITÓRIO; ATIVAÇÃO DE HOMOLOGAÇÃO PENDENTE

**Contexto:**
Após a decisão arquitetural, foi definido que a landing privada será a única
origem oficial de novos documentos. O Google Drive não deve permanecer nos
workflows ativos. A migração precisa preservar o volume antigo e permitir
rollback antes da ativação.

**Decisão/Ação:**
Implementado o volume dedicado `automacao_miller_artifacts_data`, montado em
`/data/artifacts`, com objetos organizados por SHA-256. O gateway passou a
persistir uploads atomicamente, registrar documentos e artefatos no PostgreSQL,
deduplicar por hash e liberar download somente após `concluido`. Foram criadas
as tabelas de documentos, artefatos, tentativas, análises, revisões humanas e
erros, além dos workflows internos de processamento, reconciliação e erros.
Também foram criados scripts de migração do volume antigo e backup conjunto do
PostgreSQL e dos artefatos.

**Arquivos afetados:**
`docker-compose.yml`, `.env.example`, `infra/upload_gateway/`,
`deploy/postgres/init/002_internal_repository.sql`, `deploy/backup/`,
`workflows/automacao-regulatoria-internal-v1.json`,
`workflows/automacao-regulatoria-reconcile-v1.json`,
`workflows/automacao-regulatoria-internal-error-v1.json`, testes e documentação.

**Testes:**
Serão executados os testes automatizados do gateway, conversor e contratos dos
workflows, além da validação JSON, `git diff --check` e revisão do diff para
segredos. A validação ponta a ponta depende da VPS de homologação, Ollama,
Gmail e n8n autorizados.

**Pendências:**
Executar backup da VPS, copiar o volume antigo para o novo, aplicar a migração
em banco existente, importar e validar os workflows, simular falhas e somente
então ativar o processamento interno.

**Impacto:**
O PostgreSQL passa a controlar o ciclo de vida do documento e o volume privado
passa a ser o repositório operacional. Pastas e IDs do Drive deixam de
representar estados; arquivos históricos do Drive permanecem preservados.

## 2026-09-09 — Painel operacional e envio manual

**Tipo:** FUNCIONAL / ARQUITETURA / IMPLEMENTAÇÃO
**Status:** IMPLEMENTADO NO REPOSITÓRIO; HOMOLOGAÇÃO PENDENTE

**Contexto:**
Foi definido que o operador deve conferir o relatório antes do envio e escolher
os destinatários pela interface, mantendo a landing como única origem oficial.

**Decisão/Ação:**
Criado painel autenticado com fila, indicadores, detalhe de protocolo, linha do
tempo, histórico, visualização de PDF, Markdown e JSON, revisão humana e tela de
destinatários padrão. O relatório agora permanece em `aguardando_envio` até uma
solicitação manual. Criadas as tabelas `report_recipients`,
`document_recipients` e `email_deliveries`, as rotas de operação e o workflow
n8n separado para reivindicar a entrega e enviar pelo Gmail. O download oficial
continua bloqueado até o status `concluido`.

**Arquivos afetados:**
`infra/upload_gateway/app.py`, `infra/upload_gateway/static/`,
`deploy/postgres/init/003_panel_operations.sql`, `docker-compose.yml`,
`.env.example`, `workflows/`, `tests/`, `PRD.md`, `ROADMAP.md`,
`README.md`, `workflows/README.md` e `deploy/README.md`.

**Testes:**
Testes de contrato e API cobrem autenticação, fila, artefatos, duplicidade de
destinatários, envio concorrente e revisão. A validação real do PostgreSQL,
n8n e Gmail ainda depende da homologação autorizada.

**Pendências:**
Aplicar a migração 003, importar o workflow de envio, migrar destinatários,
fazer backup conjunto e validar envio, falha, retry e download ponta a ponta.

**Impacto:**
O envio passa a ser uma decisão operacional auditável. O painel exibe os
artefatos internos sem expor caminhos do volume e o Gmail deixa de determinar
sozinho o fluxo de novos documentos.

## 2026-09-09 — Publicação em homologação da VPS

**Tipo:** DEPLOY / HOMOLOGAÇÃO
**Status:** PUBLICADO; TESTE PONTA A PONTA PENDENTE

**Contexto:**
O branch `feat/landing-upload` foi integrado em `main` e a atualização foi
solicitada para teste na VPS de homologação.

**Decisão/Ação:**
`main` foi publicado no GitHub. Na VPS, o checkout foi atualizado para o commit
`5263c50` do painel e depois para os ajustes de migração subsequentes. Foi feito
backup conjunto do PostgreSQL e do volume, o volume legado foi copiado para o
repositório interno, as migrações do schema foram aplicadas, os serviços foram
reconstruídos e os quatro workflows internos foram importados como inativos.

**Testes:**
Todos os serviços Docker ficaram saudáveis, o gateway respondeu `200` no
health check e as tabelas `report_recipients`, `document_recipients` e
`email_deliveries` foram confirmadas no PostgreSQL. O backup gerou manifestos
no diretório protegido da VPS.

**Pendências:**
Associar as credenciais PostgreSQL e Gmail aos workflows importados, migrar os
destinatários atuais para a tela, executar upload real, revisar artefatos,
enviar pelo Gmail e confirmar o download após `concluido`. Os workflows foram
mantidos inativos até essa validação.

**Impacto:**
A versão merged está disponível na VPS sem apagar o volume antigo ou os
arquivos históricos do Drive. A ativação permanece controlada para evitar
processamento sem credenciais e sem validação operacional.

## 2026-09-09 — Correção do contexto de armazenamento no workflow interno

**Tipo:** BUG / WORKFLOW / HOMOLOGAÇÃO
**Status:** CORRIGIDO NO REPOSITÓRIO; REPUBLICAÇÃO E RETESTE PENDENTES

**Contexto:**
O primeiro upload pela API autenticada alcançou o workflow interno e criou a
tentativa no PostgreSQL, mas a leitura do PDF falhou porque o nó de registro da
tentativa não devolve os campos do documento ao próximo nó.

**Decisão/Ação:**
O nó de leitura passou a obter `source_storage_key` diretamente do `Claim guard`,
preservando o contexto original entre a auditoria no PostgreSQL e a leitura do
volume privado. Foi adicionada uma asserção de contrato para impedir a regressão.

**Arquivos afetados:**
`workflows/automacao-regulatoria-internal-v1.json` e
`tests/contracts/test_deployment_contract.py`.

**Testes:**
`python -m pytest -q` passou com 37 testes; exports JSON e `git diff --check`
foram validados. A execução na VPS confirmou o erro original em
`Internal Storage - Read PDF` com `/data/artifacts/undefined`.

**Pendências:**
Republicar o workflow corrigido na VPS, reprocessar o documento de homologação e
validar conversão, Ollama, relatório, revisão, envio manual e download.

**Impacto:**
O workflow deixa de depender da saída vazia do nó de auditoria para localizar o
PDF original.

## 2026-09-09 — Correção da reconciliação de protocolos pendentes

**Tipo:** BUG / WORKFLOW / HOMOLOGAÇÃO
**Status:** CORRIGIDO NO REPOSITÓRIO; REPUBLICAÇÃO E RETESTE PENDENTES

**Contexto:**
Durante a retomada do documento de homologação, a reconciliação executava várias
sentenças SQL no mesmo nó e o n8n não entregava o resultado final ao nó HTTP.
Isso causava chamadas internas sem `submission_id` e tentativas inválidas.

**Decisão/Ação:**
A consulta foi consolidada em CTEs com um `SELECT` final único, mantendo a
recuperação de entregas e documentos presos e garantindo que cada item enviado
ao webhook contenha o protocolo. Foi adicionada uma asserção de contrato.

**Arquivos afetados:**
`workflows/automacao-regulatoria-reconcile-v1.json` e
`tests/contracts/test_deployment_contract.py`.

**Testes:**
`python -m pytest -q` passou com 38 testes e os exports JSON foram validados.
Na VPS, os logs confirmaram o sintoma anterior: chamadas de reconciliação
chegavam ao fluxo interno sem protocolo.

**Pendências:**
Republicar a reconciliação, reativá-la após o teste manual e concluir o fluxo
ponta a ponta com revisão, envio Gmail e download.

**Impacto:**
A reconciliação passa a produzir uma fila explícita de protocolos e deixa de
disparar execuções inválidas.

## 2026-09-09 — Proteção contra itens vazios no claim interno

**Tipo:** BUG / WORKFLOW / HOMOLOGAÇÃO
**Status:** CORRIGIDO NO REPOSITÓRIO; REPUBLICAÇÃO E RETESTE PENDENTES

**Contexto:**
O nó PostgreSQL pode devolver um item JSON vazio quando nenhum documento é
reivindicado. O `Claim guard` aceitava esse item e o nó seguinte tentava criar
uma tentativa com `submission_id` nulo.

**Decisão/Ação:**
O guard passou a filtrar explicitamente itens sem `submission_id`, impedindo
execuções inválidas e preservando a idempotência do processamento.

**Arquivos afetados:**
`workflows/automacao-regulatoria-internal-v1.json` e
`tests/contracts/test_deployment_contract.py`.

**Testes:**
`python -m pytest -q` passou com 38 testes; exports JSON e `git diff --check`
foram validados.

**Pendências:**
Republicar esta proteção na VPS, confirmar que a reconciliação não gera novas
execuções inválidas e concluir a validação do documento de homologação.

**Impacto:**
Chamadas repetidas, documentos já reivindicados e consultas sem resultado não
criam tentativas órfãs nem erros de chave estrangeira.

## 2026-09-09 — Liberação do volume privado para os nós de arquivo do n8n

Data: 2026-09-09
Tipo: Correção de homologação
Contexto: A execução interna já resolvia a chave relativa correta, mas o n8n recusava `/data/artifacts` por manter o diretório padrão `/home/node/.n8n-files` como único caminho permitido.
Decisão/Ação: Configurar `N8N_RESTRICT_FILE_ACCESS_TO=/data/artifacts` no serviço n8n e documentar a dependência entre essa variável e o volume privado.
Arquivos afetados: `docker-compose.yml`, `.env.example`, `deploy/README.md`, `workflows/README.md` e contrato de implantação.
Testes: A executar após recriação do serviço n8n na VPS e nova execução ponta a ponta.
Pendências: Retomar o processamento do PDF sintético de homologação e validar artefatos, envio manual e download.
Impacto: Permite que os nós de leitura e escrita de arquivos usem o repositório interno sem expor caminhos ao navegador.

## 2026-09-09 — Correção de contexto e tamanho dos artefatos internos

Data: 2026-09-09
Tipo: Correção de homologação
Contexto: Com o acesso ao volume liberado, o processamento chegou à persistência dos artefatos. O registro do Markdown ainda usava dados de um nó anterior e o tamanho do PDF renderizado chegava como texto formatado, causando chave `undefined` e valor `NaN` no PostgreSQL.
Decisão/Ação: Fazer o registro do Markdown consultar o nó que cria as chaves internas e calcular o tamanho do relatório a partir do buffer binário antes da persistência.
Arquivos afetados: `workflows/automacao-regulatoria-internal-v1.json` e `tests/contracts/test_deployment_contract.py`.
Testes: A executar localmente e na VPS após republicação do workflow.
Pendências: Confirmar processamento completo, envio manual pelo Gmail, download e cenários de falha/retomada.
Impacto: O pipeline passa a registrar chaves e tamanhos numéricos consistentes para Markdown, análise e relatório.

## 2026-09-09 — Correção do tamanho do artefato de análise

Data: 2026-09-09
Tipo: Correção de homologação
Contexto: A análise era gravada corretamente no volume, mas o registro PostgreSQL consultava um nó anterior à criação de `analysis_size_bytes`, deixando o tamanho como zero.
Decisão/Ação: Ajustar a persistência para usar o contexto do nó `Prepare analysis file`, que contém a chave e o tamanho calculados do JSON.
Arquivos afetados: `workflows/automacao-regulatoria-internal-v1.json` e `tests/contracts/test_deployment_contract.py`.
Testes: A executar localmente e na VPS após republicação.
Pendências: Retestar o documento, concluir envio Gmail, download e recuperação.
Impacto: O catálogo de artefatos passa a registrar o tamanho real do JSON de análise.
