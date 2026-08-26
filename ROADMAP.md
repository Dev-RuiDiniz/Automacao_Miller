# ROADMAP.md — Acompanhamento do Projeto

## 1. Projeto

**Nome:** Agente de Automação e Análise Regulatória  
**Stack principal:** n8n + Ollama + Google Drive + Gmail + Docker + Linux  
**Prazo comercial de referência:** até 10 dias úteis, contado após aprovação, pagamento da entrada, disponibilização dos acessos e arquivos de exemplo.

> Este roadmap é o documento operacional de acompanhamento. Datas devem ser atualizadas conforme o início real do projeto e os bloqueios encontrados.

---

## 2. Status geral

**Estado atual:** stack de homologação implantada; integrações Google e validação ponta a ponta pendentes
**MVP:** definido  
**Infraestrutura:** VPS auditada; stack Docker isolada implantada em `/opt/automacao-miller`
**Dependências externas:** acessos do cliente, Google Drive, Gmail, VPS e arquivos de exemplo  
**Critério de finalização:** fluxo ponta a ponta validado, testes aprovados e documentação entregue.

---

## 3. Legenda de status

- `TODO` — não iniciado
- `DOING` — em andamento
- `BLOCKED` — bloqueado
- `REVIEW` — aguardando revisão
- `DONE` — concluído
- `CANCELLED` — removido do escopo

---

## 4. Fase 0 — Governança e preparação

**Objetivo:** estabelecer fonte de verdade e condições para início seguro.

- [x] Definir visão inicial do produto
- [x] Criar `PRD.md`
- [x] Criar `AGENTS.md`
- [x] Criar `ROADMAP.md`
- [x] Criar `LOG.md`
- [x] Criar `README.md` comercial
- [x] Confirmar repositório oficial
- [x] Confirmar estratégia de branches (`main` como versão estável)
- [x] Criar `.gitignore`
- [x] Criar `.env.example`
- [x] Definir estrutura de diretórios
- [x] Confirmar arquivos PDF de referência para testes (documentos recebidos e registrados na matriz)
- [x] Confirmar responsáveis por validação (Miller)

**Gate de saída:** governança versionada e acessos mínimos identificados.

**Status da fase:** preparação interna concluída. O gate final permanece pendente dos bloqueios externos `EXT-001` a `EXT-005`.

---

## 5. Fase 1 — Infraestrutura base

**Objetivo:** preparar o ambiente Linux para execução do sistema.

- [x] Provisionar/confirmar VPS
- [ ] Atualizar sistema operacional
- [ ] Configurar usuário administrativo adequado
- [x] Configurar firewall e acesso SSH
- [x] Instalar Docker
- [x] Instalar Docker Compose, se utilizado
- [x] Criar estrutura persistente de volumes
- [x] Configurar política de restart
- [x] Definir backup das configurações
- [x] Validar recursos disponíveis da VPS

**Referência de infraestrutura:**

- 2 vCPU
- 8 GB RAM
- 100 GB NVMe
- Linux

**Gate de saída:** Docker funcional, armazenamento persistente e acesso seguro ao servidor.

---

## 6. Fase 2 — n8n

**Objetivo:** disponibilizar a camada de orquestração.

- [x] Implantar n8n self-hosted
- [x] Configurar persistência
- [ ] Configurar credenciais fora do código
- [x] Validar acesso ao painel
- [x] Definir workflow principal
- [x] Definir tratamento de erros
- [x] Definir estratégia de retry
- [x] Definir rastreabilidade por documento
- [x] Integrar gate HTTP PDF → Markdown
- [x] Persistir Markdown no Google Drive antes da extração
- [x] Impedir chamada ao Ollama antes da conversão validada

**Gate de saída:** n8n estável e pronto para receber integrações.

---

## 7. Fase 3 — Ollama

**Objetivo:** disponibilizar IA local compatível com a VPS.

- [x] Instalar Ollama
- [x] Selecionar modelo inicial leve e quantizado
- [x] Registrar modelo e versão no `LOG.md`
- [x] Validar memória e CPU
- [x] Executar teste básico de inferência
- [x] Medir tempo aproximado de resposta
- [x] Definir timeout do workflow
- [x] Validar chamada do Ollama a partir do n8n

**Gate de saída:** modelo local respondendo de forma estável no ambiente.

---

## 8. Fase 4 — Integração Google Drive

**Objetivo:** criar entrada automática e armazenamento dos resultados.

