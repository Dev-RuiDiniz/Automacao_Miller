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

### Estado consolidado verificado em 26/10/2026

- **Produto:** automação interna para receber PDFs regulatórios pela landing, gerar Markdown paginado, analisar com Ollama local, criar relatório Markdown/PDF e permitir envio manual.
- **Stack no repositório:** n8n, PostgreSQL, Ollama, gateway, conversor PDF, renderizador e volume privado Docker. RAG é opcional/legado e não está no caminho ativo.
- **VPS:** commit 38f5358 da main; seis containers do Miller saudáveis. O n8n 2.30.5 está preso ao loopback; Ollama 0.32.1 usa qwen2.5:3b.
- **Workflows publicados:** processamento interno e erro ativos; envio manual, reconciliação e avaliação NVIDIA sintética inativos.
- **Operação:** 3 documentos em aguardando_envio, 6 em erro e nenhum em processamento. A conta proprietária do n8n não tem e-mail/senha definidos.
- **Segurança e recuperação:** a senha root exposta e a chave NVIDIA exposta ainda precisam de rotação/revogação; o diretório de backup esperado não existe; a landing não tem entrada HTTPS publicada.
- **VPS compartilhada:** o outro projeto Docker observado é ideia-saude-agent-test. As stacks BRANDRIOT Socialsuite e Supabase Socialsuite foram removidas em 26/10/2026.

Os tópicos seguintes desta seção descrevem a proposta e a linha de base histórica. Para estado operacional e trabalho pendente, use ROADMAP.md; para requisitos, use PRD.md.

### Produto

Solução automatizada para processamento e análise de documentos regulatórios em PDF.

### Objetivo

Substituir processo manual e repetitivo por fluxo automatizado, rastreável e de baixo custo operacional.

### Stack definida na linha de base inicial (histórico)

- n8n;
- Ollama;
- Google Drive;
- Gmail;
- Docker;
- Linux em VPS.

### Arquitetura aprovada para evolução na linha de base inicial (histórico)

- PostgreSQL como fonte de verdade operacional;
- volume privado do Docker para PDFs, Markdown e relatórios;
- Google Drive apenas para importação temporária durante a transição;
- Gmail para envio;
- n8n para orquestração;
- Ollama para análise local.

Essa arquitetura ainda não está implementada nos workflows versionados. A
homologação vigente registrada nos eventos históricos continua usando o Drive.

### Fluxo de referência inicial (histórico)

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

### Capacidades previstas na linha de base inicial (histórico)

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

## 5. Pendências iniciais — snapshot histórico de 2026-08-25

> Esta tabela registra a situação inicial, não a situação atual. Consulte ROADMAP.md para as pendências vigentes.

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

## 6. Decisões que ainda precisavam ser fechadas na linha de base inicial

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

## 2026-09-09 — Homologação ponta a ponta aprovada

**Tipo:** HOMOLOGAÇÃO / OPERACIONAL / GMAIL
**Status:** CONCLUÍDO EM HOMOLOGAÇÃO

**Contexto:** Após as correções de contexto dos nós n8n e da permissão de acesso
ao volume privado, foi executado o fluxo completo pela landing e pelo painel
operacional na VPS.

**Decisão/Ação:** Validar o repositório interno como fonte operacional para o
PDF original, Markdown, análise JSON e relatório PDF. O envio manual foi
executado pelo Gmail com destinatário homologado; o download oficial só foi
liberado depois do status `concluido`.

**Arquivos afetados:** `ROADMAP.md`, `LOG.md` e registros operacionais da VPS.

**Testes:** Upload válido e deduplicação; visualização dos três artefatos;
revisão humana; PDF inválido rejeitado; dois webhooks repetidos com apenas uma
reivindicação; duas solicitações de envio simultâneas com uma aceita e outra
bloqueada; falha de credencial Gmail registrada; retry e envio real concluídos;
download oficial retornando PDF após `concluido`. O backup conjunto teve
manifesto, hashes, permissões e leitura isolada do dump/arquivo compactado
conferidos.

**Pendências:** Hardening do acesso administrativo da VPS, aceite formal do
operador e procedimento de restauração em janela de manutenção antes da
ativação produtiva.

**Impacto:** A homologação demonstra operação sem dependência do Google Drive
nos workflows ativos. Os workflows históricos do Drive permanecem inativos.

## 2026-09-09 — Correção do manifesto do backup conjunto

**Tipo:** BUG / BACKUP
**Status:** CORRIGIDO

**Contexto:** O manifesto registrava o nome do banco como `8` porque a limpeza
de quebras de linha removia também os caracteres `n` do valor `n8n`.

**Decisão/Ação:** Corrigir a expressão de limpeza em `deploy/backup/backup.sh`
para remover somente `CR` e `LF`.

**Arquivos afetados:** `deploy/backup/backup.sh`.

**Testes:** O dump e o arquivo compactado do backup anterior foram validados
com SHA-256, `pg_restore --list` e listagem do arquivo compactado. Após a
publicação, o backup final `20260909T202426Z` foi gerado com banco `n8n`,
volume `automacao_miller_artifacts_data`, hashes válidos e manifesto protegido.

**Pendências:** Nenhuma para a rotina de backup da homologação. A restauração
produtiva deve ocorrer em janela de manutenção previamente aprovada.

**Impacto:** O manifesto passa a identificar corretamente o banco PostgreSQL
sem alterar os dados do backup.

## 2026-09-09 — Ajuste para documentos extensos no Ollama

**Tipo:** BUG / IA / HOMOLOGAÇÃO
**Status:** CORRIGIDO; RETESTE EM EXECUÇÃO

**Contexto:** O PDF `2026_08_24_ASSINADO_do1.pdf`, com 128 páginas e
24.053.052 bytes, foi recebido e convertido para Markdown com 1.585.605 bytes.
Na primeira análise, o Ollama devolveu somente uma resposta parcial de 134
caracteres, que não era JSON válido, e a tentativa ficou registrada como erro.

**Decisão/Ação:** Limitar o contexto enviado ao Ollama a 18.000 caracteres,
preservando as páginas de referência e um aviso para revisão humana; definir
`num_predict=2048`; remover cercas Markdown antes da validação JSON; e aplicar
bit setgid nos diretórios do volume para manter o grupo compartilhado entre n8n
e gateway.

**Arquivos afetados:** `workflows/automacao-regulatoria-internal-v1.json`,
`infra/upload_gateway/entrypoint.sh`, `docker-compose.yml` e
`tests/contracts/test_deployment_contract.py`.

**Testes:** 38 testes locais aprovados antes do reteste; a falha original foi
reproduzida na execução 5756 e classificada na etapa `Normalize AI response`.

**Pendências:** Republicar os ajustes na VPS e confirmar a geração do relatório
com o documento real.

**Impacto:** Documentos extensos deixam de exceder silenciosamente o contexto
do modelo; quando a evidência for reduzida, o resultado continuará sinalizado
para revisão humana.

## 2026-09-09 — Homologação do documento real de 128 páginas

**Tipo:** HOMOLOGAÇÃO / IA / RELATÓRIO
**Status:** CONCLUÍDO COM REVISÃO HUMANA PENDENTE

**Contexto:** Foi processado o arquivo `2026_08_24_ASSINADO_do1.pdf`, recebido
da landing, com 24.053.052 bytes e SHA-256
`3ad26053af9898a8bfa7de5ae3a409313ab9230ed28079f1794c82238797e9b6`.

**Decisão/Ação:** A conversão gerou Markdown de 1.585.605 bytes e 128 páginas.
Após o ajuste de contexto e schema do Ollama, o fluxo persistiu análise JSON de
3.464 bytes e relatório PDF de 4.027 bytes no volume privado. A resposta passou
pela validação estrutural, mas foi classificada como `baixa_confianca` por
ocorrências sem referência de página; o documento foi colocado em
`aguardando_revisao` e o envio manual permanece bloqueado até a revisão.

**Arquivos afetados:** `workflows/automacao-regulatoria-internal-v1.json`,
`tests/contracts/test_deployment_contract.py`, `LOG.md` e `ROADMAP.md`.

**Testes:** Original, Markdown, análise JSON e relatório foram acessados pelas
rotas autenticadas. O relatório abriu corretamente em 2 páginas e o download
oficial retornou HTTP 409 antes da conclusão, conforme a regra de segurança.
O primeiro erro de JSON parcial foi reproduzido e corrigido antes do reteste.

**Pendências:** Revisar as classificações e referências de página do documento
real antes de liberar o relatório para envio. A inferência completa de DOU
extenso continua como melhoria de qualidade do modelo.

**Impacto:** O fluxo interno está operacional para o documento real, com
artefatos persistidos e trilha de revisão. O resultado não é tratado como
concluído automaticamente quando a evidência extraída é insuficiente.

## 2026-09-10 — Relatório executivo com linguagem comercial

**Tipo:** EVOLUÇÃO / RELATÓRIO / UX
**Status:** IMPLEMENTADO

**Contexto:** O relatório anterior apresentava principalmente o conteúdo do JSON
em seções técnicas, dificultando a leitura por operadores e áreas comerciais.

**Decisão/Ação:** Atualizar o renderer para abrir o PDF com resumo executivo,
indicadores de achados e atenção, explicação das implicações práticas, achados
detalhados com rótulos legíveis, evidências por página, controle de confiança e
próximos passos. A redação permanece documental e não cria conclusões que não
estejam sustentadas pelo conteúdo recebido.

**Arquivos afetados:** `infra/report_renderer/app.py`,
`tests/report_renderer/test_renderer.py`, `PRD.md`, `ROADMAP.md` e
`workflows/README.md`.

**Testes:** Testes do renderer aprovados e PDF de amostra renderizado com
inspeção visual, paginação, rodapé e hierarquia tipográfica conferidos.

**Pendências:** Publicar o renderer atualizado na VPS e regenerar o relatório
do documento real para validação final da nova linguagem.

**Impacto:** O operador passa a entender rapidamente o que foi encontrado, o
que merece atenção e qual ação deve ocorrer antes do envio, mantendo o JSON e o
Markdown como evidências auditáveis.

## 2026-09-10 — Páginas de origem obrigatórias no relatório

**Tipo:** AJUSTE / RASTREABILIDADE / RELATÓRIO
**Status:** IMPLEMENTADO

**Contexto:** Alguns achados gerados pela IA não traziam a página de origem no
JSON, dificultando a conferência comercial e operacional no documento original.

**Decisão/Ação:** Tornar `paginas_origem` obrigatório na orientação do Ollama e
exibir sempre a linha `Páginas de origem` em cada achado. O resumo do relatório
também passa a informar o recorte de páginas analisado. Quando a referência não
for comprovada, o PDF informa a pendência e mantém a necessidade de revisão, sem
inventar a página.

**Arquivos afetados:** `infra/report_renderer/app.py`,
`workflows/automacao-regulatoria-internal-v1.json`,
`tests/report_renderer/test_renderer.py`,
`tests/contracts/test_deployment_contract.py`, `PRD.md`, `ROADMAP.md` e
`workflows/README.md`.

**Testes:** Testes do renderer e contratos do workflow cobrem página informada,
página ausente e recorte de análise. A inspeção visual continua prevista após
regenerar o PDF na VPS.

**Pendências:** Publicar o renderer e o workflow atualizados na VPS quando o
arquivo de credenciais de homologação estiver disponível.

**Impacto:** O usuário consegue localizar cada achado no PDF original ou vê
claramente que a referência precisa ser confirmada antes do envio.

## 2026-09-10 — RAG híbrido e hardening de citações

**Tipo:** ARQUITETURA / IA / QUALIDADE / TREINAMENTO
**Status:** IMPLEMENTADO LOCALMENTE; HOMOLOGAÇÃO PENDENTE

**Contexto:** A análise do documento extenso precisa recuperar contexto sem
misturar protocolos e precisa tornar cada afirmação auditável por página e
trecho. O treinamento deve começar com correções humanas verificáveis.

**Decisão/Ação:** PostgreSQL passou a usar `pgvector`. Foi criado o serviço
interno de chunks por página, embeddings `nomic-embed-text`, busca textual e
vetorial combinadas, auditoria de recuperação e validação de qualidade. O
workflow interno indexa e consulta antes do Ollama. Revisões aprovadas podem
armazenar payload corrigido e o exportador gera JSONL somente para exemplos
elegíveis, com treino e validação separados. Fine-tuning continua externo e
condicionado às métricas mínimas.

**Regras aplicadas:** páginas devem existir no documento atual; a evidência deve
ser localizada após normalização de espaços e acentuação; status inválido,
cancelamento misturado a indeferimento, dispositivo classificado como produto,
campo JSON inesperado e citação ausente exigem revisão. Falhas de qualidade
geram aviso e rascunho; falhas técnicas seguem como erro do workflow.

**Arquivos afetados:** `docker-compose.yml`, `deploy/postgres/init/004_rag_and_training.sql`,
`infra/rag/`, `infra/regulatory_analysis/quality.py`, `infra/regulatory_analysis/dataset.py`,
`infra/regulatory_analysis/evaluation.py`, `scripts/export_training_dataset.py`,
workflow interno, prompts, testes e documentação operacional.

**Testes:** Foram adicionados testes para divisão por página, hash e overlap,
status e citações, isolamento do documento, dispositivos, cancelamento,
campos extras e elegibilidade do dataset. A regressão completa ainda será
executada antes do commit.

**Pendências:** aplicar a migração na homologação após backup, baixar o modelo
de embeddings, indexar os Markdowns existentes, comparar o documento real e
executar os testes de falha/recuperação. Nenhum documento ou segredo foi
adicionado ao Git.

## 2026-09-10 — Coletor do DOU e pacote de relatórios

**Tipo:** DADOS / RAG / RELATÓRIO / OPERAÇÃO
**Status:** IMPLEMENTADO; COLETA REAL PENDENTE DE CREDENCIAL

**Contexto:** Foi solicitado ampliar a base de referência com as edições
completas do DOU dos últimos 30 dias e entregar relatórios baixáveis sem
versionar os PDFs oficiais.

**Decisão/Ação:** Criados coletor autenticado do INLABS, manifesto com status,
seção, data, tamanho e SHA-256, retomada por arquivo válido e registro de
ausências/erros. Criada preparação de staging que converte PDFs, preserva
páginas e cria fila de revisão; candidatos opcionais do Ollama continuam fora
do dataset até aprovação humana. Criado empacotador com Markdown consolidado,
cinco PDFs semanais, manifesto público, checksums e ZIP sem PDFs brutos.

**Validação:** O dry-run de 12/08/2026 a 10/09/2026 produziu 270 itens
planejados e o ZIP de teste passou na verificação de integridade.

**Arquivos afetados:** `infra/dou/`, `scripts/download_dou_corpus.py`,
`scripts/prepare_dou_review_queue.py`, `scripts/build_dou_report_package.py`,
`.env.example`, `.gitignore`, documentação e testes de coleta/empacotamento.

**Pendências:** Não executar download real sem credenciais autorizadas do
INLABS. Depois da configuração, executar a coleta em staging protegido,
revisar os candidatos e exportar somente exemplos aprovados.

## 2026-09-15 — Auditoria completa e relatório executivo

**Tipo:** DOCUMENTAÇÃO / AUDITORIA
**Status:** CONCLUÍDO

**Contexto:** Foi solicitada uma visão única, técnica e comercial do projeto,
com funcionamento, fluxos, funções, rotas, riscos, pendências e evidências de
validação.

**Decisão/Ação:** Criado RELATORIO_AUDITORIA_PROJETO.md na raiz, com a
arquitetura atual landing-only, o histórico do Google Drive, os workflows,
interfaces HTTP, modelo de dados, segurança, operação, matriz de aderência ao
PRD e recomendações P0/P1/P2. O README.md passou a apontar para o relatório e
o ROADMAP.md recebeu o marco documental correspondente.

**Arquivos afetados:** RELATORIO_AUDITORIA_PROJETO.md, README.md, ROADMAP.md e
LOG.md.

**Testes:** python -m pytest -q passou com 53 testes e 2 avisos de depreciação
do FastAPI; os oito exports JSON foram validados; git diff --check passou; a
busca não encontrou credenciais reais. O Docker não está disponível na estação
local, portanto docker compose config --quiet não pôde ser executado localmente.
A validação remota histórica está descrita separadamente no relatório.

**Pendências:** Permanecem os gates de produção já registrados: hardening da
VPS, rotação/validação de acesso administrativo, revisão humana do DOU real,
migração/indexação RAG, matriz de falhas e retomada, procedimento de restauração
e aceite formal do operador.

**Impacto:** O projeto passa a ter um documento único para apresentação
comercial, onboarding técnico, operação e auditoria, sem alterar requisitos do
PRD nem expor segredos.

## 2026-09-15 — Evolução do prompt para análise técnica preliminar v2

**Tipo:** EVOLUÇÃO / IA / PROMPT / QUALIDADE
**Status:** IMPLEMENTADO LOCALMENTE; HOMOLOGAÇÃO DO MODELO PENDENTE

**Contexto:** O prompt v1 priorizava extração e classificação. Foi solicitada
uma postura mais próxima de um analista regulatório especialista, com parecer
preliminar e apontamentos técnicos úteis para operação e negócio.

**Decisão/Ação:** Criados o prompt e o schema v2, com separação entre fato
documentado e interpretação técnica, conclusão preliminar, classificação geral,
nível de risco prudente, fundamentos citados, apontamentos técnicos,
recomendações priorizadas, IDs de rastreabilidade e limites da análise. O
workflow interno passou a construir o prompt v2, exigir `parecer_tecnico`,
classificar risco alto/crítico para revisão humana e registrar a nova versão no
PostgreSQL. O renderer passou a apresentar as novas seções no PDF. O coletor
DOU foi alinhado ao mesmo contrato.

**Arquivos afetados:** `prompts/regulatory-extraction-v2.md`,
`prompts/regulatory-extraction-v2.schema.json`,
`workflows/automacao-regulatoria-internal-v1.json`,
`infra/report_renderer/app.py`, `infra/regulatory_analysis/quality.py`,
`infra/regulatory_analysis/confidence.py`, `infra/dou/package.py`,
`scripts/prepare_dou_review_queue.py`, testes e documentação.

**Testes:** Schema v2 e workflow JSON validados; `python -m pytest -q` passou
com 57 testes e 2 avisos de depreciação do FastAPI; os dez arquivos JSON foram
validados; `git diff --check` passou; a busca não encontrou segredos de alta
confiança. O Docker não está disponível na estação local, portanto
`docker compose config --quiet` não foi executado.

**Pendências:** Comparar v2 contra documentos de referência, medir cobertura de
citações, observar tempo/tamanho da resposta do `qwen2.5:3b` e revisar
humanamente o documento real de 128 páginas. A saída continua preliminar e não
constitui parecer jurídico, médico ou regulatório definitivo.

**Impacto:** O relatório passa a responder não apenas “o que foi encontrado”,
mas também “qual é a leitura técnica preliminar”, “qual o risco aparente” e
“qual o próximo passo recomendado”, mantendo evidências, limites e aprovação
humana como controles obrigatórios.

## 2026-09-15 — Evolução visual do documento final PDF v1.3.0

**Tipo:** EVOLUÇÃO / RELATÓRIO / PDF / UX
**Status:** IMPLEMENTADO LOCALMENTE; PUBLICAÇÃO NA VPS PENDENTE

**Contexto:** O conteúdo do relatório já apresentava síntese executiva e parecer
técnico, mas precisava de uma experiência mais comercial, profissional e rápida
para gestores, operadores e clientes.

**Decisão/Ação:** O renderer recebeu identidade visual da DB Tecnologia, capa
executiva, status de conferência, metadados organizados, indicadores, parecer
técnico em bloco próprio, cartões de achados, fundamentos, recomendações,
próximos passos, cabeçalho/rodapé e aviso de responsabilidade. A versão do
renderer foi atualizada para `1.3.0`. As regras de evidência, confiança, revisão
humana, rastreabilidade e liberação do relatório não foram alteradas.

**Arquivos afetados:** `infra/report_renderer/app.py`,
`tests/report_renderer/test_renderer.py`, `README.md`,
`RELATORIO_AUDITORIA_PROJETO.md`, `ROADMAP.md` e `LOG.md`.

**Testes:** `python -m pytest -q` passou com 57 testes e 2 avisos de
depreciação do FastAPI; `python -m compileall -q infra/report_renderer` passou;
os dez arquivos JSON foram validados; `git diff --check` passou; a busca por
formatos fortes de credenciais não encontrou segredos. O PDF de amostra foi
renderizado em três páginas com PyMuPDF porque `pdftoppm` não está disponível na
estação. As páginas foram inspecionadas visualmente e não apresentaram cortes,
sobreposição ou quebra de hierarquia. O Docker não está disponível na estação,
portanto `docker compose config --quiet` não pôde ser executado localmente.

**Pendências:** Publicar o renderer na VPS e regenerar/revisar o documento real
de 128 páginas. A validação local não substitui a conferência humana do corpus
real nem a homologação no ambiente autorizado.

**Impacto:** O relatório passa a funcionar melhor como documento de decisão e
acompanhamento, mantendo linguagem executiva sem transformar a análise
automatizada em parecer regulatório definitivo.

## 2026-09-15 — Relatório técnico automático sem gate de revisão humana

**Tipo:** DECISÃO / ESCOPO / IA / WORKFLOW
**Status:** REQUISITO ATUALIZADO; IMPLEMENTADO LOCALMENTE; PUBLICAÇÃO NA VPS PENDENTE

**Contexto:** Foi solicitado que o resultado não dependesse de revisão humana
para ser entregue. A equipe deve receber um relatório técnico automatizado com
padrão de análise sênior e consultar as páginas indicadas apenas quando desejar
confirmar algum ponto.

**Decisão/Ação:** O PRD foi atualizado para tornar a conferência humana
opcional. Confiança, contradições, riscos, limitações e páginas continuam sendo
calculados e exibidos, mas deixam de ser gate de conclusão ou envio. Falhas
técnicas de entrada, conversão, IA, armazenamento ou entrega continuam sendo
interrompidas e registradas. A revisão existente permanece disponível para
correção e treinamento, sem bloquear a operação normal.

**Arquivos/Componentes afetados:** `PRD.md`, `ROADMAP.md`, `LOG.md`,
`prompts/regulatory-extraction-v3.md`, `workflows/automacao-regulatoria-internal-v1.json`,
`workflows/README.md`, `infra/report_renderer/app.py`,
`infra/upload_gateway/static/`, testes e relatório de auditoria.

**Testes:** `python -m pytest -q` passou com 59 testes e 2 avisos de depreciação
do FastAPI; `python -m compileall -q infra` passou; 14 arquivos JSON foram
validados; `git diff --check` passou; a varredura por formatos fortes de
credenciais permaneceu limpa. O PDF de amostra foi renderizado em três páginas
com PyMuPDF e inspecionado visualmente sem cortes ou sobreposição. O Docker não
está disponível na estação, portanto `docker compose config --quiet` não pôde
ser executado localmente.

**Pendências:** Publicar o prompt e workflow atualizados na VPS, reprocessar o
documento real de 128 páginas e observar qualidade, cobertura de citações,
truncamento e taxa de correção operacional. A conferência humana do resultado
real permanece opcional, não sendo requisito para entrega.

**Impacto:** O tempo até a entrega do relatório é reduzido e a equipe pode agir
com base na síntese técnica, mantendo uma trilha clara para confirmar a fonte
original sem apresentar a IA como autoridade regulatória humana.

## 2026-09-15 — Atualização controlada da VPS e pausa operacional do DOU

**Tipo:** DEPLOY / HOMOLOGAÇÃO / RAG / INFRAESTRUTURA
**Status:** VPS ATUALIZADA; TESTE PEQUENO APROVADO; DOU EM PROCESSAMENTO

**Contexto:** A VPS foi atualizada a partir de `ff8c5ba` até a linha atual da
`main`, preservando banco, volume de artefatos, credenciais internas e os quatro
workflows operacionais. A janela foi encerrada antes da conclusão do segundo
documento, a pedido do operador.

**Decisão/Ação:** Foi executado backup conjunto com manifesto, SHA-256,
`pg_restore --list` e `tar -tzf`. A migração `004_rag_and_training.sql` foi
aplicada uma única vez. O modelo `nomic-embed-text` foi instalado e validado ao
lado de `qwen2.5:3b` e `qwen2.5:1.5b`. O workflow interno v3 foi reimportado
inativo com sete vínculos de credenciais preservados por workflow/node ID e
reativado junto dos workflows de envio, reconciliação e erros. Os exports
históricos do Google Drive permaneceram inativos.

**Arquivos/ambiente afetados:** `docker-compose.yml`, `.env.example`,
`workflows/automacao-regulatoria-internal-v1.json` e a configuração operacional
da VPS. O timeout do Ollama passou a ser configurado em segundos e convertido
explicitamente para milissegundos; na VPS ficou definido em 3600 segundos.

**Testes:** O PDF pequeno `automacao-miller-homologacao-2.pdf` completou o
ciclo, teve artefatos de Markdown, análise e PDF, envio real ao destinatário de
homologação, estado `concluido` e download oficial HTTP 200. No DOU
`2026_08_24_ASSINADO_do1.pdf`, a tentativa 23 persistiu 255 chunks e 8
recuperações RAG, mas falhou depois da indexação porque o Ollama encerrou a
geração antes de concluir o JSON (`done=false`). Essa falha foi registrada como
erro de IA. A tentativa 24 foi autorizada operacionalmente e estava em
`em_processamento/markdown_persistido` ao encerrar o expediente; seu resultado
final ainda não é evidência de aprovação.

**Pendências:** Acompanhar a tentativa 24; confirmar `prompt_version` v3,
`quality_checks`, relatório com parecer e páginas, envio, estado `concluido` e
download oficial do DOU. Executar a suíte completa local após a última correção,
revisar o diff documental e manter o hardening SSH da VPS como atividade
separada. Nenhum segredo foi adicionado ao versionamento.

**Impacto:** A operação pequena está validada ponta a ponta e a infraestrutura
RAG está aplicada. O documento extenso continua sendo o principal gate técnico
de desempenho e confiabilidade da homologação; falhas técnicas permanecem
explícitas e não são convertidas em ausência de informação.

## 2026-09-16 — Recuperação do acesso administrativo do n8n

**Tipo:** SEGURANÇA / OPERAÇÃO / ACESSO
**Status:** CONCLUÍDO

**Contexto:** O acesso da conta proprietária do n8n não estava disponível para
o operador. Foi utilizado o comando oficial `user-management:reset` e criada
uma nova conta proprietária pela tela de configuração local do n8n.

**Decisão/Ação:** O painel foi acessado e a lista de workflows foi carregada
com sucesso. Workflows, credenciais de integração e dados operacionais foram
preservados no volume do n8n. Os dados do novo acesso foram salvos apenas no
arquivo local `N8N_ACESSO_LOCAL.txt`, protegido pelo ignore local do Git; nenhum
segredo foi incluído neste registro, no repositório ou no GitHub.

**Testes:** A tela inicial de configuração concluiu sem erro e o painel
`/home/workflows` exibiu os workflows da instância autenticada.

**Pendências:** Rotacionar novamente o acesso caso o arquivo local seja
compartilhado ou perdido e concluir o hardening SSH da VPS em atividade
separada.

## 2026-09-16 — Simplificação do pipeline de relatório

**Tipo:** DECISÃO / ARQUITETURA / PERFORMANCE
**Status:** IMPLEMENTADO LOCALMENTE; PUBLICAÇÃO E VALIDAÇÃO REMOTA PENDENTES

**Contexto:** O processamento do DOU extenso permaneceu lento e a geração JSON
do modelo local falhou por truncamento de contexto. Foi solicitada uma solução
mais direta, sem revisão humana como pré-requisito operacional.

**Decisão/Ação:** O workflow interno foi reduzido para PDF → Markdown → prompt
do especialista → relatório Markdown → PDF. O prompt `regulatory-extraction-v3`
produz somente Markdown, com linguagem técnica sênior, parecer, apontamentos,
recomendações, limitações e referências de páginas. O relatório Markdown é
persistido como `report_markdown` antes da renderização do PDF. RAG, embeddings,
JSON estruturado e `quality_checks` foram retirados do caminho crítico, mas os
componentes permanecem versionados para evolução futura.

**Arquivos/Componentes afetados:** `workflows/automacao-regulatoria-internal-v1.json`,
`infra/report_renderer/app.py`, `infra/upload_gateway/app.py`,
`infra/upload_gateway/static/submission.html`, `deploy/postgres/init/005_simple_report_flow.sql`,
testes e documentação de governança.

**Testes:** A validação local do workflow e do renderer Markdown será executada
antes do commit. A validação remota deve confirmar o documento DOU real, o envio,
o estado `concluido` e o download oficial HTTP 200.

**Pendências:** Publicar na VPS, aplicar a migração aditiva, reconstruir gateway
e renderer, importar o workflow preservando credenciais por node ID, reiniciar o
n8n e executar o reprocessamento controlado do documento extenso.

**Impacto:** O fluxo passa a ter menos chamadas e menos transformações entre a
extração e a entrega, reduzindo o tempo de resposta e o risco de truncamento,
sem remover rastreabilidade, persistência, controle de tentativas ou segurança
do envio.

## 2026-09-16 — Validação remota do fluxo linear

**Tipo:** DEPLOY / HOMOLOGAÇÃO / VALIDAÇÃO
**Status:** CONCLUÍDO

**Contexto:** O commit `0ea18ee` foi publicado na `main` e aplicado na VPS. A
janela operacional preservou banco, volume de artefatos, credenciais e os
workflows existentes.

**Decisão/Ação:** Foi aplicada a migração aditiva `005_simple_report_flow.sql`.
Gateway e renderer foram reconstruídos. O workflow interno foi importado com 22
nós e cinco vínculos de credenciais preservados por ID de nó, ativado e carregado
após reinício do n8n. O workflow de envio, reconciliação e erros internos também
permaneceu ativo; os históricos do Google Drive permaneceram inativos.

**Testes:** O documento `2026_08_24_ASSINADO_do1.pdf` foi reprocessado como
tentativa 34. A execução gerou `report-v34.md` e `report-v34.pdf`, registrou
`prompt_version = regulatory-extraction-v3`, e o Markdown contém as seções de
resumo, parecer técnico, achados, apontamentos, recomendações, limitações e
referências de páginas. O envio de homologação foi registrado como `enviado`, o
documento terminou em `concluido` e o download oficial retornou HTTP 200. Os seis
serviços permaneceram saudáveis.

**Pendências:** O fluxo simplificado não executa RAG, embeddings, JSON
estruturado ou `quality_checks`; não há pendência nesses itens para este caminho.
Eles permanecem disponíveis como capacidade opcional. Continuam pendentes o
hardening SSH, a rotação da senha root e a matriz completa de falhas/retomadas.

**Impacto:** O DOU extenso concluiu o ciclo sem o truncamento que afetava a
saída JSON anterior. A arquitetura agora reduz chamadas intermediárias e entrega
um artefato Markdown auditável e um PDF comercial, mantendo persistência,
deduplicação, controle de tentativas, envio e download protegido.

## 2026-09-16 — Especialização comercial do prompt regulatório v4

**Tipo:** DECISÃO / PROMPT / GOVERNANÇA
**Status:** IMPLEMENTADO NO REPOSITÓRIO; HOMOLOGAÇÃO REMOTA PENDENTE

**Contexto:** O prompt v3 produzia uma síntese técnica útil, porém sem um
roteiro comercial suficientemente explícito para responder às perguntas que a
empresa precisa usar na priorização operacional e de mercado.

**Decisão/Ação:** Foi criado o `regulatory-extraction-v4` com atuação de
analista sênior de inteligência regulatória, operações, compliance e impacto de
mercado. A resposta passou a exigir, em ordem, nove perguntas: o que aconteceu;
quem é afetado; status regulatório; impacto direto no negócio; impacto potencial
de mercado; urgência ou prazo; ação imediata da empresa; pontos não comprovados;
e prioridade executiva. Também foram fixadas as seções de achados, impacto
comercial, plano de ação, riscos, limitações e referências de páginas.

**Arquivos afetados:** `prompts/regulatory-extraction-v4.md`,
`workflows/automacao-regulatoria-internal-v1.json`, `README.md`,
`workflows/README.md`, `PRD.md`, `ROADMAP.md` e
`tests/contracts/test_deployment_contract.py`.

**Testes:** JSONs do repositório validados; contrato do workflow atualizado
para v4; teste específico do prompt criado; `git diff --check` executado.

**Pendências:** Publicar a alteração na VPS e repetir a homologação controlada.
Os resultados remotos anteriores com `regulatory-extraction-v3` permanecem
válidos apenas como evidência histórica.

**Impacto:** O relatório fica mais acionável para a equipe empresarial, reduz a
ambiguidade de interpretação e acelera a confirmação no PDF por meio de
perguntas e referências padronizadas, sem transformar a análise em decisão
regulatória definitiva.

## 2026-09-23 — Limpeza controlada da base de homologação na VPS (registro histórico)

> Os fatos abaixo descrevem a observação feita em 23/09. A VPS não foi
> consultada novamente em 2026-10-02; não se afirma que o estado remoto atual
> permaneça igual.

**Data:** 2026-09-23
**Tipo:** OPERAÇÃO / HOMOLOGAÇÃO / LIMPEZA CONTROLADA
**Contexto:** A pedido do usuário, o escopo foi limitado ao Automação Miller.
Foram preservados configuração, credenciais e workflows ativos; workflows que
já estavam inativos foram removidos.

**Decisão/Ação:** Antes da limpeza, foi criado e validado um backup PostgreSQL,
um backup do volume ativo de artefatos e um arquivo separado dos volumes legados
de submissão. Os backups anteriores foram preservados. Com n8n e gateway do
Miller temporariamente parados, foram removidos quatro workflows inativos e 47
execuções com erro, quatro com crash e oito execuções travadas da reconciliação
(três na primeira varredura e cinco após o reinício). A definição da
reconciliação foi mantida, mas desativada temporariamente porque criava novas
execuções `running` a cada minuto mesmo com a base sem documentos. Os outros
três workflows operacionais permaneceram ativos. Foram zeradas as tabelas de
documentos, tentativas, análises, artefatos, revisões, erros, entregas, chunks,
avaliações e submissões; a configuração de destinatários foi preservada.
Também foram esvaziados os volumes de artefatos e submissões do Miller.

**Arquivos afetados:** Estado operacional da VPS em `/opt/automacao-miller` e
volumes Docker do Automação Miller; este registro e `ROADMAP.md`. Nenhum código
ou credencial foi alterado.

**Testes:** Checksums dos backups validados; contagens das tabelas de dados de
teste e das execuções n8n conferidas como zero; quatro definições restantes
conferidas (três ativas e a reconciliação pausada); os sete serviços do Miller
estavam saudáveis após o reinício. Não foi executado processamento funcional de
documentos nesta operação.

**Pendências registradas em 23/09:** Investigar e corrigir a reconciliação antes
de reativá-la. Naquela observação, o checkout remoto estava divergente e com
alterações locais, e o workflow ativo usava o prompt v3. A nova homologação com
o prompt v4 estava pendente. Esses estados não foram verificados em 2026-10-02.

**Impacto observado em 23/09:** O ambiente de homologação ficou sem documentos,
artefatos ou histórico de execução de teste, preservando os backups e as
credenciais. Naquela data, o workflow de reconciliação estava pausado para
evitar que execuções travadas reaparecessem.

## 2026-10-01 — Análise integral em lotes

Tipo: Correção funcional e melhoria de cobertura
Status: Implementado localmente; homologação ponta a ponta pendente

Contexto:
O workflow anterior selecionava páginas por palavras-chave e cortava o
contexto em 7.000 caracteres. Um ato posterior ao corte podia ficar fora da
análise sem que o sistema interrompesse a geração do relatório.

Decisão/Ação:
O Markdown paginado agora é dividido em lotes de até 6.000 caracteres. Cada lote
mantém os marcadores de página; páginas longas são repartidas por parágrafos e
por trechos quando necessário. O workflow exige a resposta estruturada de cada
lote, combina os achados e remove duplicatas pela página e evidência. Falha ou
resposta inválida de qualquer lote, divergência nos marcadores ou cobertura
incompleta interrompe o processamento antes da geração do relatório.

Arquivos afetados:
`workflows/automacao-regulatoria-internal-v1.json`,
`tests/contracts/test_workflow_batching.py`,
`tests/contracts/test_deployment_contract.py`,
`prompts/regulatory-extraction-v5.md`, `README.md` e `workflows/README.md`.

Testes:
Os testes direcionados passaram. O código JavaScript real do nó de divisão foi
executado com um documento sintético de três páginas: cinco lotes, limite máximo
de 6.000 caracteres, evidência após os primeiros 7.000 caracteres encontrada e
página excepcionalmente longa dividida sem perder página ou conteúdo.

Pendências:
Executar o fluxo completo com um PDF sintético na stack Docker local após
concluir a validação automática de citações e a legibilidade do PDF. Não houve
alteração ou teste na VPS nem ativação do workflow de reconciliação.

Impacto:
A cobertura deixa de depender de um recorte por palavras-chave. O tempo e o
consumo do modelo podem aumentar porque cada lote gera uma inferência.

## 2026-10-01 — Validação de evidências e sinalização de pendências

Tipo: Correção de rastreabilidade
Status: Implementado; testes direcionados aprovados; homologação ponta a ponta pendente

Contexto:
O relatório citava páginas e trechos, mas o sistema não os comparava com o
Markdown de origem. Uma citação incorreta podia parecer comprovada ao leitor.

Decisão/Ação:
Foi adicionada uma rota interna autenticada que lê o Markdown persistido e
confere cada referência. Página inexistente, evidência ausente ou localizada
em outra página agora vira referência pendente explícita. A cobertura mede
páginas processadas e não é apresentada como confiança da IA. A cobertura
incompleta ou falha técnica interrompe a geração; referência pendente não
bloqueia o relatório nem o envio manual.

Arquivos afetados:
`infra/regulatory_analysis/report_validation.py`,
`infra/upload_gateway/app.py`, `tests/regulatory_analysis/test_report_validation.py`,
`tests/upload_gateway/test_api.py`, `tests/contracts/test_deployment_contract.py`,
`workflows/automacao-regulatoria-internal-v1.json`, `prompts/regulatory-extraction-v5.md`,
`PRD.md`, `ROADMAP.md`, `README.md` e `workflows/README.md`.

Testes:
`python -m pytest tests/regulatory_analysis/test_report_validation.py
tests/upload_gateway/test_api.py tests/contracts/test_deployment_contract.py -q`;
35 testes passaram. Inclui citações confirmadas e pendentes, página inexistente,
trecho fora da página citada, cobertura incompleta, rota autenticada e formato
de tabela legado durante a transição.

Pendências:
Completar a homologação Docker com PDF sintético e confirmar a persistência do
relatório, a saída PDF, a cobertura e o estado `aguardando_envio`.

Impacto:
O leitor recebe um aviso verificável para citações pendentes. A entrega segue
disponível para conferência e nenhum relatório é produzido se páginas não
tiverem sido analisadas.

## 2026-10-01 — Relatório PDF com listas

Tipo: Melhoria de legibilidade
Status: Implementado; testes e inspeção do PDF de exemplo aprovados

Contexto:
O modelo era orientado a produzir tabelas Markdown. O renderizador atual
apresenta linhas como parágrafos e não cria uma grade de tabela, deixando os
separadores visíveis e o conteúdo confuso.

Decisão/Ação:
As instruções do prompt e do workflow foram simplificadas para usar listas com
marcadores nas respostas, plano de ação e referências. O Markdown continua sendo
a origem comum do relatório e do PDF; não foi adicionada lógica de tabela ao
renderizador.

Arquivos afetados:
`prompts/regulatory-extraction-v5.md`,
`workflows/automacao-regulatoria-internal-v1.json`, `workflows/README.md`,
`tests/report_renderer/test_renderer.py` e
`tests/contracts/test_deployment_contract.py`.

Testes:
`python -m pytest tests/report_renderer/test_renderer.py
tests/contracts/test_deployment_contract.py -q`; 16 testes direcionados e 73
testes da suíte completa passaram. `docker compose config --quiet` passou e os
sete serviços estavam saudáveis. Foi gerado PDF de exemplo, conferido por
extração de texto e renderização da página em imagem; listas e evidências
estavam legíveis e não havia linhas de tabela Markdown.

Pendências:
O PDF sintético foi processado em três lotes com cobertura 3/3; Markdown, PDF
e estado `aguardando_envio` foram persistidos e não houve e-mail. Essa execução
começou com o prompt anterior, que ainda pedia tabelas: as seis referências
foram sinalizadas como pendentes e não bloquearam a entrega. O workflow local
foi atualizado depois para instruir listas e a nova redação passou pelos testes
de contrato e renderização, sem uma segunda inferência lenta.

Limitação operacional:
O último nó da execução integrada foi `State - Report persisted`, sem erro no
resultado do workflow, mas o registro n8n permaneceu `running`. O log local
mostrou `r.firstEvent.getTime is not a function` no serviço de consolidação de
estatísticas. O gateway, PostgreSQL e demais serviços estavam saudáveis, e o
estado final e os dois relatórios ficaram persistidos. A exceção do rollup de
estatísticas está fora desta correção e deve ser investigada separadamente.

Impacto:
As listas melhoram a leitura do PDF e deixam o relatório Markdown mais simples.

## 2026-10-02 — Retomada de entregas de e-mail paradas

Tipo:
Correção de workflow

Status:
Implementado; contratos e consulta SQL local aprovados

Contexto:
A reconciliação voltava uma entrega parada para `solicitado`, mas descartava o
`delivery_id` no resultado final e enviava somente `submission_id` ao workflow
de processamento. A análise do PDF não reivindica uma entrega de e-mail, então
ela podia continuar parada sem ser retomada.

Decisão/Ação:
A consulta agora devolve tarefas tipadas como `email_delivery` ou `document`.
Entregas recuperadas incluem `delivery_id` e são encaminhadas ao webhook do
workflow de envio; documentos continuam sendo enviados ao processamento
interno. O `delivery_id` continua sendo reivindicado pelo workflow de envio,
que usa bloqueio e estado para evitar duas reivindicações simultâneas.

Arquivos afetados:
`workflows/automacao-regulatoria-reconcile-v1.json`,
`workflows/README.md`, `tests/contracts/test_deployment_contract.py` e
`ROADMAP.md`.

Testes:
`python -m pytest tests/contracts/test_deployment_contract.py -q`: 10 passaram.
A consulta real exportada foi executada no PostgreSQL Docker local com uma
entrega sintética envelhecida; retornou `email_delivery`, protocolo e
`delivery_id`. A transação foi revertida e nenhum webhook ou Gmail foi chamado.

Pendências:
O workflow permanece inativo no export e não foi ativado no n8n local nem
consultado na VPS. A homologação de execução n8n/Gmail segue para etapa
autorizada, sem envio real.

Impacto:
O recuperador retoma o envio pendente no workflow adequado, sem reprocessar o
PDF nem perder o identificador da entrega.

## 2026-10-02 — Delimitação do último estado remoto observado

Tipo:
Correção de documentação operacional

Status:
Concluído; teste de contrato aprovado

Contexto:
O topo do roadmap apresentava como atuais os estados anotados na operação de
limpeza da VPS em 2026-09-23. Essa VPS não foi consultada nesta atualização, e a
última homologação ponta a ponta registrada usou o prompt v3.

Decisão/Ação:
O status geral agora distingue a observação de 23/09 do estado remoto atual,
que permanece desconhecido. A seção operacional e o registro de 23/09 foram
marcados como históricos, preservando os fatos e a trilha da operação.

Arquivos afetados:
`ROADMAP.md`, `LOG.md` e `tests/contracts/test_deployment_contract.py`.

Testes:
`python -m pytest tests/contracts/test_deployment_contract.py -q`: 11 passaram.
O teste exige datas explícitas e a declaração de que não houve consulta atual à
VPS.

Pendências:
Consultar e homologar a VPS fica para uma atividade autorizada separada; não
houve conexão remota nem alteração nesta tarefa.

Impacto:
Quem lê o roadmap sabe quando o estado foi observado e não confunde um registro
histórico com uma checagem da situação da VPS hoje.

## 2026-10-02 — Decisão de saída do produto e uso de RAG

Tipo:
Decisão de requisito e arquitetura

Status:
Implementado; documentação alinhada e teste de contrato aprovado

Contexto:
O fluxo ativo analisa todas as páginas em lotes, usa JSON apenas como formato
temporário de consolidação e persiste o relatório em Markdown/PDF. RAG não é
chamado no fluxo ativo. Parte do PRD, README e auditoria descrevia JSON
persistido, RAG ativo e campos de confiança da análise; o prompt vigente pede
prioridade executiva, que expressa urgência de ação e não confiança.

Decisão/Ação:
O requisito do MVP é o relatório final Markdown/PDF, com cobertura de páginas
e confirmação literal de referências. Não há requisito de artefato JSON
estruturado persistido, RAG ativo ou nota de confiança semântica da IA. JSON por
lote segue interno e temporário; a prioridade executiva continua sendo a
prioridade das ações. Esquemas e recursos de RAG existentes serão documentados
como legado/capacidade opcional fora do caminho ativo. PRD, README e operação dos
workflows foram alinhados; o relatório de auditoria recebeu aviso de vigência.

Arquivos afetados:
`PRD.md`, `README.md`, `ROADMAP.md`, `workflows/README.md`,
`RELATORIO_AUDITORIA_PROJETO.md` e `tests/contracts/test_deployment_contract.py`.

Testes:
`python -m pytest tests/contracts/test_deployment_contract.py -q`: 12 passaram.
O contrato verifica a descrição do formato de saída, o status de RAG, a
distinção entre prioridade e confiança e o aviso de vigência da auditoria.

Pendências:
Nenhuma mudança funcional foi necessária para esta decisão. Os schemas, tabelas
e exports históricos permanecem no repositório, documentados como legado ou
opção futura; não foram removidos.

Impacto:
Alinha o contrato do produto ao processamento implementado e separa cobertura
de evidência da prioridade executiva, sem representar nenhuma delas como
confiança semântica da IA.

## 2026-10-02 — RAG optativo e menor dependência na inicialização

Tipo:
Simplificação de infraestrutura

Status:
Implementado localmente; perfil padrão e perfil RAG validados

Contexto:
O workflow ativo não chama RAG, mas o Compose iniciava `rag-service` e exigia
que estivesse saudável antes de iniciar o n8n. Isso mantinha uma dependência e
mais 512 MiB de limite máximo no caminho padrão. O n8n também não recebia a URL
do webhook de envio que agora é chamada pela reconciliação.

Decisão/Ação:
O serviço foi movido ao perfil optativo `rag`; o n8n não depende dele nem recebe
variáveis de RAG. As URLs de processamento e envio passaram a ser fornecidas ao
n8n. O perfil padrão soma 6.912 MiB de limites configurados e o perfil com RAG
soma 7.424 MiB. A stack Docker local foi recriada no perfil padrão e o
`rag-service` foi parado, preservando os volumes.

Arquivos afetados:
`docker-compose.yml`, `.env.example`, `deploy/README.md`, `ROADMAP.md`,
`tests/contracts/test_deployment_contract.py` e este registro.

Testes:
`docker compose ... config --quiet` passou sem perfil e com `--profile rag`.
`python -m pytest tests/contracts/test_deployment_contract.py -q`: 12 passaram.
`python -m pytest -q`: 75 passaram, com dois avisos de depreciação de
`on_event` do FastAPI já existentes.
O cálculo das configurações confirmou seis serviços/6.912 MiB no padrão e sete
serviços/7.424 MiB no perfil RAG. Na stack local, os endpoints de prontidão do
n8n e do gateway responderam HTTP 200 e os seis serviços ficaram saudáveis.
Nenhum Gmail foi chamado.

Pendências:
Não houve alteração na VPS. O perfil RAG fica disponível apenas para avaliação
específica; as cotas configuradas representam limites, não consumo real.

Impacto:
A inicialização padrão perdeu a dependência do serviço RAG e reserva mais
memória para o sistema na VPS de referência. A reconciliação também recebe no
n8n a configuração do webhook de envio.

## 2026-10-02 — Estabilização do processamento de PDFs longos no Ollama

Tipo:
Correção de workflow e infraestrutura local

Status:
Correção aplicada e testada; reprocessamento completo interrompido pelo usuário
devido à lentidão do modelo local

Contexto:
O PDF enviado pelo operador tem 26,6 MiB, 142 páginas e gerou 1,63 MB de
Markdown. Tentativas anteriores apontaram timeout do conversor configurado em
milissegundos como se fossem segundos, cópia do Markdown completo para cada lote
e 334 chamadas Ollama iniciadas em paralelo pelo nó HTTP do n8n. A concorrência
derrubava o contêiner por falta de memória.

Decisão/Ação:
O timeout do conversor agora é convertido de segundos para milissegundos e usa
300 segundos por padrão, sem retry automático. O preparo dos lotes deixou de
replicar o Markdown integral em cada item. O workflow usa `Loop Over Items` com
`batchSize=1` para aguardar a resposta antes do próximo lote e limita o contexto
de cada chamada a 4.096 tokens. O normalizador do workflow de erro usa `Set`, e
o registro de erro atualiza tentativa, protocolo e entrega em uma única consulta
atômica. O workflow foi exportado antes da alteração, reimportado e publicado
no n8n local, preservando a credencial PostgreSQL local. O gateway, banco e
Ollama continuaram locais; nenhum e-mail foi disparado.

Arquivos/Componentes afetados:
`docker-compose.yml`, `tests/contracts/test_deployment_contract.py`,
`workflows/README.md`, `workflows/automacao-regulatoria-internal-error-v1.json`,
`workflows/automacao-regulatoria-internal-v1.json`, n8n/PostgreSQL/Ollama locais.

Testes:
`python -m pytest tests/contracts/test_deployment_contract.py -q`: 13 passaram.
`python -m pytest -q`: 76 passaram; dois avisos existentes de depreciação do
FastAPI. `docker compose -p codex-miller-local config --quiet` passou. A
tentativa 8 converteu o PDF e alcançou a chamada sequencial ao Ollama sem OOM.
O uso chegou a cerca de 2,3 GiB, sem reinicialização durante essa execução.
O modelo produziu aproximadamente 1,6 token/s; o usuário escolheu interromper
antes do término dos 334 lotes. O protocolo e a tentativa foram marcados como
`erro`, sem relatório final. Ollama foi descarregado e o n8n ficou saudável.

Pendências:
A conclusão ponta a ponta de um documento longo não foi comprovada porque a
análise foi interrompida por lentidão. O protocolo precisa de novo
reprocessamento em um ambiente com capacidade adequada quando o usuário quiser.
Não houve consulta à VPS, validação do relatório final nem envio real de e-mail.

Impacto:
O caminho deixou de disparar centenas de inferências ao mesmo tempo, reduzindo
o risco de OOM. A execução integral preserva a cobertura, mas o modelo local em
CPU torna o processamento muito demorado; estabilidade e tempo são limitações
distintas e ambas ficam explícitas no estado e na documentação.


## 2026-10-02 — Integração das PRs #1/#2 e roteiro de teste local

Registro histórico incorporado da branch da PR #3 em 16/11/2026; os resultados
abaixo pertencem à validação original, não foram repetidos nesta integração.

As PRs #1 e #2 foram integradas à `main` em 02/10/2026. A PR #3 foi preparada
com um override de Compose que publica a landing somente em loopback e um guia
para subir a stack local, enviar PDF de teste e conferir o estado
`aguardando_envio` sem disparar e-mail. README, implantação, workflows, roadmap
e log receberam referências para esse roteiro.

A descrição original da PR registra 75 testes Python aprovados, Compose local
válido, seis serviços saudáveis e respostas HTTP 200 do gateway e do n8n. Ela
também informa que não foi feito novo upload ponta a ponta, nenhum e-mail foi
enviado e a VPS não foi consultada.

## 2026-10-03 — Validação na VPS

Data: 2026-10-03
Tipo: Implantação e correção de workflow
Status: stack instalada; fluxo principal chegou a aguardando_envio em teste sintético; homologação real pendente

Contexto:
A VPS foi preparada para testar o repositório após a limpeza autorizada. A máquina
tem 2 vCPU e 7,8 GiB de RAM; portanto, o RAGFlow não foi implantado. A versão
5862ee25b42b7788f6074140063dc5aec107f1a9 do repositório foi instalada em
/opt/automacao-miller com o perfil Docker padrão.

Decisão/Ação:
A stack usa PostgreSQL, Ollama (qwen2.5:3b), conversor de PDF, renderizador de
relatório, gateway de upload e n8n. n8n foi publicado apenas no loopback do host;
o gateway ficou interno ao Compose. Uma credencial PostgreSQL foi criada no n8n
sem inserir segredos nos exports. Os workflows interno e de erro foram publicados;
reconciliação e envio pelo Gmail ficaram inativos.

As execuções de teste revelaram validação frágil do cabeçalho das seções e
citações reformuladas pelo modelo. O fluxo agora completa cabeçalhos ausentes com
Não localizado nos achados analisados. e monta a seção de referências com as
evidências estruturadas extraídas. O gateway continua conferindo cada citação
contra o Markdown original e mantém evidências não localizadas como pendentes.
A associação de erros por execution_id também foi corrigida para fechar a
tentativa e o documento quando o Error Trigger não fornece submission_id.

Arquivos afetados:
workflows/automacao-regulatoria-internal-v1.json,
workflows/automacao-regulatoria-internal-error-v1.json,
tests/contracts/test_deployment_contract.py, ROADMAP.md e este registro.

Testes:
docker compose config --quiet passou; os seis serviços ficaram saudáveis e o
modelo foi baixado. O teste sintético 452cf9dc-ef31-4c46-a554-6a310ad32358
terminou em aguardando_envio, gerou Markdown e PDF, cobriu 1/1 páginas e teve
2/3 referências comprovadas e uma pendente. Um PDF inválido controlado terminou
em erro, com tentativa e evento registrados na etapa PDF Converter. Erros
anteriores causados por títulos omitidos e achado incompleto também foram
encerrados como erro; o documento sintético da primeira tentativa foi corrigido
no banco para não ficar preso em em_processamento. Nenhum e-mail foi enviado.
A validação local dos nós JavaScript e os contratos de workflow passaram.

Pendências:
Executar o conjunto integral de testes do repositório; conferir o estado final da
stack e limpar arquivos temporários de credencial. Repetir a homologação com
documentos reais representativos e PDFs longos, revisar a qualidade do relatório
e testar o envio manual somente quando uma conta Gmail estiver configurada e
autorizada. Investigar o erro recorrente do rollup de estatísticas do n8n
(firstEvent.getTime). Não há domínio/TLS de produção configurados.

Impacto:
A automação está instalada e completa o caminho de PDF sintético até a revisão
manual, mas ainda não está aprovada para uso produtivo. Trechos não comprovados
continuam visivelmente pendentes e não foram enviados por e-mail.

## 2026-10-03 — Homologação opcional com API externa

Data:
2026-10-03

Tipo:
Decisão de arquitetura e privacidade

Contexto:
O processamento local do PDF real de 142 páginas foi lento no modelo Ollama
executado em CPU. O usuário autorizou testar um provedor externo para comparar
tempo e qualidade. A chave da API ainda não está configurada na VPS.

Decisão/Ação:
Preparar uma variante de homologação GroqCloud com `openai/gpt-oss-120b`,
separada e inativa por padrão; manter Ollama como padrão. A variante não deve
transmitir o protocolo interno, precisa tratar texto do documento como conteúdo
não confiável e manter as validações locais de estrutura, páginas e citações.
Não haverá fallback automático nem envio de e-mail. Nenhum conteúdo foi enviado
ao provedor até a configuração e validação da credencial.

Arquivos afetados:
`PRD.md`, `ROADMAP.md`, `workflows/README.md`,
`workflows/automacao-regulatoria-internal-groq-v1.json`,
`tests/contracts/test_deployment_contract.py` e este registro.

Testes:
Pendentes. A documentação oficial do Groq descreve aproximadamente 500 tokens/s
para o modelo, JSON Schema estrito e limites que variam por plano. Isso é dado
publicado pelo provedor, não uma medição da automação. A política atual informa
que inferências não são retidas por padrão, mas logs de confiabilidade/abuso
podem incluir entradas e saídas por até 30 dias; esses dados ficam em buckets
GCP nos Estados Unidos. ZDR é uma opção de Data Controls. Fontes: [modelo e
velocidade](https://console.groq.com/docs/model/openai/gpt-oss-120b), [saídas
estruturadas](https://console.groq.com/docs/structured-outputs), [dados e
retenção](https://console.groq.com/docs/your-data).

Pendências:
Criar e associar no n8n a credencial HTTP Header Auth para Groq, validar o plano
e os limites aplicáveis, importar a variante inativa, apontar o gateway ao
webhook de homologação e executar o PDF completo. Comparar o tempo, cobertura,
referências confirmadas/pendentes e qualidade do relatório com a tentativa local.

Impacto:
Permite medir uma opção potencialmente mais rápida sem alterar o caminho local
ou transmitir documentos sem credencial e escolha operacional explícitas.

## 2026-10-03 — Verificação da API gratuita da NVIDIA

Data:
2026-10-03

Tipo:
Avaliação de provedor externo e restrição de dados

Contexto:
O usuário pediu para verificar o catálogo de API gratuita da NVIDIA como opção
para acelerar a análise documental.

Decisão/Ação:
O catálogo oferece endpoints gratuitos para prototipação; o `openai/gpt-oss-20b`
usa endpoint compatível com OpenAI Chat Completions, tem janela de 131 mil tokens
e está marcado como Free Endpoint. Porém, os Termos da API Trial proíbem enviar
informações confidenciais, sensíveis e governamentais, salvo permissão expressa
do serviço; também autorizam coleta de conteúdo para melhoria de produtos e
modelos e monitoramento antifraude/abuso. O PDF `...do1` aparenta ser uma edição
do Diário Oficial da União; por isso, a API gratuita da NVIDIA não foi aprovada
para receber o documento real. Nenhum conteúdo foi transmitido à NVIDIA.

Arquivos afetados:
Este registro; decisão sobre o próximo provedor/fixture de teste pendente da
resposta do usuário.

Testes:
Consulta às páginas oficiais do [catálogo de modelos](https://build.nvidia.com/models),
ao [endpoint gpt-oss-20b](https://build.nvidia.com/openai/gpt-oss-20b), ao
[FAQ de acesso ao NIM](https://docs.api.nvidia.com/nim/docs/product) e aos
[Termos da API Trial](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf).
O Developer Program oferece API hospedada sem custo para prototipação e teste;
os termos atuais reservam produção para licença NVIDIA AI Enterprise. Não foi
encontrada no catálogo uma cota fixa pública de RPM/TPM por conta/modelo; validar
limites e créditos no painel antes de qualquer chamada em lote.

Pendências:
O usuário escolherá entre testar NVIDIA com conteúdo sintético, continuar a
comparação com outro provedor para o PDF real, ou aguardar uma opção com termos
adequados. A API externa Groq também continua sem credencial configurada.

Impacto:
Evita enviar um documento potencialmente governamental para um serviço cujos
termos de teste vedam esse tipo de dado e preserva a comparação externa como
uma decisão explícita, condicionada ao provedor e ao conteúdo.

## 2026-10-03 — Escopo do teste NVIDIA com conteúdo sintético

Data:
2026-10-03

Tipo:
Decisão de teste e privacidade

Contexto:
Após a avaliação dos termos da NVIDIA API Trial, o usuário escolheu seguir com
NVIDIA usando um documento sintético, sem enviar o PDF do Diário Oficial.

Decisão/Ação:
Substituir a variante Groq ainda não implantada por um workflow manual, isolado
e inativo para chamar o endpoint NVIDIA com `openai/gpt-oss-20b`. Foi criado um
fixture fictício sem dados reais que verifica JSON, página e evidência literal.
O workflow não acessa o gateway, o processamento de documentos reais nem e-mail.
A credencial deve ser criada pelo operador no n8n; a chave não será gravada em
código, `.env`, export ou chat. O teste mede uma pequena chamada sintética e não
comprova velocidade ou qualidade no PDF real.

Arquivos afetados:
`PRD.md`, `ROADMAP.md`, `LOG.md`, `workflows/README.md`,
`workflows/nvidia-synthetic-api-eval-v1.json`,
`tests/fixtures/synthetic-regulatory-sample.md` e
`tests/contracts/test_deployment_contract.py`. A variante Groq criada durante
preparação não foi publicada e será removida em favor do escopo escolhido.

Testes e validação:
`python -m pytest tests/contracts/test_deployment_contract.py -q` passou com
14 testes; `python -m pytest -q` passou com 77 testes e dois avisos preexistentes
de depreciação do FastAPI. O JSON, as conexões e a sintaxe JavaScript dos nós
foram validados. O workflow foi importado na VPS e confirmado inativo, com quatro
nós e sem credencial associada. Nenhuma chamada NVIDIA foi realizada por falta
da credencial; nenhum conteúdo foi transmitido à NVIDIA.

Pendências:
Associar no n8n a credencial NVIDIA `HTTP Header Auth`; executar apenas o fixture
sintético, medir latência/estrutura e confirmar que o workflow permanece inativo.

Impacto:
Permite testar o endpoint gratuito sem expor conteúdo real ou criar risco de
acionamento acidental pelo caminho de upload.

## 2026-10-03 — Verificação de credencial para execução NVIDIA

Data:
2026-10-03

Tipo:
Pré-validação de integração

Contexto:
O usuário solicitou iniciar a chamada de teste à API NVIDIA com o fixture
sintético.

Decisão/Ação:
Inspecionados somente os metadados do workflow e das credenciais no PostgreSQL
da VPS. O nó `NVIDIA - Analyze synthetic fixture` não tem credencial associada
e não foi encontrada credencial com tipo HTTP Header Auth ou nome NVIDIA. Não
foi feita chamada externa nem transmitido conteúdo.

Arquivos afetados:
`LOG.md`.

Testes:
Consulta somente leitura ao banco do n8n confirmou o workflow ainda inativo,
sem vínculo de credencial no nó NVIDIA. Os testes estáticos do contrato seguem
com 14 aprovações; nenhum teste autenticado contra a API foi executado.

Pendências:
Criar no n8n a credencial HTTP Header Auth com a chave NVIDIA, vinculá-la ao nó
de análise sintética e executar o workflow manual para medir latência e validar
a resposta.

Impacto:
O teste permanece restrito ao fixture sintético até que a credencial seja
configurada no n8n.

## 2026-10-03 — Handoff de acesso à NVIDIA

Data:
2026-10-03

Tipo:
Bloqueio de autenticação e aceite de termos

Contexto:
O usuário pediu que a configuração da API fosse feita pelo agente.

Decisão/Ação:
Aberto o portal NVIDIA Build. A sessão não está autenticada; a tela solicita
identificação por e-mail e informa que prosseguir implica aderir ao NVIDIA
Developer Program e aceitar os NVIDIA Technology Access Terms of Use. A etapa
foi deixada para o usuário, sem inserir credenciais, aceitar termos ou criar
uma chave.

Arquivos afetados:
`LOG.md`.

Testes:
Nenhuma chamada API foi realizada e nenhum documento foi transmitido.

Pendências:
O usuário deve concluir a autenticação e decidir sobre o aceite dos termos,
criar a chave NVIDIA e salvá-la diretamente no n8n como `HTTP Header Auth`,
associada ao nó de avaliação sintética. Depois, o agente pode executar o fixture.

Impacto:
O workflow segue inativo e sem credenciais até a conclusão do handoff.

## 2026-10-03 — Chave NVIDIA exposta durante configuração

Data:
2026-10-03

Tipo:
Incidente de credencial

Contexto:
Durante a preparação do acesso à API gratuita NVIDIA, uma chave de API foi
exibida na captura da tela de geração e depois enviada pelo usuário no chat.

Decisão/Ação:
Não copiar, armazenar em arquivo/configuração nem usar a chave. Orientar o
usuário a revogá-la e gerar uma substituta; a nova chave deve ser salva
diretamente na credencial protegida do n8n, sem passar pelo chat.

Arquivos afetados:
`LOG.md` (sem registrar o valor da chave).

Testes:
Nenhuma chamada foi feita à API NVIDIA e nenhum conteúdo sintético foi
transmitido.

Pendências:
Revogar a chave exposta; criar uma substituta e associá-la no n8n ao nó
`NVIDIA - Analyze synthetic fixture`; então executar o fixture e registrar
latência e validação estrutural.

Impacto:
A credencial exposta deve ser considerada comprometida. O fluxo continua
inativo e sem credencial segura até a substituição.

## 2026-10-03 — Avaliação sintética no NVIDIA Playground

Data:
2026-10-03

Tipo:
Teste de modelo e prompt

Contexto:
O usuário autorizou expressamente aceitar os termos de trial na tela do
Playground e testar apenas o fixture sintético com `openai/gpt-oss-20b`.

Decisão/Ação:
Enviadas duas chamadas do fixture fictício pelo NVIDIA Playground na sessão
autenticada do NVIDIA Build. Nenhum documento real foi enviado. O valor textual
da chave compartilhada no chat não foi copiado para arquivos nem para o n8n.

Arquivos afetados:
`ROADMAP.md` e `LOG.md`.

Testes:
As respostas foram observadas em aproximadamente 16 s e 19 s na interface,
sem métrica exata de servidor ou tokens. Ambas extraíram a alteração de 90 para
120 dias, apontaram página 1 e ignoraram a instrução maliciosa simulada. A
primeira resposta era JSON válido, mas juntou duas passagens no campo `evidencia`;
uma checagem local confirmou que o valor inteiro não é substring contínua do
fixture, embora a frase central seja literal. A segunda resposta incluiu aspas
delimitadoras sem escape no valor de evidência e falhou `JSON.parse`. O Playground
não exercitou o `response_format` com JSON Schema estrito configurado no workflow.

Pendências:
Revogar a chave exposta no chat/captura e criar outra; o usuário deve salvá-la
diretamente no n8n como `HTTP Header Auth` e associá-la ao workflow. Depois,
executar o workflow integrado, validar a evidência e registrar latência/tokens.

Impacto:
O teste confirma que o modelo extraiu o fato principal e resistiu à injeção do
fixture, mas os resultados brutos do Playground não passam de forma consistente
pela validação de evidência/JSON. A automação integrada segue sem teste ponta a
ponta e permanece inativa.

## 2026-10-08 — Consolidação da documentação do projeto

Data: 2026-10-08
Tipo: documentação, segurança e validação

Contexto:
O usuário pediu a leitura dos documentos e áudios do repositório e a consolidação
da documentação principal na raiz. A última observação da VPS disponível nos
registros é de 2026-10-03; nenhuma consulta remota foi feita nesta atualização.

Decisão/Ação:
Foram preparados README.md comercial, PRD.md, AGENTS.md, ROADMAP.md,
FLUXOGRAMA.md e ACESSOS.md com escopo e linguagem consistentes. O roadmap foi
reduzido a uma lista ordenada de pendências; o histórico cronológico permanece
no LOG.md. Documentos auxiliares foram corrigidos ou identificados como
históricos quando ainda descreviam Google Drive ou RAG como parte ativa do
fluxo.

ACESSOS.md informa os locais de configuração e as ações de rotação, sem guardar
senhas ou tokens. O arquivo .env local foi identificado como ignorado pelo Git,
não foi aberto e não foi incluído.

A matriz de homologação passou a distinguir testes unitários de validação
integrada. A leitura do prompt ativo revelou que o PRD exige tratamento
explícito de comandos embutidos nos PDFs como conteúdo não confiável; essa
garantia ainda precisa ser confirmada no workflow ativo. A pendência e um caso
sintético foram adicionados ao roadmap e à matriz, sem alterar o prompt nesta
tarefa.

O inventário encontrou 21 documentos Markdown no projeto, três PDFs temporários
de teste e nenhum arquivo de áudio ou vídeo. Os PDFs temporários são amostras e
relatórios sintéticos; um relatório contém afirmações deliberadamente sem
evidência e não foi tratado como resultado válido do produto.

Arquivos afetados:
AGENTS.md, ACESSOS.md, FLUXOGRAMA.md, LOG.md, PRD.md, README.md, ROADMAP.md,
RELATORIO_AUDITORIA_PROJETO.md, deploy/README.md,
docs/checklists/acessos-e-responsaveis.md,
docs/checklists/matriz-documentos-referencia.md,
docs/superpowers/plans/2026-08-25-documentacao-inicial-produto.md,
infra/pdf_converter/README.md, prompts/regulatory-extraction-v1.md,
prompts/regulatory-extraction-v2.md, prompts/regulatory-extraction-v3.md,
prompts/regulatory-extraction-v4.md, tests/contracts/test_deployment_contract.py,
workflows/README.md e workflows/pdf-to-markdown-gate.md.

Testes:
python -m pytest -q: 77 testes passaram; dois avisos preexistentes de depreciação
do FastAPI.
docker compose --env-file .env config --quiet: passou.
git diff --check: passou.
Checagem de 21 arquivos Markdown: links locais existentes e cercas de código
balanceadas.

Pendências:
Confirmar na VPS o estado da execução do PDF real de 142 páginas antes de criar
outra execução. Revogar a chave NVIDIA exposta e, se o teste ainda for desejado,
gerar outra e guardá-la somente no n8n. Confirmar hardening SSH, credenciais e
restauração de backup. Validar a proteção do prompt ativo contra instruções
maliciosas em documentos antes de produção.

Impacto:
A documentação agora separa visão comercial, requisitos, execução, estado,
fluxo e tratamento de acessos. Nenhum segredo foi incluído e nenhuma mudança de
requisito ou configuração remota foi feita nesta tarefa.

## 2026-10-23 — Verificação do login n8n e exposição de credencial SSH

Data: 2026-10-23
Tipo: Acesso / Segurança
Contexto: Foi solicitado identificar o usuário e a senha do n8n. O endereço
fornecido foi acessado com a chave SSH já configurada no computador, sem usar a
senha root compartilhada na conversa.

Decisão/Ação:
O host respondeu como `srv1728832.hstgr.cloud`. O container
`automacao-miller-n8n-1` estava saudável. A consulta somente de leitura ao banco
usado pelo n8n encontrou um registro sem e-mail e sem senha; portanto, não há
credencial de login recuperável nessa conta. Nenhuma senha, hash ou segredo foi
copiado para este registro, e nenhuma credencial do n8n foi alterada.

A senha administrativa root foi exposta na conversa e deve ser considerada
comprometida. Ela não foi repetida nem usada. A rotação ainda está pendente para
ser feita e guardada no cofre aprovado; o acesso SSH por chave foi validado.

Arquivos afetados:
ACESSOS.md e LOG.md.

Testes:
Acesso SSH somente por chave com verificação estrita do host; estado do
container n8n; consulta SQL somente de leitura dos indicadores de e-mail e senha
configurados. Nenhum teste de aplicação foi executado.

Pendências:
Rotacionar a senha root e guardá-la no cofre aprovado. Configurar um usuário
proprietário do n8n pelo fluxo de configuração suportado, caso a tela de
configuração inicial esteja disponível.

Impacto:
O usuário e a senha solicitados não podem ser fornecidos porque não há uma
credencial de proprietário configurada no registro consultado. O valor root
compartilhado não é uma credencial do n8n e requer rotação.

## 2026-10-26 — Verificação e sincronização do repositório e da VPS

Data: 2026-10-26
Tipo: Operação / Sincronização / Estado de homologação
Contexto: O usuário pediu para verificar atualizações no Git remoto e na VPS,
sincronizar o projeto e resumir o estado e as oportunidades de melhoria.

Decisão/Ação:
O `origin/main` não tinha commits novos em relação ao checkout local, que estava
em `911d0ef`. A VPS respondeu como `srv1728832.hstgr.cloud`; o checkout estava
um commit atrás (`5862ee2`). Os dois exports de workflow com mudanças locais na
VPS eram idênticos aos arquivos do commit remoto, então foram preservados e o
checkout foi avançado para `origin/main` após a atualização documental.

A instância tem seis serviços do Automação Miller saudáveis. O export das
versões publicadas mostrou somente os workflows de processamento e erro; a
lógica de nós, parâmetros e conexões corresponde ao repositório. As diferenças
observadas estão nas referências às credenciais da instalação, que não devem
ser copiadas entre ambientes. Os workflows de envio e reconciliação continuam
sem publicação. Não houve importação de workflows nem reinicialização de
serviços.

No PostgreSQL havia três documentos em `aguardando_envio`, seis em `erro` e
nenhum em `em_processamento`. O único PDF acima de 25 MB, correspondente ao
documento de 142 páginas citado em outubro, está em erro na etapa
`Ollama - Analyze each batch`, categoria `infraestrutura`; não há execução em
andamento. A conta proprietária do n8n segue sem e-mail e senha configurados.

O servidor tem 2 vCPU, 7,8 GiB de RAM e 99 GiB de disco. Durante a consulta,
havia 2,4 GiB de memória disponível, 724 MiB de swap usados e 58 GiB livres em
disco. Um Ollama de outro projeto usava 2,93 GiB de seu limite de 4 GiB. Também
foram observados containers de `ideia-saude-agent-test`, `brandriot-socialsuite`
e uma stack Supabase; `atendimento` e `rtk-renata`, citados em agosto, não
apareceram no `docker ps` desta verificação.

O `.env` da VPS estava com permissão 600. O diretório esperado para backups,
`/opt/backups/automacao-miller`, não existe. A senha root exposta em conversa
continua pendente de rotação; o acesso por chave SSH foi validado.

Arquivos afetados:
README.md, ROADMAP.md, ACESSOS.md e LOG.md.

Testes/Verificações:
Fetch do `origin`; comparação do checkout da VPS e das versões publicadas dos
workflows; SSH com verificação estrita do host; estado dos seis containers;
consultas agregadas de status do banco; permissões do `.env`, uso de recursos e
existência do diretório de backups. `git diff --check` e checagem dos links
Markdown locais. Nenhum teste de aplicação foi executado, pois o código da
aplicação e os workflows em execução não foram alterados. A última suíte local
registrada passou com 77 testes em 08/10/2026.

Pendências:
Rotacionar a senha root e guardá-la no cofre aprovado; configurar o usuário
proprietário do n8n; revogar a chave NVIDIA exposta; investigar a falha e decidir
sobre o reprocessamento controlado do PDF longo; homologar envio e reconciliação
Gmail; criar e testar backup/restauração; validar proteção contra instruções
embutidas em PDFs antes de produção.

Impacto:
O checkout local, o remoto e o código versionado na VPS ficaram sincronizados.
As execuções ativas do n8n não foram reiniciadas ou modificadas, porque os
workflows publicados já correspondiam à lógica do repositório e suas
credenciais são específicas da instalação.

## 2026-10-26 — Avaliação operacional e atualização da documentação

Data: 2026-10-26
Tipo: DOCUMENTAÇÃO / AVALIAÇÃO / OPERAÇÃO
Status: documentação atualizada; pendências de homologação preservadas

Contexto:
O usuário solicitou uma avaliação completa da Automação Miller, leitura dos documentos disponíveis e criação/atualização da documentação principal em linguagem fácil de entender e executar.

Decisão/Ação:
Foram revisados os documentos Markdown versionados e auxiliares, os exports e prompts relevantes, o Compose, os serviços principais e os artefatos PDF sintéticos existentes. O inventário do projeto não encontrou arquivos de áudio. O arquivo .env local não foi aberto. A auditoria por SSH foi somente de leitura e usou a chave configurada no computador.

A documentação foi alinhada para separar requisitos do produto, comportamento implementado e estado ativo na VPS. README.md, PRD.md, AGENTS.md, ROADMAP.md, FLUXOGRAMA.md e ACESSOS.md foram atualizados. Também foram alinhados workflows/README.md, deploy/README.md, docs/checklists/matriz-documentos-referencia.md e o contexto inicial deste LOG.md, sem apagar o histórico cronológico.

Estado observado na VPS:
O checkout estava no commit 38f5358, sincronizado com origin/main. Os seis containers do Miller estavam saudáveis. Somente os workflows de processamento interno e erro estavam ativos; envio manual, reconciliação e avaliação NVIDIA estavam inativos. Havia 3 documentos em aguardando_envio, 6 em erro e nenhum em processamento. O registro proprietário do n8n não tinha e-mail nem senha definidos. O arquivo .env remoto existia com permissão 600; o diretório de backup esperado estava ausente. O gateway não tinha entrada pública HTTP/HTTPS identificada. A VPS compartilhava recursos com ideia-saude-agent-test; as stacks BRANDRIOT Socialsuite e Supabase Socialsuite removidas em 26/10 não apareciam mais no inventário Docker.

Risco de qualidade:
Um relatório sintético temporário apresentou afirmações sem apoio no documento e 0 de 6 referências comprovadas. O validador marcou as referências como pendentes, mas a regra atual não bloqueia o envio por esse motivo. O roadmap registra a decisão de produto necessária; nenhum requisito foi alterado nesta atualização.

Arquivos afetados:
README.md, PRD.md, AGENTS.md, ROADMAP.md, FLUXOGRAMA.md, ACESSOS.md, LOG.md, workflows/README.md, deploy/README.md e docs/checklists/matriz-documentos-referencia.md.

Testes e verificações:
Não foram executados testes da aplicação nem alterações funcionais. Foram feitas consultas somente de leitura à VPS, inventário e leitura dos documentos, conferência de estado dos containers, workflows e contagens agregadas do banco, verificação de permissão do .env sem ler seu conteúdo e checagem do estado Git. A última suíte automatizada registrada continua sendo a de 77 testes aprovada em 08/10/2026; ela não foi repetida nesta tarefa.

Pendências:
Seguir os itens P0 e P1 do ROADMAP.md: rotacionar/revogar credenciais expostas, configurar o proprietário do n8n, publicar a landing por HTTPS, estabelecer backup e restauração, decidir o tratamento de relatórios sem referências comprovadas, ativar e homologar envio/reconciliação, reforçar o prompt contra instruções embutidas e concluir a matriz de falhas com dados autorizados.

Impacto:
A documentação deixa explícito que a stack saudável ainda não equivale a uma operação pronta. O caminho esperado, os bloqueios atuais, os riscos de qualidade e a ordem de execução agora podem ser entendidos sem consultar senhas ou tratar registros históricos como estado atual.

## 2026-10-26 — Adiciona contexto determinístico ao processamento

Data: 2026-10-26
Tipo: FUNCIONAL / CONTEXTO / EVIDÊNCIAS
Status: implementado e testado localmente; ainda não implantado na VPS

Contexto:
O usuário decidiu avançar com uma camada determinística para preservar contexto entre páginas e pediu implementação e testes.

Decisão/Ação:
Foi adicionado `build_deterministic_context`, que varre o Markdown paginado, localiza termos regulatórios de uma lista controlada e identificadores de processo em formatos conhecidos, mantendo trecho e página. Identificadores exatamente iguais encontrados em mais de uma página são agrupados como pistas de contexto; nenhuma classificação ou decisão regulatória é inferida pelo código.

O gateway passou a oferecer a rota interna autenticada `POST /internal/submissions/{id}/deterministic-context`. A rota lê a versão mais recente do Markdown no volume, confere o SHA-256 registrado e rejeita marcadores ausentes, repetidos ou fora de ordem. O workflow versionado chama a rota depois de persistir o Markdown, associa ligações literais aos achados, apresenta menções e ocorrências no relatório e valida suas citações contra o Markdown original.

O prompt foi atualizado para v6 e instrui explicitamente a IA a tratar o PDF, as evidências e as relações entre páginas como dados não confiáveis e ignorar comandos embutidos. A IA ainda analisa todos os lotes; a seleção de páginas ambíguas e o modo sem IA continuam pendentes. A lista de regras é limitada, não substitui a leitura integral e não comprova correção semântica.

Arquivos afetados:
`infra/regulatory_analysis/deterministic_context.py`, `infra/upload_gateway/app.py`, `workflows/automacao-regulatoria-internal-v1.json`, `prompts/regulatory-extraction-v6.md`, testes de análise regulatória, gateway e contrato de workflow, além de `PRD.md`, `README.md`, `AGENTS.md`, `ROADMAP.md`, `FLUXOGRAMA.md`, `workflows/README.md` e `deploy/README.md`.

Testes e verificações:
`python -m pytest -q` passou com 89 testes. O conjunto cobriu termos literais, processo repetido entre páginas, conteúdo repetido em páginas diferentes, marcadores inválidos, autenticação da rota interna, hash ausente/inválido/divergente, seleção da versão mais recente do Markdown, composição do workflow e inclusão das citações determinísticas no relatório. Foram usados somente fixtures sintéticos; não foram processados documentos reais, não foi chamada uma instância Ollama e não houve mudança na VPS. A suíte emitiu dois avisos de depreciação preexistentes do evento `on_event` do FastAPI.

Pendências:
Atualizar a VPS após backup, reconstruir o gateway, importar o export inativo preservando credenciais, validar o workflow de três páginas em homologação e confirmar com o fixture que o Ollama ignora comandos embutidos. Depois de medir a qualidade, decidir se deve existir um modo sem IA e se as chamadas ao modelo podem ser limitadas a passagens ambíguas.

Impacto:
O relatório passa a expor ocorrências de termos e identificadores com página e citação, e a síntese ganha ligações entre páginas sem aumentar paralelismo ou habilitar embeddings. O fluxo remoto permanece inalterado até homologação e implantação controladas.

## 2026-10-26 — Interrompe tentativa local e avalia NVIDIA API

Data: 2026-10-26
Tipo: OPERAÇÃO / INTEGRAÇÃO / BLOQUEIO
Status: tentativa local encerrada; processamento externo não iniciado

Contexto:
Durante o reprocessamento controlado de um PDF oficial, o usuário escolheu usar
a NVIDIA API em vez de aguardar a análise local. O PRD vigente restringe a
NVIDIA API Trial a testes com conteúdo artificial.

Decisão/Ação:
Foi verificado que a VPS não tem credencial NVIDIA configurada. O único workflow
NVIDIA disponível é a avaliação sintética, inativa e sem credencial; o registro
de proprietário do n8n continua sem e-mail e senha utilizáveis. A documentação
oficial da NVIDIA descreve os endpoints do NVIDIA Developer Program/API Catalog
como destinados a prototipagem e limita o acesso Trial a teste e avaliação; o
uso em produção depende de assinatura/licença apropriada. A licença da conta
NVIDIA do usuário não foi verificada. Nenhum PDF real foi enviado à NVIDIA e
nenhum requisito do PRD foi alterado.

A parada individual da execução não estava disponível sem sessão autenticada do
n8n. Como havia apenas uma execução n8n ativa, o contêiner Ollama do Miller foi
parado para interromper essa tentativa e em seguida reativado. O n8n registrou a
execução 16 como erro em `Ollama - Analyze each batch`. O PDF original, o
Markdown v1 e os artefatos anteriores foram preservados. Não foi gerado relatório
v2 nem enviado e-mail.

Arquivos afetados:
`ROADMAP.md` e `LOG.md`.

Testes e verificações:
Consultas operacionais confirmaram a execução 16 em erro, 3 documentos em
`aguardando_envio`, 6 em `erro`, nenhum em processamento e o contêiner Ollama
saudável após reinício. Foram conferidos os metadados de workflows e credenciais
sem ler ou exibir valores secretos. Não foram executados testes de aplicação nem
chamadas à API NVIDIA.

Pendências:
Configurar o proprietário do n8n por acesso administrativo seguro. Se o usuário
quiser seguir com NVIDIA, provisionar endpoint e assinatura/licença apropriados
para produção, revisar as condições de privacidade e guardar a credencial no
n8n. Executar primeiro o fixture sintético aprovado. Só então decidir se o PRD
deve mudar e reprocessar o PDF real. A chave Trial exposta anteriormente ainda
precisa ser revogada.

Impacto:
A análise local atual foi interrompida sem apagar entradas ou artefatos. O
processamento externo continua bloqueado até haver acesso NVIDIA de produção
configurado e autorizado; a rota Trial permanece restrita a conteúdo sintético.

## 2026-10-26 — Chave NVIDIA compartilhada no chat

Data: 2026-10-26
Tipo: SEGURANÇA / CREDENCIAL
Status: chave não utilizada; revogação pendente no portal NVIDIA

Contexto:
O usuário enviou uma chave NVIDIA pelo chat e pediu que fosse configurada no
projeto. O segredo ficou exposto no histórico da conversa.

Decisão/Ação:
A chave foi tratada como comprometida. Não foi copiada para arquivos, logs,
VPS ou credenciais do n8n e não foi usada para chamar a API. O valor não é
registrado neste histórico. A finalidade informada está relacionada à API
NVIDIA; o workflow disponível na VPS segue inativo e é restrito a fixture
sintético. Nenhum documento real foi transmitido.

Arquivos afetados:
`ACESSOS.md` e `LOG.md`.

Testes e verificações:
Não houve chamada à API NVIDIA nem alteração na VPS. Foi conferido somente o
estado Git e atualizado o registro de acesso sem incluir o segredo.

Pendências:
Revogar no portal NVIDIA a chave enviada pelo chat e confirmar se a chave
registrada como exposta em 03/10/2026 também segue ativa. Se for necessário
testar a API, gerar outra credencial e guardá-la diretamente no cofre n8n após
configurar o proprietário. Usar a API Trial apenas com fixture sintético; o
processamento de documentos reais depende de endpoint e acesso de produção
aprovados.

Impacto:
Nenhuma credencial exposta foi reutilizada ou instalada. A chave enviada deve
ser substituída antes de qualquer teste futuro.

## 2026-10-26 — Planeja integração NVIDIA NIM de produção

Data: 2026-10-26
Tipo: REGRA DE NEGÓCIO / PRIVACIDADE / INTEGRAÇÃO
Status: regra documental atualizada; endpoint externo não configurado

Contexto:
O usuário pediu para alterar as regras do projeto e adotar a NVIDIA API para
processar o PDF oficial selecionado. O ambiente só tem um workflow NVIDIA Trial
manual, inativo e sem credencial. A chave enviada pelo chat está comprometida.

Decisão/Ação:
O PRD e os guias passam a prever uma integração NVIDIA NIM de produção para
documentos reais, condicionada a endpoint e licença/assinatura apropriados,
permissão expressa para o tipo de dado, revisão de privacidade e autorização do
documento/destino. O processamento local por Ollama permanece como a
implementação atualmente implantada; a integração externa ainda não existe.

Os termos oficiais do NVIDIA API Trial (seções 2.6 e 4.3) restringem informação
governamental, confidencial e sensível sem permissão específica do serviço. A
seção 3.3 informa que conteúdo de usuário pode ser usado para melhoria de
produtos e modelos. A FAQ do NIM diferencia o acesso Developer para prototipagem
da licença NVIDIA AI Enterprise voltada à produção. Alterar regras locais não
altera esses termos. Por isso, a chave do chat não foi reutilizada, salva ou
chamada contra a API; nenhum conteúdo do PDF foi transmitido.

Fontes consultadas: [termos oficiais da NVIDIA API Trial](https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf) e [FAQ oficial do NVIDIA NIM](https://docs.api.nvidia.com/nim/docs/product).

Arquivos afetados:
`AGENTS.md`, `PRD.md`, `README.md`, `ROADMAP.md`, `FLUXOGRAMA.md`, `ACESSOS.md`,
`workflows/README.md` e `LOG.md`.

Testes e verificações:
Foram revisados os termos oficiais da API Trial e a FAQ do NIM, e o diff
documental foi conferido. Não foram executados testes de aplicação, chamadas à
NVIDIA, alterações na VPS ou processamento de documento.

Pendências:
Revogar a chave enviada no chat. Configurar o proprietário do n8n e provisionar
um endpoint/licença NVIDIA de produção cujos termos permitam o documento
governamental. Guardar a nova credencial no cofre n8n, validar primeiro com
fixture sintético e só então retomar o processamento autorizado do PDF. Não
usar API Trial para esse documento.

Impacto:
O projeto agora permite como objetivo uma integração externa NVIDIA de produção
com condições explícitas de privacidade e licença. O caminho real continua
local enquanto o endpoint não estiver configurado e homologado.

## 2026-10-27 — Implementa processamento híbrido determinístico e auditoria por IA

Data: 2026-10-27
Tipo: ARQUITETURA / IMPLEMENTAÇÃO / TESTE / DOCUMENTAÇÃO
Status: implementado localmente; ainda não implantado na VPS

Contexto:
Foi escolhida uma primeira passagem em Python sem IA, seguida por uma auditoria
da IA para procurar lacunas e uma síntese interpretativa final. A meta é
registrar observações com evidência rastreável e impedir que citações inventadas
entrem na síntese sem conferência mecânica.

Decisão/Ação:
O contexto determinístico passou a registrar identificadores, termos, datas e
durações literais em formatos conhecidos, incluindo a linha de origem e a
versão das regras. O gateway recebeu a rota autenticada
`POST /internal/submissions/{id}/validate-ai-audit`, que relê o Markdown
persistido, confere o hash e separa candidatos aceitos de pendentes conforme a
página, lote e citação literal. O workflow v2 inativo audita todos os lotes com
IA e envia para a síntese final apenas as observações e candidatos aceitos.
Candidatos pendentes são excluídos do prompt final.

O fluxo continua usando IA para procurar lacunas em todos os lotes e para
interpretar o relatório. A validação Python localiza citações; não comprova a
correção semântica dos fatos ou da interpretação. O export v1 foi preservado,
nenhum workflow foi ativado e nenhum documento oficial foi processado.

Arquivos afetados:
`infra/regulatory_analysis/deterministic_context.py`,
`infra/regulatory_analysis/report_validation.py`,
`infra/upload_gateway/app.py`, testes de análise, API e contrato n8n,
`workflows/automacao-regulatoria-internal-v2-hybrid.json`,
`prompts/regulatory-gap-audit-v1.md`,
`prompts/regulatory-gap-audit-v1.schema.json`, `PRD.md`, `README.md`,
`AGENTS.md`, `ROADMAP.md`, `FLUXOGRAMA.md`, `workflows/README.md` e `LOG.md`.

Testes e verificações:
`python -m pytest -q`: 94 testes aprovados. O teste foi realizado com fixtures
sintéticos; nenhum PDF real foi enviado a modelo ou serviço externo. O JSON do
workflow v2 foi validado. A execução exibiu dois avisos de depreciação do
evento `on_event` do FastAPI. Não houve acesso à VPS.

Pendências:
Revisar o diff e depois planejar backup, importação do export v2 preservando as
credenciais, e homologação com fixture sintético em ambiente controlado. A
última verificação disponível da VPS, em 26/10/2026, indicava v1 ativo; o v2
permanece apenas local e inativo. Não processar o PDF oficial nesta etapa.

Impacto:
O Python cobre a primeira passagem de menções conhecidas e valida as citações
dos candidatos produzidos pela IA. A cobertura das regras é limitada; a
auditoria por IA continua necessária e a revisão humana continua disponível.

## 2026-10-27 — Publica o v2 e executa homologação ponta a ponta

Data: 2026-10-27
Tipo: IMPLANTAÇÃO / TESTE / QUALIDADE
Status: workflow v2 publicado; teste técnico concluído; qualidade do relatório reprovada para uso real

Contexto:
O usuário concluiu a criação do proprietário do n8n e confirmou a troca do workflow ativo e o teste sintético. O repositório local e a VPS estavam um commit atrás antes da atualização.

Decisão/Ação:
O commit `a5e036c` foi enviado para `main` e sincronizado na VPS. Foi feito backup protegido do PostgreSQL, do volume de artefatos e dos cinco workflows antes da importação. O proprietário foi criado no painel; a senha foi definida pelo usuário e não foi copiada para chat, Git ou documentação. O v1 foi despublicado e o v2 híbrido publicado; o workflow de erros permaneceu ativo. Envio manual e reconciliação continuaram inativos.

Um PDF totalmente sintético de duas páginas foi enviado pelo gateway, processado pelo Ollama local `qwen2.5:3b` e concluído na execução n8n 18, protocolo `e6904fac-45c8-4321-a53b-cf296e4df23d`, estado `aguardando_envio`. A conversão cobriu as duas páginas; o registro da tentativa não tem erros; não houve entrega ou e-mail. A frase de injeção do fixture não levou à revelação de segredos.

A validação das referências confirmou 8 de 10; duas ficaram pendentes por formato não reconhecido. O relatório não reconheceu a concessão seguida do cancelamento, recomendou cronograma de renovação depois do cancelamento e colocou as seções fora da ordem. O PDF mostra âncoras Markdown sem resolução. A homologação técnica passou, mas a qualidade do relatório não foi aprovada para uso real.

Arquivos afetados:
`docker-compose.yml`, `.env.example`, `ROADMAP.md`, `ACESSOS.md`, `workflows/README.md`, `LOG.md` e artefatos em `output/e2e-sintetico-20261027-e6904fac/`.

Testes e verificações:
`python -m pytest -q`: 94 aprovados, dois avisos de depreciação do FastAPI. `docker compose config --quiet` passou localmente e na VPS. Os seis containers Miller estavam saudáveis após o teste. O relatório PDF foi renderizado e conferido visualmente: legível e sem corte, mas com ordem e âncoras incorretas.

Pendências:
Corrigir a síntese e a validação estrutural do relatório, incluir regressões para mudança de status entre páginas, referência pendente e ordem das seções, e repetir este fixture antes de processar documento real. Confirmar a guarda da senha do proprietário, rotacionar a senha root exposta e revogar as chaves NVIDIA expostas. Testar restauração de backup, publicar a landing com HTTPS e homologar separadamente envio manual e reconciliação. Nenhum PDF real foi processado nesta tarefa.

Impacto:
O v2 está ativo na VPS; o v1 permanece disponível no repositório/backup para rollback. Os relatórios atuais devem ser tratados como rascunho sujeito a revisão, não como resultado aprovado.

## 2026-10-29 — Modo local autorizado para gerar somente Markdown

O usuário solicitou implementar a geração de arquivos .md para simulações
manuais posteriores, após limpar os experimentos anteriores. Decisão: uma
interface local de upload/conversão/download reutiliza o conversor existente,
sem depender de n8n, PostgreSQL, Ollama, API de IA ou credencial. O serviço e
Compose de teste ficam separados do caminho operacional; o workflow completo
e os estados de documentos da landing não serão alterados.

O arquivo exportado é texto-fonte paginado, não relatório regulatório nem
análise concluída. Deve preservar o corpo convertido, SHA-256 do PDF, versão,
metadados seguros e avisos explícitos antes das páginas. Não há OCR; falha ou
ausência de texto não significa ausência de informação. A aplicação não envia
nada ao ChatGPT: o operador decide sobre compartilhamento de material autorizado.
Integração futura com API OpenAI e escolha de modelo permanecem fora desta etapa.

O modo local não substitui a entrada oficial pela landing, não registra
protocolos, não envia e-mail e não constitui novo painel administrativo.
Publicação somente em 127.0.0.1:18080, sem volumes do ambiente operacional.
Skill global karpathy-guidelines indisponível; aplicadas as regras do repositório.
Implementação e testes em preparação; nenhum resultado histórico será tratado
como validação atual. Não houve contratação, acesso remoto, commit ou push.

## 2026-10-29 — Modo local Markdown implementado e validado

Criados local_app.py e três recursos estáticos do conversor, Compose exclusivo
em deploy/markdown-local e proteção .dockerignore contra envio de temporários,
metadados Git e configurações locais ao contexto de build. O conversor legado
e sua API, o Compose principal, os workflows e a landing não foram alterados.
PRD RF-20, README, fluxo, roadmap e guia do conversor registram o novo caminho
local separado, sem promover a API OpenAI ou qualquer modelo.

Tela com upload até 100 MiB, conversão única por vez, prévia texto puro e
download completo UTF-8. Arquivo contém metadados JSON-quoted, notas locais,
avisos e corpo paginado preservado. PDF inválido/sem texto, excesso de tamanho,
conversão concorrente ou falha interna não produz resultado válido. Uploads
são fechados. Hosts/origens externos são rejeitados, sem CORS, telemetria,
credenciais ou biblioteca de terceiros no navegador. Não é interface pública.

Validação final: 115 testes Python passaram (37 novos de API local e um de
isolamento do Compose), além de 21 testes JavaScript da interface. Três avisos
de depreciação Starlette/AnyIO/FastAPI, sem falhas. O teste documental que fixava
a manutenção do roadmap em 08/10 passou a conferir uma data explícita, mantendo
as exigências da data histórica de consulta à VPS, que não foi consultada.
Ambiente de teste temporário isolado em /tmp, Python 3.12, com requisitos dos
serviços instalados, sem mudar o Python global. TestClient precisou sair da
restrição de rede do sandbox; não acessou a VPS ou uma API externa.

Build Docker, health check e configuração do Compose aprovados. Um PDF público
local de uma página percorreu upload, conversão e download pelo navegador;
hash do Markdown baixado conferido com o mostrado na tela. A extração herdada
tem caracteres de controle no cabeçalho dessa fonte; por isso foi acrescentado
um aviso explícito no exportador, sem remover ou corrigir texto silenciosamente.
Três regressões verificam preservação do corpo/hash e ausência de mutação do
resultado original. A imagem local foi reconstruída com esse aviso.

Teste HTTP final com o DOU público local de 100 páginas: HTTP 200 em 49,449 s,
1.314.196 bytes de Markdown, sequência de páginas 1–100, hashes do PDF e do
Markdown conferidos, zero avisos nessa fonte. Não é homologação de fidelidade
visual, de conteúdo regulatório, do documento do cliente ou da meta de 90 min;
mede somente conversão/exportação local, sem IA, relatório ou PDF final.

O contêiner exclusivo miller-markdown-local-markdown-local-1 ficou saudável em
127.0.0.1:18080 para os testes do usuário. Não há volumes operacionais montados;
outros serviços não foram reconfigurados ou parados. O arquivo de teste baixado
pelo navegador ficou em Downloads. O encerramento documentado afeta somente
esse projeto Compose. Nenhum documento enviado ao ChatGPT/NVIDIA/OpenAI, nenhum
e-mail, segredo, serviço pago, commit ou push. git diff --check aprovado.

## 2026-10-31 — Correção isolada dos scripts da entrega manual V5

Após a auditoria da entrega manual, o usuário autorizou seguir ao próximo passo.
Decisão: corrigir os scripts fornecidos no ZIP em cópia local isolada, adicionar
regressões reais e sintéticas e gerar uma entrega reproduzível. Não integrar
essas regras específicas da edição na aplicação, nem substituir o prompt ou
workflow operacional. ZIP original e fonte preservados; nenhum envio externo.
Skill PDF aplicada para renderização e revisão; karpathy-guidelines global
indisponível, mantidas as regras pertinentes do repositório.

Corrigidos pertencimento de composição por produto, vacinas, CNPJ em linhas
separadas, rótulos de certificação com caixa variável, expedientes de AFE,
fronteiras de artigo, escopo farmacêutico explícito e preservação de motivos,
ausências e divergências. O validador agora reprova os erros conhecidos da V5
original, além de composição com CNPJ e identidade explícita omitida ou no
papel errado. A revisão independente encontrou essas duas classes adicionais
antes da entrega; foram corrigidas e cobertas por regressões. Não foram
completados dados por suposição nem ajustados nomes de empresas na regra.

Execução final: 144 testes aprovados, sem skips, com um aviso de depreciação do
ReportLab. G1–G8 aprovadas; 710 eventos incluídos e 320 excluídos; preservadas
310 apresentações. PDF de 304 páginas, 919721 bytes, 710 links distintos
reconciliados e 7118 campos conferidos na própria ficha. Revisão visual
assistida por IA em 13 páginas críticas sem cortes/sobreposições nas amostras.
Reextração independente igual ao JSONL publicado, sem os objetos internos de
linhas. Hashes dos oito scripts, fonte, dados e PDF conferidos com o recibo.

SHA-256 da fonte Markdown:
a4a5cfce74a2950c04404d559990eefdf4122eb4639234e3961564cec5c2ad30.
SHA-256 do PDF final:
33964c39de4fbcd9e196e7dab480a6c82306c4cc9c42d451c5d277beee9dc874.
As saídas e o pacote são artefatos locais não versionados em output/pdf;
código experimental e resultados intermediários ficam em tmp/anvisa-v5-corrigida.
Nenhum documento privado ou artefato deve ser incluído em commit.

Limites: parser baseado nos formatos desta edição do DOU de 01/06/2026, fonte
de análise exclusivamente Markdown, sem OCR nem conferência visual integral
contra o PDF original. Avisos de tabelas nas páginas-fonte 122/123 mantidos.
Casos conhecidos aprovados não significam homologação individual dos 710
eventos. Há refinamentos não bloqueantes de apresentação; aceite do cliente
e revisão do original continuam pendentes.

O pipeline local levou 68,952 segundos, já partindo do Markdown e incluindo
testes/verificações/renderização. Não mede conversão do PDF original, IA, API,
Ollama, VPS, n8n ou cumprimento da meta operacional de 90 minutos. Não houve
acesso remoto, mudança da aplicação/infraestrutura, uso de credenciais,
contratação, commit ou push nesta etapa. ROADMAP registra a validação limitada
e o próximo aceite, sem alterar requisitos do PRD.

Pacote final com 37 arquivos, manifesto de hashes e integridade ZIP conferida.
Após extração em outro diretório temporário, os mesmos 144 testes passaram
novamente em 24,70 segundos, usando somente o runtime local já disponível.
Nenhum ambiente virtual, segredo ou resultado intermediário foi empacotado.
git diff --check aprovado; alterações locais anteriores preservadas.

## 2026-10-31 — Esclarecimento do objetivo e prompt manual Anvisa V6

O usuário esclareceu que precisa melhorar e testar o prompt para depois
adicionar a camada de IA, não corrigir os scripts gerados na rodada V5. A
entrega anterior corrigiu scripts, mas não corrigiu nem validou o prompt para
esse objetivo. O histórico e os artefatos anteriores foram preservados como
experimento separado, sem apresentá-los como avaliação de um modelo/prompt.

Lido o prompt V5 original da entrega manual e contrastado com as falhas
auditadas. Criados prompts/chatgpt-anvisa-pdf-v6.txt e o guia de teste separado.
A V6 retira a obrigação de programar parser, verificador e suíte durante a
análise. Prioriza interpretação pela IA, fronteiras e papéis por evento,
composição própria, artigos decisórios completos, escopo farmacêutico explícito,
evidências e ausência distinta de falha. Ferramentas locais podem apoiar
leitura, armazenamento, conferências mecânicas e geração do PDF.

Revisão independente das instruções corrigiu ambiguidades sobre composição
compartilhando linha com identificadores e múltiplos papéis na certificação.
O prompt não contém nomes, páginas ou contagens da edição como metas. Casos
reais conhecidos ficam apenas no guia externo de conferência, não na entrada
da geração. Índice inicial, PDF e dados/cobertura/verificação da mesma rodada
permitem avaliar o resultado futuro sem depender apenas da aparência do PDF.

Aplicada OpenAI Docs e consultada documentação oficial de prompting para
separar objetivo, instruções, fonte, saída e avaliação. A skill global
karpathy-guidelines não está disponível. Não houve chamada de modelo/API,
envio de documento, geração de novo PDF ou alteração da aplicação, workflow,
infraestrutura, credencial ou contrato ativo regulatory-extraction-v5.md.

Estado: candidato revisado documentalmente, ainda NÃO executado/validado no
ChatGPT. Os 144 testes do experimento anterior validam scripts, não a V6.
Próximo passo: nova conversa com Markdown original autorizado e prompt V6;
conferir arquivos resultantes, regressões e amostras fora dos casos usados no
ajuste. Após uma rodada satisfatória e aceite, validar outro documento antes
da integração. O guia registra que ChatGPT/API e a renderização exigem testes
próprios; não foi contratado nem integrado provedor nesta tarefa.

Checagens desta etapa: texto UTF-8, nomes dos quatro arquivos consistentes,
links locais existentes, exemplo estrutural JSON válido, presença das regras
de evidência/cobertura/ausência e ausência de gabarito real no prompt. São
verificações estáticas das instruções, não avaliação do comportamento da IA.
SHA-256 do prompt V6:
492c05e6ea8e4bd11a02391d19e7edeb42126501dd8aeb45b91b37a58bd31cb3.
git diff --check aprovado. Suíte da aplicação não executada nesta tarefa
documental; mudanças preexistentes preservadas, sem commit ou push.

## 2026-10-31 — Auditoria da entrega V6 e revisão do prompt manual V7

Recebido anvisa_v6_arquivos.zip com PDF, JSONL, cobertura e verificação da rodada
manual. A fonte declarada coincide com o Markdown autorizado da comparação.
Auditoria: PDF de 72 páginas, 132 fichas incluídas/links com destinos corretos,
163 registros no JSONL e 1603 evidências localizadas literalmente na página
de origem. Esses controles não comprovaram completude semântica. A entrega
declarou somente quatro das 198 páginas integralmente analisadas; parte das
outras páginas teve blocos revisados. Não houve falsa alegação de cobertura total.

Falhas comprovadas: identificação/localização de unidades omitida em eventos
incluídos, dispositivos de prorrogação e fundamentos clínicos cortados, evidência
de retificação insuficiente no próprio campo da decisão. As perdas já existiam
nos registros de análise; corrigir somente o PDF não resolveria. A rodada não
foi aprovada como entrega final nem como validação concluída do prompt.

A pedido explícito do usuário, criada a candidata prompts/chatgpt-anvisa-pdf-v7.txt
com guia separado. Preservados os arquivos V6. Acrescentadas conferência inversa
fonte -> ficha, identificação de unidades por papel, fechamento semântico de
dispositivos/fundamentos, antes/depois com evidências, checkpoints cumulativos
por bloco e distinção entre cobertura e integridade. O PDF deve preservar os
dados das unidades; contexto comum completo pode ser referenciado por várias
fichas, sem repetir o texto integral em todas. Índice diferencia assuntos genéricos.

O prompt principal não contém empresas, páginas ou quantidades do corpus como
gabarito. As regressões ficam no guia externo, que não deve acompanhar a entrada
da geração. Nova execução parte do Markdown original; retomadas reaproveitam
apenas checkpoints da mesma V7, conferidos contra a fonte. O usuário executará
o teste no ChatGPT; não houve chamada de modelo ou envio de documento nesta revisão.

OpenAI Docs aplicada para estrutura e avaliação com documentação oficial.
karpathy-guidelines indisponível; seguidas as regras pertinentes do repositório.
Escopo exclusivamente documental/manual: PRD, aplicação, contrato ativo,
workflows, modelo, infraestrutura e credenciais não alterados por esta revisão.
O experimento permite checkpoints parciais identificados; isso não altera o
bloqueio de relatório parcial por falha técnica no fluxo operacional do PRD.

Estado da V7: candidata para teste, não homologada. Próxima rodada deve verificar
regressões, amostras fora dos casos conhecidos, cobertura e correspondência dos
quatro artefatos; documento separado e aceite do cliente continuam pendentes
antes da futura integração. Mudanças locais preexistentes preservadas.

Verificações documentais: revisão independente das instruções, UTF-8, exemplo
estrutural JSON válido, nomes dos quatro artefatos consistentes, links locais do
roadmap existentes e ausência de empresas/hash da fonte no prompt principal.
Revisão corrigiu a divisão de tabelas entre eventos completos e a reconciliação
das páginas vazias. Hash da V6 permanece inalterado. git diff --check aprovado.
Não houve execução da V7 pelo modelo, geração de relatório ou suíte da aplicação
nesta tarefa; nenhum commit ou push. SHA-256 do prompt V7 (31536 bytes):
dd1b9fb55fb028bec518541b58562b913faa81d238695d152a317b65166756d2.

## 2026-10-31 — Auditoria V7 e correção da ordem de leitura na aplicação

Recebido o ZIP V7 do teste manual. A auditoria encontrou PDF de 39 páginas,
81 fichas incluídas e cobertura ainda parcial (quatro páginas integralmente
analisadas). Os suplementos da continuação das páginas 114/115 foram vinculados
à RE 2.140/deferimento, embora pertençam à RE 2.143/cancelamento. A fonte
intermediária da aplicação já colocava RE 2.140/DANISCO depois das RE 2.141,
2.142 e 2.143: a extração seguia a ordem interna dos objetos, não a leitura visual.
O resultado da IA não foi aprovado e esse diagnóstico não é autorização para
inventar vínculos a partir de contexto incompleto.

O usuário autorizou corrigir a geração do Markdown na aplicação e depois
retestar o mesmo V7. Implementado conversor `0.4.0`, sem novas dependências:
extração de palavras por coordenadas com pdfplumber, cortes espaciais de regiões,
leitura de colunas, tabelas com grade tratadas como objetos indivisíveis e
tratamento conservador de células curtas alinhadas sem bordas. O algoritmo
não contém regras de empresas, atos ou páginas desta edição. Há verificações
de preservação de caracteres antes/depois da reorganização, liberação do cache
por página e fallback explícito com pypdf quando a geometria não puder ser usada.
Avisos de ordem/ambiguidade aparecem também na própria página do Markdown,
identificados como notas da ferramenta. O exportador local continua em `0.1.0`.

PRD RF-03 explicita o critério de ordem visual e rastreabilidade de novas versões.
Guia V7 e ROADMAP passam a exigir novo Markdown do mesmo PDF, em nova conversa,
sem reaproveitar checkpoints do hash antigo. O prompt V7 permaneceu byte a byte
inalterado; não foi criado V8 nem corrigido manualmente o documento fonte.
PDF original e Markdown antigo preservados. Nenhuma mudança no n8n, VPS,
credenciais, provedor ou prompt operacional; nenhuma chamada de IA ou e-mail.

Validação da implementação: 129 testes Python aprovados (incluindo 14 regressões
novas de leitura) e 21 testes JavaScript aprovados. A suíte Python apresentou
três avisos de depreciação das dependências/eventos existentes; não são falhas
de conversão. Build e Compose local validados. A primeira tentativa da suíte
ficou bloqueada no sandbox e foi interrompida; a execução local autorizada fora
desse isolamento concluiu. Um monkeypatch de teste foi ajustado à nova assinatura
do extrator antes da aprovação final. A revisão também corrigiu uma mensagem
que afirmava preservação antes de confirmar o sucesso do fallback: erro e retorno
vazio agora têm aviso próprio, coberto por duas variantes de teste. Não foram
alteradas dependências do projeto.

Revisão independente nas páginas 114, 115, 122 e 123: 37 âncoras sequenciais de
atos/conteúdos corretas; multiconjunto de caracteres não brancos conferido contra
a camada textual do PDF, sem perda/acréscimo nas quatro amostras. Inspeção visual
da fonte e revisão de conteúdo incluíram suplementos, retificações, continuidade
de atos, processos clínicos e tabelas de largura inteira. Isso não constitui
conferência semântica integral das 198 páginas nem homologação de qualquer PDF.
Tabelas sem bordas complexas, elementos sobrepostos e layouts não exercitados
permanecem sujeitos a conferência. Skill PDF utilizada para comparação visual;
karpathy-guidelines indisponível, mantidas as regras pertinentes do repositório.

Verificação desta versão autossuficiente: duas revisões independentes sem
bloqueantes; UTF-8, exemplo JSON, nomes das saídas, links e git diff --check
conferidos. Busca de dependências V7 e localizadores da edição no prompt sem
ocorrências. Hashes da V7, complemento V8, guia histórico, contrato operacional
e Markdown preservados. Prompt novo: 38.462 bytes, SHA-256
3e75a9619a9cd5e7ce7080b22faad815148172cd0ffe30aa9db85e3b43b804e7.
Não houve execução pelo modelo, geração de relatório ou teste de aplicação
nesta tarefa; os arquivos estão preparados para o teste manual do usuário.

A amostra adicional das páginas 113, 116, 144 e 145 não revelou troca de atos ou
entidades, mas encontrou palavras unidas em linhas comprimidas. Ajustada a
tolerância horizontal à fonte (`x_tolerance_ratio=0.2`), inclusive nas tabelas
suplementares. Comparação com 0.15/0.1 em seis páginas produziu as mesmas
separações; mantido o maior limiar que resolveu os casos. Identificadores foram
preservados nas amostras e o novo teste sintético de palavras separadas por
dois pontos falhou antes e passou depois do ajuste. As conversões exploratórias
foram interrompidas ao reconstruir o contêiner; não foram entregues como
artefatos concluídos. Não confundir preservação de caracteres com prova de
espaçamento, vínculos semânticos ou cobertura regulatória integral.

Conversão integral concluída pela API da aplicação local, na imagem reconstruída:
HTTP 200 em 674,182534 segundos, 198 páginas, 2.173.841 bytes de Markdown,
marcadores consecutivos 1–198, hashes conferidos. Fonte PDF preservada com
SHA-256 10ab4a9643e68640b3d420920e33453d003b2a4da452a3e8e8df6747aa68f58f.
Novo Markdown: c0438df8900bcd7179cf20f4c0468ea55c877d0c01fb92efce0169cdc66c0514.
O hash antigo a4a5cfce74a2950c04404d559990eefdf4122eb4639234e3961564cec5c2ad30
permanece inalterado. Prompt V7 também preservado:
dd1b9fb55fb028bec518541b58562b913faa81d238695d152a317b65166756d2.

Mantidos 89 avisos no artefato: 86 possíveis tabelas preservadas em texto e
três tabelas estruturadas detectadas automaticamente. Não houve página sem
texto, falha de extração ou fallback na conversão completa. Conferidas no
arquivo exportado as sequências de atos das páginas 114/115/122/123 e a
separação de palavras da apresentação comprimida na página 116. O tempo medido
é somente conversão/exportação nesta máquina: não mede IA, VPS ou meta total
de 90 minutos. Antes de implantar no workflow, reavaliar recursos e
PDF_CONVERTER_TIMEOUT_SECONDS (padrão de 300 s no export; não modificado aqui).

Entregues como artefatos locais não versionados, sem incluir o PDF original no
repositório: output/markdown/2026_06_01_ASSINADO_do1_colunas_v040.md e
output/markdown/validacao_conversao_v040.json. Aplicação local permanece em
127.0.0.1:18080. Próximo passo: usuário executar o mesmo V7 em conversa nova
com o novo Markdown e retornar os quatro arquivos da mesma revisão. A V7
continua não homologada. Sem commit ou push; mudanças preexistentes preservadas.

## 2026-11-01 — Auditoria do checkpoint V7 final e complemento corretivo V8

Recebido anvisa_v7_documentos_finais.zip, revisão v7-cp027-20261101, ligado ao
Markdown corrigido de hash c0438df8900bcd7179cf20f4c0468ea55c877d0c01fb92efce0169cdc66c0514.
Pacote com 1.685 registros (710 incluídos, 972 excluídos, 3 representações
duplicadas) e PDF de 414 páginas. A declaração de 198 páginas analisadas não
foi aceita como prova de completude. Encontradas nove certificações de
medicamentos omitidas na continuação do anexo da RE 2.175, fonte página 146,
entre NOVONORTE e RE 2.225, apesar de o texto estar legível no Markdown.

Outros achados: artigos de vigência ausentes nas RE 2.233/2.127; campo de
escopo DECARES marcado como limitação embora legível; inclusão Takeda com
escopo farmacêutico não demonstrado no trecho; 34 notas de cobertura
incompatíveis com o estado analisada; hash do PDF diferente do registrado
no TXT. Hash real do PDF recebido:
b1cf6de3c1663ffe0d3eba9b34132810d8adfcccbec0c6367c8f1e42438ba080.
As falhas de suplementos e evidência própria do OZIVY foram corrigidas nessa
rodada. Não houve nova falha comprovada do conversor nesses casos.

Conferências independentes da rodada recebida: 12.433 trechos de evidência
localizados literalmente na página declarada; 710 links com ID/destino correto;
9.352 valores não nulos encontrados na própria ficha do PDF, após normalização
de espaços/caixa e remoção de cabeçalhos/rodapés interpostos; 58 dispositivos
distintos preservados. Inspeção visual de 22 páginas sem cortes físicos ou
sobreposições nas amostras. Checagens mecânicas e amostras semânticas não
homologam as 710 fichas; as nove omissões impedem o aceite como entrega completa.

O usuário solicitou V8 como instrução complementar, para usar na mesma conversa
e corrigir a saída antes de integrar IA. Criados prompts/chatgpt-anvisa-pdf-v8.txt
e prompts/LEIA_ME-chatgpt-anvisa-v8.txt. A V8 depende da V7 e do checkpoint da
mesma fonte; preserva IDs anteriores, arquivos de origem e regras não alteradas.
Acrescenta reconciliação de unidades da fonte com destinos/IDs, fechamento de
continuações sem saltos, correções localizadas, cobertura sem notas obsoletas,
separação do histórico e da reconferência V8 e hash do PDF efetivamente entregue.

Decisão explícita para esta rodada: incluir no complemento os localizadores
das falhas conhecidas para reparar o documento já processado. Eles são pistas
a conferir, não dados para copiar nem metas de contagem. Isso difere do teste
inicial sem gabarito do prompt-base V7; resultado corretivo não pode ser
apresentado como avaliação independente de generalização. Depois do reparo,
consolidar regras gerais e validar outro documento autorizado sem essas pistas.

OpenAI Docs utilizada para estruturar objetivo, contexto, correções e saídas,
preservando as instruções-base. karpathy-guidelines continua indisponível.
Esta é mudança documental/manual: sem alteração de requisitos operacionais
do PRD, contrato regulatory-extraction-v5.md, aplicação, fonte, conversor,
infraestrutura, modelos ou credenciais. ROADMAP atualizado, preservando as
etapas anteriores como histórico. Nenhuma execução do V8 ou chamada de IA
externa foi realizada nesta preparação; V8 permanece candidata não homologada.

Validação documental desta preparação: duas revisões independentes do V8 e
guia; incorporadas a distinção explícita de destino pendente por ambiguidade
e a ordem acíclica de fechamento dos hashes PDF/JSONL, cobertura e verificação.
Conferidos UTF-8, término de linha, nomes dos quatro arquivos/ZIP e links novos
do ROADMAP. git diff --check sem erros. Hashes da V7, Markdown-fonte e contrato
operacional V5 conferidos e preservados. SHA-256 do complemento V8 final:
6b795f9f5cecbe0b9aa6ee034d183cf9a96e861a66cba37441536b94346d2815.
Não foram executados testes da aplicação, pois esta etapa não mudou código;
essas verificações documentais não validam a saída futura do modelo.

## 2026-11-01 — V8 autossuficiente para teste com somente dois arquivos

O usuário relatou que o ChatGPT interrompeu a execução do complemento V8 por
falta do prompt e dos quatro artefatos V7. A interrupção correspondia ao contrato
do complemento, mas não ao teste desejado pelo usuário, que esclareceu a entrada
de somente prompt + Markdown. Não é falha da aplicação ou corrupção da fonte.

Criado prompts/chatgpt-anvisa-pdf-v8-autossuficiente.txt, reunindo o conteúdo
completo da V7 e os reforços gerais da V8: inventário direto da fonte e reconciliação
de unidades/continuações, artigos de vigência, escopo com evidência própria,
ambiguidade distinta de omissão, cobertura consistente, referências a contexto
comum e fechamento acíclico dos hashes dos quatro artefatos. A análise inicia
do zero; todos os controles são saídas. Nenhuma dependência de V7, resultados,
ZIP, revisão cp027, hash predefinido ou histórico da conversa. Progresso criado
na própria execução pode apoiar continuação, sem exigir outros anexos ao usuário.

Retirados do prompt principal os localizadores específicos dos erros desta
edição; permanecem no histórico/guia para auditoria externa à geração.
Isso não torna a edição inédita para avaliação: ela já orientou os ajustes.
Nenhum ganho de completude, desempenho ou generalização foi demonstrado ainda.

Complemento V8 anterior preservado byte a byte. Seu guia foi preservado em
prompts/LEIA_ME-chatgpt-anvisa-v8-complementar-historico.txt; o guia principal e
ROADMAP indicam apenas a versão autossuficiente para o próximo teste. O segundo
arquivo de entrada é o Markdown já existente da aplicação, sem reconversão,
edição ou criação de uma fonte substituta. Contrato operacional, PRD, código,
infraestrutura e credenciais não foram alterados nesta tarefa. OpenAI Docs
utilizada para preservar instruções e esclarecer entradas/saídas; skill
karpathy-guidelines indisponível, mantidas as regras pertinentes do repositório.

## 2026-11-10 — Decisão: integrar o V8 autossuficiente com Terra no OpenRouter

O usuário informou o aceite do PDF revisado pelo cliente e autorizou integrar
o V8 autossuficiente ao fluxo da aplicação, com Terra no OpenRouter. O aceite
informado refere-se ao PDF revisado; a API e os novos resultados requerem
validação própria. O prompt aprovado deve permanecer byte a byte inalterado.

O modo OpenRouter será selecionado explicitamente no servidor. A fonte enviada
será apenas o Markdown paginado, sem PDF bruto, protocolo ou credenciais no
conteúdo. A aplicação vai persistir a saída no fluxo existente e gerar o PDF
com índice inicial e fichas. A chave fica no ambiente protegido; sem chave ou
em caso de falha não há troca automática para outro provedor. O teste local
usa documento artificial e não ativa workflows na VPS.

## 2026-11-10 — Fluxo Anvisa V8 implementado e testado localmente

Após persistir o Markdown, o export interno seleciona o provedor configurado.
Em `openrouter`, o renderizador autenticado envia o prompt V8 original e as
páginas da fonte ao `openai/gpt-6.1-terra`. Processa os blocos em ordem, amplia
o contexto para continuações e subdivide saídas truncadas sem descartar páginas.
Valida páginas, IDs, evidências literais e inventário; gera o relatório com
índice inicial e fichas, confere os destinos dos links e fecha o ZIP com os
quatro arquivos V8. A conclusão operacional continua depois da persistência
do PDF; a entrega por Gmail permanece manual. O export anterior continua
disponível no histórico do Git em `911d0ef`.

O hash do prompt não mudou:
`3e75a9619a9cd5e7ce7080b22faad815148172cd0ffe30aa9db85e3b43b804e7`.
O modo Ollama continua disponível com seleção explícita no ambiente; não há
troca automática quando a opção OpenRouter falha. A chave é passada somente
ao serviço renderizador e não é incluída no export nem no conteúdo enviado.

Validação final local: 81 testes Python aprovados, incluindo PDF sintético de
oito páginas convertido, chamadas do Terra simuladas, divisão por truncamento,
continuação com contexto anterior, correção de evidência, dois links de
petições, leitura do PDF e identidade do PDF no ZIP. As duas páginas do
relatório de teste foram inspecionadas visualmente. Os nós JavaScript de seleção
e preparação foram exercitados com dados simulados; os dois arquivos Compose
e `git diff --check` passaram. Nenhuma chave OpenRouter estava configurada,
portanto não houve chamada real, teste integrado no n8n, envio ou implantação
na VPS. Qualidade, tempo e custo com o Terra real permanecem por validar.

`output/` fica fora do Git e do contexto Docker. Prompts históricos e testes
avulsos foram preservados localmente em `output/historico-integracao-v8-20261110/`
com manifesto de hashes. O V8 autossuficiente e as regressões automatizadas
dos contratos alterados foram mantidos. Aplicadas a skill PDF e as orientações
publicadas de `karpathy-guidelines`, sem instalar a skill global ausente.

## 2026-11-11 — Preparação da stack completa local com OpenRouter

O usuário solicitou subir a stack completa no computador local para testar o
fluxo com OpenRouter. A instalação foi preparada na branch existente
`feature/performance-test`, sem modificar exports versionados ou a VPS.
A skill global `karpathy-guidelines` continuava indisponível nos diretórios
locais consultados; foram mantidos escopo mínimo, preservação de configuração
e validação dos resultados observáveis.

Criado `deploy/full-local/compose.yml` como complemento do Compose principal:
projeto `miller-full-local`, landing em `127.0.0.1:18085`, n8n em
`127.0.0.1:25678`, cookie adequado ao HTTP local e volume de artefatos próprio.
Banco, n8n e Ollama também usam os volumes do projeto local. O perfil RAG não
foi iniciado. A configuração anterior do `.env` foi preservada em arquivo
ignorado e protegido; a chave OpenRouter preexistente foi mantida. Valores de
exemplo necessários à inicialização foram substituídos por segredos gerados
localmente e URLs internas, sem exibir valores.

O usuário escolheu gerar a senha da landing e guardá-la em arquivo local
protegido. Os acessos da landing e da conta administrativa do n8n ficaram em
`.env.local-access`, com permissão `600`; a aplicação recebeu somente o hash
PBKDF2 da senha. O `.env` e sua cópia anterior também ficaram com permissão
`600`. A credencial PostgreSQL foi cadastrada diretamente no cofre do n8n.

Os quatro exports internos foram importados a partir de cópias temporárias,
com referência à credencial PostgreSQL local. Processamento e erros foram
publicados por CLI; o n8n foi reiniciado e a publicação foi conferida pela API.
Envio manual e reconciliação permaneceram inativos conforme o procedimento
local. Nenhuma credencial Gmail foi configurada e nenhum e-mail foi enviado.

Validação atual: build das três imagens da aplicação concluído; Compose válido;
seis serviços saudáveis; HTTP 200 nos endpoints de saúde, login da landing e
painel autenticado; cookie HttpOnly conferido; 15 testes de contrato de
implantação aprovados. Um PDF artificial inválido foi recebido com HTTP 202,
despachado ao n8n e terminou em `erro`, com uma tentativa e um registro de falha.
O erro HTTP retornado pelo conversor foi classificado como `infraestrutura`,
mostrando uma dívida na classificação de falhas que precisa de correção própria.

O provedor `openrouter` foi confirmado no n8n, sem chave nesse serviço. Não
houve chamada real de análise ao OpenRouter nem processamento de documento
real. Permanecem pendentes o caso sintético válido com relatório Markdown/PDF,
a conferência de tempo/custo/conteúdo e a configuração/teste de Gmail OAuth.
Ollama ficou saudável sem modelo baixado no volume novo; seu uso exigirá baixar
o modelo e selecionar o provedor explicitamente. Guias de uso e mapa de acessos
foram atualizados sem incluir segredos.

## 2026-11-11 — Falha HTTP 402 no primeiro teste local com OpenRouter

Depois da preparação da stack, o usuário enviou um PDF pela landing local.
A execução 3 recebeu o protocolo, leu o PDF, concluiu a conversão e persistiu
o Markdown. Em seguida chamou o renderizador para a análise Anvisa V8 com o
OpenRouter. Às 22h57min55s, horário de São Paulo, a execução encerrou em `erro`
com a mensagem `OpenRouter retornou HTTP 402`. Nenhum relatório final foi
persistido; o PDF original e o Markdown permaneceram no armazenamento privado.

Os seis serviços locais continuavam saudáveis. O workflow de erros registrou
a falha e encerrou a tentativa, mas classificou o problema de IA como
`infraestrutura`, no nó `OpenRouter - Prepare verification bundle`, que propaga
o erro devolvido pelo renderizador. Isso confirma uma limitação da classificação
atual, sem demonstrar defeito na conversão nem conclusão bem-sucedida da IA.

Uma consulta autenticada somente de leitura a `/api/v1/key` confirmou que a
chave era aceita e possuía limite mensal com pouco orçamento restante. O corpo
detalhado da rejeição original não foi preservado pelo cliente HTTP; por isso
não foi possível distinguir definitivamente limite da chave, saldo da conta ou
outro orçamento do provedor. A documentação oficial associa HTTP 402 a essas
restrições de crédito/orçamento. Nenhum valor de chave, saldo ou identificador
do documento foi incluído neste registro.

Pendências: revisar crédito/orçamento no OpenRouter, executar um caso sintético
válido antes do próximo documento real e conferir os relatórios. A análise não
foi reexecutada, limites e cobrança não foram alterados, nenhum e-mail foi
enviado e a VPS permaneceu inalterada. Mudanças desta investigação limitadas
ao registro do resultado observado e à atualização do roadmap.

## 2026-11-11 — Retomada pelo último checkpoint no botão Reprocessar

O usuário solicitou corrigir o botão para que o cliente retome o processamento
sem repetir etapas já concluídas. O botão anterior chamava `retry-email`, e o
Retry genérico do n8n repetiria a validação da resposta 402 salva. Definido o
RF-21: retomar pelo último artefato registrado e íntegro, com nova tentativa,
auditoria e preservação dos erros e versões anteriores. A recuperação não
pressupõe checkpoints de lotes de IA que nunca foram persistidos.

Implementados a prévia de retomada e `POST /api/v1/submissions/{id}/reprocess`.
O gateway valida caminho privado, tamanho, hash, identidade da fonte e sequência
de páginas; decide a etapa no servidor, registra o operador e reserva a
solicitação com lock transacional do documento. A falha de despacho anterior
ao claim permite nova tentativa, sem devolver ao estado de erro um documento
que já foi reivindicado. Processamento e nova tentativa de e-mail têm botões
e rotas distintos. Nenhum envio é solicitado pela retomada de processamento.

O workflow identifica o marcador de retomada durante o claim e carrega o
contexto por rota interna autenticada, vinculada ao número da tentativa e à
execução. Markdown legado com hash e cabeçalho verificáveis é reutilizado;
quando seus avisos estruturados não foram guardados, essa limitação é informada.
Relatório com hash e vínculo à fonte permite saltar a análise. No V8, a
integridade do ZIP e a identidade do PDF da mesma revisão são verificadas.
No caminho comum, o relatório pode ser renderizado novamente sem IA, ou o PDF
íntegro pode ser reutilizado. Relatório anterior a uma nova conversão não é
reaproveitado silenciosamente. A saída da nova tentativa usa novas versões.

Passaram 104 testes Python da suíte ativa e três testes JavaScript da tela.
A coleta inicial sem indicar `tests/` também encontrou cópias históricas em
`output/` e falhou em um import relativo; os históricos não foram alterados e a
suíte ativa foi executada explicitamente. Os avisos de depreciação existentes
do FastAPI/TestClient permaneceram. Não foram adicionadas dependências,
variáveis de ambiente, migrações, serviços permanentes ou mudanças no prompt.

Teste integrado em um workflow separado no n8n local, com PDF sintético,
conversor real e IA simulada: uma conversão e uma análise simulada com erro;
retomada pelo botão com apenas mais uma análise, sem reconversão; nova
finalização com relatório salvo sem chamadas adicionais de IA, com PDF
idêntico. Duas solicitações concorrentes produziram HTTP 202 e HTTP 409, com
somente um despacho. Testados também renderização comum e reaproveitamento do
PDF: uma renderização, nenhuma análise/conversão e PDF idêntico na retomada.
O histórico e as versões anteriores foram preservados nos cenários.

Antes da alteração, foram guardados os exports versionados e um export do
workflow local implantado. A atualização local preservou credenciais e
configurações, conferiu a ausência de execução principal ativa e publicou a
nova versão. Gateway e renderizador locais foram reconstruídos. A prévia do
protocolo real confirmou o checkpoint de Markdown, sem reexecutar seu conteúdo.
O usuário pode iniciar a retomada pelo botão. Não houve chamada real de IA,
envio de e-mail ou alteração na VPS nesta implementação. A skill global
karpathy-guidelines continuava indisponível; mantidos os princípios de escopo
mínimo, estado explícito e verificação observável, sem instalar uma skill.

A reserva também confere a versão do documento lida antes da validação do
checkpoint. Assim, uma solicitação atrasada não dispara outra tentativa se uma
execução concorrente já iniciou e falhou rapidamente. Esse comportamento foi
conferido no PostgreSQL local. Na conferência final, os seis serviços estavam
saudáveis, a tela e a prévia responderam HTTP 200 e o protocolo real permanecia
em erro com somente sua tentativa original. O workflow, o protocolo, os arquivos
e os contêineres temporários da validação sintética foram removidos; o histórico
e os artefatos reais permaneceram preservados.

### 11/11/2026 — Confirmação de reprocessamento registrada como pendência

Por solicitação do usuário, registrado no RF-21 e no ROADMAP que o clique em
**Reprocessar** deve abrir uma tela de confirmação, com **Cancelar** e
**Confirmar reprocessamento**. O fluxo só deve ser disparado após confirmação
explícita; cancelar ou fechar não deve iniciar tentativa nem alterar o estado
do documento. A exigência evita acionamentos acidentais.

Esta alteração apenas documenta o requisito e a pendência. A interface e a
stack local não foram alteradas; o comportamento atual ainda dispara a
retomada no primeiro clique. Conferido o diff documental; testes de aplicação
não executados nesta alteração.

### 11/11/2026 — Atualização automática do andamento registrada como pendência

Por solicitação do usuário, registrado no RF-15 e no ROADMAP que o detalhe do
protocolo deve mostrar automaticamente o andamento e a etapa atual, incluindo
as tentativas e os erros do elemento `#history`, sem atualização manual da
página. A exigência também se aplica à retomada: novas etapas, falhas e
conclusão devem aparecer conforme o fluxo as registrar, preservando o histórico
anterior e sem antecipar sucesso.

Conferida a implementação em `infra/upload_gateway/static/submission.html`:
os dados são carregados ao abrir a tela e após algumas ações; não existe
acompanhamento contínuo do processamento. Esta alteração somente documenta a
pendência, sem mudar a interface, os workflows ou a stack local. Conferidos o
diff e as referências locais; testes de aplicação não executados nesta alteração.

## 2026-11-12 — Troca do modelo Anvisa V8 para GPT-6.1 Sol

Por solicitação do usuário, substituído GPT-6.1 Terra por GPT-6.1 Sol
(`openai/gpt-6.1-sol`) no transporte Anvisa V8 do renderizador. A documentação
oficial da OpenAI confirmou o modelo e a compatibilidade com Chat Completions;
o catálogo público do OpenRouter confirmou o identificador, os parâmetros de
JSON e o alias canônico `openai/gpt-6.1-sol-20260929`. A validação de identidade
aceita somente o modelo Sol solicitado ou esse alias; respostas identificadas
como Terra são recusadas. Não foi introduzido fallback entre modelos.

Preservados o prompt V8 aprovado e seu SHA-256, os blocos documentais, os
controles de cobertura/evidência e a chave somente no ambiente protegido do
renderizador. Atualizados PRD, roadmap, guias de uso, fluxograma e comentário
de configuração. O histórico de uso do Terra permanece neste LOG.

Onze testes do renderizador passaram em contêiner descartável, incluindo a
conversão sintética, geração e integridade do PDF/ZIP, registro do modelo no
contexto e aceitação/recusa dos identificadores de resposta. Permaneceu um aviso
de depreciação existente do TestClient. A suíte completa não foi reexecutada
nesta troca de modelo.

Confirmada a ausência de execução principal ativa antes da atualização local.
A imagem anterior foi preservada com a tag `before-sol-20261112` e somente o
serviço `report-renderer` foi reconstruído/recriado. Uma chamada ao endpoint
interno com Markdown de uma página sintética usou a API real do OpenRouter e
respondeu HTTP 200 em 13,22 segundos. Conferidos modelo Sol, cobertura da página,
PDF válido, hashes do PDF/ZIP e conteúdo correspondente no pacote completo.
Os resultados sintéticos não foram inseridos no protocolo real nem enviados
por e-mail. Essa validação não comprova correção semântica em documentos reais
nem resolve por si só a inconsistência observada na tentativa anterior.

A troca não reprocessou o documento real, não alterou workflows do n8n nem a
VPS. A confirmação de reprocessamento e a atualização automática do histórico
continuam pendentes. A skill global karpathy-guidelines permaneceu indisponível;
mantidos escopo mínimo e validação observável. Usada a skill OpenAI Docs para
conferir a migração, sem alterar o prompt.

Na conferência final, os seis serviços locais estavam saudáveis e o protocolo
real permanecia em erro, com suas duas tentativas anteriores e nenhuma tentativa
ativa. Diff sem erros de whitespace, referências locais conferidas e nenhum
segredo do ambiente encontrado nas alterações.

## 2026-11-12 — Confirmação de retomada e acompanhamento automático do fluxo

Implementadas as duas pendências solicitadas: o botão **Reprocessar** abre um
diálogo com o ponto salvo, **Cancelar** e **Confirmar reprocessamento**. O POST
de retomada ocorre somente na confirmação explícita. Cancelar, Escape e fechar
pelo fundo não despacham solicitação. Durante o despacho, os controles impedem
cliques repetidos; falha mantém o erro visível e permite tentar novamente. Se
outra sessão iniciar o processamento, a atualização fecha a confirmação antiga.
Mantida a recuperação do último artefato íntegro e a ação separada de e-mail.

O detalhe consulta a API a cada cinco segundos após a consulta anterior, apenas
enquanto a página estiver visível. Consultas concorrentes compartilham uma
requisição; ao sair, o agendamento para. O estado persistido aparece no painel
Processamento e nos metadados, com tentativas e erros atualizados. Destinatários,
observações, JSON em edição e aba selecionada são preservados; um artefato
inalterado não é recarregado. O PDF surge quando registrado. Falha de consulta
conserva os últimos dados e informa que a atualização será tentada novamente,
sem inventar erro do documento ou percentual de conclusão. Corrigida também a
URL do visualizador autenticado por sessão para incluir `?disposition=inline`.

A API passou a expor `current_stage`, campo já existente no PostgreSQL, também
na listagem. O workflow registra recuperação de checkpoint, conversão, análise
e preparação do PDF no documento e na tentativa correspondente à execução
ativa. Os nós seguintes preservam suas fontes de dados anteriores. Os pontos
rápidos podem ocorrer entre consultas da tela; durante uma chamada de IA não
há atualização por lote interno. A fonte é o último estado persistido, sem
antecipar a conclusão das etapas obrigatórias.

Validação atual: 107 testes Python da suíte ativa e 14 testes JavaScript da
interface aprovados. Incluem confirmação/cancelamento, Escape, clique duplo,
falha de despacho, retomada iniciada por outro cliente, progressão e erro,
recuperação de consulta, pausa em aba oculta, ausência de consultas simultâneas,
preservação do formulário/aba e exibição do novo artefato. Permaneceram três
avisos de depreciação existentes. Um contrato ainda esperava a conexão direta
do Markdown ao seletor de provedor; foi atualizado para incluir o registro
de análise antes do seletor, e a suíte completa passou após esse ajuste.

Em cópia separada do workflow n8n local, com PDF sintético, conversor real e IA
simulada, a primeira análise falhou. A segunda tentativa reutilizou o Markdown:
uma conversão, duas análises simuladas, histórico anterior preservado e
documento em `aguardando_envio`. Observadas as etapas de conversão, análise,
preparação do PDF e relatório pronto pela API; os dados de execução confirmaram
sucesso nos novos nós, inclusive recuperação do checkpoint. Não houve chamada
de IA real nem envio de e-mail nesta implementação.

Limitação encontrada na infraestrutura: após o sucesso do último nó da segunda
tentativa sintética, o n8n manteve a execução como `running`, sem consulta ativa
no banco e sem execução disponível para interromper pela API. Os logs também
mostraram `r.firstEvent.getTime is not a function` nas estatísticas, sem causa
comum confirmada. Não se declarou encerramento bem-sucedido da execução n8n;
os artefatos e o estado operacional do documento foram conferidos separadamente.
A investigação dessa inconsistência permanece como pendência de infraestrutura.

Antes da mudança foram preservados o export e a configuração implantada em
diretório temporário protegido. O workflow local correspondia ao export e não
havia execução principal ativa. Publicada a versão com 44 nós, preservando
credenciais e configurações; o export do Git continua inativo e sem credenciais.
A imagem anterior do gateway foi preservada com a tag `before-progress-20261112`
e apenas esse serviço foi reconstruído/recriado. A página, os arquivos estáticos
e a API autenticada responderam HTTP 200; o script servido corresponde ao fonte.
A inspeção visual não foi possível porque o acesso ao navegador estava
indisponível. O protocolo real permaneceu em erro com suas duas tentativas,
checkpoint de análise disponível e sem reprocessamento automático. A VPS não
foi alterada.

A cópia sintética foi desativada, arquivada e excluída pela API do n8n. Seus
registros e arquivos foram removidos com conferência de protocolo, nome e hash;
contêineres de teste e arquivo de ambiente protegido também foram removidos.
As fontes e o histórico reais foram preservados. A skill global
karpathy-guidelines continuava ausente nos diretórios consultados; mantidos
escopo mínimo, estado explícito e verificação observável, sem instalar skill.

Conferência final desta alteração: seis serviços locais saudáveis, sintaxe
JavaScript válida, diff sem erros de whitespace, links locais e conexões do
workflow válidos, hash do prompt preservado e nenhum segredo real encontrado
nos arquivos alterados ou novos elegíveis ao Git.

## 2026-11-12 — Retorno ao GPT-6.1 Terra para novo teste local

Após a tentativa com Sol, o usuário solicitou voltar ao Terra para testar.
A consulta ao protocolo confirmou três tentativas, todas encerradas em erro.
A tentativa com Sol foi iniciada às 00h31min30s e terminou às 01h21min24s,
horário de São Paulo, com `evidência literal não localizada na página indicada`
na validação do V8. Não havia relatório final; o PDF original e o Markdown
continuavam preservados. Essa observação não identifica qual citação falhou
nem demonstra que trocar o modelo resolve a causa.

Restaurado `openai/gpt-6.1-terra` no transporte e no contexto de auditoria.
A documentação oficial da OpenAI confirmou o modelo; o catálogo público do
OpenRouter confirmou o alias canônico `openai/gpt-6.1-terra-20261026` e os
parâmetros usados pelo cliente atual. A verificação de identidade agora aceita
somente Terra ou esse alias e recusa respostas identificadas como Sol.
Mantidos o endpoint, o prompt V8 com seu SHA-256 aprovado, o tamanho dos blocos,
os controles de evidência/cobertura e a ausência de fallback automático.

Atualizadas as referências ativas no PRD, guias, fluxograma e comentário de
configuração. A passagem pelo Sol permanece no histórico do roadmap e deste
LOG. Não foram adicionadas variáveis, dependências, migrações ou mudanças nos
workflows, no botão de confirmação e no acompanhamento automático da tela.

Validação atual: 11 testes do renderizador aprovados em contêiner descartável
sem segredos, cobrindo o modelo solicitado, alias, recusa de modelo diferente,
conversão sintética, evidências e pacote PDF/ZIP. Permaneceu um aviso de
depreciação existente do TestClient. A suíte completa não foi reexecutada
nesta troca de modelo.

Conferida a ausência de execução principal ativa antes da atualização. Código
anterior preservado em diretório temporário protegido e imagem com Sol guardada
na tag `before-terra-retest-20261112`. Somente o renderizador local foi
reconstruído/recriado. Uma chamada ao endpoint interno com uma página sintética
usou a API real do OpenRouter e respondeu HTTP 200 em 6,84 segundos. Conferidos
modelo Terra, hash do prompt, cobertura integral da página, PDF válido,
hashes do PDF/ZIP e correspondência dos arquivos no pacote completo. O teste
não certifica a análise semântica do documento real.

A troca não iniciou nova tentativa do protocolo real nem envio de e-mail;
a retomada permanece disponível pela confirmação na tela, aproveitando o
Markdown salvo. A VPS não foi alterada. A chave continuou somente no ambiente
protegido do renderizador. Aplicada a skill OpenAI Docs para conferir o modelo;
karpathy-guidelines permaneceu ausente, com escopo mínimo e verificação
observável mantidos.

Na conferência final, os seis serviços locais estavam saudáveis e o documento
real permanecia em erro com exatamente três tentativas encerradas. Conferidos
o diff, as referências locais e a ausência de segredos reais nas alterações.

## 2026-11-12 — Investigação da evidência literal não localizada

O usuário solicitou investigar a repetição da falha de evidência. Consultados
somente os dados já existentes do protocolo e das execuções n8n, sem iniciar
reprocessamento, consultar conteúdo em provedor externo ou consumir créditos
de IA. O protocolo continuava com três tentativas: a primeira falhou com HTTP
402, a segunda na reconciliação de ID/destino/páginas e a terceira na evidência
literal. Há apenas uma tentativa com essa última mensagem e um registro em
`workflow_errors` associado à mesma execução. A interface concatena as duas
fontes; por isso a mesma falha aparece em duas entradas, sem representar duas
execuções distintas desse erro no protocolo consultado.

O n8n guardou a resposta HTTP 422 do renderizador com somente `detail` e a
mensagem genérica. `_request` não preserva o envelope/ID da geração; `analyze`
mantém os retornos em memória e propaga a exceção, e a rota não persiste o
bloco, o registro, a página nem a citação rejeitados. Assim, esses dados não
estão disponíveis para determinar qual evidência real falhou. Não foi atribuída
a causa exata à IA ou à implementação sem essa comparação.

Conferida a fonte documental guardada: hash correspondente ao registro,
198 marcadores em ordem e conteúdo em NFC, sem espaços inseparáveis nem hifens
discricionários. Isso confirma a integridade e a sequência do artefato; não
constitui inspeção visual da conversão nem comprova completude semântica.

O código `_evidence` aceita a citação somente quando a página é um inteiro
permitido e a string não vazia está contida literalmente no corpo daquela
página. Página inválida, citação vazia e divergência textual produzem a mesma
mensagem. Reproduzidos cinco casos sintéticos na função instalada, sem API:
cópia literal aceita; mesmas palavras com quebra substituída por espaço,
página como string, página fora do registro e citação vazia rejeitadas com a
mensagem investigada. Essa reprodução demonstra condições possíveis, sem
reconstruir ou presumir a resposta real que foi descartada.

Conferido também o retry: ao falhar a validação, a aplicação envia novamente
o bloco com uma instrução genérica de correção, sem indicar campo/página/ID
da evidência rejeitada nem incluir a resposta anterior. Se a validação falha
novamente, encerra o processamento; os blocos já analisados não são checkpoints
persistidos. Trocar o modelo mantém essas mesmas condições de validação e
diagnóstico e, por si só, não demonstra solução da causa.

Registrada no roadmap a pendência de diagnóstico protegido e específico por
bloco/campo/página, associado à tentativa, e de distinguir visualmente as duas
entradas de auditoria. O prompt e o validador não foram alterados, a stack não
foi reiniciada e não houve chamada real de IA. A validação desta investigação
limitou-se às consultas, à integridade/paginação da fonte e aos cinco casos
sintéticos; a suíte de aplicação não foi reexecutada. A skill global
karpathy-guidelines continuava ausente; mantidos escopo mínimo e hipóteses
explicitamente separadas dos resultados observados.


## 2026-11-12 — Diagnóstico privado e correção direcionada de evidências V8

A pedido do usuário, implementado o registro que faltava na investigação da
falha literal. O validador agora distingue tipo de página inválido, página fora
do registro, página ausente na fonte, tipo de trecho inválido, trecho vazio e
texto não localizado. O diagnóstico identifica JSON Pointer, ID do registro,
página, citação rejeitada e páginas permitidas. A coincidência apenas após
normalizar espaços é registrada como pista, mantendo a rejeição literal.

Cada rejeição de validação de bloco salva o Markdown enviado, a resposta
rejeitada, modelo, hash do V8, ID da geração quando informado pelo provedor,
ordem da chamada e motivo. O registro inclui hash da fonte, protocolo,
tentativa e execução, recebidos somente na rota interna do renderizador.
Esses identificadores, o nome do arquivo e as credenciais não são adicionados
à solicitação ao OpenRouter. O histórico de falha recebe página, motivo e
referência aleatória `ANV8D-...`, sem transcrição ou caminho privado.

Criado o volume exclusivo `automacao_miller_diagnostics_data`, montado somente
no renderizador em `/data/diagnostics`, com diretórios `700` e arquivos `600`.
Não há nova rota pública, serviço ou tabela. Escritas usam criação exclusiva,
flush e fsync; uma falha remove o arquivo incompleto quando possível e encerra
com erro de armazenamento. A preparação do diretório ocorre antes da primeira
chamada de IA. Documentados acesso administrativo e backup protegido. Não foi
adicionada variável de ambiente.

A chamada corretiva recebe a resposta anterior e o diagnóstico específico,
com instrução técnica para copiar a evidência exata da fonte, preservar os
demais eventos e devolver o bloco completo. O material retornado e seus nomes
de campo continuam tratados como dados não confiáveis. Mantido o limite de
uma correção de validação por bloco. O limite de tamanho da solicitação também
considera a resposta anterior; caso excedido, continua a divisão existente de
blocos, sem truncar fonte ou resposta. Os blocos já aceitos continuam somente
em memória, sem novo checkpoint intermediário de IA.

Preservados o modelo Terra e o arquivo V8 aprovado, SHA-256
`3e75a9619a9cd5e7ce7080b22faad815148172cd0ffe30aa9db85e3b43b804e7`.
O complemento técnico da correção mudou; o prompt documental aprovado não foi
editado. A resposta antiga descartada não pode ser recuperada com esta mudança.
A distinção visual entre tentativa e erro associado permanece pendente.

Validação atual: 123 testes Python e 14 testes da interface passaram. Cobertos
os motivos específicos, caminho escapado, correção aceita, segunda rejeição,
vínculo à tentativa, ausência de identificadores internos no conteúdo enviado,
permissões privadas, contexto inválido e falhas de armazenamento antes/depois
da chamada de IA. Permanecem três avisos de depreciação das bibliotecas/testes.

Dois casos sintéticos passaram por um workflow isolado no n8n local usando o
mesmo corpo da chamada interna e o renderizador real, com resposta de IA
simulada e chave fictícia. A correção literal gerou PDF e ZIP com HTTP 200;
a segunda rejeição retornou HTTP 422 com referência segura. Conferidos três
diagnósticos vinculados às respectivas execuções e persistência após recriar
o contêiner. O workflow, contêiner e volume de teste foram removidos. Não houve
chamada externa ou consumo de créditos nesses testes. Essa simulação não
homologa a capacidade do Terra de corrigir o documento real.

Antes da alteração foram preservados o export implantado, o export fonte e os
arquivos anteriores em diretório privado de `/tmp`; a imagem em execução foi
marcada `before-evidence-diagnostics-20261112` para reversão. Confirmada ausência
de execução principal ativa. Aplicados somente o renderizador e a nova versão
do workflow principal na stack local, preservando credenciais e os 44 nós;
a versão ativa corresponde ao export atualizado. O export do Git continua
inativo e sem credenciais. Os seis serviços estavam saudáveis ao final.
O protocolo real permaneceu em erro com exatamente três tentativas encerradas,
sem reprocessamento, relatório novo ou envio de e-mail. A VPS não foi alterada.

Atualizados PRD, ROADMAP, fluxo, guias de operação e acessos. Conferidos diff,
referências locais e ausência de segredos reais nas alterações. Nenhum commit
ou push foi feito. A skill global karpathy-guidelines continuava indisponível;
aplicados escopo mínimo, hipóteses explícitas e verificações observáveis.

## 2026-11-12 — Retomada real autorizada a partir do Markdown

O usuário solicitou verificar a disponibilidade da aplicação e confirmar a
retomada se a confirmação indicasse o Markdown salvo. Os seis serviços locais
já estavam saudáveis; não foi necessário subir ou reiniciar a stack. O acesso
ao navegador estava indisponível. Consultados a prévia autenticada e os arquivos
de interface servidos pela própria aplicação: o diálogo usa a prévia para
exibir `análise do Markdown salvo`, com etapa interna `analysis`.

Confirmada uma única retomada pela mesma API usada pelo botão, com HTTP 202.
A tentativa 4 foi iniciada às 11h49 de Brasília, execução n8n 20. Conferidos
documento e tentativa em `em_processamento`, etapa `analise_markdown`, e execução
n8n em `running`, sem horário de término. A retomada reutiliza o Markdown
guardado e refaz a análise de IA. Não foi solicitado envio de e-mail.

Esta operação inicia o teste real com os diagnósticos novos; não representa
homologação ou sucesso final. O resultado ainda não foi apurado. O consumo
de tokens/custo por documento continua sem registro na aplicação. Não houve
alteração de código, workflow ou configuração; a suíte de testes não foi
reexecutada nesta operação. Conferido o diff documental.

## 2026-11-12 — Causa confirmada nas tentativas 4 e 5: justificativa dos excluídos

O usuário solicitou analisar a nova falha. Consultados somente os dados locais
existentes, sem reiniciar serviços, reprocessar ou chamar o provedor. Os seis
serviços estavam saudáveis. A tentativa 4, execução 20, terminou às 11h55 de
Brasília após aproximadamente 6m24s. Também consta a tentativa 5, execução 22,
das 13h42 às 13h44, duração aproximada de 2m13s. Ambas encerraram em erro, sem
relatório final; permanecem apenas o PDF original e o Markdown guardado.

Os novos diagnósticos preservaram as respostas inicial e corretiva de cada
tentativa. A tentativa 4 falhou no bloco de páginas-alvo 21–25; a 5 no bloco
1–5. Em cada retorno há oito registros com destino `excluido`, justificativa
textual não vazia em `justificativa` e ausência de `justificativa_destino`.
IDs, destino e páginas desses registros satisfazem a condição que os valida.
A rejeição efetiva é a exigência de `justificativa_destino`, agrupada na mesma
mensagem genérica de reconciliação de ID/destino/páginas.

Identificada incompatibilidade com a seção 6 do V8 aprovado: incluídos e
pendências pertinentes usam `justificativa_destino`; para excluídos e
representações duplicadas, o prompt permite registro compacto com
`justificativa`. O validador exige a primeira chave de todos os eventos.
Portanto, a falha destas tentativas é de compatibilidade do código com o
contrato compacto permitido pelo prompt; não se atribuiu erro à extração
literal ou ao documento com base nessa mensagem.

Reprodução local em memória com o código instalado: os quatro retornos
preservados reproduziram a mesma exceção original. Em cópia de cada resposta,
transferida apenas a justificativa existente dos compactos para a chave
exigida pelo código, sem alterar evidências, páginas, IDs ou inventário.
Os quatro blocos passaram então por `_validate_block`: oito registros por
retorno e 61, 61, 61 e 63 evidências literais conferidas, respectivamente.
A reprodução prova a condição que interrompeu esses blocos; não comprova
qualidade semântica, cobertura dos demais blocos ou sucesso do relatório final.
Nenhum retorno ou artefato real foi editado.

O retry recebe detalhes de campo somente para `EvidenceValidationError`.
Nesta falha estrutural, o diagnóstico inclui somente `validacao_bloco` e a
mensagem genérica, sem nomear `justificativa_destino`. Assim, a IA repetiu a
forma compacta permitida pelo V8. Os testes anteriores de diagnóstico usavam
excluídos com `justificativa_destino`, deixando descoberta essa variante
compacta autorizada. Registrada no roadmap a correção de contrato e cobertura
de testes, mantendo o V8 e as validações documentais.

Conferida ainda a apresentação do erro na execução 22: o renderizador retornou
HTTP 422 com motivo e referência; o n8n separou a descrição do texto final,
deixando somente `ANV8D-... [line 4]` em `error.message`. O workflow de erro
persiste apenas esse campo, sem `error.description`, e classifica a falha como
infraestrutura pelo nome do nó. Isso explica a referência isolada no painel;
não indica erro de criação do ZIP, embora o último nó tenha esse nome.

Conferidos nos quatro diagnósticos o modelo Terra, o mesmo hash da fonte e o
hash do V8 aprovado; o arquivo instalado permanece íntegro. Atualizados apenas
LOG e ROADMAP com causa e pendências. A suíte completa não foi reexecutada;
a validação atual consistiu na reprodução local dos quatro blocos e nas
consultas descritas. Não houve nova tentativa, chamada externa, alteração de
código/workflow ou consumo adicional de créditos nesta investigação. Conferido
o diff documental. A skill global karpathy-guidelines continuava ausente;
mantidas hipóteses separadas dos resultados observados.


## 2026-11-12 — Compatibilidade dos registros compactos V8 e resumo de erros

A pedido do usuário, corrigida a incompatibilidade identificada nas tentativas
4 e 5. Excluídos e representações duplicadas aceitam a chave `justificativa`
prevista na seção 6 do V8 e preservam compatibilidade com `justificativa_destino`.
As justificativas fornecidas precisam ser textuais e não vazias. Quando ambas
as chaves existem, seus valores são preservados sem escolha, cópia ou fusão.
Incluídos e pendentes continuam exigindo `justificativa_destino` e a ficha
completa. Não foram preenchidas justificativas ausentes por suposição nem
normalizados os registros recebidos.

Separadas as condições que antes produziam mensagens genéricas de estrutura.
O diagnóstico privado agora identifica JSON Pointer, ID do registro quando
aplicável, motivo, valor recebido e condição esperada para cobertura, identidade,
páginas, destino, categoria, justificativa, ficha e inventário. A chamada
corretiva recebe esses dados e a resposta anterior, mantendo uma única correção
por bloco. O resumo público conserva somente o motivo seguro e a referência;
valores retornados pelo modelo e caminhos derivados deles continuam privados.
O complemento técnico da correção foi ajustado para distinguir estrutura de
evidência. Não foram relaxadas as verificações literais, de cobertura, páginas,
identidade, revisão ou reconciliação.

O workflow interno de erros agora combina `error.message` e `error.description`,
sem repetir strings idênticas, preservando o motivo que o n8n separa da
referência. A classificação considera ambos e reconhece `ANV8D-...` como
validação, antes de recorrer ao nome do nó. O tratamento continua em nó Set,
com a mesma gravação transacional no PostgreSQL. Não houve migração de banco,
nova dependência, serviço ou variável de ambiente. Erros históricos não foram
reescritos, e a duplicação visual entre tentativa e registro associado permanece
fora desta correção.

Validação atual: 161 testes Python e 14 testes da interface passaram, com os
mesmos três avisos de depreciação já conhecidos. Novos casos cobrem compactos
com ambas as chaves permitidas, preservação de valores distintos, rejeição de
justificativa ausente/inválida, exigência da ficha completa nos pertinentes,
validação literal, cobertura, inventário, IDs duplicados, falhas de estrutura,
correção direcionada e segunda rejeição. Expressões do export de erros foram
executadas em Node.js contra os formatos de mensagem/descrição divididas,
incluindo classificação e ausência de texto duplicado.

As quatro respostas reais preservadas das tentativas 4 e 5 foram validadas
sem edição, inicialmente em contêiner sem rede com fonte e diagnósticos somente
leitura, e novamente no renderizador atualizado. Aceitos oito registros por
resposta, com 61, 61, 61 e 63 evidências literais conferidas. Confirmada ausência
de mutação dos registros. Essa verificação cobre os blocos existentes, sem
homologar qualidade semântica ou o restante do documento.

Três cenários sintéticos passaram no n8n local com renderizador real e IA
simulada: compacto aceito diretamente com PDF e ZIP, campo ausente corrigido
na segunda chamada e campo ausente novamente rejeitado. O terceiro percorreu
o nó real de preparação do pacote e o export corrigido de erros, gravando no
banco categoria validação, motivo e referência na tentativa e no registro de
erro. Conferidos três diagnósticos privados com o campo específico. Dados,
workflows, contêiner e volume sintéticos foram removidos ao final. Nenhuma
chamada ao OpenRouter ou consumo adicional de créditos foi realizado nos testes.

Antes das alterações, preservados fontes e exports implantados em diretório
privado de `/tmp`, e marcada a imagem anterior como
`before-compact-fix-20261112`. Verificada a ausência de execução principal ativa.
Aplicados somente o renderizador e a nova versão do workflow de erros na stack
local, preservando credenciais e conferindo a versão ativa. O workflow principal
não precisou ser alterado. Os exports do Git continuam inativos e sem
credenciais. Os seis serviços estavam saudáveis ao final; o documento real
permaneceu em erro com cinco tentativas, sem novo processamento ou envio.
A VPS não foi alterada.

Preservados o modelo Terra e o arquivo V8 aprovado, SHA-256
`3e75a9619a9cd5e7ce7080b22faad815148172cd0ffe30aa9db85e3b43b804e7`.
Atualizados PRD, ROADMAP, fluxo e guia dos workflows. Conferidos diff, links
locais e ausência de segredos reais nas alterações. Não houve commit ou push.
A skill global karpathy-guidelines continuava ausente; mantidos escopo mínimo,
hipóteses explícitas e validação observável.

## 2026-11-12 — Tentativa 6 interrompida por cobertura parcial nas páginas 114–115

O usuário solicitou analisar outra falha. Consultados os dados locais existentes
da tentativa 6, execução 28: início às 14h59m43s e término às 15h23m50s de
Brasília, duração aproximada de 24m07s. Documento e execução terminaram em erro
de validação. Os seis serviços estavam saudáveis. Permanecem apenas o PDF
original e o Markdown como artefatos do protocolo, sem relatório final.

Foram encontrados três diagnósticos dessa tentativa. O primeiro corresponde
ao bloco 6–10, com uma evidência do inventário na página 10 que coincide com
a fonte somente após normalizar espaços. A execução posteriormente chegou ao
bloco 111–115; portanto aquela condição não foi o bloqueio final. A resposta
corretiva aceita desse bloco inicial não foi guardada como diagnóstico de falha.

O segundo diagnóstico registra `cobertura_pagina_invalida` no caminho
`/paginas/4/estado`: a página 115 foi devolvida como `pendente`. A resposta
informa que unidades de suplementos, retificações e medicamentos ainda não
haviam sido individualizadas e conferidas integralmente. O inventário contém
dois blocos pendentes. O campo adicional `impedimento` também retifica a própria
observação de revisão da página 114: os itens haviam sido inventariados, sem
as fichas individuais correspondentes. Esse dado impede tratar a declaração
inicial de análise dessa página como prova de trabalho concluído.

Após a única correção permitida, o terceiro diagnóstico registra a mesma
categoria no caminho `/paginas/3/estado`: agora a página 114 está pendente,
assim como a 115. O retorno passa de 11 para 13 registros e declara acréscimo
de dois eventos, mantendo unidades por tratar e dois blocos de inventário
pendentes. A IA explica que a declaração anterior de análise integral estava
incorreta e que precisa continuar sem duplicar IDs. A rejeição acontece na
conferência de cobertura, antes de validar os demais campos e evidências desse
bloco; não se concluiu que o restante desses registros esteja validado.

Reproduzidas localmente, sem alteração das respostas, as três exceções com o
validador instalado. Conferidos nos diagnósticos o modelo Terra, o hash esperado
do V8 e o mesmo hash da fonte. O bloco 111–115 foi enviado com contexto 109–117,
cerca de 109 mil caracteres; as respostas inicial e corretiva têm cerca de
22 mil e 30 mil caracteres, respectivamente. A IA alegou limite de resposta,
mas os diagnósticos não preservam consumo ou limite efetivamente atingido.
O transporte só devolve os objetos analisados quando o término informado é
`stop`; um término `length` acionaria outro caminho. Assim, a causa comprovada
é a análise declaradamente parcial, e não um limite técnico específico do
provedor, indisponibilidade ou falha de conversão demonstrada.

Identificada a limitação da orquestração: os lotes começam com cinco páginas
e duas páginas de contexto em cada direção. Há expansão de contexto e divisão
para limite técnico de saída ou tamanho de solicitação. Um bloco retornado
como parcial, porém, recebe apenas correção de validação do bloco completo;
não há continuação das unidades pendentes ou checkpoint persistido dos lotes
já aceitos. O V8 aprovado permite continuar por grupos de eventos completos e
determina que páginas permaneçam pendentes enquanto a revisão não terminar.
O bloqueio do PDF final está correto; é necessário tratar a continuação parcial
na aplicação, preservando essa exigência.

Registrada no roadmap a necessidade de continuação com unidades completas,
lotes menores e checkpoints verificáveis, sem alterar rótulos de cobertura
para simular conclusão. A retomada atual continua reutilizando apenas os
artefatos persistidos, e os lotes anteriores em memória não podem ser
recuperados automaticamente desta execução encerrada. A resposta de erro
atual já preserva motivo e referência no histórico e categoria validação.

Não houve alteração de código, workflow, configuração ou dados do protocolo,
nem nova chamada de IA ou consumo adicional de créditos nesta investigação.
A suíte de aplicação não foi reexecutada: a validação atual foi a reprodução
das três exceções e a comparação das respostas, do código e do V8. Atualizados
somente LOG e ROADMAP e conferido o diff documental. A skill global
karpathy-guidelines continuava indisponível; mantida a distinção entre fatos
observados e causas de limite não comprovadas.


## 2026-11-12 — Continuação por eventos e checkpoints privados da análise V8

O usuário autorizou reduzir blocos densos, continuar itens pendentes preservando
IDs/evidências e salvar lotes concluídos para retomada. Implementada a
orquestração incremental no renderizador, sem novos serviços, dependências,
variáveis de ambiente, tabelas ou alterações dos workflows implantados.
O arquivo V8 aprovado permanece intacto e o modelo continua Terra.

A fila começa com até cinco páginas-alvo e divide recursivamente conjuntos que
ultrapassam 32 mil caracteres nos alvos. Cada página e seu texto permanecem
inteiros, com contexto inicial de duas páginas em cada direção e possibilidade
de expansão. Limite técnico de saída/tamanho também permite reduzir lotes
novos; continuidade já estabelecida não é descartada para refazer os eventos.
Lotes parciais com registros válidos continuam por grupos de até quatro novos
eventos solicitados ao modelo, mantendo cobertura e inventário acumulados.

Separada a validação dos registros da exigência de fechamento das páginas.
Apenas o caminho intermediário aceita cobertura/inventário pendentes. Registros
precisam satisfazer estrutura, fonte, páginas e evidências literais antes de
ser preservados. Um ID já guardado não pode mudar conteúdo ou tipos JSON;
repetição idêntica não duplica o evento. Duplicação exata com outro ID, omissão
de IDs reservados ou reserva fora dos alvos são rejeitadas. O inventário final
precisa reconciliar todos os IDs e a cobertura final permanece estrita.
Nenhuma página foi promovida a analisada por conveniência.

A continuação recebeu complemento técnico próprio, com os resultados anteriores
tratados como dados não confiáveis e instrução para continuar unidades completas.
Há uma correção de validação por grupo, até três expansões de contexto e até
32 chamadas por lote em cada execução, além do prazo total já configurado.
Duas respostas consecutivas sem progresso encerram com checkpoint preservado.
Um resultado válido retornado no fim do prazo é salvo antes de impedir outra
chamada. A renderização só começa quando todos os lotes estão completos.

Criado controle privado em `/data/diagnostics/checkpoints`, no volume exclusivo
já existente do renderizador. A identidade inclui protocolo, hash do Markdown,
modelo, V8, instruções e código da análise; mudança de identidade cria outro
namespace e conserva o anterior. O estado guarda lotes concluídos e registros
validados de lotes pendentes, sem publicar `analysis_json`. Envelopes possuem
digest, limite de tamanho, arquivos `600`, diretórios `700`, gravação temporária,
fsync e substituição atômica. Um bloqueio de arquivo impede concorrência da
mesma identidade. A marca persistida no arquivo de bloqueio distingue estado
removido de uma análise nova. Falha ou corrupção conhecida impede nova chamada
de IA e não provoca reinício silencioso. A exclusão do volume inteiro continua
apagando o progresso; documentado backup protegido do volume completo.

Antes de retomar, todos os registros, lotes e a partição de páginas carregados
são revalidados contra o Markdown autorizado. O contexto de protocolo/tentativa/
execução fica interno; não é incluído na solicitação ao provedor. Uma análise
já concluída pode ser reutilizada após falha de PDF sem consumir IA novamente.
O ZIP e o contexto do relatório registram quantos lotes/páginas foram reutilizados.
O botão e a etapa visível continuam sendo a retomada da análise do Markdown;
o navegador não escolhe os arquivos de checkpoint.

Validação final: 182 testes Python e 14 testes da interface passaram, com três
avisos de depreciação já existentes. Cobertos continuação e grupos pendentes,
redução de alvos sem corte de fonte, falha após lote concluído, retomada de
registros de página pendente, preservação de IDs/valores/evidências, duplicação,
reservas, limites, ausência de progresso, prazo, concorrência, falha de escrita,
remoção/corrupção/inconsistência de estado e reutilização após falha de PDF.

Dois retornos parciais reais da tentativa 6 foram conferidos em contêiner sem
rede e com fonte/diagnósticos somente leitura: 11 e 13 registros satisfizeram
as verificações intermediárias, com 62 e 86 referências literais. A cobertura
permaneceu pendente. Essa conferência não promove os retornos a resultado final
nem migra lotes antigos para checkpoints válidos.

Integração na imagem definitiva, por workflow n8n isolado e IA simulada:
concluído e salvo um lote de cinco páginas; salvos dois eventos do lote seguinte;
a rota retornou HTTP 502 por falha sintética. Após remover/recriar o contêiner
com o mesmo volume, a retomada preservou os dois eventos e fez apenas uma nova
chamada simulada para concluir o lote restante. O PDF e o ZIP continham os
quatro IDs e evidências esperados. Outra consulta à análise completa fez zero
chamadas de IA. Uma fonte sintética densa foi dividida em quatro lotes menores.
O workflow, contêiner e volume de teste foram removidos. Não houve chamada ao
OpenRouter, documento real reenviado ou consumo adicional de créditos.

Preservados fontes anteriores e estado implantado dos workflows em diretório
privado de `/tmp`, além da imagem `before-incremental-20261112`. Confirmada
ausência de execução principal ativa antes da atualização. Aplicado somente
o renderizador local e conferidos os hashes dos quatro arquivos de execução,
a escrita/leitura privada, o Terra e o V8 aprovado, SHA-256
`3e75a9619a9cd5e7ce7080b22faad815148172cd0ffe30aa9db85e3b43b804e7`.
Os seis serviços estavam saudáveis; workflows principal e de erros mantiveram
as mesmas versões ativas. O protocolo real permaneceu em erro com seis
tentativas, sem nova execução, relatório final ou envio. A VPS não foi alterada.

As seis tentativas anteriores não guardaram seus lotes concluídos: esse
progresso em memória não pode ser recuperado retroativamente. O salvamento
novo protege as próximas execuções; a homologação completa do documento real
continua pendente de nova retomada autorizada. Atualizados PRD, ROADMAP, README,
fluxograma, guias dos workflows/stack local e acessos. Conferidos diff, links e
segredos; sem commit ou push. A skill global karpathy-guidelines continuava
indisponível; mantidos escopo mínimo e testes observáveis.

## 2026-11-12 — Tentativa 7 encerrada por HTTP 402, com primeiros lotes preservados

O usuário solicitou investigar outra falha. Consultados PostgreSQL, execução
n8n 38, diagnóstico privado e checkpoint existentes. A tentativa 7 começou
às 16h19m38s e terminou às 16h22m32s de Brasília, aproximadamente 2m55s.
Documento, tentativa e execução estão em erro; o último nó é
`OpenRouter - Prepare verification bundle`, com mensagem HTTP 402 do OpenRouter.
A categoria persistida continua `infraestrutura`, embora a causa conhecida seja
recusa de crédito/orçamento do provedor de IA. Não houve reclassificação ou
alteração dos registros históricos. Os seis serviços locais estavam saudáveis.

A sequência apurada é: três lotes aceitos; resposta do lote 6–7 rejeitada por
`trecho_nao_localizado`, página 7, campo
`/reconciliacao_anexos/7/unidades_fonte/0/evidencias/1`; chamada corretiva recusada
com HTTP 402. A evidência rejeitada tem 45 caracteres, não coincide apenas
normalizando espaços e não aparece literalmente nas demais páginas enviadas.
A falha literal foi reproduzida com a resposta e fonte preservadas, sem editar
os dados. A consulta da geração já existente confirmou término `stop`, Terra
e custo de US$ 0,0559805 daquela chamada, sem executar nova geração. Esse custo
não é o total da tentativa nem do documento.

Consultas somente leitura a `GET /api/v1/key` e `GET /api/v1/credits` mostraram:
limite mensal da chave de US$ 10, uso acumulado de US$ 9,848618745, restante
de US$ 0,151381255 e reinício previsto para 01/12/2026 às 00h00 UTC. A conta
informa US$ 20 em créditos totais e US$ 9,848618745 utilizados, com saldo
calculado de US$ 10,151381255. São números acumulados da chave/conta, não
medição deste processamento. Não foram consultados ou expostos valores de
credenciais, nem alterado orçamento ou saldo.

A documentação oficial distingue saldo da conta, limite por chave e orçamento
de requisições em andamento. O transporte solicita até 48 mil tokens de saída.
O catálogo público consultado informa US$ 0,000005 por token de saída do Terra:
até US$ 0,24 somente de saída, antes dos tokens de entrada. Isso supera o
restante da chave e reforça o orçamento por chave como principal indício da
recusa. Porém o tratamento de `HTTPError` fecha a resposta sem guardar seu corpo
ou cabeçalhos; somente o status 402 foi preservado. Não é possível recuperar
`error.metadata.limit_source`, o cálculo de reserva ou `Retry-After` da chamada
rejeitada. Portanto, não se afirma que o saldo global acabou nem se atribui
um subtipo exato de 402 sem a evidência correspondente.

Referências técnicas consultadas:
[limites e tratamento de 402](https://openrouter.ai/docs/api_reference/limits) e
[formato dos erros](https://openrouter.ai/docs/api_reference/errors-and-debugging).
Pendência: revisar o limite mensal da chave e preservar metadados seguros dos
erros HTTP para distinguir as causas futuras. Nenhuma correção funcional foi
aplicada nesta investigação.

Em contêiner isolado sem rede e com volumes somente leitura, conferidos hash
e 198 marcadores do Markdown, digest e identidade do checkpoint e validação
completa de seu estado contra a fonte. Os três lotes concluídos cobrem os alvos
1–2, 3 e 4–5, com oito registros e 82 referências literais válidas. Há 96 lotes
pendentes e o próximo alvo é 6–7, sem registros aceitos naquele lote. O checkpoint
permite reutilizar as páginas 1–5 numa próxima retomada compatível; não exige
reiniciar a análise pela página 1. Permanecem somente PDF original e Markdown
como artefatos operacionais, sem relatório final.

Validação atual limitada à investigação, reprodução da rejeição literal e
revalidação do checkpoint; a suíte de aplicação não foi reexecutada porque não
houve mudança de código. Nenhuma nova tentativa, chamada de análise, envio,
alteração de workflow, implantação ou mudança na VPS foi realizada. Atualizados
LOG e ROADMAP. A skill global karpathy-guidelines continuava ausente na busca
local; mantida a distinção entre fatos comprovados e inferência de orçamento.

## 2026-11-12 — Tentativa 8: revisão de fichas pendente bloqueia a continuação

O usuário solicitou analisar nova falha. Antes dessa tentativa, informou o
aumento do limite mensal da chave; a consulta somente leitura confirmou limite
de US$ 100 e margem de US$ 90,151381255. Esses números são do orçamento da chave,
não do saldo global nem do custo de um processamento. A tentativa 8, execução
n8n 40, começou às 16h59m14s e terminou às 17h43m11s de Brasília, duração de
aproximadamente 43m57s. Documento, tentativa e execução estão em erro de
validação. A mensagem final preserva `conferencia_integridade_pendente` e a
referência do diagnóstico; não há HTTP 402 como erro final desta tentativa.
Os seis serviços locais estavam saudáveis na investigação.

O lote 61–62 havia recebido uma rejeição de inventário às 17h19. A execução
posteriormente chegou ao lote 113–115, portanto essa rejeição anterior foi
superada e não é a causa final. O último checkpoint foi salvo às 17h36m07s.

Os dois diagnósticos finais têm os mesmos alvos 113–115 e contexto 111–117.
Os alvos somam 30.609 caracteres; o bloco enviado tem 81.803 caracteres com
contexto. Cada resposta possui 26 registros e cerca de 55,6 mil caracteres.
Inicialmente, o primeiro impedimento é a conferência pendente do registro
`ANV8-P113-006`, caminho `/registros/5/conferencia_integridade`. O modelo declara
que não executou conferência inversa e pesquisa de ocorrências no documento
integral. Há outra ficha de retificação e nove fichas de suplementos também
com revisão pendente; estas últimas mencionam a continuação do anexo.
As páginas 114–115 e dois inventários permanecem pendentes, com impedimento
explícito de análise parcial. A declaração de página 113 analisada não elimina
a pendência de revisão das fichas daquela página.

Na resposta corretiva, somente a conferência de `ANV8-P113-006` muda de pendente
para revisada, com ajuste de pendências/observação. Nenhum outro campo dos 26
registros foi alterado. A primeira rejeição passa então para `ANV8-P113-007`,
em `/registros/6/conferencia_integridade`; outras nove fichas continuam com a
mesma revisão pendente. A aplicação encerra após a única correção permitida.
A própria resposta declara progresso parcial e não deve ser promovida a
resultado completo por mera alteração de rótulo.

Identificada a limitação da implementação incremental: `_validate_records`
exige `conferencia_integridade.estado == revisada` e ausência de pendências
em toda ficha incluída ou pertinente. Esse validador é chamado antes da decisão
de continuação parcial e do salvamento. O parâmetro intermediário `allow_pending`
abrange cobertura e inventário, mas não revisões de fichas. Assim, uma ficha
inacabada transforma o grupo inteiro em erro de correção em vez de permitir
separar eventos completos e continuar a revisão pendente. A correção direcionada
recebe apenas a primeira exceção encontrada; corrigir uma ficha não remove as
outras pendências. O limite de quatro novos eventos existe somente na mensagem
de continuação, que não foi alcançada nesse lote. A primeira chamada e a
correção ainda solicitaram o bloco inteiro. A divisão por tamanho também não
ocorreu: os alvos ficaram abaixo dos 32 mil caracteres, embora o número e a
complexidade dos eventos tenham produzido saída extensa. O que se comprova é
trabalho declarado incompleto e tratamento insuficiente na orquestração;
nenhum limite técnico de saída efetivamente atingido foi demonstrado.

Reproduzidos os dois erros com as respostas guardadas e o validador instalado.
Verificações individuais encontraram 15 registros válidos na primeira resposta
e 16 na correção; os demais 11/10 falharam na conferência pendente. A busca
literal isolada dos registros passou, inclusive nos ainda não revisados, e as
36 evidências do inventário de cada resposta também foram localizadas. Isso
não dispensa a revisão dos campos e associações nem homologa o lote inteiro.

Executada a orquestração real em contêiner isolado, sem rede, com a fonte e os
diagnósticos montados somente leitura, substituindo a função de requisição por
reprodução das duas respostas. O checkpoint usado nessa reprodução existia
somente em memória. Confirmadas duas chamadas simuladas, sem instrução de
continuação/limite de eventos, correção da primeira ficha e rejeição seguinte.
Houve somente o salvamento inicial em memória: nenhum dos registros do lote
113–115 passou ao estado aceito. Não foram editados estado, fonte ou respostas
do ambiente operacional.

Na mesma conferência isolada, validados o hash do Markdown e seus 198 marcadores,
digest, identidade e todos os registros do checkpoint contra a fonte. Estão
preservados 59 lotes concluídos, páginas 1–112, 143 registros e 1.612 referências
literais válidas. Há 40 lotes pendentes; o próximo alvo é 113–115, sem registros
aceitos nele. Esse progresso não precisa ser refeito em uma retomada com a
mesma identidade. Qualquer correção de código muda a identidade atual; preservar
os 59 lotes numa nova versão exige migração explícita e revalidada, sem aceitar
automaticamente um estado de implementação diferente.

Registrado no ROADMAP o ajuste necessário: grupos pequenos desde a primeira
chamada; separação dos eventos completos dos que ainda exigem revisão;
continuação com IDs, fonte e evidências preservados; correção com todas as
pendências conhecidas; validação final estrita e preservação verificável do
progresso existente. Não foi aplicada correção funcional nesta investigação.
Não houve nova tentativa, chamada de IA externa, consumo adicional por geração,
envio, alteração de workflow, implantação ou mudança na VPS. A suíte de aplicação
não foi reexecutada; a validação atual foi a reprodução e a revalidação descritas.
Atualizados somente LOG e ROADMAP, sem commit ou push. A skill global
karpathy-guidelines permanece ausente conforme a busca local; mantidos escopo
mínimo, investigação observável e separação entre fatos e hipóteses.

## 2026-11-12 — Grupos desde a primeira chamada e continuação das fichas em revisão

O usuário autorizou implementar grupos pequenos desde a primeira chamada,
salvar eventos completos e continuar a revisão dos demais preservando IDs e
evidências. Lidos PRD, ROADMAP, LOG, AGENTS e os fontes/testes relacionados.
A skill global karpathy-guidelines continuava ausente na busca local; mantidos
escopo mínimo e validação observável. Preservadas as mudanças locais anteriores,
sem commit ou push.

O transporte agora solicita até quatro eventos por resposta desde a primeira
chamada e também nas correções. O contexto de continuidade está sempre presente,
com listas separadas de eventos completos e fichas em revisão. Enquanto houver
fichas abertas, solicita zero eventos novos e prioriza até quatro IDs para
conferência inversa contra a fonte. Uma resposta maior que a solicitada não é
truncada nem perde registros válidos por quantidade; a solicitação seguinte
volta a orientar o grupo pequeno. Mantidos limites de chamadas/contexto/prazo,
interrupção após duas respostas sem progresso e salvamento do trabalho válido.

Separados `records` e `drafts` nos lotes pendentes. Fichas em revisão também
precisam passar pela estrutura, páginas e evidências literais, mas a conferência
ainda aberta não rejeita o grupo inteiro. Eventos completos são imutáveis.
Revisões mantêm IDs e as evidências literais anteriores, permitem dados
recuperados/corrigidos após releitura e guardam a versão anterior em
`review_history`, sem publicá-la como relatório final. Esse histórico é
revalidado contra a fonte e as evidências preservadas ao carregar o checkpoint.
Busca literal não comprova a semântica ou associação dos valores: a conferência
do conteúdo continua a cargo da análise e do caminho humano opcional.

Falhas estruturais/literais de registros do mesmo grupo são coletadas e enviadas
conjuntamente à única correção permitida, em `falhas_registros`; mensagem pública
continua segura e os detalhes ficam privados. O arquivo V8 aprovado não foi
alterado. Ajustadas somente as instruções técnicas de grupo/continuação/correção.
O modelo permanece `openai/gpt-6.1-terra`.

A regressão das respostas reais revelou uma condição adicional antes encoberta
pela primeira rejeição das fichas: um inventário declarava `revisada` e listava
a conferência de fichas ainda pendente. O caminho intermediário passou a tratar
pendências explícitas de ficha/inventário como trabalho aberto, mesmo com esse
rótulo, preservando os valores recebidos sem forçar sucesso. A validação final
continua exigindo todas as revisões concluídas e nenhuma pendência técnica.
Não foram apagadas notas nem promovidas páginas/fichas por conveniência.

O formato incremental passou à versão 2. Criada ferramenta privada e explícita
`infra.report_renderer.migrate_checkpoint`, sem rede e sem chamada de IA, para
a implementação anterior conhecida. Confere a chave/identidade exata de origem,
fonte, protocolo, modelo, V8, digest, páginas, registros e inventários. Bloqueia
origem/destino, salva atomicamente na nova identidade com procedência e mantém
o original. A repetição da mesma migração não apaga progresso posterior; outro
estado no destino impede sobrescrita. Não há fallback, migração automática na
rota HTTP ou parâmetro de checkpoint no navegador. Sem serviço, variável,
tabela ou dependência de produção nova.

Validação atual: 194 testes Python passaram no contêiner isolado, com dez testes
que exigem Node.js não executados ali; esses dez passaram separadamente no host,
totalizando 204 testes Python aprovados. Mantidos três avisos de depreciação
preexistentes. O arquivo de testes JavaScript da tela passou. Novos casos cobrem
salvamento de fichas completas junto das pendentes, retomada de revisão após
falha, IDs/evidências/histórico, recuperação de campos, imutabilidade de eventos
completos, omissão/renumeração, pendências apesar de rótulo revisada, coleta
conjunta de falhas, estado malformado/corrompido, ausência de progresso sem PDF,
migração revalidada, idempotência, bloqueio e recusa de sobrescrita.

Integração na imagem definitiva, por workflow n8n isolado e IA simulada: um lote
concluído, uma ficha completa e duas fichas em revisão foram salvos antes de
uma falha HTTP 502 sintética. Após remover/recriar o contêiner com o mesmo
volume, a retomada fez uma nova chamada simulada para concluir as duas revisões,
sem reenviar o lote anterior ou refazer sua ficha completa. Conferidos os
quatro IDs, evidências e PDF no ZIP. Outra consulta ao estado completo fez
zero chamadas. Fonte densa foi dividida em lotes menores. Workflow, contêiner
e volume de teste removidos ao final; não houve chamada ao OpenRouter.

Em contêiner sem rede e com volumes originais somente leitura, copiado o
checkpoint real para armazenamento temporário e executada sua migração. As duas
respostas reais da tentativa 8 foram reproduzidas sem edição: agora o lote
113–115 guarda 16 fichas completas, dez em revisão e uma versão anterior no
histórico, mantendo intactos os 59 lotes anteriores. A chamada seguinte recebeu
as revisões pendentes e foi interrompida propositalmente pela simulação, depois
do salvamento. Isso demonstra continuidade e preservação, sem afirmar que o
restante foi revisado. Esse progresso simulado não foi importado no ambiente
operacional.

Antes da implantação, preservados fontes, imagem anterior e checkpoints em
diretório privado de `/tmp`; imagem marcada `before-review-groups-20261112`.
Confirmada ausência de execução principal ativa e estabilidade do protocolo e
das versões dos workflows. Migrados explicitamente somente os 59 lotes já
concluídos do checkpoint operacional: páginas 1–112, 143 registros e 1.612
referências literais verificadas contra o Markdown. O estado original permaneceu
com o mesmo hash; o novo usa arquivo `600`, diretório `700` e usuário do
renderizador. Fonte, modelo e prompt foram preservados.

Aplicada somente a imagem do renderizador local
`sha256:671589590b2cc64bf80e9485ad09354e2c7fe0196a71b1184278354daff01c55`.
Conferidos os hashes dos fontes instalados, identidade do checkpoint novo,
permissões e seis serviços saudáveis. Workflows principal e de erros mantiveram
as mesmas versões ativas. O V8 permanece com SHA-256
`3e75a9619a9cd5e7ce7080b22faad815148172cd0ffe30aa9db85e3b43b804e7`.
A prévia autenticada do botão respondeu `análise do Markdown salvo`; os próximos
alvos são 113–115. O documento continuou em erro com oito tentativas, sem nova
execução real, relatório final ou envio. A VPS não foi alterada.

Atualizados PRD, ROADMAP, README, fluxo, acessos e guias de operação/migração.
A homologação completa das 198 páginas permanece pendente da próxima retomada
confirmada pelo operador. Não houve consumo adicional de créditos de IA nesta
implementação; os testes usaram simulação ou dados já guardados, sem geração
externa. Conferidos diff, links locais e ausência de segredos nas alterações.

## 2026-11-12 — Tentativa 9 bloqueada por contexto integral acima do teto local

O usuário solicitou analisar outra falha e avaliar se seria melhor recomeçar.
Consultados os registros locais da tentativa 9, execução n8n 54: início às
19h58m42s e término às 20h03m43s de Brasília, duração aproximada de 5m01s.
Documento, tentativa e execução estão encerrados em erro. A mensagem informa
que fonte e continuidade excedem o tamanho suportado e nenhum texto foi
cortado. Os seis serviços estavam saudáveis. A categoria persistida é
infraestrutura, mas a causa apurada é a proteção de tamanho do orquestrador
da aplicação, não uma falha demonstrada da infraestrutura ou do provedor.

O lote continua com os alvos 113–115. Foram guardados quatro registros completos
e quatro fichas em revisão; estas declaram não ter conferido outras ocorrências
dos identificadores no documento integral. O contexto acumulado em `sent` passou
das sete páginas iniciais, 111–117, para as 198 páginas da fonte. A continuidade
tem dez blocos de inventário e 43 unidades. Não há diagnóstico de rejeição de
validação associado à tentativa 9; o limite dispara fora daquele caminho.
As respostas de solicitação de contexto não são guardadas como diagnóstico,
portanto não se atribui um número exato de expansões ou chamadas a esse estado.

O transporte constrói cada entrada juntando todas as páginas de `sent`, o
inventário acumulado, registros completos e fichas em revisão. O corpo de
dados reconstruído tem 2.251.331 bytes. O código interrompe ao exceder 480.000
bytes, antes de chamar a função de requisição ao OpenRouter. O contexto é
persistido no checkpoint antes dessa verificação. Após já existir continuidade,
o tratamento de limite não divide o lote para evitar perder seus registros.
Com a janela integral agora gravada, uma nova retomada sem ajuste repete o erro
antes de realizar a próxima chamada de IA.

Essa é a causa raiz demonstrada: expansão de contexto sem orçamento de tamanho
por janela, acumulada no estado retomável, sem caminho de recuperação da janela
excessiva quando o lote já tem continuidade. O teto local protege contra o envio
excessivo, mas o fluxo não consegue atender gradualmente à pesquisa integral
solicitada. Não se comprovou limite técnico do modelo, recusa HTTP do OpenRouter
ou novo esgotamento de crédito. O pedido de revisão exige buscar ocorrências;
não deve ser resolvido marcando a revisão como feita ou eliminando essa pendência.

Em contêiner isolado sem rede, com os volumes somente leitura, conferidos hash
do Markdown, 198 marcadores, digest e identidade do checkpoint, todos os lotes,
registros e revisões. Permanecem válidos 59 lotes concluídos, páginas 1–112,
143 registros e 1.612 referências literais. No lote pendente, os quatro registros
completos e as quatro fichas em revisão somam 142 referências literais válidas;
isso não conclui as conferências semânticas pendentes. O estado anterior à
migração também continua guardado separadamente, sem novos grupos.

Reproduzida a orquestração usando o estado atual em memória e uma função de
requisição que falharia caso fosse chamada. Obtida exatamente a exceção de
tamanho antes da função de IA; não houve mutação do estado. Com a janela inicial
111–117 e as páginas citadas pelos registros/inventário, o corpo reconstruído
teria 130.900 bytes, abaixo do teto. Essa comparação é apenas diagnóstico:
nenhuma página foi removida do checkpoint e não se considera cumprida a busca
de ocorrências nas outras páginas.

Recomendado preservar PDF, Markdown e checkpoint e corrigir a recuperação de
contexto: localizar ocorrências no Markdown e enviar páginas relevantes em
janelas controladas, checando o tamanho antes de gravar/enviar a expansão.
Pesquisas ainda não executadas precisam permanecer explícitas e continuar em
etapas, sem inventar ausência de informação. A recuperação do estado atual numa
nova implementação deve ser explícita e revalidada, conservando lotes, IDs,
evidências e fichas abertas. Reiniciar pela página 1 não elimina a causa e
refaz as 112 páginas que passaram na validação; não há corrupção demonstrada
que justifique descartá-las. Não recomendar outra tentativa com a mesma janela
excessiva antes do ajuste.

Atualizados LOG e ROADMAP; corrigido também um caractere de formatação indevido
no PRD, sem mudar requisito. Nenhuma alteração de código, workflow, ambiente,
checkpoint operacional ou VPS foi feita. Nenhum reinício ou nova chamada de IA
foi realizado. A suíte de aplicação não foi reexecutada: a validação atual foi a
revalidação e a reprodução isolada descritas. Conferidos diff e links locais,
sem commit ou push. A skill global karpathy-guidelines continuava ausente na
busca local; mantida a distinção entre fatos comprovados e limites não apurados.

## 2026-11-12 — Recuperação de contexto em janelas e retomada da tentativa 9

O usuário autorizou implementar e testar o ajuste definido na investigação da
tentativa 9. A causa era o envio cumulativo das 198 páginas em cada chamada,
com 2.251.331 bytes de dados e teto local de 480.000 bytes. O objetivo é atender
ao pedido de pesquisa sem perder os lotes ou declarar revisão não executada.

Criado `context_window.py`: a recuperação mantém páginas solicitadas e
entregues, resultados de buscas e a última janela sem resposta aceita. Cada
pacote é medido em bytes UTF-8, incluindo continuidade, diagnóstico e resposta
anterior na correção, antes de persistir uma ampliação. Envia páginas inteiras,
priorizando alvos, evidências das fichas/histórico e ocorrências recuperadas.
Vizinhas opcionais cedem espaço à fila. Se nem uma página obrigatória com a
continuidade couber, interrompe com o progresso guardado, sem cortar a fonte.

O modelo pode pedir até 16 termos por `buscas_necessarias`, além dos números de
página por `contexto_necessario`. Identificadores confirmados nas quatro fichas
priorizadas também geram pesquisa local. A busca percorre todo o Markdown por
substring literal exata e informa método, total examinado e páginas com
ocorrências; estas e suas vizinhas entram na fila. Zero ocorrências não atesta
ausência semântica/documental. Há limite de 256 termos por lote, sem truncar
resultados já guardados. Mantidos Terra e V8 aprovado, sem nova dependência,
variável de ambiente, serviço, fallback ou mudança de workflow.

Pedidos grandes são atendidos em várias chamadas; entregar uma janela não
consome outro pedido de contexto nem prova sua revisão. Um lote não fecha
enquanto restar página solicitada por entregar. A continuidade preserva eventos
completos, fichas em revisão, IDs, evidências e histórico. Limite de saída após
pedido aceito não divide o lote descartando sua fila. Resposta rejeitada mantém
a janela necessária à retomada. O teste inicial encontrou perda de uma página
adicional na correção: as páginas reais citadas pelo grupo rejeitado passaram
a compor a chamada corretiva, respeitando o mesmo orçamento.

O protocolo privado passa ao formato 3, cuja identidade inclui as instruções
e o código de recuperação. A migração explícita aceita apenas as implementações
conhecidas dos formatos 1 e 2, revalida todo o estado contra a mesma fonte e
mantém o original. No formato 2, o `sent` antigo vira solicitação pendente;
não se presume que páginas salvas antes de uma falha tenham sido entregues.
O núcleo é reconstituído pelos alvos e evidências, com busca dos identificadores
das fichas priorizadas e conferência da próxima janela antes de gravar.
Conservados bloqueios, escrita atômica, origem registrada, idempotência e
recusa de sobrescrita. Não há migração pela landing nem edição manual do estado.

Antes da implantação, preservados fontes, checkpoints e imagem anterior em
cópia local protegida. Os testes finais passaram: 211 testes Python em
contêiner sem rede e dez contratos dependentes de Node.js executados no host,
totalizando 221. O módulo de testes da interface em Node também passou.
Cobertos orçamento UTF-8/correção, páginas inteiras, busca literal, pedido
integral, falha e retomada, proteção da fila sob limite de saída, rejeição e
reenvio da janela, corrupção e migração com fichas preservadas. Permanecem
somente os avisos de depreciação conhecidos do ambiente de testes.

Integração local com workflow n8n temporário e IA simulada: documento sintético
de 30 páginas acima do teto total, falha após salvar uma janela, recriação do
contêiner com o mesmo volume privado e retomada com HTTP 200. Foram entregues
as 30 páginas solicitadas, preservados os três IDs e gerado PDF/ZIP. O maior
pacote tinha 453.489 bytes. A análise já concluída foi reutilizada sem novas
chamadas. Uma expectativa do simulador precisou ser corrigida para reconhecer
a ficha que já passara a concluída; a execução final passou. Workflow,
contêiner e volume sintéticos foram removidos.

Regressão da tentativa 9 sem rede, com originais somente para leitura e estado
em cópia temporária: mantidos os 59 lotes concluídos, páginas 1–112 e 143
registros, além dos quatro registros completos e quatro fichas abertas do
lote 113–115. Três janelas foram recebidas e salvas, com maior pacote de
479.732 bytes e 102 páginas ainda na fila após a interrupção sintética. A
continuidade documental ficou idêntica e o arquivo original permaneceu intacto.
Isso confirma o avanço técnico além do antigo bloqueio; não homologa a revisão
semântica nem a conclusão das 198 páginas. Nenhuma chamada externa de IA ou
consumo adicional de créditos foi realizado nos testes.

Implantada somente a imagem final do renderizador local,
`sha256:2695b6adaca7130c539b916736cf8032abd2de9dd71d59d49112310a2e0d6416`.
Antes e depois, confirmados protocolo inalterado com nove tentativas, ausência
de processamento principal ativo e mesmas versões dos workflows principal e
de erro. A ferramenta migrou o checkpoint operacional do formato 2 para nova
identidade do formato 3, preservando o arquivo de origem e todos os lotes,
registros, fichas, evidências e histórico. As 198 páginas do `sent` anterior
ficaram solicitadas, sem presumir entrega ou revisão. Conferidos hashes dos
fontes instalados, usuário 10002, arquivos 600, diretórios 700, Terra, hash do
V8 aprovado e seis serviços saudáveis. A prévia autenticada continua mostrando
`análise do Markdown salvo`; os próximos alvos são 113–115.

Atualizados PRD, ROADMAP, README, fluxo, acessos e guias de operação. Conferidos
diff, links locais, exports inativos/sem credenciais e ausência dos valores
protegidos nos arquivos alterados, sem exibir segredos. Preservadas as mudanças
locais preexistentes. Sem commit, push, nova tentativa real, envio ou mudança
na VPS. O processamento integral aguarda a confirmação de **Reprocessar**.
O backup permanece local e protegido. A skill global karpathy-guidelines não
foi encontrada; aplicados os princípios de escopo mínimo e validação por
evidência, sem instalar dependências ou skills adicionais.

## 2026-11-12 — Tentativa 10: limite de pedidos de contexto, distinto do tamanho

O usuário informou outra falha e pediu comparar com a última. Consultados
documento, tentativas, erros, execução n8n, imagem instalada, código e
checkpoint privado em modo de investigação. A tentativa 10, execução 69,
começou às 20h55m07s e terminou às 21h08m09s de Brasília, aproximadamente
13m02s. Está encerrada em erro, sem processamento principal ativo nem relatório
final. A mensagem é `limite de novos pedidos de contexto do lote atingido;
fila preservada`. Os seis serviços estão saudáveis. A imagem permanece a
versão final da correção anterior, com Terra e protocolo privado de formato 3.

O erro anterior da tentativa 9 era o corpo cumulativo de 2.251.331 bytes acima
de 480.000. O erro atual é o contador `context_requests` em `incremental.run`:
ele nasce uma vez por lote e cresce sempre que `context_window.request` aceita
uma busca nova ou ampliação de páginas. Uma busca inédita conta mesmo que
suas ocorrências já pertençam a páginas entregues. Após três pedidos novos,
o quarto dispara a proteção. Salvar progresso dos grupos não reinicia esse
contador. A interrupção ocorre antes de gravar a proposta do quarto pedido;
a mensagem de fila preservada se refere ao estado anteriormente aceito.
Não há arquivo de diagnóstico da tentativa 10 para recuperar o corpo exato
desse pedido; não se atribuem termos específicos ao pedido que disparou o erro.

Houve progresso com a recuperação em janelas: o checkpoint registra entrega
das 198 páginas solicitadas e nenhuma página ainda pendente de envio, sem
atestar leitura ou revisão semântica completa. Guarda 43 buscas literais,
revalidadas contra o Markdown. Permanecem inalterados os 59 lotes concluídos,
páginas 1–112, 143 registros. O lote 113–115 passou de quatro completos e
quatro em revisão para 24 completos e zero em revisão, com quatro versões
históricas. Seu inventário contém 24 IDs, todos com registro guardado, mas o
lote permanece parcial; isso não homologa cobertura ou encerramento da análise.

Em contêiner sem rede e com volumes somente para leitura, conferidos SHA-256
da fonte, 198 marcadores, identidade, digest e validação integral do estado.
Os lotes concluídos ficaram idênticos ao estado anterior; os quatro eventos
completos originais permanecem idênticos, e os IDs/evidências das quatro fichas
antes abertas continuam preservados. A próxima chamada usa as páginas 111–117
e 203.514 bytes de dados, abaixo do teto de 480.000. Isso confirma que a próxima
janela não reproduz o bloqueio de tamanho da tentativa 9.

Reproduzido o caminho atual com cópia do estado apenas em memória e respostas
de busca sintéticas: no quarto pedido novo ocorreu exatamente a exceção da
tentativa 10. O checkpoint original permaneceu intacto, sem requisição externa
de IA. Os dois primeiros comandos de verificação não concluíram a validação
por configuração de stdin e nome de campo no script de inspeção; corrigido
o script, a execução final confirmou todos os resultados acima. Não foram
falhas adicionais da aplicação.

Recomendação: distinguir buscas locais de ampliações de páginas, vincular o
controle de repetição ao progresso entre grupos e guardar o pedido pendente
antes de interromper. Preservar os limites de tamanho, chamadas, prazo e
quantidade de buscas, além da detecção de repetição sem progresso. Cobrir em
teste mais de três grupos de buscas inéditas com avanço válido no mesmo lote;
essa sequência não estava coberta na integração anterior de janela integral,
falha e retomada. Não há corrupção demonstrada que justifique reiniciar pela
página 1 ou reenviar o PDF. Uma retomada sem ajuste reinicia o contador, mas
pode atingir a mesma proteção de novo; não foi disparada automaticamente.

Atualizados somente LOG e ROADMAP. Nenhuma alteração funcional, workflow,
modelo, configuração, checkpoint operacional ou VPS foi realizada. Nenhuma
nova tentativa real, envio ou consumo adicional de créditos nesta investigação.
A suíte de aplicação não foi reexecutada: as verificações atuais são a
revalidação e a reprodução offline descritas, além de diff e links locais.
Preservadas mudanças preexistentes, sem commit ou push. A skill global
karpathy-guidelines continua ausente na busca local; aplicados os princípios
de escopo mínimo e conclusão limitada à evidência obtida.

## 2026-11-12 — Separação de buscas locais e ampliações com avanço dos grupos

O usuário autorizou aplicar o ajuste identificado na tentativa 10. Lidos PRD,
ROADMAP, LOG, AGENTS e implementação relacionada. Antes de alterar o ambiente,
preservados fontes/documentos, checkpoints e imagem anterior em cópia local
protegida. Confirmado protocolo em erro com dez tentativas e nenhuma análise
principal ativa. A skill global karpathy-guidelines continua ausente na busca
local; mantidos escopo mínimo e validação por evidências, sem instalar skills.

`context_window.request` agora distingue ampliação explícita de páginas e
busca literal. Somente páginas inéditas em `contexto_necessario` consomem o
orçamento de ampliações; buscas locais não o consomem, mesmo quando suas
ocorrências acrescentam páginas à fila. Consultas permanecem limitadas a 16
termos por pedido e 256 por lote. Uma repetição sem busca inédita nem página
pendente continua rejeitada. Entregar uma fila já aceita não é nova ampliação.

`incremental.run` mantém o teto de três ampliações desde o último progresso
validado do grupo, em vez de somar buscas ao longo de todo o lote. Novos
registros, fichas concluídas, páginas analisadas ou inventários revisados
reabrem o orçamento. Uma resposta idêntica, busca ou entrega de contexto não
representa esse progresso. Mantidos limite de 32 chamadas por lote/execução,
prazo total, duas respostas sem progresso, limite de dados de 480.000 bytes,
integridade das evidências e revisão final estrita. Não há troca de modelo,
prompt V8, fallback, dependência, serviço ou variável de ambiente.

Após conferir que a janela cabe, o pedido válido é salvo antes de interromper
por limite de ampliações. Assim, o quarto pedido sem avanço permanece na fila
e é entregue na retomada. Não foi removida a proteção contra laços indefinidos:
pesquisas inéditas consecutivas continuam sujeitas aos limites de termos,
chamadas e prazo, e buscas já atendidas sem trabalho novo são rejeitadas.

O formato de estado permanece 3; a identidade muda pelo código. A migração
explícita passou a reconhecer também a implementação anterior de janelas,
mediante hashes exatos de código/instruções. Revalida fonte, modelo, V8 e
todo o estado, conservando lotes, registros, fichas, versões históricas,
buscas, entregas e fila. A origem fica intacta e registrada no destino;
idempotência, bloqueios e recusa de sobrescrita continuam. Não há migração
automática na API nem parâmetro de checkpoint no navegador.

Validação atual: 219 testes Python no contêiner sem rede e dez contratos que
dependem de Node.js no host, totalizando 229. O módulo JavaScript da interface
também passou. Os 79 testes direcionados do renderizador passaram antes da
suíte completa. Novos casos verificam seis grupos de buscas com registros e
evidências preservados; buscas sem gasto de ampliações; renovação após avanço;
grupo idêntico/entrega sem renovação; quarto pedido salvo e retomado; repetição
de busca bloqueada; consultas inéditas respeitando o limite total; migração
com contexto preservado e rejeição de contexto corrompido. Permanecem apenas
os avisos de depreciação conhecidos do ambiente de testes.

Integração n8n com workflow temporário e IA simulada, usando o contrato do nó
HTTP real: superados quatro grupos de buscas e salvos quatro registros do lote
pendente, além do lote anterior concluído. Uma falha intencional interrompeu
a análise. Recriado o contêiner com o mesmo volume, a retomada reutilizou
páginas 1–5, completou seis grupos de buscas e gerou PDF/ZIP com sete IDs
preservados. Maior pacote de 6.695 bytes; nova consulta à análise completa
fez zero chamadas. Workflow, contêiner e volume temporários foram removidos.

Regressão offline da tentativa 10: volumes originais somente para leitura,
cópia temporária do checkpoint e migração com a imagem candidata. Lotes e
grupos permaneceram idênticos ao estado original após migrar. A simulação
aceitou quatro buscas inéditas e parou intencionalmente antes de concluir
o documento real; pacotes de até 204.090 bytes. Preservados 59 lotes, páginas
1–112, 143 registros, os 24 completos do lote 113–115, versões históricas e
entregas. As consultas sintéticas ficaram somente na cópia temporária. A
fonte e o checkpoint original permaneceram intactos. Essa prova técnica não
homologa a revisão semântica ou o relatório integral das 198 páginas.

Implantada apenas a imagem do renderizador local
`sha256:6e006235e4e94c59c3e9ff671d896bbbb707bac8fccab2e6d1dc4a6b424d0ffc`.
Migrado explicitamente o estado operacional da implementação anterior do
formato 3 para a identidade nova, com comparação integral dos lotes e tarefas
pendentes contra o original. O destino mantém 59 lotes, 112 páginas, 143
registros e, no lote 113–115, 24 completos, zero fichas abertas, quatro versões
históricas, 43 buscas e as 198 páginas entregues. Não foram importadas buscas
sintéticas nem presumida revisão das páginas pelo controle de entrega.

Conferidos hashes instalados, identidade, Terra, V8 aprovado, usuário 10002,
arquivos 600/diretórios 700 e seis serviços saudáveis. Antes e depois da
implantação, documento permaneceu com dez tentativas, nenhuma análise principal
ativa e mesmas versões dos workflows principal e de erro. A prévia autenticada
do botão confirma `análise do Markdown salvo`; próximos alvos 113–115.

Atualizados PRD, ROADMAP, fluxo e guias de operação/migração. Conferidos diff,
links locais, exports inativos sem credenciais e ausência dos valores reais
protegidos nas alterações. Preservadas mudanças preexistentes. Sem commit,
push, nova tentativa real, envio, chamada externa de IA, consumo adicional de
créditos ou mudança na VPS. A retomada real aguarda confirmação do operador.

## 2026-11-12 — Tentativa 11 interrompida por HTTP 402 do OpenRouter

O usuário perguntou se a nova falha ocorreu por créditos. Consultados os
registros locais: tentativa 11, execução 74, iniciada às 21h29m49s e encerrada
às 22h18m47s de Brasília, aproximadamente 48m58s. Documento e tentativa em
erro; nenhuma execução principal ativa. Mensagem final: `OpenRouter retornou
HTTP 402`. Os erros anteriores de tamanho e quantidade de pedidos de contexto
não são a mensagem desta interrupção.

Consultados somente `GET /api/v1/key` e `GET /api/v1/credits`, com a credencial
protegida do renderizador e sem enviar documento ou gerar conteúdo. A chave
tem limite mensal de US$ 100, uso acumulado/mensal de US$ 19,512259845 e margem
de US$ 80,487740155. A conta informa US$ 20 de créditos totais e o mesmo uso
acumulado, resultando em saldo de US$ 0,487740155. Não atribuir esse uso
acumulado ao custo exclusivo da tentativa ou do documento.

A documentação oficial de
[erros do OpenRouter](https://openrouter.ai/docs/api_reference/errors-and-debugging)
associa HTTP 402 a créditos insuficientes e também descreve orçamento de
requisições em trânsito. O saldo baixo da conta é o principal indício atual;
a margem mensal da chave não está esgotada. O transporte descarta corpo e
cabeçalhos de erros HTTP, portanto não foi possível confirmar retrospectivamente
o subtipo do 402 nem o montante de reserva exigido pela chamada. Não declarar
saldo zero, pois a consulta mostrou saldo positivo inferior a US$ 0,49.

Recomendado verificar/repor o saldo da conta antes de retomar pelo mesmo
protocolo. Aumentar o limite da chave não adiciona saldo. Não houve recarga,
alteração de limite, reprocessamento automático ou chamada de geração de IA.
Atualizados somente LOG e ROADMAP; sem mudança funcional, testes de aplicação,
commit, push ou alteração na VPS. Credencial não exibida nem copiada para os
registros; preservadas mudanças preexistentes.

## 2026-11-14 — Tentativa 12 bloqueada pelo crescimento da continuidade

Após o usuário informar nova falha no teste local, consultados PostgreSQL,
estado dos serviços e checkpoints privados. A tentativa 12 do mesmo protocolo,
execução n8n 76, começou às 14h18m14s e terminou às 14h41m40s de Brasília,
aproximadamente 23m25s. Documento e tentativa estão em erro. A mensagem final
é `uma página inteira ou a continuidade obrigatória não cabe na janela;
progresso preservado`. Os seis serviços estavam saudáveis; nenhuma execução
principal estava ativa na consulta. Essa interrupção ocorre no orçamento local
do pacote, antes da próxima chamada ao provedor.

Causa raiz identificada no envio incremental: `context_window.data` inclui
todas as fichas completas do lote em `registros_preservados` a cada chamada.
No lote 116–117, as 70 fichas já validadas ocupam 449.218 bytes. O inventário
ocupa 24.437 bytes e o controle de contexto, com 93 buscas, ocupa 11.945 bytes.
Contando estrutura e demais campos, o pacote sem nenhum texto documental já
tem 486.330 bytes. Com as duas páginas obrigatórias, tem 511.269 bytes, acima
do teto de 480.000 bytes UTF-8 previsto no RF-04.

Grupos de até quatro eventos limitam a resposta, mas não os registros antigos
reenviados. A divisão inicial considera o tamanho do texto das páginas;
`incremental.run` não divide o lote por `AnvisaOutputLimit` depois que já existe
continuidade. O lote aceita e salva novos grupos, até a chamada seguinte
não comportar o estado acumulado. A proteção interrompe sem cortar a fonte,
mas a implementação atual não consegue continuar desse checkpoint.
O nó `OpenRouter - Prepare verification bundle` propaga o detalhe recebido do
renderizador; seu nome não significa falha na montagem do ZIP. A categoria
`infraestrutura` registrada no banco não identifica esse limite de montagem.

Reprodução com a imagem instalada em contêiner temporário, rede desabilitada,
usuário 10002 e os dois volumes originais somente para leitura. Usados o
parser de páginas e os módulos instalados. Hash do Markdown, digest do estado
e validação integral do checkpoint passaram. A chamada de IA foi substituída
por bloqueio em memória; `incremental.run` reproduziu a mesma exceção com zero
chamadas. O hash do arquivo de checkpoint permaneceu igual antes e depois.
Não foram executadas a suíte de aplicação nem uma nova análise real.

Estado preservado: 60 lotes completos, páginas 1–115 e 180 registros desses
lotes; mais 70 fichas completas no lote 116–117, cujo inventário continua
pendente. Existem 39 lotes pendentes. Isso comprova preservação e validação
mecânica do progresso, não homologação semântica do relatório integral de
198 páginas. Ainda não há relatório final.

Registrado como próximo trabalho corrigir o crescimento da continuidade
reenviada em lotes densos, conservando fichas integrais, IDs, evidências e
inventários no armazenamento privado e validando o limite de pacote e a
retomada antes de outra tentativa real. Repetir a retomada com o código atual
reproduz a falha antes da IA. Nenhuma solução funcional foi aplicada nesta
análise; mantidos os requisitos e o limite do PRD.

Atualizados somente este LOG e o ROADMAP. Sem edição/migração de checkpoints,
nova tentativa, envio, chamada externa de IA, commit, push ou mudança na VPS.
Exibidos apenas metadados, contagens e mensagens técnicas; documentos e
credenciais permaneceram protegidos. Preservadas mudanças locais anteriores.

## 2026-11-14 — Continuidade densa corrigida e aplicada no renderizador local

O usuário autorizou aplicar a correção para continuar os testes. Lidos PRD,
ROADMAP, LOG, AGENTS, implementação e testes relacionados. A skill global
karpathy-guidelines segue ausente na busca local; mantidos escopo mínimo e
validação por evidências. Antes de alterar, confirmados documento em erro com
12 tentativas e nenhuma execução principal ativa. Preservados fontes e guias,
backup privado do volume de diagnósticos/checkpoints e imagem anterior. A
cópia local usa diretório 700 e arquivos 600, sem inclusão no Git.

`context_window.build` primeiro tenta enviar as fichas concluídas completas.
Se não couberem, usa somente no pacote da chamada um índice de todos os
eventos concluídos, com ID, categoria, destino, páginas, hash canônico e
referências confirmadas de até 256 caracteres, sem cortar valores. As
instruções de transporte explicam que esse índice não é ficha ou evidência,
que campos ausentes não indicam ausência documental e que seus IDs precisam
permanecer no inventário. Nenhuma ficha completa é removida do checkpoint.
O aplicativo reúne os originais no resultado final e continua rejeitando
alterações de eventos concluídos, duplicações e perda de IDs. Fichas em
revisão, inventários, diagnóstico e resposta rejeitada continuam integrais.
Todas as páginas obrigatórias dos alvos e evidências/histórico permanecem;
se esse conteúdo ainda não couber, a proteção continua interrompendo.

Mantidos limite de 480.000 bytes, modelo Terra, V8 aprovado byte a byte e
formato de checkpoint 3. Mudaram código e instruções adicionais de transporte,
portanto a identidade é nova. A migração explícita reconhece os hashes exatos
da implementação anterior de buscas, revalida o estado e confere a primeira
janela antes de salvar o destino. Conserva origem, proveniência, bloqueios e
idempotência; não existe migração automática pela API, dependência nova,
mudança de workflow ou variável adicional.

Validação atual: 228 testes Python em contêiner sem rede e dez contratos com
Node.js no host, totalizando 238, mais o módulo JavaScript da interface.
Passaram casos de índice com todas as fichas preservadas, retomada após salvar
um novo grupo, reaproveitamento de lotes concluídos, alteração indevida de
ficha, duplicação com outro ID, omissão de inventário, revisão pendente,
correção integral com suas páginas, excesso obrigatório ainda bloqueado e
migração idempotente. A API sintética gerou PDF e ZIP após a retomada, e o
JSONL do pacote contém todas as fichas originais completas. Restam somente
avisos de depreciação conhecidos. Os dez contratos omitidos no contêiner por
ausência de Node.js passaram no host. A coleta foi direcionada a `tests/`;
uma coleta inicial na raiz alcançou testes em cópia histórica de `output/`.

Na regressão offline do documento real, volumes originais somente para
leitura, cópia temporária do checkpoint, imagem candidata e rede desabilitada.
Migrados 60 lotes completos e todo o primeiro lote pendente sem alterar
fichas, inventários ou contexto. A janela que exigia 511.269 bytes mínimos
passou a 186.088 bytes, incluindo as páginas vizinhas 114–119. Duas chamadas
simuladas tiveram esse tamanho; a segunda interrompeu intencionalmente após
validar a continuidade sem acrescentar achados ao documento real. Confirmadas
persistência e migração idempotente. Nenhuma chamada de IA externa foi feita,
e o checkpoint operacional de origem permaneceu igual ao backup.

Implantada somente a imagem do renderizador local
`sha256:5b78a177fb69d236abfeb8a6f745986a88c40b8330705e2ddc7f461779e96ab5`.
Com análise parada, migrado explicitamente o checkpoint da implementação
anterior para a identidade nova e comparados integralmente `completed` e
`pending` contra o original. Preservados 60 lotes, páginas 1–115, 180 registros
dos lotes concluídos e 70 fichas completas do lote 116–117; 39 lotes continuam
pendentes. Conferidos hashes de código instalados, identidade, digest do
estado, proveniência, V8, Terra e arquivos 600/diretórios 700. O hash da
origem é idêntico ao arquivo do backup protegido. Os seis serviços ficaram
saudáveis, a landing respondeu HTTP 200 e a prévia autenticada do protocolo
retornou `análise do Markdown salvo`.

Atualizados PRD, ROADMAP, fluxo e guias técnicos. A retomada real fica para o
operador no mesmo protocolo; não é necessário reenviar o PDF. A reprodução
e o teste sintético não homologam a revisão semântica ou o relatório integral
de 198 páginas. Conferidos diff e links locais; Gitleaks não encontrou segredos
no diff isolado desta correção. Sem nova tentativa real, envio, chamada externa
de IA, commit, push ou alteração na VPS. Preservadas mudanças locais preexistentes.

## 2026-11-14 — Tentativa 13 interrompida pelo prazo global da análise

Após o usuário informar nova falha, consultados PostgreSQL, configuração
efetiva do renderizador/n8n, snapshot do workflow da execução e checkpoint.
A tentativa 13, execução 78, começou às 15h08m21s e terminou às 16h39m29s de
Brasília, aproximadamente 1h31m08s. Documento e tentativa estão em erro, com
mensagem `tempo total excedido; o progresso validado foi preservado no
checkpoint`. Nenhuma execução principal ativa na consulta; seis serviços
saudáveis. O registro usa categoria `infraestrutura` e o último nó de
preparação do ZIP, mas a condição responsável está no renderizador.

Causa confirmada: `OPENROUTER_TIMEOUT_SECONDS=5400` nos dois serviços. A
entrada de análise transforma esse valor em um único deadline monotônico
para todos os lotes e grupos da tentativa. `incremental.run` calcula o tempo
restante antes de cada chamada e interrompe quando ele chega a zero, mesmo
que os últimos grupos tenham produzido progresso. Avanço e salvamento não
renovam esse prazo. O nó HTTP do snapshot da execução usa o mesmo valor mais
120 segundos, total de 5.520 segundos; a mensagem corresponde à guarda
explícita do renderizador, não ao timeout HTTP desse nó. A duração da execução
inclui as demais etapas; os registros disponíveis não discriminam o tempo de
cada resposta do provedor, validação ou escrita.

A correção anterior permitiu concluir o lote 116–117, com 102 registros.
O estado final desta tentativa guarda 61 lotes completos, páginas 1–117 e
282 registros desses lotes, mais 76 fichas completas do lote 118–120. Não há
fichas abertas em revisão; há 38 lotes pendentes, e o inventário do lote atual
continua aberto. Foram preservados 108 registros adicionais em relação ao
estado anterior à tentativa. O checkpoint foi atualizado às 16h39m28s, cerca
de um segundo antes do erro, demonstrando progresso salvo até a interrupção.

Conferidos hash do Markdown, digest e revalidação integral do checkpoint.
A janela seguinte contém páginas 116–122 e 458.570 bytes, abaixo do teto de
480.000, sem necessidade de índice nesta chamada. Reprodução em contêiner
sem rede, com os volumes originais somente para leitura e checkpoint em
memória: deadline expirado gerou a mesma mensagem antes de qualquer chamada;
com prazo novo, chegou à próxima solicitação dos alvos 118–120 e foi
interrompido intencionalmente antes da IA. Zero chamadas externas e hash do
checkpoint original inalterado. Essa prova não homologa os resultados ainda
pendentes nem prevê a duração da análise restante.

Retomar pelo mesmo protocolo permite continuar desse estado, com um novo
orçamento por tentativa. Como evolução operacional, avaliar continuação
controlada antes do fim do prazo, preservando checkpoint e limites globais
contra execuções indefinidas. Não foi aplicada renovação automática, aumento
de timeout ou qualquer mudança funcional durante o diagnóstico.

Atualizados apenas LOG e ROADMAP. Sem nova análise real, chamada externa de
IA, envio, alteração de configuração, checkpoint, workflow ou VPS, commit ou
push. Não foi executada a suíte de aplicação nesta investigação. Preservadas
mudanças locais preexistentes; exibidos somente metadados e mensagens técnicas.

## 2026-11-14 — Meta de 90 minutos separada do prazo máximo de execução

O usuário esclareceu que 90 minutos era um valor ideal de desempenho, não uma
regra para parar o processamento, e solicitou desabilitar a trava. Registrada
a decisão no RNF-08 do PRD e ajustadas as referências de prazo do RF-04 para
preservar timeout por chamada. A skill karpathy-guidelines segue ausente na
busca local; mantidos escopo mínimo e validação por evidências. Antes de
alterar, confirmados 13 tentativas, documento em erro e nenhuma análise
principal ativa. Preservados fontes/guias, `.env`, banco, workflow implantado,
volume de diagnósticos/checkpoints e imagem anterior em backup privado com
diretório 700 e arquivos 600, fora do Git.

`OPENROUTER_TIMEOUT_SECONDS=0` passa a ser o padrão da API, Compose e exemplo
de ambiente, significando ausência de deadline global da análise. O mesmo
valor foi aplicado ao `.env` local protegido; comparação com o backup
confirmou que nenhuma outra variável foi alterada. `anvisa_v8.analyze` passa
deadline `None` nesse modo. `incremental.run` continua limitando cada chamada
ao provedor a 360 segundos, além dos tetos de grupos, contexto, buscas,
validação e duas respostas sem progresso. Um prazo global positivo, até
14.400 segundos, permanece opcional se configurado explicitamente; a meta de
90 minutos não ativa esse corte. V8, Terra e instruções de conteúdo permanecem.

Conferido o código instalado do n8n 2.30.5 e o transporte HTTP real. O nó
HTTP 4.2 transforma timeout zero numérico no padrão de cinco minutos. A
alternativa de string `"0"` foi rejeitada no teste: Axios/follow-redirects
aciona expiração imediata. Alterado somente `OpenRouter - Analyze and render
V8` para `typeVersion: 2`, disponível na mesma instalação e que transmite
zero numérico sem substituição. Convertidos seus parâmetros equivalentes,
mantendo URL, corpo JSON, contexto de diagnóstico, header interno, resposta
completa e tratamento de HTTP não 2xx. Conexões, demais nós, configurações e
referências de credenciais foram comparados integralmente ao export anterior
e permaneceram iguais. O conteúdo documental enviado é idêntico.

Export versionado permanece inativo e sem credenciais. A revisão local foi
importada no mesmo ID e publicada pelo CLI. Recriado o n8n para carregar a
revisão e o ambiente zero; confirmados `active=true` e versão publicada igual
à atual. O n8n já tinha prazo global de execução desabilitado (`-1`), e o
workflow não define outro prazo total. Não foi alterada essa configuração.

Validação: 238 testes Python no contêiner isolado, 13 contratos dependentes de
Node.js no host, total de 251, e o módulo JavaScript da interface. Após a
mudança do nó, os 30 contratos completos passaram no host. O teste adicional
com a classe e o adaptador HTTP reais do n8n, em contêiner sem rede externa,
conferiu timeout zero no socket, body e header fictícios, HTTP 200 e 502,
propagação literal do detalhe e timeout finito de chamada. Relógio simulado
avançou cinco horas com análise concluída e timeout de 360 segundos em cada
chamada. Casos sem progresso e excesso de grupos continuam interrompendo;
prazo positivo opcional ainda salva progresso antes de impedir outra chamada.
Permanecem somente os avisos de depreciação conhecidos da suíte.

A identidade muda pelo código, mantendo checkpoint formato 3. Acrescentada
ao migrador a implementação anterior com índice, reconhecida por hashes
exatos. Na cópia temporária do estado real, com volumes originais somente
para leitura e rede desabilitada, migrados 61 lotes e todo o progresso
pendente. Duas solicitações simuladas de 458.570 bytes e timeout de 360
segundos alcançaram os alvos 118–120 mesmo após duas horas simuladas. A
segunda interrompeu intencionalmente antes da IA. Preservados registros,
inventários, contexto e idempotência; checkpoint de origem inalterado.

Implantada a imagem local do renderizador
`sha256:2a4b936f3c7953bb31f476b71ceebe0dd7822d62ea26fe32f17cdc2044f79867`.
Com a análise parada, migrado explicitamente o checkpoint para a nova
identidade. Comparados integralmente `completed` e `pending`: 61 lotes
completos, páginas 1–117, 282 registros e 76 fichas completas do lote 118–120.
Conferidos origem idêntica ao backup, digest, identidade, V8, Terra e arquivos
600/diretórios 700. Renderizador e n8n carregaram `OPENROUTER_TIMEOUT_SECONDS=0`.
Os seis serviços estão saudáveis, landing e prévia autenticada responderam
HTTP 200; a retomada continua como `análise do Markdown salvo`.

Atualizados PRD, ROADMAP, README, fluxo, configuração de exemplo e guias.
Revisados diff e links locais; Gitleaks não encontrou segredos no diff isolado
desta mudança. Export versionado conferido inativo e sem credenciais.
Documento permanece em erro com 13 tentativas, pronto para retomada pelo
operador no mesmo protocolo. Sem nova análise real, chamada externa de IA,
envio, commit, push ou mudança na VPS. A validação sintética não homologa o
relatório integral de 198 páginas. Preservadas mudanças locais anteriores.

## 2026-11-14 — Continuação automática das janelas e retry de transporte

Após a explicação dos limites de seis minutos por chamada e 32 grupos por
lote, o usuário solicitou aplicar a tratativa de recuperação automática.
Lidos PRD, ROADMAP, LOG, AGENTS, implementação e testes. A skill global
karpathy-guidelines continua ausente na busca local; mantidos escopo mínimo
e validação por evidências. Confirmados documento em erro com 13 tentativas
e nenhuma análise principal ativa. Preservados fontes/guias, testes,
checkpoints privados e imagem anterior, com diretório de backup 700 e arquivos
600, fora do Git. Não houve mudança no workflow ou nas variáveis de ambiente.

As 32 chamadas passam a ser uma janela técnica, não uma condição de erro.
`incremental.run` recarrega e revalida o último checkpoint e continua o lote
na mesma requisição HTTP e tentativa do documento, mantendo o bloqueio de
concorrência. A comparação canônica exige que o estado persistido corresponda
ao estado corrente; ausência, corrupção ou divergência bloqueia outra chamada.
O contador da janela reinicia, mas a contagem total usada no diagnóstico
permanece acumulada. Correção em andamento, resposta rejeitada, ausência de
progresso, buscas, ampliações e falhas de transporte não são renovadas pela
troca da janela. Não há promoção artificial de páginas ou inventários.

`TransientAnvisaError` distingue conexão/timeout e HTTP 408, 429, 500, 502,
503 e 504. Essas falhas admitem a tentativa inicial e mais duas, com esperas
de 5 e 15 segundos. Antes de repetir, revalidar o checkpoint e reutilizar o
mesmo pacote, incluindo diagnóstico e resposta anterior de uma correção.
Receber uma resposta reabre o orçamento de transporte para a próxima chamada;
trocar a janela não o reabre. A terceira falha encerra com mensagem explícita
e checkpoint preservado. Crédito/autorização, JSON inválido, validação,
armazenamento e integridade não recebem esse retry. Uma retentativa não
concede outra correção estrutural ou literal, nem refaz os lotes concluídos.

Mantidos timeout individual de 360 segundos, prazo global zero, Terra, V8
aprovado e instruções de conteúdo. Não há fallback ou nova integração,
dependência, variável ou etapa no n8n. O resultado técnico final passa a
informar `continuacoes_automaticas` e `retentativas_transporte` daquela
execução. O formato privado continua 3; a identidade muda pelo código. O
migrador reconhece a implementação anterior sem prazo global por hashes
exatos e conserva estado original, proveniência, bloqueios e idempotência.

Validação atual: 270 testes Python no contêiner sem rede e 13 contratos com
Node.js no host, totalizando 283. Os 30 contratos completos passaram no host;
também passaram o módulo JavaScript da interface e o teste do nó/transporte
HTTP reais do n8n, sem chamadas externas. Casos novos e ajustados verificam
36 chamadas no lote com revalidação, retry com pacote igual, duas falhas e
sucesso, três falhas persistentes atravessando janelas sem renovar orçamento,
retomada posterior sem repetir lotes, renovação só após resposta recebida,
correção mantida durante retry e segunda rejeição sem outra correção. Também
verificados falta de progresso, limites de buscas/ampliações, corrupção,
ausência e divergência sem consumo adicional, classificação de HTTP,
crédito sem retry e API sintética com PDF após duas falhas HTTP 503. Permanecem
somente os avisos de depreciação já conhecidos.

Regressão offline do estado real: volumes originais somente para leitura,
cópia temporária do checkpoint e imagem candidata sem rede. Migrados 61 lotes
e todo o estado pendente sem alterar fichas, inventário ou contexto. Com uma
janela reduzida somente na simulação, uma falha de timeout foi recuperada,
o mesmo pacote de 458.570 bytes foi reutilizado e duas fronteiras de janela
foram revalidadas. A terceira solicitação simulada interrompeu antes da IA.
Nenhum achado foi acrescentado ao documento real. Conservados registros,
idempotência e origem com o mesmo hash; zero chamadas externas de IA.

Implantada apenas a imagem do renderizador local
`sha256:b547c6b3f10aaf4dc55e7e21a64b4d9559cd29ebe4919d6deed16e170663f45e`.
Com a análise parada, migrado explicitamente o checkpoint operacional e
comparados integralmente `completed` e `pending` contra a origem: 61 lotes,
páginas 1–117, 282 registros completos e 76 fichas do lote 118–120.
Conferidos hashes instalados, identidade, digest, V8, Terra, prazo global
zero, janela 32, esperas 5/15, arquivos 600 e diretórios 700. A origem é
idêntica ao backup. Seis serviços saudáveis, landing HTTP 200 e prévia
autenticada `análise do Markdown salvo`. O workflow principal permaneceu
na mesma versão publicada; n8n e configuração não foram alterados.

Atualizados PRD, ROADMAP, README, fluxo e guias. O operador pode retomar pelo
mesmo protocolo; a execução real continua pendente de conferência integral.
Revisados diff e links locais; Gitleaks não encontrou segredos no diff isolado
desta correção. Mantidos o export inativo e as referências de acesso protegidas.
Sem nova tentativa real, geração externa de IA, envio, commit, push ou mudança
na VPS. Preservadas mudanças locais anteriores; documentos e credenciais não
foram exibidos nem incluídos no diff.

## 2026-11-14 — Gargalo observado na análise sequencial do OpenRouter

O usuário questionou a lentidão, mantendo a orientação de não afetar a
execução atual. Consultados somente banco, contadores de processo/contêiner,
checkpoint, tamanhos de Markdown e diagnósticos existentes da tentativa 14,
execução 80, em análise do Markdown. Nenhum processo foi pausado, reiniciado,
instrumentado ou alterado. O tempo de CPU acumulado do uvicorn foi 56,75
segundos em 7.190,48 segundos de vida, média de 0,79% de um núcleo. Na amostra
Docker, renderizador estava em 0,20% de CPU e 78,76 MiB/512 MiB; n8n em 0,21%
e 333,3 MiB/2 GiB; PostgreSQL em 0,04% e 51,02 MiB/512 MiB. Ollama em 0%.
Esses dados não indicam saturação local de CPU/RAM nessa etapa.

Inspeção do código confirma uma requisição síncrona ao OpenRouter por vez,
grupos solicitados de até quatro fichas, reenvio de páginas e continuidade
completa quando ela ainda cabe no pacote, e cobertura/inventário acumulados
em cada resposta. O índice de fichas completas entra somente como alternativa
quando o pacote integral não cabe. A base de prompt/transporte/continuação
medida tinha 43.109 bytes, sem contar todo o contexto adicional. Dois blocos
densos já concluídos tinham 125 fichas em três páginas e 36 em duas páginas;
um lote posterior concluiu com zero fichas. Assim, página não é uma unidade
homogênea de custo, e a projeção anterior de 27 horas é apenas extrapolação
de baixa confiança, não previsão firme para o restante do documento.

Lida a documentação oficial de
[metadados de geração do OpenRouter](https://openrouter.ai/docs/api/api-reference/generations/get-generation)
e feitos dois GETs nesse endpoint, usando apenas IDs de gerações já
encerradas, com a chave protegida. Não foram enviados prompts/documentos,
gerado conteúdo ou consultado o endpoint de conteúdo da geração. A amostra
do lote 121–122 informou 76.061 tokens nativos de entrada, 10.092 em cache,
10.485 de saída, 102 de raciocínio, `generation_time=117423` e `latency=4059`.
O intervalo entre criação registrada pela API e diagnóstico local foi cerca
de 118 segundos. Voltaram quatro fichas; a resposta JSON compacta tinha
16.968 bytes de registros, 10.096 de inventário e 444 de cobertura.

A outra amostra, do alvo 128, informou 29.483 tokens nativos de entrada,
10.092 em cache, 3.258 de saída, 1.341 de raciocínio,
`generation_time=37542` e `latency=20401`. O intervalo até o diagnóstico local
foi cerca de 38 segundos. Não retornou fichas; vieram inventário e cobertura,
com uma referência literal rejeitada. Ambas passaram pelo provedor OpenAI
com Terra. São duas respostas que geraram diagnóstico de validação, não uma
amostra representativa de toda a execução. Os campos brutos de timing foram
registrados sem somar latência ao tempo de geração.

Conclusão observacional: espera de geração e quantidade de rodadas seriais,
amplificadas por grande entrada/saída e repetição do inventário, são os
principais candidatos ao gargalo. Ainda não há tempos persistidos para
todas as respostas aceitas, portanto não foi atribuído percentual exato a
provedor, rede, leitura, validação ou escrita. A troca automática de janelas
e os retries evitam interrupções recuperáveis, mas não reduzem esse trabalho.

Registrado como próximo trabalho medir todas as chamadas, reduzir repetição
no transporte mantendo fichas e inventários completos no servidor e avaliar
paralelismo somente de unidades independentes, sempre validando evidências,
cobertura e reconciliação. Nenhuma dessas propostas foi implementada durante
a execução. O checkpoint avançou de 122 para 130 páginas nas consultas,
reforçando a variação de densidade e de custo entre lotes.

Atualizados somente LOG e ROADMAP. Sem mudança funcional, teste de carga,
suíte de aplicação, chamada de geração, alteração de configuração, checkpoint,
workflow, modelo, prompt, contêiner, VPS, commit ou push. Preservadas alterações
locais anteriores e a execução corrente; exibidos somente metadados técnicos.

## 2026-11-14 — Execução 80 cancelada manualmente a pedido do usuário

O usuário solicitou parar o processamento por sua duração elevada.
Confirmados tentativa 14, execução 80, em análise do Markdown, e nenhuma
outra execução principal ativa. Solicitado cancelamento pelo endpoint
autenticado do n8n, usando os acessos locais protegidos e sessão somente em
memória, sem exibir credenciais. HTTP 200 e estado nativo `canceled`, com
encerramento registrado às 19h42m02s de Brasília.

Encerrado também o processo do renderizador, único serviço executando essa
análise, para impedir que a requisição síncrona continuasse após cancelar
o workflow. Os volumes foram preservados. Em contêiner sem rede e com os
volumes originais somente para leitura, conferidos hash do Markdown, digest
e revalidação integral do checkpoint. Preservados 130 de 198 páginas
concluídas, 477 registros dos lotes completos e 20 fichas completas do lote
131–132, sem fichas abertas em revisão. O último salvamento foi às 19h41m32s.
Nenhuma ficha foi promovida a concluída ou completada por suposição.

O cancelamento do n8n deixou documento e tentativa como `em_processamento`.
Após confirmar `canceled` e ausência de análise principal ativa, ajustados
somente os registros daquele protocolo/tentativa em transação condicionada:
status operacional `erro`, categoria `cancelamento_manual` e mensagem
`Processamento interrompido a pedido do usuário; progresso salvo preservado.`
Mantida a etapa `analise_markdown`, encerrada a tentativa com o horário do
n8n e acrescentado um evento de auditoria em `workflow_errors`. Essa mensagem
identifica uma decisão do operador, não uma nova falha técnica. Mantidos
14 tentativas e todo o histórico anterior.

Reiniciado somente o serviço do renderizador para manter a aplicação
disponível, sem retomar o trabalho cancelado. Não foi acionado reprocessamento,
envio ou nova tentativa. Checkpoints, artefatos, modelo, prompt, configuração
e workflows não foram alterados. Registrado o estado no ROADMAP; futuras
otimizações e retomada dependem da próxima ação autorizada do operador.
Sem teste de aplicação, commit, push ou alteração na VPS. Preservadas as
mudanças locais preexistentes e os dados privados.

## 2026-11-14 — Simulação de transporte incremental sem perda de dados

O usuário perguntou como reduzir repetição preservando dados e validação,
comparando duração anterior de cerca de quatro horas com a projeção recente
de 22–27 horas. A projeção anterior partia de poucas páginas densas e não
permite afirmar regressão de uma execução completa nessas proporções.
Revisados serialização do contexto, continuidade, merge, validação e regras
de inventário do V8. Mantida a execução 80 cancelada, sem nova chamada de IA.

Simulações em contêiner sem rede e com volumes somente para leitura. No
checkpoint parado do lote 131–132, com 20 fichas completas, a mesma janela
129–134 tinha 112.630 bytes de dados JSON com o transporte atual e 99.070
com índice, redução de 12%. Texto documental e originais permaneceram iguais.
Outra comparação usou as 36 fichas finais do lote já fechado 121–122 e o
mesmo texto das páginas 119–124: 266.459 bytes com fichas completas contra
134.692 com índice, redução de 49,5%. É uma comparação de representações do
estado final, não uma reconstrução da chamada histórica ou teste de latência.

Na resposta diagnóstica rejeitada com quatro fichas, um protótipo apenas em
memória compartilhou 11 objetos de evidência repetidos e trocou as ocorrências
por referências. O JSON passou de 27.557 para 25.096 bytes, redução de 8,9%,
e sua expansão foi estruturalmente idêntica ao original. Isso preserva também
o erro que motivou a rejeição: não houve homologação semântica da resposta.
O inventário acumulado correspondia a 10.096 bytes daquela saída. Reduções
em bytes não comprovam redução de tokens, custo ou tempo na mesma proporção.
Os percentuais são de casos e componentes diferentes e não devem ser somados.

Proposta para próxima implementação: fichas concluídas sempre por índice
compacto; saída apenas com fichas novas/revisadas e mudanças de inventário;
merge por IDs/versões estáveis, preservando originais e histórico no servidor;
validação literal, de cobertura e reconciliação sobre o resultado expandido.
Referências de evidências compartilhadas devem ser resolvidas somente no
escopo da fonte e rejeitadas se desconhecidas, sem completar campos ausentes
por suposição. A IA continua responsável pela leitura e conferência documental;
a consolidação do servidor não substitui a verificação semântica da fonte.

Medições por chamada e comparação de blocos densos/leves devem preceder
compromisso de duração. Grupos adaptativos e paralelismo de unidades realmente
independentes são propostas posteriores, sujeitas à mesma reconciliação.
Nenhuma delas foi implantada nessa avaliação. O checkpoint permaneceu
inalterado. Atualizados somente LOG e ROADMAP, sem alteração funcional,
modelo, prompt, configuração, workflow, serviço, envio, commit, push ou VPS.
Não houve teste de aplicação ou geração externa; preservadas mudanças locais.

## 2026-11-14 — Implementação do transporte compacto e amostra autorizada

O usuário autorizou três mudanças: índice de fichas concluídas desde o início,
inventário incremental consolidado no servidor e evidências compartilhadas.
Grupos adaptativos e paralelismo foram explicitamente adiados. Autorizou também
algumas chamadas reais ao OpenRouter para medir duração e estimar o restante,
sem retomar automaticamente a execução 80 cancelada. Conferida ausência de
execuções principais ativas. Preservados código, documentos, imagem anterior
e volume de diagnósticos em backup privado, sem imprimir dados ou credenciais.

A skill global karpathy-guidelines citada no AGENTS não foi localizada no
catálogo nem na busca local; aplicados escopo mínimo, preservação dos dados,
verificação de hipóteses e validação específica, sem instalar dependências.

Novo módulo de transporte reconstitui objetos completos antes dos validadores
V8. O índice usa ordem estável das referências confirmadas. Deltas exigem hash
da base e IDs locais estáveis de bloco/unidade; omissão preserva valores e
remoções, duplicações, lacunas ou substituições disfarçadas são rejeitadas.
Evidências compartilhadas têm escopo da chamada, expansão limitada antes da
cópia e conferência literal. Não são aceitas referências desconhecidas,
redefinições ou encadeamentos. Diagnósticos preservam o transporte original,
dicionário e métricas; a correção desvincula referências da chamada rejeitada.
Mantidos V8 aprovado, Terra, fichas concluídas imutáveis, grupos de quatro,
sequência única, prazo global zero e demais proteções. A forma integral de
inventário anterior continua aceita com as mesmas validações.

A identidade inclui o novo módulo/instruções. O migrador reconhece por hashes
a implementação anterior de recuperação automática, preservando integralmente
os lotes, fichas, revisões, buscas, fila de contexto e origem.

Na revisão final, passaram 292 testes Python em contêiner sem rede, com 13
contratos dependentes de Node pulados ali e executados com sucesso no host:
305 testes Python distintos. Os 30 contratos completos passaram no host e a
interface JavaScript passou. Casos novos verificam reversibilidade, índice
em lote pequeno, expansão antes da validação, versão divergente, IDs e
unidades inválidos, remoção de evidências, amplificação, escopo de referência,
única correção, retomada e migração integral da implementação anterior.

A amostra sintética real, isolada em volume privado separado, concluiu em
uma chamada de 16,121 segundos (16,289 segundos incluindo validação e arquivos).
A API informou 11.005 tokens de entrada e 1.298 de saída. Usou inventário
incremental, quatro evidências novas e sete referências, com reconstrução e
conferência literais aceitas. PDF reaberto e ZIP conferidos pelo mesmo código
da aplicação. Os tempos são de um fixture sintético de uma página e não
permitem projetar o documento real. A revisão final alterou apenas o tratamento
de referências rejeitadas, validado pelos testes sem chamadas pagas adicionais.

O comando para uma amostra de até seis chamadas com a cópia do documento real
foi rejeitado pela revisão automática antes de executar, por falta de autorização
inequívoca para enviar esse documento específico e seus derivados ao OpenRouter.
Solicitada essa autorização explicitamente ao usuário, identificando o documento
de 198 páginas e o destino externo. Nenhuma chamada real desse documento foi
feita nesta tarefa nem houve tentativa de contornar a rejeição. A estimativa
continua pendente; não foi usado o tempo sintético para extrapolar 198 páginas.

Implantada somente a imagem local final do renderizador
`sha256:cb60d5307776225552eebcc1e751c2d6ae290e2bf75123bd77ff1ca8d6f67236`.
Mantida a anterior na tag `miller-renderer:before-transport-20261114`; backup
privado do código e diagnósticos preservado. Migração explícita sem rede da
origem cancelada para `dd3bbebaa4fcd039539ea5801a8242836e29559fda54ed960d7f07f3526ef12f`,
com comparação integral de completed/pending e origem byte a byte intacta:
130 páginas, 477 registros e 20 fichas completas do lote 131–132. Arquivos 600.
Conferidos identidade instalada, V8 original, Terra, prazo global zero, grupos
de quatro, seis serviços saudáveis e HTTP 200 na landing/renderizador.

Uma medição local, sem rede e com os originais somente para leitura, comparou
a mesma janela 129–134 do lote 131–132: 112.630 bytes no pacote integral
anterior e 101.682 no transporte final (9,72% menor), com uma evidência
compartilhada. O novo protocolo tem metadados próprios; esse valor substitui
para esta implementação a simulação anterior de índice isolado. Não equivale
a ganho medido em tokens ou duração.

Atualizados PRD, ROADMAP, fluxo e guia local. A execução 80 permanece cancelada,
sem nova tentativa, envio, alteração de workflow, n8n, configuração, commit,
push ou VPS. Revisados diff, links locais e segredos no diff isolado; preservadas
as mudanças preexistentes. Implementação concluída; amostra real e estimativa
aguardam a autorização específica solicitada pela revisão automática.

## 2026-11-14 — Amostra real autorizada do transporte compacto

Após a confirmação explícita do usuário, executado o teste de até seis
chamadas com o Markdown e dados derivados do documento de 198 páginas no
OpenRouter. Usada a imagem local já implantada, Terra e V8 originais, com
limite somente no script da amostra, não na aplicação. Checkpoint copiado
para o volume privado `miller-transport-benchmark-20261114`; volumes de
origem de diagnósticos e artefatos montados somente para leitura. Chave
obtida do ambiente autorizado em memória, sem argumentos com valor de
credencial, impressão ou registro em arquivo. A rejeição anterior da revisão
automática foi resolvida pela nova autorização, sem contorno de proteção.

Concluídas seis chamadas em 150,226 segundos de teste. Tempos individuais:
23,802; 14,690; 19,956; 26,013; 24,619; 25,643 segundos. Soma de espera na
API: 134,723 segundos; média 22,454. A diferença para o total inclui leitura,
validação, salvamento e instrumentação específica do teste. Informados pela
API 279.606 tokens de entrada e 11.311 de saída no agregado. Não foi medido
custo em moeda nem saldo de crédito. Não houve nova geração após a sexta.

A primeira resposta tentou substituir evidências existentes em uma unidade
do inventário e foi rejeitada por `delta_evidencia_removida`. O diagnóstico
orientou a única correção prevista, aceita na segunda chamada. As chamadas
3–6 também foram aceitas. O checkpoint de teste passou de 497 para 517 fichas
concluídas somando lotes fechados e fichas completas do lote aberto: 20 fichas
novas, todas excluídas. Mantidas 130 páginas fechadas e nenhuma ficha em
revisão; o lote 131–132 não foi encerrado. A correção não foi contada como
outras quatro fichas novas. Ritmo com todo o custo observado: 7,511 segundos
por ficha nova, aproximadamente 7,988 fichas por minuto. A resposta inválida
e os metadados ficaram somente no armazenamento privado da amostra.

Comparação de representações dos mesmos dados: entrada JSON agregada das
seis chamadas 726.873 bytes integral contra 632.321 compacta, redução de
13,01%. Nas cinco respostas aceitas, 144.980 bytes após expansão/consolidação
contra 24.300 no transporte, redução de 83,24%. A chamada rejeitada não entrou
na comparação de saída, pois não se expande validamente, mas seu tempo e
tokens foram incluídos no custo da amostra. Conferida offline a comparação
da segunda chamada: a instrumentação inicial reutilizava diagnóstico e
resposta anterior ainda com referências, sem expandi-los no baseline.
Reproduzido exatamente o pacote de correção sem IA e corrigida sua base
integral de 117.174 para 121.146 bytes. O agregado passa de 722.901 para
726.873 bytes e a redução de 12,53% para 13,01%, sem alterar os dados brutos
ou fazer outra chamada. Esses percentuais não medem redução de latência,
custo ou tokens contra uma execução anterior.

Projeções condicionais, sem apresentar o trecho como representativo de tudo:
na origem existem 68 páginas abertas; o inventário já guardado do lote 131–132
tem 100 unidades, com 20 fichas completas. Supondo uma ficha por unidade,
restariam 80 nesse lote. Para as 66 páginas seguintes, usar a média das 130
páginas fechadas (477/130 = 3,669 fichas/página) resulta em 40,3 minutos no
ritmo amostrado. Usar a densidade do lote atual (100/2 = 50 unidades/página)
resulta em 7,05 horas. Fórmula de cada cenário: (80 + 66 × densidade) ×
150,226/20 segundos. Não são intervalo estatístico ou limite máximo; a
amostra só tem excluídos, não fecha páginas e não mede o custo de fichas
completas nem a densidade das páginas futuras. Não é possível confirmar
uma previsão única ou duração total de quatro horas a partir dessas chamadas.

Amostra encerrada pelo limite de chamadas do teste, sem erro persistente,
sem retomar o workflow, enviar relatório ou incorporar a cópia na operação.
A origem permaneceu idêntica; o estado operacional mantém as 130 páginas,
477 registros dos lotes fechados e 20 fichas completas no lote aberto.
Atualizados LOG e ROADMAP; grupo quatro e execução sequencial mantidos, sem
aplicar as opções de grupos adaptativos ou paralelismo. Nenhuma mudança de
código, configuração, imagem, workflow, contêiner operacional, commit, push
ou VPS nesta avaliação. Sem reexecução da suíte unitária: a validação atual
foi a amostra externa e a revalidação local dos checkpoints.

## 2026-11-14 — Grupos de oito e acréscimo de evidências autorizados

O usuário autorizou os dois próximos ajustes, deixando paralelismo para
depois, e solicitou repetir os testes reais para medir tempo. Preservadas
a autorização já concedida para o mesmo documento no OpenRouter e a decisão
de manter a execução original cancelada. Backups privados do código, imagem
e diagnósticos preparados. A skill global karpathy-guidelines continua ausente
na busca local; mantidos escopo mínimo e verificação de hipóteses.

Implementados grupos fixos de até oito e máximo conferido no servidor,
inclusive correções. Priorizar até oito fichas em revisão, mantendo os
eventos concluídos imutáveis. No delta do inventário, adicionar_evidencias
conserva a ordem e todos os objetos anteriores e acrescenta somente objetos
novos; campos.evidencias usa a mesma união por compatibilidade. Lista vazia
não apaga; representações simultâneas, objetos malformados, evidência falsa,
referências desconhecidas e remoção de IDs continuam rejeitados. Somente
acrescentar dispensa campos vazio. Demais arrays e fichas não mudam de regra.

Nova identidade mantém formato 3 e reconhece a implementação anterior do
transporte compacto para migração explícita sem perda. Preservados V8, Terra,
fonte paginada, prazo global zero, limites de contexto e correção, validação
literal e reconciliação.

Passaram 306 testes Python no contêiner, com 13 contratos dependentes de Node
pulados ali e aprovados no host: 319 testes Python distintos. Os 30 contratos
completos passaram no host e a interface JavaScript passou. Verificados oito
registros completos em uma chamada, nove rejeitados por exceder o máximo
e uma única correção, prioridade de oito revisões, migração do transporte anterior,
idempotência e preservação integral das evidências, malformações e literal
falso. Reproduzida offline a primeira resposta real do benchmark anterior,
que era rejeitada: agora aceita, mantendo todos os objetos de evidência
anteriores e as mesmas validações. Nenhuma chamada paga nessa reprodução.

Teste sintético real no mesmo fixture: uma chamada de 14,872 segundos,
15,002 segundos com validação e geração dos arquivos, 11.140 tokens de
entrada e 1.208 de saída. PDF reaberto e ZIP conferidos. Em seguida, repetidas
as seis chamadas autorizadas no mesmo documento, checkpoint inicial e alvos
131–132, com novo volume privado `miller-eight-benchmark-20261114`. Originais
somente para leitura, chave em memória e cópia do checkpoint separada.

Tempos individuais da amostra: 28,676; 37,584; 35,726; 42,002; 36,493;
35,392 segundos. Duração total 230,256 segundos, média 35,979 por chamada.
As seis retornaram oito fichas e foram aceitas sem correção: 48 fichas novas,
todas excluídas, passando de 497 para 545 fichas completas na cópia, somando
lotes fechados e lote aberto. Mantidas 130 páginas fechadas; o lote 131–132
ainda tem trabalho. Informados pela API 292.608 tokens de entrada e 18.076
de saída. Não foi consultado saldo nem convertido o consumo em moeda.

A métrica comparável de tempo por ficha, incluindo todo o teste, caiu de
150,226/20 = 7,511 para 230,256/48 = 4,797 segundos, redução de 36,14%.
Vazão de 7,988 para 12,508 fichas/minuto, aumento de 56,58%. A chamada
individual ficou maior porque entrega o dobro de fichas; o teste durou mais
e produziu 2,4 vezes as fichas novas. Não atribuir o ganho isoladamente ao
tamanho ou à união: ambos mudaram e a API/modelo podem variar entre execuções.

Comparações de representação na nova amostra: 668.581 bytes de dados enviados
contra 804.278 integrais equivalentes (16,87% menor). Saída 46.526 bytes contra
220.581 após expansão e consolidação (78,91% menor). Na correção, se existir,
a instrumentação agora expande também diagnóstico/resposta anterior antes de
calcular a base; nenhuma correção foi necessária aqui. Percentuais em bytes
não representam os ganhos em tokens ou duração contra a execução anterior.

Mantida a mesma hipótese densa usada antes para tornar a projeção comparável:
80 unidades sem ficha no lote atual da origem, mais 66 páginas futuras com
50 unidades/página, uma ficha por unidade. Restante estimado: (80 + 66 × 50)
× 4,797 segundos = 4,504 horas adicionais, aproximadamente 4h30, contra
7,05 horas no benchmark anterior. Não é prazo, limite ou previsão firme:
somente um lote com excluídos foi amostrado; densidade real das páginas
futuras, fichas completas e retrabalho não foram medidos. Nenhum cenário
promove páginas a concluídas nem desabilita validações. O tempo global da
aplicação continua sem trava; o limite de seis chamadas existe só no teste.

Implantada somente a imagem local do renderizador
`sha256:ba1ba60e416a7c74b7253a547afa4d030e5220ac2e4b0037b29ec6c2436b2061`.
Anterior preservada em `miller-renderer:before-eight-20261114`, com backup
privado do código/documentos e diagnósticos. Migrada explicitamente a origem
`dd3bbebaa4fcd039539ea5801a8242836e29559fda54ed960d7f07f3526ef12f`
para `9c389d2b6fa844f31ff6bfc44895cd7012b4a283962d64ee7543d43f2900c968`.
Comparados completed/pending integralmente e revalidados os digests contra
a mesma fonte. Origem byte a byte intacta: 130 páginas, 477 registros de lotes
fechados e 20 fichas completas do lote aberto. A cópia adicional com 48 fichas
novas não foi incorporada à operação. Arquivos 600, identidade instalada,
V8 original, Terra, grupo oito, prazo global zero e HTTP 200 conferidos.
Seis serviços saudáveis; execução original cancelada e nenhuma execução
principal ativa. Atualizados PRD, ROADMAP, fluxo e guia local; revisados
diff, links locais e segredos no diff isolado. Sem paralelismo, envio,
workflow novo, alteração de configuração/n8n/VPS, commit ou push. Preservadas
as mudanças locais preexistentes e os dados privados.

## 2026-11-14 — Paralelismo coordenado e nova medição autorizados

O usuário autorizou implementar o paralelismo e repetir a medição. Mantidas
a autorização do mesmo documento no OpenRouter e a execução 80 cancelada.
Lida a documentação de referência; karpathy-guidelines segue ausente na
busca local, mantendo escopo mínimo e verificações concretas. Preservados
código/documentos e identidade anterior em backup privado antes de alterar.

Extraído o processamento por lote em geradores, com um único coordenador
responsável por validação e gravação e até duas threads somente para o I/O
do provedor. Continuar um lote permanece sequencial; contexto, evidências,
páginas de unidades conhecidas ou pedidos sobrepostos serializam os despachos.
IDs continuam vinculados ao alvo onde inicia a unidade. Partição global
completa e registros são conferidos, e os resultados fora de ordem ficam
ordenados no checkpoint e reunidos somente após todos os lotes concluírem.
Não confundir independência operacional de solicitações com prova semântica
de ausência de relação entre unidades: leitura e revisão V8 continuam exigidas.

Erro persistente impede novos despachos e drena as respostas em voo para
salvar progresso válido; falha de armazenamento impede novas promoções.
Retentativas e janela 32 recarregam o estado atual do coordenador, incluindo
progresso dos outros lotes, sem renovar correção, buscas ou falta de avanço.
O prazo global opcional é novamente conferido no despacho; padrão zero.
Orçamentos explícitos por lote existem só para amostra interna em cópia, sem
entrada na rota operacional e sem publicar relatório com páginas pendentes.
Nova identidade reconhece para migração explícita a versão anterior com oito.

Na revisão final passaram 315 testes Python no contêiner, com 13 contratos
com Node pulados ali e aprovados no host: 328 testes distintos. Os 30 contratos
completos e a interface JavaScript passaram no host. Casos concorrentes usam
barreiras e eventos reais para verificar duas chamadas em voo, conclusão fora
de ordem, escritor único, serialização por expansão/contexto adjacente,
dependência de páginas no inventário sem citação literal, erro persistente
com preservação da resposta saudável, falha de armazenamento sem promoção,
retry e rollover sem perder progresso de outro lote, migração e PDF somente
após todos terminarem. As regressões anteriores fixam um lote por vez e os
novos casos habilitam explicitamente dois. Ajuste final também aproveita o
tempo decorrido da espera de retry enquanto o par trabalha, evitando repetir
a espera inteira ou executar espera ocupada após falha. Suíte completa
reexecutada na revisão final; nenhuma validação foi relaxada.

Teste sintético real: uma chamada de 10,574 segundos, 10,652 segundos no total,
11.140 tokens de entrada, 785 de saída e PDF/ZIP conferidos. Depois comparados
os mesmos alvos 131–132 e 138–140, com estado inicial idêntico, dois diretórios
privados no volume `miller-parallel-benchmark-20261114` e orçamento de até três
chamadas por lote. O controle terminou antes de iniciar o paralelo, preservando
a comparação sem competição entre amostras. Originais montados somente para
leitura; credencial somente no ambiente em memória. A revisão final posterior
ao sintético modificou apenas a espera/drenagem, coberta pelos testes e usada
nas duas amostras reais. Não houve outra geração após os limites internos.

Controle sequencial: 230,487 segundos no total, quatro chamadas aceitas sem
correção, 32 fichas novas e uma chamada simultânea. Tempos: 37,272; 38,195;
31,610; 102,426 segundos, soma de 209,503; média de 52,376 por chamada.
O lote 138–140 foi declarado fechado pelo modelo numa resposta com oito
excluídos, passando a 133 páginas fechadas na cópia. O lote 131–132 preservou
24 fichas novas, além das 20 da origem. Informados 176.589 tokens de entrada
e 18.336 de saída. Média agregada de 7,203 segundos por ficha nova.

Amostra paralela: 165,819 segundos, seis chamadas aceitas sem correção,
48 fichas novas e duas chamadas simultâneas efetivamente observadas.
Tempos por ordem de despacho: 35,947; 64,593; 36,058; 46,928; 28,793;
37,302 segundos; soma 249,621; média 41,603. Informados 256.570 tokens de
entrada e 21.576 de saída. Checkpoint de teste passou de 497 para 545 fichas
completas, somando lotes fechados e abertos, permanecendo 130 páginas fechadas.
O lote 131–132 acrescentou 24 e 138–140 acrescentou 24, ambos ainda abertos.
Média observada de 3,455 segundos por ficha, ou 17,368 fichas/minuto.

Resultado inesperado a preservar: nos mesmos alvos e estado inicial, o modelo
variou a quantidade de fichas e a declaração de fechamento do lote 138–140.
Assim, não são dois trabalhos finais equivalentes e não há benchmark controlado
de latência total com resultados idênticos. As chamadas iniciais de cada lote
usaram os mesmos tamanhos de entrada e número de tokens nos dois modos, e a
implementação mantém fonte, V8 e transporte iguais; a variação de saída não
foi apagada nem resolvida escolhendo uma versão. Revalidada mecanicamente cada
cópia separadamente. A queda observada de 28,06% no tempo da amostra e 52,04%
no tempo por ficha não deve ser atribuída integralmente ao paralelismo; não
foi realizada revisão semântica independente de equivalência/abrangência.
Validar a variação de granularidade e cobertura antes da homologação integral.

Para manter a mesma hipótese densa das projeções anteriores, usar 3.380 fichas
restantes na origem (80 no lote atual mais 66 páginas a 50 unidades/página,
uma ficha por unidade) × 165,819/48 segundos. Resultado condicional: 3,243
horas adicionais, aproximadamente 3h15. Não é limite, prazo garantido nem
medição das 68 páginas: custo das fichas completas, granularidade, densidade
futura e retrabalho podem alterar muito o tempo. Não foi usado o ganho percentual
do controle para simplesmente dividir a projeção anterior de 4h30. O orçamento
de amostra não é configurado nem exposto pela API operacional.

Implantada apenas a imagem local do renderizador
`sha256:4c3e6d7e0dd37fe587213f1552a76016e213bc77ff6cc1e318aa974a90f60596`.
Anterior preservada em `miller-renderer:before-parallel-20261114`, com backup
privado de código/documentos e diagnósticos. Migrada explicitamente a origem
`9c389d2b6fa844f31ff6bfc44895cd7012b4a283962d64ee7543d43f2900c968`
para `9975b89ffdfae990793df8d403f2eb415587a20f379004f56a1712b151d74fc4`.
Comparados completed/pending integralmente, digest e fonte; origem byte a byte
intacta, SHA-256 do arquivo anterior
`77202fa805d8570edede8953aabf2c99077789957aa2cbcc77ad553f76da9391`.
Operação segue com 130 páginas fechadas, 477 registros e 20 fichas do lote
aberto; nenhuma cópia foi incorporada. Ambas as amostras e o estado operacional
foram revalidados contra a mesma fonte, com arquivos 600. Conferidos identidade
instalada, V8 original, Terra, grupo oito, máximo dois e prazo global zero.
Landing/renderizador HTTP 200, seis serviços saudáveis, execução 80 cancelada
e nenhuma principal ativa. Atualizados PRD, ROADMAP, fluxo e guia local;
revisados diff, links locais e segredos no diff isolado. Sem novo workflow,
alteração de configuração/n8n/VPS, envio, commit ou push. Preservadas todas
as mudanças locais preexistentes e os dados privados.

## 2026-11-14 — Grupos adaptativos autorizados e itens seguintes adiados

O usuário autorizou somente o item 1, condicionando fila dinâmica e campos
comuns ao resultado. Mantidos a autorização do documento no OpenRouter e o
processamento original cancelado. Backups de código/documentos e identidade
anterior em diretório privado. Karpathy-guidelines continua ausente na busca
local; mantidos escopo mínimo e verificações pertinentes.

Política por lote inicia em oito e pode crescer 12/16 após grupo compacto
aceito com progresso e métricas reais. Critérios conservadores: grupo cheio,
objetos até 4.000 bytes e média até 2.500, saída até 1.000 tokens por registro
e duração até 120 segundos. Respostas acima de 16.000 tokens, 120 segundos
ou objeto de 8.000 bytes reduzem o próximo tamanho; completas/correções
conservam ou retornam a até oito. Após redução/correção, dois sucessos sem
crescer. Contadores e limite ficam em metadado privado validado por lote.

Máximo total varia por chamada; grupo com incluído/pendente permanece com
até oito eventos. Correção conserva limite e orçamento; transporte repete
o pacote. Truncamento fora de correção reduz pelos degraus 16/12/8/4/2/1 sem
aproveitar saída parcial. Se continuar truncado, erro explícito e política
preservada mesmo após dividir alvos. Limite de contexto não é contornado
reduzindo dados obrigatórios. Inventário mantém unidades restantes pendentes,
fichas concluídas imutáveis e V8 original, com validação literal e cobertura.

Novo módulo faz parte da identidade e o migrador reconhece o paralelismo
anterior, preservando todos os dados e iniciando em oito quando não há
medição anterior. O coordenador só conserva o metadado ao concluir o lote;
a fila e os campos comuns não mudaram.

Respostas intermediárias que deixam de ser curtas (acima de 4.000 bytes por
objeto, média 2.500 ou 1.000 tokens por registro) também conservam/retornam a
até oito, sem apagar dados. Critérios de crescimento não se aplicam a grupos
rejeitados, sem avanço ou sem métricas. O tamanho de correção fica congelado;
se surgir um grupo extenso de fichas completas, até oito são corrigidas e as
unidades restantes precisam continuar reservadas em inventário pendente.

Passaram 332 testes Python no contêiner sem rede, com 13 contratos com Node
pulados ali e aprovados no host: 345 testes distintos. Os 30 contratos no
host e a interface JavaScript passaram. Os 17 casos adaptativos verificam
8/12/16, retomada em 16, retry do pacote idêntico, redução 8/4 sem cortar fonte,
respeito ao contexto, correção única congelada, limite de completas, política
corrompida antes de IA, políticas independentes nos dois lotes, herança da
redução nos filhos e migração anterior sem inventar medidas. Uma correção
que reduz 16 completas a oito mantém as demais unidades reservadas e termina
com todos os registros após a continuação. Conferidos dados e evidências.

Fixture sintético real no OpenRouter: uma chamada de 13,595 segundos, 13,707
com validação e arquivos. Informados 11.296 tokens de entrada e 1.090 de saída.
PDF reaberto e ZIP conferidos. Não houve chamada ao documento real: o comando
preparado para o controle de até 12 chamadas foi rejeitado pela revisão
automática antes de executar, por ampliar o limite anterior de seis sem
consentimento específico. Solicitada autorização para até 24 chamadas no
total (12 fixas e 12 adaptativas) para fechar o mesmo lote, ou preferência
por seis por amostra. Não foi contornada a revisão e a medição aguarda o
usuário. Não atualizar a projeção de duração usando o fixture sintético.

Aplicada somente a imagem local do renderizador
`sha256:72047f407cf7d6069f9530294700151f78a4a1b19268d712ef5beb5d3084fd43`.
Anterior preservada em `miller-renderer:before-adaptive-20261114`, com backups
privados do código/documentos e diagnósticos. Migrada explicitamente a origem
`9975b89ffdfae990793df8d403f2eb415587a20f379004f56a1712b151d74fc4`
para `6773478eae21605e2a82d432cefa850e0c5976bc4fb642c26685782d1e9b44c1`.
Completed/pending idênticos à origem, sem metadado de medidas inventado.
Origem intacta, SHA-256 do arquivo
`cd254dd6c7890c442ce24d29ff40b38da86ea48876ca3003b46b68c0b702e550`.
Preservados 130 alvos fechados, 477 registros e 20 fichas do lote aberto.
Conferidos identidade instalada, V8 original, grupo inicial oito, máximo 16,
dois lotes, prazo global zero, arquivos 600 e HTTP 200 na landing/renderizador.

Atualizados PRD, ROADMAP, fluxo e guia local. Revisados diff, links locais
e segredos no diff isolado; preservadas mudanças anteriores. Nenhum ajuste
da fila dinâmica ou compartilhamento de campos comuns, nova tentativa,
retomada, envio, alteração de workflow/n8n/configuração/VPS, commit ou push.
Implementação concluída; comparação real e resultado de desempenho permanecem
pendentes da autorização de orçamento solicitada pela revisão automática.

## 2026-11-14 — Comparação autorizada dos grupos fixos e adaptativos

Após a autorização explícita do usuário para até 24 chamadas reais no
OpenRouter, com teto de 12 por modo, executada a comparação pendente em
cópias privadas separadas. Usadas 16 chamadas no total: dez fixas e seis
adaptativas. Nenhuma chamada adicional foi realizada para consumir o saldo
do orçamento. Mesmo Terra, V8 original, fonte de 198 páginas, checkpoint
inicial e alvo 131–132. Somente esse lote ficou elegível em cada amostra,
com concorrência observada de um; o paralelismo operacional continua em dois.
A execução original não foi retomada.

| Medida do mesmo lote | Fixo em oito | Adaptativo |
| --- | --- | --- |
| Tempo total, incluindo preparação/validação/persistência da amostra | 344,491 s | 318,723 s |
| Soma das requisições ao OpenRouter | 306,952 s | 248,626 s |
| Chamadas aceitas | 10 | 6 |
| Fichas novas / total no lote | 80 / 100 | 80 / 100 |
| Unidades reconciliadas com IDs | 100 | 100 |
| Tokens de entrada informados | 511.354 | 301.819 |
| Tokens de saída informados | 26.151 | 21.655 |
| Bytes enviados / recebidos | 1.742.365 / 70.875 | 1.029.463 / 62.259 |
| Correções, respostas rejeitadas ou pedidos de contexto | 0 | 0 |

O controle recebeu dez grupos de oito. O adaptativo solicitou limites
8/12/16/16/16/16 e recebeu 8/12/16/16/16/12, fechando o mesmo lote sem chamada
extra. Política final em 16, dois aumentos e nenhuma redução. Ganho observado
de 25,768 segundos, ou 7,48% no tempo total; 40% menos chamadas e 40,98% menos
tokens de entrada. A soma do tempo de API caiu aproximadamente 19%; chamadas
maiores levam mais tempo individualmente. O tempo fora das requisições foi
37,539 contra 70,097 segundos, incluindo no adaptativo um intervalo de 50,336
segundos entre duas chamadas. Esse intervalo não foi perfilado nem atribuído
a uma causa confirmada; foi mantido integralmente na medição, sem desconto.

Ambos os checkpoints fecharam 132 páginas e 577 fichas contabilizadas,
partindo de 130 páginas e 497 fichas (477 em lotes fechados e 20 no lote
aberto). Inventário final com as mesmas 100 unidades e IDs por unidade,
todos os eventos com destino excluído. As novas redações não são byte a byte
idênticas; não houve revisão semântica independente nem aceite humano. Todas
as 497 fichas anteriores foram comparadas integralmente e preservadas, assim
como evidências e IDs antes reservados no inventário. Arquivos privados 600,
digest, estrutura, cobertura e evidências literais revalidados sem rede
contra a mesma fonte. As duas amostras declararam a origem preservada.

Esta medição melhora a comparação anterior por concluir exatamente o mesmo
lote. Continua sendo uma observação de duas páginas densas com fichas
excluídas, sem representar o custo de fichas completas, páginas futuras ou
utilização de dois lotes em paralelo. Não aplicar 7,48% às 3h15 anteriores
como nova previsão: aquela projeção também se baseava em densidade e
granularidade ainda não medidas no restante do documento.

Conferidos a origem legada byte a byte pelo SHA-256 já registrado e o
checkpoint operacional migrado: schema/completed/pending idênticos à origem,
com a proveniência da migração esperada. Somente esse metadado difere entre
as duas identidades; não é progresso produzido pelo teste. Operação mantém
130 páginas fechadas, 477 registros e 20 fichas no lote aberto. SQL somente
leitura confirmou execução 80 cancelada e nenhuma principal ativa; os seis
serviços locais estão saudáveis. Nenhuma amostra foi incorporada à operação.

Atualizados somente ROADMAP e este registro, preservando os históricos da
rejeição anterior e das validações da implementação. Nenhuma alteração
adicional de código, workflow, configuração, n8n ou VPS; itens 2 e 3 seguem
adiados. Sem retomada, envio, commit ou push. A suíte de 345 testes citada no
evento anterior não foi repetida nesta medição; a validação atual compreende
as duas amostras reais, revalidação offline dos checkpoints e verificações
documentais de diff, links e segredos.

## 2026-11-14 — Melhor ocupação das duas vagas e nova medição do restante

O usuário confirmou os títulos dos itens e autorizou implementar somente o
ponto 2, com medição e cálculo do tempo restante. Campos comuns (ponto 3)
continuam adiados. Mantidos Terra, V8, dados completos, validação, grupos
adaptativos, máximo de duas chamadas e prazo global zero. A skill global
karpathy-guidelines continua ausente nas raízes globais pesquisadas; aplicados
escopo mínimo, preservação e verificações pertinentes. Backup privado de
código/documentos e diagnósticos em `/tmp/miller-fila-20261114-225528`;
imagem anterior preservada em `miller-renderer:before-queue-20261114`.

Identificada reserva das vagas por `len(jobs)`: dois geradores iniciados
impediam um terceiro lote, mesmo quando um estava em retry ou com solicitação
bloqueada por sobreposição. Agora o limite operacional considera somente
chamadas em voo. Geradores suspensos preservam suas variáveis, contexto,
pacotes e orçamentos; lotes novos precisam ser independentes dos já iniciados.
Retomadas elegíveis precedem novos lotes. Retry desconta o tempo transcorrido
durante outros trabalhos, sem somar a espera outra vez. Sem chamada elegível,
aguarda a próxima retentativa; com as duas vagas ocupadas, não gira em espera
ativa por retry já vencido. O modo interno sequencial conserva sua ordem.

Permanecem validação/persistência numa thread, bloqueio exclusivo, conferência
global de IDs, orçamento opcional da amostra, prazo revisto no despacho,
parada de novos envios após falha persistente e drenagem dos já enviados.
Uma chamada ainda em voo continua ocupando sua vaga. Nenhum dado de contexto
foi omitido para declarar independência. A migração reconhece a versão
adaptativa anterior por hashes exatos e conserva sua política por lote.

Passaram 72 testes direcionados. A suíte oficial em `tests/` passou com 336
testes e 13 contratos com Node pulados no contêiner; esses 13 passaram no host,
totalizando 349 testes Python distintos. Os 30 contratos no host e a interface
JavaScript passaram. Os quatro casos acrescentados demonstram terceiro lote
durante retry/contexto bloqueado, máximo dois, retry com pacote idêntico,
orçamento não renovado por progresso alheio e migração sem perder política.
O primeiro comando amplo de pytest tentou coletar uma cópia histórica em
`output/` e falhou na importação relativa; a execução oficial foi restringida
a `tests/`, sem alterar ou remover o histórico.

Fixture sintético real validado antes do documento: uma chamada de 16,423
segundos, 16,581 no total com validação e PDF/ZIP; 11.296 tokens de entrada e
1.377 de saída. Amostra real com teto de seis chamadas, duas por lote, usando
três recortes independentes da mesma origem: 131–132, 138–140 e 146–147.
Usadas cinco chamadas em 230,939 segundos. Não houve sexta chamada porque um
lote fechou com uma resposta e os outros atingiram duas. Quatro respostas
aceitas e uma recuperação de contexto, sem correções ou retentativas.

| Medida atual | Resultado |
| --- | --- |
| Fichas novas completas | 22: 20 excluídas e duas incluídas |
| Tempo por ficha nova, incluindo toda a amostra | 10,497 s |
| Vazão | 5,716 fichas/minuto |
| Média por requisição | 58,408 s |
| Tokens informados de entrada / saída | 210.665 / 25.856 |
| Concorrência máxima | 2 |
| Tempo com duas chamadas simultâneas | 70,379 s |
| Tempo sem chamada em voo | 9,264 s |
| Ocupação das duas vagas na amostra | 63,23% |

O lote 131–132 acrescentou 20 excluídas e ficou parcial com 40 fichas e 100
unidades; a política chegou a 16. O lote 138–140 declarou três páginas fechadas
com oito unidades de inventário e nenhuma ficha, variando em relação às
amostras históricas. O lote 146–147 pediu contexto, acrescentou duas incluídas
e permaneceu parcial com nove unidades conhecidas; a política reduziu de oito
para quatro pelo tamanho das fichas. Na cópia, o total passou de 130 para 133
páginas fechadas e de 497 para 519 fichas completas, sem rascunhos. O pedido
de contexto não promoveu a ficha que acompanhava essa resposta; foram aceitas
apenas as duas entregues e validadas na continuação.

A amostra terminou com somente um lote elegível por sua restrição interna de
alvos/orçamento. Não representa ocupação sustentada de toda a fila operacional.
Não houve retry ou espera de contexto bloqueado por outra chamada nessa
amostra real; o benefício nessas condições foi demonstrado nos testes
sintéticos. Não há controle real antes/depois equivalente para atribuir ganho
percentual a esta mudança. A nova média mistura inventário sem ficha, fichas
completas e contexto; não comparar diretamente com as exclusões compactas
da medição anterior como se fosse regressão ou melhora de desempenho.

Para atender ao cálculo do restante, usadas hipóteses explícitas a partir da
origem parada, sem incorporar a cópia: faltam 80 fichas no inventário atual
se mantida uma ficha por unidade, mais 66 páginas futuras. Com a densidade
histórica de 477/130 fichas por página, resultam 322,169 fichas equivalentes
× 10,497 s = 3.381,884 segundos, aproximadamente 56 minutos adicionais. Se as
66 páginas repetirem 50 fichas por página, serão 3.380 × 10,497 s = 35.480,628
segundos, aproximadamente 9h51 adicionais. Não são intervalo de confiança,
limite ou previsão confirmada, nem ganho demonstrado contra as 3h15 anteriores.
Densidade, granularidade, custo de contexto e tipos de ficha ainda variam.
Semântica/abrangência do fechamento declarado permanecem para homologação.

Revalidados sem rede digest, estrutura, cobertura e evidências literais da
cópia, com comparação integral das 497 fichas anteriores: todas preservadas.
Checkpoint privado 600 e fonte íntegra. Nenhum progresso da amostra foi
incorporado à operação. São seis chamadas reais nesta tarefa: uma sintética
e cinco documentais, sem envio ou nova tentativa do protocolo principal.

Migração explícita da origem
`6773478eae21605e2a82d432cefa850e0c5976bc4fb642c26685782d1e9b44c1`
para `98da7763547fe6f89facc8dd73c1a74077fb90a80a81e99efa411f1d93be2da9`.
Origem byte a byte intacta, SHA-256
`1e345cce7a9d76f2db5ea38346fe8a8aed67a8086d5a18669fd92c0da3f59bd2`.
Schema/completed/pending e demais dados iguais; somente a proveniência da
migração foi atualizada. Preservados 130 alvos fechados, 477 registros nesses
lotes e 20 fichas do lote aberto, com filas, buscas, revisões e políticas.

Aplicada somente a imagem local do renderizador
`sha256:9e826fc0562246ba6161c580e21beab912b5a28380712dff2db96f121a696843`,
implementação `e83a941e242794fea02740a026f4e2dec7ae1a65f266463aeb3e826b93c21b5c`.
Saúde HTTP 200, V8 original, Terra, grupos adaptativos 8/12/16, máximo dois e
prazo global zero conferidos. SQL somente leitura confirmou execução 80
cancelada e nenhuma principal ativa; seis serviços saudáveis. Atualizados
PRD, ROADMAP, fluxo e guia local, com revisão do diff, links e segredos.
Sem alteração de campos comuns, workflow, configuração, n8n ou VPS, retomada,
envio, commit ou push. Preservadas as alterações locais anteriores.

## 2026-11-15 — Retomada do ponto 3: campos compartilhados entre fichas

Após reinício da máquina, localizada a conversa interrompida e confirmada a
instrução de implementar o ponto 3 e medir o desempenho. O usuário dispensou
explicitamente karpathy-guidelines somente nesta tarefa, mantendo as demais
regras do AGENTS. O código salvo ainda não tinha campos comuns. Preservados
fontes/documentos em `/tmp/miller-campos-20261115`, imagem anterior em
`miller-renderer:before-shared-fields-20261115` e volume privado de backup
`miller-before-shared-fields-20261115`. Mudanças locais anteriores conservadas.

O transporte de saída aceita `campos_compartilhados` e referências `$campo`
explícitas nos campos documentais permitidos de cada ficha. Cada valor é
integral; não há herança, união, preenchimento nem sobrescrita. Valores
diferentes continuam separados. IDs, destino, categoria, páginas da ficha,
justificativa e conferência de integridade são individuais. O dicionário é
local à resposta, sem reutilização entre chamadas ou encadeamento. Evidências
podem usar o transporte compacto anterior; tudo é expandido antes da mesma
validação literal, estrutural e de cobertura. Conferida amplificação antes
de copiar valores. Fichas guardadas, revisões e PDF/ZIP continuam integrais.
O diagnóstico preserva o transporte original e a correção recebe valores
resolvidos ou referência rejeitada identificada, sem vinculação a outro valor.

Passaram 41 testes direcionados de transporte/campos e a suíte oficial com
355 testes no contêiner, com 13 contratos de Node pulados ali e aprovados no
host. Depois, acrescentados e aprovados dois casos de revisão de fichas
pendentes e geração de PDF/ZIP: 357 casos distintos no contêiner, somados a
13 no host, totalizando 370 testes Python distintos. Os 30 contratos completos
e a interface JavaScript passaram no host. Sem rede nos testes de aplicação.
Casos novos conferem diferenças documentais, referências inválidas e fora do
escopo, campos omitidos, cadeia, amplificação, evidência falsa/página errada,
correção, persistência sem referências e retomada sem chamada de IA.

Construída e aplicada somente a imagem local do renderizador
`sha256:b96df7748d995711d86213dc497c412eb7a46315a99c1597fe6066e3e4a2033a`.
O migrador reconhece a implementação anterior da fila por hashes exatos.
Migração explícita, sem rede, de
`98da7763547fe6f89facc8dd73c1a74077fb90a80a81e99efa411f1d93be2da9`
para `b02c28e1f01c7bb9ba2e6c59573ddffdfe494d418022e5e2470eb0e1a99a0d57`.
Dados integralmente iguais, exceto proveniência da migração; origem intacta,
SHA-256 do arquivo `c5290797ddf45f02f13da8eaf9e119c79fecca6273e5088214f02f9d3bb5f552`.
Mantidos 67 lotes, páginas 1–130, 477 registros fechados e 20 do lote aberto,
contexto, inventários, revisões e políticas. Novo arquivo 600. Identidade
instalada `632770b707fd518b7204ed992e093ba0b4c8423c691ed6bebd18bb77a27dca55`,
V8 aprovado, Terra e HTTP 200 conferidos. Seis serviços saudáveis; SQL somente
leitura confirmou dois documentos e 15 tentativas em erro e nenhuma execução
n8n ativa. Sem retomada operacional, nova tentativa, envio ou alteração na VPS.

Preparada medição em cópia privada, com originais somente leitura, chave em
memória e teto de uma chamada sintética mais cinco documentais nos mesmos
recortes 131–132, 138–140 e 146–147. A revisão automática rejeitou o comando
antes de executar: não reconheceu autorização explícita verificável nesta
conversa para enviar esse Markdown privado ao OpenRouter com a chave protegida.
O histórico local contém autorização anterior de pequeno teste nesse destino;
uma nova avaliação também recusou aceitá-la como autorização verificável.
Nenhuma chamada ou consumo do teste ocorreu. Não houve contorno da recusa;
a nova medição aguarda autorização do usuário para material, destino e teto.

A referência de 14/11 permanece 230,939 s / 22 fichas = 10,497 s por ficha.
Sob a hipótese histórica de 80 unidades restantes no lote atual e 66 páginas
com densidade 477/130, seriam 322,169 fichas restantes e cerca de 56 minutos
adicionais. Extrapolando a mesma taxa para as 819,169 fichas totais estimadas,
a análise desde o início teria cerca de 2h23; somando a conversão histórica
de 674,18 s, cerca de 2h35 antes da finalização/envio. Não é nova medição nem
previsão confirmada do ponto 3; PDF final, densidade, contexto e retrabalho
não foram medidos no documento inteiro. A hipótese densa de 50 fichas por
página futura ainda levaria a cerca de 9h51 restantes. Não usar esses cenários
como intervalo de confiança, garantia ou limite de execução.

Atualizados PRD, ROADMAP, fluxo e guia local. Nenhuma dependência, variável,
serviço ou workflow adicionado; sem mudança de modelo/prompt V8. Sem commit
ou push, para não incorporar o amplo trabalho local preexistente.
Conferidos diff e links locais; Gitleaks no diff isolado não encontrou segredos.

## 2026-11-15 — Amostra autorizada após o ponto 3, sem execução integral

O usuário autorizou algumas chamadas para obter a média, vedando a execução
completa nesta etapa e reservando-a para a aplicação. Mantidos o mesmo
Markdown autorizado de 198 páginas, Terra, V8, grupos adaptativos e máximo
de duas chamadas simultâneas. Volume operacional e fonte montados somente
para leitura; credencial apenas em memória, sem impressão ou cópia em arquivo.
Dados de teste no volume privado `miller-shared-fields-benchmark-20261115`.
Origem inicial idêntica à medição anterior: 130 páginas fechadas, 477 fichas
de lotes fechados e 20 do lote aberto, totalizando 497 fichas completas.

Realizadas seis chamadas no total. A primeira sintética levou 5,762 s e foi
rejeitada porque trouxe unidades_fonte dentro de campos do delta. O limite
de uma chamada interrompeu antes de correção. A resposta original foi
preservada e reproduzida sem rede, com diagnóstico do próprio validador para
a chamada corretiva real, de 4,261 s; caso sintético e PDF/ZIP passaram.
Para manter o teto de seis, reduzidas as documentais de cinco para quatro,
duas no recorte 131–132 e duas em 146–147. O recorte 138–140 não foi chamado.
Dois erros de preparação do script isolado ocorreram antes de novas chamadas
(diretório existente e parâmetro do adaptador de reprodução); foram corrigidos
somente em `/tmp`, sem consumir API nem alterar a aplicação.

| Chamada documental | Alvos | Duração da requisição | Estado conferido |
| --- | --- | --- | --- |
| 1 | 131–132 | 32,739 s | Aceita: oito excluídos |
| 2 | 146–147 | 116,539 s | Pedido de contexto; fichas não promovidas |
| 3 | 131–132 | 41,844 s | Aceita: 12 excluídos |
| 4 | 146–147 | 71,308 s | Rejeitada: referência de campo fora do escopo |

Os despachos 1/2 e 2/3 se sobrepuseram; concorrência máxima observada de dois.
Janela da primeira requisição à última resposta, incluindo intervalos internos:
188,387 s, aproximadamente 3min08s. Exclui preparação, sintético e auditoria
final, não representa o tempo integral de execução do script. A média das
quatro requisições foi 65,608 s. A sinalização interna AnalysisSampleComplete
encerrou pelo orçamento; nenhuma chamada posterior foi feita. Recuperadas as
métricas persistidas e conferido o estado em auditoria offline, sem substituir
essa janela por um tempo total que não ficou registrado pelo script.

Na cópia, 497 → 517 fichas completas, 20 novas excluídas, zero rascunhos e
130 páginas fechadas. Média agregada da janela por ficha nova válida:
188,387/20 = 9,419 s; vazão aproximada de 6,37 fichas/minuto. A amostra inclui
o tempo de contexto e rejeição, mas não o custo da correção que ficou fora
do orçamento. Informados 170.626 tokens de entrada e 23.132 de saída nas
quatro documentais; o uso da primeira sintética não ficou registrado, portanto
não somar esses tokens como se fossem o consumo total das seis chamadas.

O retorno de contexto tinha duas incluídas e oito referências a quatro campos
compartilhados; as fichas não foram promovidas, conforme a regra vigente de
processar primeiro o pedido. A última resposta tinha duas incluídas e 12
referências a seis valores, mas colocou `$campo` dentro de
`/registros/0/campos_adicionais/validade_certificacao`. A referência só pode
substituir um campo integral autorizado, portanto foi rejeitada como
referencia_campo_invalida. A correção não chegou a ser enviada porque a
amostra atingiu quatro chamadas. Não houve relaxamento, edição dos retornos
reais ou promoção dessas fichas. O teste não comprovou ganho do ponto 3.

Auditoria sem rede reproduziu exatamente as quatro respostas com suas
métricas originais, confirmou os estados aceita/contexto/aceita/rejeitada e
gerou os mesmos completed/pending da cópia real. Revalidados estrutura,
digest, páginas e evidências literais; todas as 497 fichas anteriores ficaram
idênticas. Retornos e diagnóstico privado permanecem no volume da amostra;
nenhum foi incorporado ao checkpoint operacional.

Cálculo condicional usando a densidade histórica: 80 unidades restantes no
lote atual + 66 páginas × 477/130 fichas/página ≈ 322,169 fichas equivalentes;
× 9,419 s = 3.034,631 s, cerca de 50min35s adicionais. Total estimado de
819,169 fichas × a mesma taxa = 7.716,057 s de análise, cerca de 2h09. Com a
conversão histórica de 674,18 s, 8.390,237 s, aproximadamente 2h20 antes da
finalização/envio. O cenário de 50 fichas/página nas páginas futuras daria
8h51 restantes e aproximadamente 10h20 para análise/conversão desde o início.
São hipóteses de baixa confiança, sem intervalo estatístico ou garantia:
somente excluídos foram aceitos, correções adicionais e fichas completas não
foram concluídas, a densidade futura é desconhecida e a conversão não foi
medida novamente. Sem controle equivalente, não atribuir a diferença da média
anterior ao compartilhamento de campos; os recortes e tipos de trabalho variam.

Conferido o checkpoint operacional antes/depois, SHA-256
`ae69e68569a87783b137d454259e14a12bb7325aafa79668399d600edbbf4401`,
byte a byte intacto. SQL somente leitura permaneceu com dois documentos e
15 tentativas em erro e nenhuma execução n8n ativa. Renderizador HTTP 200 e
seis serviços saudáveis. Sem nova tentativa, processamento completo, envio,
mudança de código/configuração/workflow/VPS, commit ou push. Suíte da
implementação não foi repetida; a validação atual é a amostra real limitada,
reprodução offline, integridade operacional e verificações documentais.

## 2026-11-15 — Upload duplicado identifica o protocolo e o cancelamento anteriores

O usuário relatou na tela de upload a mensagem de processamento interrompido
a seu pedido. Consulta somente leitura confirmou que pertencia à tentativa
14, execução 80, encerrada em 14/11, e que nenhum processamento novo havia
começado. O mesmo SHA-256 retorna o protocolo existente, conforme RN-07.
A interface anunciava protocolo registrado e mostrava seu erro sem indicar
que era um reenvio, causando a impressão de falha atual.

Preservados código/documentos em `/tmp/miller-upload-duplicado-20261115` e
imagem anterior em `miller-gateway:before-duplicate-message-20261115`.
A API agora retorna `duplicate:true` no reenvio e `false` no upload novo;
se não conseguir localizar o registro duplicado, devolve erro de serviço em
vez de inventar um protocolo não registrado. A tela explica que nenhum novo
processamento foi iniciado, distingue o status do protocolo existente e
oferece **Abrir protocolo existente**, preservando autenticação por sessão
ou token. Mensagem e histórico do cancelamento não foram alterados.

Extraído o script de upload para arquivo próprio. A seleção de outro arquivo
invalida consultas antigas e esconde o resultado anterior; uma resposta
atrasada não pode contaminar o novo envio. Reenvio não dispara retomada nem
e-mail. A retomada continua no detalhe, com confirmação do operador. A
aplicação atual não oferece reinício integral do mesmo PDF; essa ação não
foi introduzida por esta correção de identificação do upload.

Passaram 62 testes de upload e contratos no contêiner sem rede, com 13
contratos dependentes de Node pulados ali e aprovados no host: 75 testes
Python distintos. Os 30 contratos completos e as suítes JavaScript do detalhe
e upload passaram. Novos casos verificam reenvio após cancelamento sem novo
despacho, preservação de histórico, erro sem protocolo fictício, indicação
de duplicado com link autenticado, upload novo e resposta atrasada. Um erro
inicial na montagem do histórico sintético do teste foi corrigido e o conjunto
direcionado repetido. A suíte completa da aplicação não foi executada nesta
correção; não reutilizar a contagem histórica do renderizador como validação.

Construída e aplicada somente a imagem local do gateway
`sha256:a94e7f79679f63de5ad6bebda19869be9afaf22f1dde2761219491fc895e4ff3`.
Verificação protegida na API local reenviou os mesmos bytes do PDF cadastrado
e recebeu HTTP 200, `duplicate:true` e o mesmo protocolo. Comparados detalhe,
histórico e hash do original antes/depois: íntegros e idênticos. O script
instalado foi servido com a nova identificação. Token usado somente em
memória; sem impressão de segredo, credencial ou conteúdo documental.

SQL somente leitura confirmou dois documentos e 15 tentativas em erro,
sem execução n8n ativa. Seis serviços saudáveis. Nenhuma análise, nova
tentativa, chamada externa, envio ou mudança de workflow, configuração,
modelo, checkpoint ou VPS. Atualizados PRD, ROADMAP e fluxo; preservadas
as mudanças locais preexistentes, sem commit ou push.

## 2026-11-15 — Causa raiz da tentativa 15: refinamento do limite perde objeto de evidência

A pedido do usuário, investigada somente a falha do processamento mais
recente, sem corrigir código ou retomar a execução. SQL somente leitura
identificou tentativa 15, execução principal 81, iniciada em 15/11 às
18h30m52s e encerrada às 18h48m51s de Brasília: 1.079,526 s, aproximadamente
18 minutos. Categoria validação; mensagem final ligada ao diagnóstico
`ANV8D-20d7ce87c913470da59a2e165943403a`. O nó n8n de preparação do ZIP
propagou a falha da análise; o erro não demonstra falha do renderizador PDF.

Lidos os seis diagnósticos dessa execução e o código instalado, sem imprimir
trechos documentais. Houve rejeições intermediárias por citação não localizada,
referências `$campo` em subcampos não permitidos e evidência removida do
inventário. Os diagnósticos de campos compartilhados identificaram
`/registros/1/peticoes/0/motivo` no lote 131–132 e
`/registros/0/entidades/0/cnpj` no lote 144–145. Esse último foi a rejeição da
quinta chamada do lote 144–145. A sexta chamada, corretiva, superou essa
barreira, mas falhou por `delta_evidencia_removida` em
`/reconciliacao_delta/blocos/B4`. Não há nova correção para essa mesma resposta
porque o orçamento estrutural/literal é único por grupo.

Reproduzida exatamente a rejeição com o retorno preservado, inventário do
checkpoint e mesma fonte, em contêiner sem rede e volumes somente leitura.
Conferidos hash da base do delta, digest, estrutura, cobertura, IDs e
evidências literais do checkpoint. O delta alterava estado_revisao,
pendencias e limites do bloco B4. Limites tinha inicio/fim antes e depois;
o início continuou idêntico. Não foi perda de uma chave por atualização
parcial: a evidência do fim da página 144 mudou de 78 para 109 bytes.
Ambos os trechos existem literalmente na fonte, e o novo contém integralmente
o anterior. Portanto, a rejeição final não é citação inventada ou ausente na
fonte: o objeto exato da evidência anterior deixou de existir no inventário.

O servidor substitui valores de campos presentes em campos e compara todos
os objetos de evidência anteriores/atuais fora das unidades do bloco. A
semântica aditiva é exclusiva de evidencias/adicionar_evidencias; limites não
possui união automática. A IA reenviou o limite ampliado sem guardar a
evidência antiga nessa lista, e o bloco não tinha outras evidências onde
ela permanecesse. A proteção de preservação, corretamente acionada segundo
o contrato atual, rejeitou essa substituição. Essa é a incompatibilidade
entre refinamento do inventário e preservação do objeto anterior que bloqueou
a entrega; não atribuir genericamente a queda de serviço, crédito ou timeout.

Teste de hipótese exclusivamente em memória acrescentou a evidência antiga
em adicionar_evidencias do B4, sem modificar o limite novo. merge_inventory
passou e conservou os dois valores documentais. Nenhum retorno, checkpoint
ou arquivo operacional foi editado. A prova valida essa etapa da fusão,
não todos os campos da resposta ou o relatório inteiro. Correção futura deve
definir o refinamento dos limites com preservação e origem auditável das
evidências, informar a evidência exata ausente no diagnóstico direcionado e
manter literalidade, base do delta e orçamento único. Não remover a proteção
nem simplesmente aumentar a quantidade de correções. Referências aninhadas
do ponto 3 também precisam ser tratadas dentro do escopo autorizado do transporte.

O mesmo tipo de erro de preservação já havia aparecido em uma unidade do
inventário no benchmark de 14/11, antes dos campos comuns. A união de
evidencias resolveu aquela forma; a regra de limites permaneceu a anterior.
As referências aninhadas do ponto 3 causam retrabalho nesta tentativa, mas
não são o motivo final que encerrou a execução 81.

Estado salvo revalidado: 73 lotes concluídos, 141 páginas fechadas, 728 fichas
nesses lotes e sete completas no lote aberto 144–145, total de 735 fichas,
sem rascunhos nesse lote. Páginas fechadas não formam prefixo contínuo:
136–137 continuam pendentes apesar de haver lotes fechados até 143. SHA-256
do arquivo de checkpoint inspecionado:
`8979272cb3b759c38d1d246dd330f5d8cd4b0b05de120660f06983f0e3eb4dbb`.
Os seis serviços estavam saudáveis; a identidade permanece a instalada após
o ponto 3. Não foi necessária conversão nova nem há perda demonstrada do
progresso que justifique reiniciar da página 1.

Atualizado o bloqueio no ROADMAP. Investigação somente leitura e ensaios em
memória, sem chamada externa, tentativa, reprocessamento, envio, mudança
funcional, implantação, commit ou push. Testes de aplicação não foram
executados: a validação atual compreende reprodução do erro real e hipótese
de fusão, revalidação do estado e verificações documentais.

## 2026-11-15 — Correção autorizada do refinamento das evidências nos limites

O usuário autorizou aplicar a correção após a análise da tentativa 15.
Mantida a dispensa da skill ausente no contexto desta implementação, as
demais regras do projeto e a execução real parada. Preservados fontes e
documentos em `/tmp/miller-evidencias-20261115`, imagem anterior em
`miller-renderer:before-evidence-refinement-20261115` e cópia privada do volume
em `miller-before-evidence-refinement-20261115`. Alterações locais anteriores
mantidas, sem inclusão em commit.

No delta do inventário, refinamento explícito de limites deve conservar as
chaves e os locais de referência existentes. O servidor mantém os limites
novos recebidos e acrescenta à lista evidencias do mesmo bloco/unidade os
objetos exatos das citações anteriores que foram deslocadas e não permanecem
em outro campo local. Preserva todos os atributos, a ordem das evidências
existentes e adições explícitas, sem duplicar objetos idênticos. Não infere
limites, normaliza trechos ou escolhe a validade semântica de versões.

Limites apagados, nulos ou sem suas referências anteriores continuam
rejeitados. Evidências antigas e novas passam pelas mesmas verificações de
literalidade, páginas e escopo. Remoção de evidência fora de limites permanece
erro e agora informa campo anterior e objeto exato ausente no diagnóstico
privado enviado à única correção. Conferido também o tamanho do inventário
consolidado após a preservação pelo servidor. IDs, fichas concluídas,
revisão pendente, orçamentos, paralelismo e campos compartilhados mantêm
suas demais regras. Referências aninhadas fora do contrato do ponto 3
continuam rejeitadas; esta correção não amplia seu escopo permitido.

Passaram 58 testes direcionados inicialmente. A preparação de um caso novo
foi ajustada para expandir as referências de evidência compactadas do
diagnóstico, sem mudar a aplicação; o conjunto direcionado passou novamente.
Acrescentado caso de citação diferente preservando ambas e a revisão pendente.
Suíte oficial completa final: 382 testes no contêiner, com 13 contratos de
Node pulados ali e aprovados no host; total de 395 testes Python distintos.
Os 30 contratos completos e as suítes JavaScript do detalhe/upload passaram.
Testes de aplicação sem rede cobrem refinamento em bloco/unidade, atributos,
ordem, idempotência, adições explícitas, duplicação, rejeições de limites,
evidência falsa/página inválida, remoção fora do escopo, diagnóstico direcionado,
correção única, orçamento, retomada e migração sem perda.

Reproduzida sem rede e sem edição dos dados a resposta real do diagnóstico
`ANV8D-20d7ce87c913470da59a2e165943403a`, com a mesma fonte e base do delta.
Passaram decodificação, estrutura das quatro fichas recebidas, evidências,
conferência global de IDs, preservação dos anteriores e validação do conjunto:
11 fichas e 211 ocorrências de evidências literais no lote 144–145. A citação
antiga está guardada na lista evidencias e o novo limite está intacto. O lote
continua parcial conforme a resposta e o contexto, sem promoção a concluído.
Fonte e checkpoint de origem permaneceram byte a byte íntegros. A reprodução
também passou na imagem final. As quatro fichas rejeitadas não foram importadas
na operação; o teste não homologa todo o documento nem gera PDF real final.

Construída e aplicada somente a imagem local do renderizador
`sha256:62a8401c9835118420dc3aa720a924fcff6a97692a1fdb3b646e719140fc6413`.
Identidade instalada de implementação
`2856f024795ea974eea1b8b51ce8a6840c70d80d3ce281a4a361ad8a5e7cd717`,
instruções `43cdff0461ade11ce3106778bfffdd12df0aea3eed4fc868b95adefbb8474b05`.
O migrador reconhece a versão anterior dos campos comuns por hashes exatos.
Migração explícita, sem rede e com bloqueio, da origem
`b02c28e1f01c7bb9ba2e6c59573ddffdfe494d418022e5e2470eb0e1a99a0d57`
para `9a22bdbd4d318de6f01d5eea4977479d96710380343ad978fd23a6205bc5c339`.
Dados integralmente iguais, exceto proveniência da migração; origem intacta,
SHA-256 `8979272cb3b759c38d1d246dd330f5d8cd4b0b05de120660f06983f0e3eb4dbb`.
Preservados 73 lotes, 141 páginas fechadas, 728 fichas nesses lotes e sete
completas no lote aberto, total 735, incluindo inventários, buscas, revisões
e políticas. Novo arquivo 600. A migração não acrescenta evidências nem
reinterpreta limites de dados já salvos; o tratamento ocorre na próxima
resposta efetivamente recebida e validada.

V8 original, Terra, identidade corrigida e HTTP 200 conferidos. SQL somente
leitura permaneceu com dois documentos e 16 tentativas em erro, sem execução
n8n ativa. Nenhuma nova tentativa, chamada externa, envio ou alteração de
workflow, gateway, variáveis, dependências, provedor ou VPS. Atualizados PRD,
ROADMAP, fluxo e guia local. Sem commit ou push. A retomada e conclusão do
documento continuam sob a ação do operador em Reprocessar.

## 2026-11-15 — Tentativa 16: proteção de repetição do contexto e lacuna de diagnóstico

O usuário solicitou analisar o novo erro. Consultas somente leitura
identificaram tentativa 16, execução 83, iniciada às 19h07m33s e encerrada às
19h30m19s de Brasília: 1.366,179950 s, aproximadamente 22min46s. Mensagem final
`pedido de contexto sem nova busca ou página pendente`, propagada pelo nó de
preparação do ZIP. Categoria persistida infraestrutura. Os seis serviços
locais estavam saudáveis; não há indício nesse erro final de falta de crédito,
timeout, falha do conversor ou renderização PDF.

A correção anterior avançou: o checkpoint possui o lote 144–145 concluído,
assim como 136–137. A nova causa terminal não é delta_evidencia_removida.
Os três diagnósticos ANV8D dessa execução registram rejeições intermediárias:
página fora do registro em uma conferência do lote 144–145 e referências
aninhadas a campos compartilhados no lote 161–162. O último diagnóstico,
`ANV8D-a29fa8fd25ea4bfe960c820afc2d2f7e`, é da chamada 12 desse lote e trata
`/registros/0/entidades/0/endereco`, não o erro terminal de contexto.

Causa imediata confirmada no código: incremental._task_steps identifica a
presença de contexto_necessario ou buscas_necessarias antes de validar os
registros. Após reconhecer e persistir a janela entregue, context_window.request
verifica se o pedido acrescentou alguma página ao conjunto solicitado ou um
termo novo. Quando isso não acontece e requested-delivered está vazio, lança
o erro observado, encerrando a análise. Uma busca vazia também satisfaz essa
condição; contexto_necessario vazio tem outra mensagem específica de entrada
inválida. Não é o limite de três ampliações nem o teto de 256 buscas locais.

Há uma lacuna demonstrada nessa regra: entrega histórica não significa
disponibilidade no pacote atual, e cada chamada contém somente sua janela.
O estado do lote 151–152 registra 14 páginas entregues, nenhuma pendente,
seis buscas conhecidas e última janela com oito páginas:
144, 145, 149, 150, 151, 152, 153, 154. As páginas 146, 147, 148, 155, 156 e
157 foram entregues em outra janela e estão ausentes desta. Reconstruir o
pacote pelo código instalado mantém somente as mesmas oito, pois a fila
usa requested-delivered e fica vazia para qualquer página entregue antes.
Uma releitura legítima de página ausente pode ser tratada como repetição
sem progresso. Mesmo busca nova com ocorrências em páginas antigas não as
torna pendentes de novo; o pedido exato da tentativa permanece desconhecido.

Em contêiner sem rede, com diagnóstico e fonte somente leitura, revalidado
o checkpoint e reproduzidas três entradas construídas em memória sobre
esse estado: reler uma página já entregue e fora da janela, buscas_necessarias
vazio e repetição de um termo conhecido. As três retornaram a mesma mensagem
terminal. São provas da condição e da lacuna de releitura, não reprodução
do retorno real. Nenhum desses exemplos foi atribuído à IA como fato.

Limitação de evidência: o ramo de pedido de contexto fica fora do try/except
que grava diagnóstico de validação. A resposta final e o pedido que acionaram
o erro não foram guardados, e o checkpoint foi persistido antes dessa rejeição.
Não há base para escolher entre releitura necessária, repetição, lista vazia
ou para dizer quais páginas/termos estavam no retorno. O último last_window
pendente aponta o lote 151–152 como origem provável; não há corpo preservado
que permita confirmar seu conteúdo exato ou eventuais fichas devolvidas junto.

Lidos somente os campos de erro da execução n8n preservada: mensagem
`pedido de contexto sem nova busca ou página pendente. [line 4]`, descrição
`IA` e último nó `OpenRouter - Prepare verification bundle`. O classificador
reconhece IA: com dois-pontos ou o estágio de análise; a divisão em
mensagem/descrição e o estágio de preparação fazem esse erro cair no padrão
infraestrutura. Esse rótulo é um problema adicional de diagnóstico e não a
causa da interrupção. O código do renderizador mapeia AnvisaError com prefixo
IA para HTTP 502; esse status genérico tampouco identifica uma queda de serviço.

Encaminhamento técnico, sem implementação nesta análise: separar páginas
historicamente entregues das disponíveis na chamada, definir releitura
controlada sem loops ou renovação de orçamentos, tratar campos vazios de
pedido, preservar a resposta/pedido/janela e estado do contexto antes de
rejeitar e classificar a causa de forma específica. Manter páginas inteiras,
literalidade, revisão explícita, máximo duas chamadas e progresso salvo.

Checkpoint com digest e conteúdo revalidados contra o mesmo Markdown:
75 lotes concluídos, páginas 1–145 em sequência, 771 fichas desses lotes e
36 completas no lote aberto 161–162, total 807, zero rascunhos. SHA-256 do
arquivo antes/depois da análise:
`f09b02c9943247613987d33da76d482373168dc77cf03be8653b33018cc6f618`.
SQL final registra dois documentos e 17 tentativas em erro e nenhuma execução
n8n ativa. Nenhuma chamada externa, nova tentativa, correção de dados,
implantação, mudança de código/workflow, commit ou push. Atualizado ROADMAP.
Suíte de aplicação não repetida: a validação atual é revalidação do checkpoint,
leitura dos erros e reprodução em memória das condições descritas, com seus
limites explicitados.

## 2026-11-15 — Quatro ajustes do contexto com verificação de desempenho

O usuário autorizou os quatro pontos propostos para corrigir o bloqueio de
contexto, exigindo manter ou melhorar principalmente o tempo total. Consulta
inicial confirmou tentativa 16 encerrada e nenhuma execução ativa; o teste
do usuário não foi interrompido. Mantida a dispensa da skill ausente neste
contexto e as demais regras do repositório. Baseline de fontes/documentos em
`/tmp/miller-contexto-20261115`. Preservadas todas as alterações anteriores.

Implementada distinção entre entrega histórica e janela atual. Páginas
entregues e agora ausentes podem entrar em fila opcional reread no contexto,
sem remover o histórico de delivered. Metadata registra pending, seen e
requests somente quando há releitura, conservando o formato 3 e sem aumentar
o pacote do provedor no caminho normal. Até três pedidos que acrescentem
releituras são permitidos sem avanço documental validado; o contador persiste
na troca de janela e retomada. Entrega, retry e progresso de outro lote não
o renovam. Avanço do próprio lote libera esse orçamento e conserva a fila
remanescente, sem alterar os demais limites.

Buscas conhecidas reutilizam o resultado local sem nova varredura. Páginas
encontradas/vizinhas ausentes podem ser reenfileiradas; ao percorrer uma fila,
repetir a mesma busca não reenfileira páginas já atendidas nesse ciclo. Um
pedido explícito de página ausente permanece limitado pelo contador próprio.
Pedidos de páginas presentes sem nova busca ou fila pendente continuam
interrompendo. Listas opcionais vazias de contexto/buscas passam pelo caminho
normal de validação das fichas na mesma resposta; não geram chamada extra.
Uma resposta só com campos vazios continua incompleta e tem no máximo a
correção estrutural já prevista, sem loop novo.

O ramo de pedido de contexto agora captura rejeições, preservando resposta
de transporte original, pedido, janela efetiva, contexto anterior/proposto,
motivo, métricas e geração da chamada, vinculados pelo escritor privado à
fonte/tentativa/execução. O erro retorna como validação HTTP 422 com referência
ANV8D, já reconhecida pelo workflow de erros; não foi necessário alterá-lo.
Falha ao guardar diagnóstico retorna armazenamento HTTP 500. O detalhe
documental permanece privado. Não há gravação de diagnóstico nas respostas
normais aceitas nem aumento de correções ou retries.

Preservados máximo de duas chamadas, fila dinâmica, grupos adaptativos,
480.000 bytes com páginas inteiras, índices/fichas completas, validação
literal, correção única e prazo global zero. As instruções de contexto foram
ajustadas sem crescimento: 2.319 → 2.317 bytes. No caminho normal, conjuntos
constantes de chaves e tratamento condicional do metadado evitam alocações
desnecessárias. Nenhum serviço, dependência, variável ou mudança de modelo.

Passaram 90 regressões iniciais e 98 casos de contexto/orquestração após os
casos novos. Suíte final completa: 400 testes no contêiner e 13 contratos
dependentes de Node pulados ali e aprovados no host, total de 413 testes
Python distintos. Os 30 contratos completos e as suítes JavaScript de
detalhe/upload passaram. Os 18 casos novos cobrem releitura, histórico,
cache sem varredura, pedidos vazios com fichas válidas em uma chamada,
limites persistidos através de janelas/retomada, conclusão após releitura,
retomada sem nova IA, corrupção de metadados, diagnóstico privado/HTTP e
armazenamento, migração e escopo concorrente. Nenhuma validação foi relaxada.

Benchmark isolado sem rede comparou baseline e correção em 15 repetições
alternadas por versão, após aquecimento. Mesma fonte artificial de 20 páginas,
100 fichas, mesmas respostas e latência de provedor simulada de 5 ms, com
gravações atômicas reais de checkpoint. Resultados completos idênticos.

| Métrica do benchmark controlado | Antes | Depois |
| --- | --- | --- |
| Chamadas simuladas | 12 | 12 |
| Gravações de checkpoint | 25 | 25 |
| Concorrência máxima | 2 | 2 |
| Bytes agregados das mensagens | 669.667 | 669.643 |
| Mediana local | 352,551 ms | 346,199 ms |
| Mínimo / máximo | 329,915 / 407,262 ms | 316,850 / 448,121 ms |

Não houve regressão observada no ensaio; as faixas se sobrepõem e a pequena
diferença não comprova aceleração estatística ou do OpenRouter. Não há
garantia medida do tempo total real: nenhuma API externa foi chamada. A
evidência de não aumentar trabalho no caminho comparável é a mesma quantidade
de chamadas/gravações, mesma concorrência, resultados idênticos e nenhuma
expansão das mensagens. Releitura necessária é trabalho que a versão anterior
interrompia, não comparar uma execução corrigida com uma abortada como ganho.

Revalidado em memória o checkpoint real sem editar fonte ou estado. Pedido
construído para reler página 146 ausente da janela 151–152 foi atendido:
o pacote reconstruído passou de oito páginas/97.242 bytes para sete/87.092,
incluindo a página pedida e preservando a história. Não reenviado o histórico
inteiro. Repetir a página presente continuou rejeitado. Campos vazios deixaram
de ser pedidos. Esse ensaio não reconstrói o retorno final perdido da
tentativa 16 e não promove fichas. As 807 fichas permaneceram intactas.

Imagem anterior em `miller-renderer:before-context-recovery-20261115` e backup
privado do volume em `miller-before-context-recovery-20261115`. Construída e
aplicada somente a imagem local do renderizador
`sha256:a5289833930115d96ee95a51d4c8a16e2ddec247004a0b6d8870c1fe2009f749`.
Implementação `2d82eb1598f6eab4db3e1baecd49aed88b5686f6f9c80fcd0865e4fdaa1c2cf5`,
instruções `1c26ea5b1e7ad1f0eb152da397f1a69741a00a1e8b492633f25f161dac11c250`.
Migração explícita, com bloqueio e revalidação, da identidade
`9a22bdbd4d318de6f01d5eea4977479d96710380343ad978fd23a6205bc5c339`
para `9081e787f0f8ff430bf7053d6d99725f16edd12a4dfaaf1773f1ba9236f71862`.
Completos/pendentes e demais dados iguais, exceto proveniência. Origem intacta,
SHA-256 `f09b02c9943247613987d33da76d482373168dc77cf03be8653b33018cc6f618`.
75 lotes, páginas 1–145, 771 fichas fechadas e 36 completas no lote aberto,
total 807, preservados com filas, revisões, buscas e políticas. Novo arquivo
600. A migração não inventa pedidos/counters nem importa respostas rejeitadas.

Confirmados V8 original, Terra, identidade instalada, HTTP 200, seis serviços
saudáveis, dois documentos e 17 tentativas em erro e nenhuma execução ativa.
Sem nova tentativa, chamada externa, envio ou alteração de workflow, gateway,
configuração ou VPS. Atualizados PRD, ROADMAP, fluxo e guia local. Sem commit
ou push para não incorporar o amplo trabalho local preexistente. Retomada
e medição real de ponta a ponta permanecem na execução pela aplicação.

## 2026-11-15 — Pausa solicitada e preservação para retomada

O usuário iniciou a retomada pela aplicação após a correção de contexto.
A tentativa 17, execução n8n 85, começou às 20h09m15s de Brasília. A pedido
do usuário, a execução foi cancelada pela API autenticada do n8n às 21h02m45s,
com resposta HTTP 200 e estado nativo `canceled`. O renderizador foi encerrado
para interromper também a análise HTTP em curso. Em transação condicionada
ao cancelamento e à ausência de outra execução ativa, documento e tentativa
receberam `erro`, categoria `cancelamento_manual`, com a mensagem
`Processamento pausado a pedido do usuário; progresso salvo preservado para retomada.`
Foi registrado um evento de auditoria, sem alterar os erros anteriores.

Encerrados upload-gateway, n8n, pdf-converter, ollama e PostgreSQL. Conferidos
os seis serviços parados via Compose, sem remover contêineres ou volumes.
Nenhum serviço de outro projeto foi interrompido. O cancelamento manual
não representa nova falha de validação nem conclusão do relatório.

O último checkpoint foi salvo às 21h02m48s e revalidado, sem rede, contra
o Markdown persistido: 84 lotes concluídos, 159 de 198 páginas fechadas,
977 fichas em lotes fechados e 26 completas em lotes abertos, total de 1.003,
sem rascunhos. Preservados os demais inventários, filas, revisões e políticas.
Checkpoint `9081e787f0f8ff430bf7053d6d99725f16edd12a4dfaaf1773f1ba9236f71862`,
SHA-256 do arquivo `47249fcbaa3bd6fe4efd60d8de3e599f7a341c3aa1482c466cc8822e95a0a87f`.
Cópia do volume privado em `miller-paused-progress-20261115`, com o checkpoint
conferido byte a byte contra o original. Artefatos e banco permanecem nos
volumes da stack. A retomada exige subir a aplicação e confirmar Reprocessar
no mesmo protocolo; nenhuma execução futura foi iniciada ou agendada.

O usuário solicitou consolidar em commit as alterações acumuladas desta
implementação, com descrição. Mantidas as validações funcionais registradas
na entrada anterior, sem repetir a suíte nem chamar o provedor para esta
pausa e consolidação. A execução real de ponta a ponta e a conferência do
PDF final continuam pendentes; estimativas anteriores não são uma medição
de conclusão. Nenhum push foi autorizado.

## 2026-11-15 — Conciliação da main com as melhorias Anvisa V8

Tipo: INTEGRAÇÃO / DOCUMENTAÇÃO / TESTE
Status: conflitos locais resolvidos e integração validada

O usuário solicitou resolver os conflitos surgidos ao integrar a main
`29a6b4b` na branch `feature/performance-test`, então em `eaf90bd`. Foram
conciliados dez arquivos conflitantes e preservadas as alterações recebidas
sem conflito. Backup dos arquivos e do índice anterior em diretório protegido
sob `/tmp/miller-merge-txwibrux`, fora do repositório.

O gateway conserva os imports e rotas de retomada e recebe o contexto
determinístico e a validação de candidatos do v2. No workflow v1, a nova
varredura ocorre somente no ramo Ollama. Nós, parâmetros, configurações e
conexões existentes do V8 e da retomada foram comparados com a versão anterior
e preservados; o v2 híbrido continua em export próprio, inativo no Git.
Os requisitos determinísticos e da auditoria híbrida recebem RF-22 e RF-23,
sem sobrescrever RF-20 (conversão local) e RF-21 (retomada).

Documentação conciliada por ambiente e data: fotografia da VPS de 27/10 e
histórico local Anvisa V8 de novembro. Preservados integralmente os 117 registros
datados da branch e os 72 da main, inclusive os compartilhados, com os eventos
de outubro inseridos antes dos de novembro. Nenhuma validação histórica foi
apresentada como execução atual. As falhas de qualidade do v2 e a conclusão
real ainda pendente do V8 continuam registradas.

Validação desta integração:
- Suíte Python em contêiner descartável sem rede e com cópia somente leitura
  dos arquivos versionados: 415 aprovados e 15 contratos pulados por falta de
  Node na imagem; os 32 contratos completos passaram no host, cobrindo os 15.
  Total de 430 testes Python distintos. Três avisos de depreciação de
  Starlette/AnyIO e FastAPI, sem falhas.
- Duas suítes JavaScript de detalhe e upload aprovadas.
- Compose principal, complemento local e conversão local validados sem ler
  valores do `.env` protegido.
- JSON dos workflows, conexões, unicidade de IDs, `active=false`, ausência de
  vínculos de credenciais, sintaxe Python, links Markdown e diff conferidos.
- Gitleaks local sem rede: nenhum segredo encontrado nos arquivos versionados.

A primeira execução dos contratos detectou a expectativa antiga de ligação
direta do seletor ao lote Ollama. O contrato foi conciliado para exigir o novo
nó de contexto nesse ramo e manter a ligação direta ao V8 no outro; a suíte
completa posterior passou. Mantidas também as verificações documentais das
duas branches, sem relaxar cobertura ou evidências.

Nenhuma chamada a provedor, uso de documento real, implantação, alteração de
credencial, reinício da aplicação pausada ou push foi realizado. A recuperação
operacional do V8 e a homologação da VPS continuam sendo tarefas separadas,
com as pendências e autorizações anteriores preservadas.

## 2026-11-16 — Integra as PRs #5 e #3 e alinha a documentação

Data: 2026-11-16
Tipo: INTEGRAÇÃO / DOCUMENTAÇÃO / ROADMAP
Status: PRs integradas ao GitHub `main`; sem implantação em ambiente

Contexto:
O usuário solicitou integrar as PRs abertas #5 (V8/retomada) e #3 (guia de
teste local), além de atualizar a documentação e o roadmap. A PR #5 estava
mesclável; a #3 partia de uma base antiga e conflitava em README, ROADMAP,
LOG, implantação e workflows.

Decisão/Ação:
A PR #5 foi mesclada por squash no commit `2aabff7`. A branch da PR #3 foi
atualizada sobre essa base; os documentos atuais foram preservados e o guia
local e seus links foram incorporados. A PR #3 foi então integrada. O código
da PR #5 acrescenta a opção Anvisa V8 com OpenRouter/Terra, checkpoints privados,
retomada e transporte otimizado; o Ollama permanece como padrão local e o v2
híbrido continua separado. A PR #3 acrescenta o teste local com Ollama até
`aguardando_envio`, mantendo envio e reconciliação desligados.

PRD, README, ROADMAP, FLUXOGRAMA, ACESSOS, implantação, workflows e os dois
guias locais foram alinhados para distinguir comportamento versionado,
validação local e fotografia histórica da VPS. A fotografia da VPS continua
sendo a verificação de 27/10/2026; o merge no GitHub não ativa exports nem
implanta a stack.

Validação:
GitHub confirmou a PR #5 mesclada e a PR #3 foi atualizada e integrada após a
resolução dos conflitos. Os conflitos e links locais foram revisados, sem
marcadores remanescentes; `git diff --check` passou. As 430 verificações da
conciliação local da PR #5 e os 75 testes históricos citados na PR #3 não foram
reexecutados nesta etapa. Não houve chamada ao OpenRouter, teste de aplicação,
upload, e-mail, acesso à VPS, troca de credencial ou reinício da stack local.

Pendências:
A VPS não foi consultada nem atualizada. O V8 local continua pausado desde
15/11 com checkpoint preservado para retomada no mesmo protocolo; não há PDF
final homologado. Permanecem as falhas de qualidade do teste híbrido sintético,
além das tarefas de segurança, backup, HTTPS, envio e reconciliação registradas
no ROADMAP.md.

Impacto:
As duas PRs e as atualizações documentais estão versionadas em `main`. O V8
está disponível no código, mas não está confirmado como implantado ou ativo na
VPS. O usuário deve consultar ROADMAP.md antes de retomar a operação.

## 2026-11-21 — Instala o Miller na VPS do cliente

O commit `3cac700` foi transferido a `srv2147368.hstgr.cloud`, em uma
instalação nova com Docker e Compose dos repositórios Ubuntu. Após autorização
do usuário, o registro A de `reportai.info` passou a apontar para `2.25.172.95`,
com TTL de 60 segundos exigido pelo painel. O Caddy passou a servir a landing
por HTTPS e a redirecionar `www.reportai.info` para o domínio principal.

Foram verificados os seis serviços saudáveis, o certificado da landing, os
redirecionamentos, o acesso privado, o login, o logout, o cookie seguro e os
hashes do backup inicial. Os 15 testes locais de contrato de implantação
passaram com o commit implantado.

Foram importados quatro workflows inativos com credencial PostgreSQL própria.
O n8n foi configurado para Anvisa V8 via OpenRouter. O comando
`miller-configurar-openrouter` ficou no servidor para validar e aplicar a chave
de forma interativa e publicar o processamento e o tratamento de erros. A
pedido do usuário, a validação terminou com zero execuções no n8n. A chave do
cliente, a configuração administrativa do n8n e o OAuth do Gmail seguem
pendentes. O Gmail ficou para depois da indicação da conta pelo cliente ou
pelo líder técnico. O backup fica na VPS e a restauração isolada segue por
verificar. O roteiro das próximas implantações foi consolidado em
[DEPLOY.md](DEPLOY.md) e referenciado em [AGENTS.md](AGENTS.md).

## 2026-11-23 — Conclui o processamento com download direto do PDF

O relatório passa a ficar disponível no detalhe autenticado do protocolo assim
que o workflow salva o PDF e registra, em uma operação PostgreSQL, o artefato
e a conclusão do documento e da tentativa. O painel exibe **Baixar relatório
PDF** após detectar a conclusão e conferir a presença do arquivo. A conferência
das referências continua disponível no detalhe.

O envio pelo Gmail, a gestão de destinatários e as rotas de entrega foram
removidos da aplicação e dos exports. A reconciliação encaminha somente
protocolos de processamento. A migração 006 adequa os protocolos anteriores
com PDF registrado, preserva as tabelas históricas existentes e encaminha
protocolos sem registro de PDF para erro de armazenamento.

Validação local com dados sintéticos:

- 434 testes Python aprovados. O contêiner cobriu 419 casos e os 15 contratos
  que exigem Node foram executados no host.
- 17 testes JavaScript de painel e upload aprovados. Dois testes E2E no
  Chromium verificaram conclusão, download com hash igual ao artefato,
  bloqueio sem sessão e ausência de download durante o processamento ou após
  falha na análise. A resposta simulada do Ollama manteve o teste determinístico.
- No PostgreSQL isolado, o SQL de conclusão dos dois exports internos
  concluiu protocolos sintéticos. A migração foi reaplicada e o teste cobriu
  conflito de armazenamento, registro de erros e reconciliação.
- O n8n 2.30.5 voltou a registrar a falha conhecida no serviço de estatísticas
  (`r.firstEvent.getTime is not a function`). Os estados operacionais no
  PostgreSQL e os dois cenários de navegador foram confirmados.

A mudança está no repositório. A VPS não foi consultada ou alterada nesta
etapa. O roteiro de atualização e homologação está em [DEPLOY.md](DEPLOY.md).

## 2026-11-23 — Prepara a instalação da chave OpenRouter em produção

A consulta por SSH confirmou o commit `3cac700`, o renderizador saudável,
quatro workflows inativos e zero execuções na VPS do cliente. O usuário
informou que recebeu a chave da OpenRouter. O instalador ganhou a opção
`--somente-chave` para validar a credencial e aplicá-la ao renderizador. A
versão anterior do instalador foi preservada e a sintaxe da nova versão
foi conferida. A entrada da chave pelo administrador ficou pendente. A
ativação dos workflows será feita após a atualização para download direto.

## 2026-11-23 — Confirma a chave OpenRouter na VPS do cliente

O administrador inseriu a chave pelo terminal SSH com `--somente-chave`.
A consulta verificou a presença da variável no renderizador, health HTTP
`200` e permissão `600` do `.env`. A VPS executava o commit `3cac700` e o
n8n registrava quatro workflows inativos e zero execuções. A publicação
dos workflows e a homologação com PDF sintético seguem pendentes da
atualização para download direto.

## 2026-11-23 — Implanta o download direto do PDF na VPS do cliente

A `main` remota foi sincronizada antes da mudança. O commit `b006b7f` foi
transferido com verificação SHA-256, construído e iniciado em produção. A
migração `006` terminou com `COMMIT`. As constraints de documento e
tentativa foram verificadas. A versão `3cac700` e suas imagens foram
preservadas para recuperação.

O diretório `/opt/backups/automacao-miller/pre-b006b7f-20261124T020251Z`
guarda banco, artefatos, diagnósticos, os quatro workflows anteriores e o
Caddyfile original. Foram conferidos hashes, índice do dump e leitura do
arquivo de diagnósticos.

Foram confirmados os dez vínculos PostgreSQL, o vínculo com o tratamento
de erros, as versões atuais de processamento v1 e erros publicadas e o
webhook registrado. Os seis serviços estavam saudáveis, a chave OpenRouter
estava presente no renderizador e o n8n registrou zero execuções. Não havia
documentos na VPS.

Na versão empacotada passaram 15 testes de contrato, 56 testes do gateway
em contêiner local e duas suítes JavaScript. Em produção foram conferidos
HTTPS, login, logout, consulta à fila e autorização da rota de download.
Uploads e reprocessamentos públicos retornam `503` até a homologação com
PDF sintético autorizado. O proprietário do n8n e a reconciliação seguem
pendentes.

## 2026-11-23 — Define a administração do n8n sob demanda

O usuário decidiu manter o n8n em execução contínua, com o editor acessado
por túnel SSH quando houver necessidade de administração. A verificação na
VPS confirmou Docker habilitado no boot, n8n saudável com a política
`restart: unless-stopped`, porta `127.0.0.1:25678` e dois workflows publicados.
O n8n registrava zero contas configuradas. O cadastro do proprietário fica
para o primeiro uso administrativo do editor e saiu do checklist de
liberação ao cliente.

## 2026-11-23 — Libera novos uploads para o teste do cliente

O usuário autorizou novos uploads para a simulação prevista para 24/11 e
informou que a chave OpenRouter do cliente tem limite de gastos. O Caddy foi
validado e recarregado após retirar a suspensão do novo upload. A regra
`@reprocessamentoSuspensoDownload` preservou a suspensão do reprocessamento.
O Caddyfile anterior está em
`/opt/backups/automacao-miller/caddy-uploads-20261124T022317Z`.

Foram verificados o login e o logout do operador, HTTP `200` em `/new` com
sessão e `403` sem sessão. O webhook de entrada estava registrado, com zero
documentos e zero execuções. A homologação de análise e download fica para
a simulação do cliente.

## 2026-11-24 — Permite rodada extra controlada de releitura

No teste do cliente de 24/11, o quarto pedido de releitura incluiu páginas
repetidas e páginas ainda não solicitadas para releitura naquele ciclo. O
renderizador rejeitou o pedido inteiro ao atingir o limite de três. O ajuste
admite uma rodada extra para enfileirar somente as páginas ainda não solicitadas
no ciclo. Preserva a fila anterior e encerra a análise se houver novo pedido
de contexto antes de avanço validado ou se a fila acabar sem avanço. A conclusão
validada do lote encerra a rodada.

O contador existente guarda o uso da rodada extra, inclusive na retomada. A
identidade muda com a implementação. A migração explícita reconhece os hashes
do renderizador de `b006b7f`, copia o estado validado para a nova identidade e
preserva o arquivo original. A versão anterior rejeita estados pendentes cujo
contador já esteja em quatro.

Os testes sintéticos reproduziram o erro antes da correção e passaram com o
ajuste. Os quatro casos conferem a seleção de páginas, a migração e retomada
de um checkpoint com três pedidos, a entrega da fila em várias janelas, a
conclusão após avanço e o bloqueio persistente sem avanço. A simulação usa
respostas locais. A VPS não foi consultada durante a alteração de código.
Implantação e retomada do documento do cliente seguem pendentes.

## 2026-11-25 — Implanta o hotfix de releitura e migra o checkpoint do cliente

A `main` local avançou para `0894805`, merge da PR #7. O pacote versionado
teve commit e SHA-256 conferidos. Na VPS, a imagem anterior do renderizador
foi preservada e a nova foi construída antes da janela. A primeira passagem
terminou após o backup preliminar e restaurou a entrada antes da troca. A
execução final suspendeu novos uploads, confirmou zero execuções em andamento
e verificou os backups PostgreSQL, de artefatos e de diagnósticos em
`/opt/backups/automacao-miller/pre-0894805-20261125T160734Z`.

A atualização recriou apenas o renderizador. O migrador usou o Markdown
persistido, com hash conferido, e preservou o checkpoint original. O destino
correspondeu à identidade da versão ativa e manteve integralmente os lotes
concluídos e pendentes, incluindo 7 lotes e 18 das 228 páginas concluídas.
O diretório anterior foi guardado em
`/opt/automacao-miller-anterior-20261125T160734Z`.

Foram verificados os seis serviços saudáveis, os dois workflows publicados,
o webhook de entrada, a prontidão do n8n e a presença da configuração da
OpenRouter no renderizador. A entrada pública de novos uploads foi restaurada.
O teste HTTPS confirmou login, painel, página de novo upload e logout com
`200`, painel sem sessão com `403`, rota interna com `404` e reprocessamento
público com `503`. A execução do protocolo e sua homologação seguem pendentes
de autorização operacional. A migração ocorreu dentro da VPS, sem chamada
ao provedor de IA.

## 2026-11-25 — Libera o reprocessamento do protocolo migrado

O usuário autorizou a retomada do documento do protocolo migrado pela
OpenRouter. Foram consultados os [termos de uso](https://openrouter.ai/terms)
e a [política de privacidade](https://openrouter.ai/privacy) do provedor.
A configuração de produção seleciona OpenRouter para o Anvisa V8. O modelo
configurado para a próxima tentativa é `openai/gpt-6.1-terra`.

Na VPS, a integridade do checkpoint foi conferida e a prévia autenticada
indicou retomada pela análise do Markdown salvo. O Caddy foi validado e
recarregado com uma exceção no bloqueio para a rota exata do protocolo. A
rota retornou `403` sem sessão, e o controle de outro protocolo retornou
`503`. A validação manteve o contador de tentativas. A configuração anterior
está em `/opt/backups/automacao-miller/pre-liberacao-reprocessamento-20261125T165343Z`.
Aguardando a confirmação do cliente no painel e a validação do PDF.

## 2026-11-25 — Mantém páginas de releitura na janela até avanço validado

A consulta à VPS confirmou `0894805` em execução e 12 lotes concluídos
no checkpoint migrado. A tentativa 2 parou no lote das páginas 6 a 10 ao
pedir novamente a página 17, ausente da janela apesar de já ter sido
entregue no ciclo. O pacote reconstruído com a página 17 cabia no teto local.

A seleção local prioriza a fila pendente e conserva as páginas já relidas
enquanto couberem até avanço validado. O migrador reconhece a identidade
de `0894805`. O teste sintético confirmou o reaproveitamento de 12 lotes
sem novas chamadas para eles. Em 25/11/2026, um ensaio em memória na VPS
validou o checkpoint real e preservou integralmente os 12 lotes e a fila.
A janela reconstruída incluiu a página 17 em 83.206 bytes. O ensaio não
gravou o destino nem chamou a IA. A implantação e a retomada seguem pendentes.
