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