- [ ] Configurar credenciais do Google Drive
- [ ] Definir pasta de entrada
- [ ] Definir pasta de processamento
- [ ] Definir pasta de concluídos
- [ ] Definir pasta de revisão
- [ ] Definir pasta de erro
- [ ] Configurar monitoramento de novos PDFs
- [ ] Implementar controle contra duplicidade
- [ ] Validar download do documento
- [ ] Validar upload dos artefatos finais

**Gate de saída:** um PDF de teste pode entrar e ser recuperado automaticamente pelo workflow.

---

## 9. Fase 5 — Extração e normalização

**Objetivo:** transformar o PDF em conteúdo utilizável pelo modelo.

- [x] Implementar leitura de PDFs com texto extraível no serviço local
- [x] Identificar PDFs sem conteúdo textual
- [x] Não tratar falha de extração como ausência de informação
- [x] Converter/normalizar conteúdo para Markdown
- [x] Gerar representação Markdown com `## Página N`
- [x] Preservar metadados básicos, hash e versão do conversor
- [x] Criar contrato HTTP `/healthz` e `/v1/convert`
- [x] Implantar o serviço no Docker da VPS
- [ ] Persistir o Markdown no Google Drive
- [ ] Validar documentos de exemplo

**Observação:** OCR comercial pago está fora do escopo inicial.

**Gate de saída:** PDFs suportados geram conteúdo textual/Markdown consistente.

---

## 10. Fase 6 — Prompt e análise regulatória

**Objetivo:** produzir análise estruturada com IA local.

- [x] Criar prompt/contrato base versionado
- [x] Definir campos estruturados e schema JSON
- [x] Identificar status regulatório `deferido`, `indeferido`, `cancelado` e `outro`
- [x] Definir campos de medicamentos
- [x] Definir campos de suplementos alimentares
- [x] Definir campos de ensaios clínicos e tipo de produto relacionado
- [x] Identificar exigências
- [x] Identificar pendências
- [x] Definir política de evidência insuficiente
- [x] Definir controle de confiança
- [x] Definir regra de conteúdo contraditório
- [x] Definir regra de revisão humana
- [ ] Criar conjunto de documentos de validação

**Gate de saída:** saída estruturada consistente nos casos de referência.

---

## 11. Fase 7 — Relatório e PDF

**Objetivo:** transformar a análise em artefato final padronizado.

- [x] Definir template do relatório
- [x] Mapear dados estruturados para o relatório
- [x] Diferenciar campos encontrados, ausentes e inconclusivos
- [x] Gerar relatório
- [x] Converter relatório para PDF
- [x] Validar legibilidade do PDF
- [ ] Salvar PDF no Google Drive (aguarda credencial Google)
- [x] Associar relatório ao documento de origem

**Gate de saída:** um documento processado produz PDF final válido e armazenado.

---

## 12. Fase 8 — Gmail

**Objetivo:** entregar automaticamente o relatório.

- [ ] Configurar credenciais Gmail
- [ ] Definir remetente autorizado
- [ ] Definir destinatários/regras de destinatário
- [ ] Criar assunto e corpo padrão
- [ ] Anexar ou referenciar relatório conforme regra aprovada
- [ ] Enviar e-mail de teste
- [ ] Tratar falha de envio
- [ ] Impedir status `concluído` quando envio obrigatório falhar

**Gate de saída:** relatório de teste enviado com sucesso.

---

## 13. Fase 9 — Tratamento de erros e revisão humana

**Objetivo:** impedir falhas silenciosas e resultados inseguros.

- [x] Classificar tipos de erro
- [x] Implementar log mínimo por execução
- [x] Criar caminho de retry
- [x] Criar caminho de revisão humana
- [x] Criar status de baixa confiança
- [x] Criar status de erro técnico
- [x] Garantir que erro não seja interpretado como dado ausente
- [ ] Validar comportamento de retomada

**Gate de saída:** falhas e ambiguidades possuem destino claro.

---

## 14. Fase 10 — Testes integrados

**Objetivo:** validar o fluxo ponta a ponta.

### Casos mínimos

