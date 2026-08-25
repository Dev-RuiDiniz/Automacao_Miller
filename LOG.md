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
→ extração
→ Markdown
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

## 5. Pendências abertas

| ID | Pendência | Tipo | Prioridade | Status |
|---|---|---|---|---|
| P-001 | Confirmar VPS | INFRA | Alta | Aberta |
| P-002 | Receber credenciais do Google Drive | BLOQUEIO | Alta | Aberta |
| P-003 | Receber credenciais Gmail | BLOQUEIO | Alta | Aberta |
| P-004 | Receber PDFs de exemplo | TESTE | Alta | Aberta |
| P-005 | Selecionar modelo Ollama inicial | MODELO | Alta | Aberta |
| P-006 | Definir estrutura final da saída da IA | PROMPT | Alta | Aberta |
| P-007 | Definir regra operacional de confiança | DECISAO | Alta | Aberta |
| P-008 | Definir template do relatório | IMPLEMENTACAO | Média | Aberta |
| P-009 | Definir destinatários dos e-mails | ESCOPO | Média | Aberta |
| P-010 | Definir comportamento para PDF escaneado | DECISAO | Média | Aberta |

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
