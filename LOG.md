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