- [x] Conversor: PDF textual simples
- [x] Conversor: PDF inválido
- [x] Conversor: PDF sem camada textual
- [x] API: health check e contrato de conversão
- [ ] PDF válido
- [ ] PDF com status regulatório
- [ ] PDF com medicamentos
- [ ] PDF com suplementos
- [ ] PDF com ensaios clínicos
- [ ] PDF de referência DOU com 128 páginas
- [ ] PDF de referência: medicamento deferido e indeferido
- [ ] PDF de referência: suplemento deferido, cancelado e ausência de indeferido
- [ ] PDF de referência: ensaio clínico relacionado a dispositivo
- [ ] PDF com exigências/pendências
- [ ] Informação ausente
- [ ] Baixa confiança
- [ ] Informação contraditória
- [ ] Falha de extração
- [ ] Falha do Ollama
- [ ] Falha de geração do PDF
- [ ] Falha no Drive
- [ ] Falha no Gmail
- [ ] Documento duplicado
- [ ] Reprocessamento autorizado

### Validação

- [x] Conferir contrato e erros do conversor local
- [ ] Conferir dados estruturados
- [ ] Conferir relatório
- [ ] Conferir PDF
- [ ] Conferir armazenamento
- [ ] Conferir envio
- [ ] Conferir logs
- [ ] Conferir revisão humana

**Gate de saída:** cenários críticos aprovados sem bloqueios de severidade alta.

---

## 15. Fase 11 — Documentação e entrega

**Objetivo:** deixar o sistema operável e rastreável.

- [ ] Atualizar `PRD.md` (sem mudança de requisito prevista; revisar no fechamento)
- [x] Atualizar `ROADMAP.md`
- [x] Consolidar `LOG.md`
- [ ] Revisar `AGENTS.md`
- [x] Documentar implantação
- [x] Documentar operação
- [x] Documentar credenciais necessárias sem expor segredos
- [x] Documentar backup
- [x] Documentar recuperação
- [x] Documentar modelo Ollama utilizado após benchmark na VPS
- [x] Documentar workflow final
- [x] Documentar serviço PDF → Markdown e gate n8n
- [ ] Entregar arquivos e acessos definidos
- [ ] Executar validação final

**Gate de saída:** operação pode ser entendida por outro responsável técnico sem depender exclusivamente do desenvolvedor original.

---

## 16. Fase 12 — Pós-entrega / backlog

Itens possíveis, mas fora do escopo inicial ou dependentes de nova aprovação:

- [ ] OCR pago
- [ ] painel administrativo
- [ ] aplicativo mobile
- [ ] fine-tuning
- [ ] modelo proprietário
- [ ] novas integrações
- [ ] observabilidade avançada
- [ ] métricas e dashboard
- [ ] filas dedicadas
- [ ] alta disponibilidade
- [ ] escalabilidade horizontal

Nenhum item deste bloco deve entrar no desenvolvimento automaticamente.

---

## 17. Bloqueios externos

Registrar aqui bloqueios que dependem do cliente ou terceiros.

| ID | Bloqueio | Responsável | Status | Impacto |
|---|---|---|---|---|
| EXT-001 | Acesso à VPS | Cliente | DONE | VPS auditada; implantação em andamento |
| EXT-002 | Acesso/credencial Google Drive | Cliente | TODO | Bloqueia integração |
| EXT-003 | Acesso/credencial Gmail | Cliente | TODO | Bloqueia envio |
| EXT-004 | PDFs reais/de exemplo | Cliente | DONE | Documentos recebidos; validação técnica segue na Fase 10 |
| EXT-005 | Definição dos destinatários | Cliente | TODO | Bloqueia regra de envio |

---

## 18. Marcos

| Marco | Resultado esperado | Status |
|---|---|---|
| M1 | Governança criada | DONE |
| M2 | Ambiente Docker + n8n + Ollama operacional | DONE |
| M3 | Entrada pelo Drive funcionando | TODO |
| M4 | Extração + Markdown funcionando | TODO |
| M5 | Análise estruturada funcionando | TODO |
| M6 | Relatório + PDF funcionando | TODO |
| M7 | Gmail funcionando | TODO |
| M8 | Revisão humana + erros funcionando | TODO |
| M9 | Testes ponta a ponta aprovados | TODO |
| M10 | Documentação e entrega | TODO |

---

## 19. Regra de atualização deste roadmap

Ao concluir uma atividade:

1. marcar o item;
2. atualizar o status da fase;
3. registrar decisão relevante no `LOG.md`;
4. adicionar novos bloqueios, se surgirem;
5. não apagar itens históricos — usar `CANCELLED` quando removidos do escopo.

Este arquivo deve refletir a realidade do projeto, e não apenas a intenção inicial.
