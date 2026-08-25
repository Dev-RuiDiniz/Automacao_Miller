# ROADMAP.md — Acompanhamento do Projeto

## 1. Projeto

**Nome:** Agente de Automação e Análise Regulatória  
**Stack principal:** n8n + Ollama + Google Drive + Gmail + Docker + Linux  
**Prazo comercial de referência:** até 10 dias úteis, contado após aprovação, pagamento da entrada, disponibilização dos acessos e arquivos de exemplo.

> Este roadmap é o documento operacional de acompanhamento. Datas devem ser atualizadas conforme o início real do projeto e os bloqueios encontrados.

---

## 2. Status geral

**Estado atual:** Planejamento / preparação para implantação  
**MVP:** definido  
**Infraestrutura:** definida em nível de proposta  
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
- [ ] Criar `.gitignore`
- [ ] Criar `.env.example`
- [ ] Definir estrutura de diretórios
- [ ] Confirmar arquivos PDF de referência para testes
- [ ] Confirmar responsáveis por validação

**Gate de saída:** governança versionada e acessos mínimos identificados.

---

## 5. Fase 1 — Infraestrutura base

**Objetivo:** preparar o ambiente Linux para execução do sistema.

- [ ] Provisionar/confirmar VPS
- [ ] Atualizar sistema operacional
- [ ] Configurar usuário administrativo adequado
- [ ] Configurar firewall e acesso SSH
- [ ] Instalar Docker
- [ ] Instalar Docker Compose, se utilizado
- [ ] Criar estrutura persistente de volumes
- [ ] Configurar política de restart
- [ ] Definir backup das configurações
- [ ] Validar recursos disponíveis da VPS

**Referência de infraestrutura:**

- 2 vCPU
- 8 GB RAM
- 100 GB NVMe
- Linux

**Gate de saída:** Docker funcional, armazenamento persistente e acesso seguro ao servidor.

---

## 6. Fase 2 — n8n

**Objetivo:** disponibilizar a camada de orquestração.

- [ ] Implantar n8n self-hosted
- [ ] Configurar persistência
- [ ] Configurar credenciais fora do código
- [ ] Validar acesso ao painel
- [ ] Definir workflow principal
- [ ] Definir tratamento de erros
- [ ] Definir estratégia de retry
- [ ] Definir rastreabilidade por documento

**Gate de saída:** n8n estável e pronto para receber integrações.

---

## 7. Fase 3 — Ollama

**Objetivo:** disponibilizar IA local compatível com a VPS.

- [ ] Instalar Ollama
- [ ] Selecionar modelo inicial leve e quantizado
- [ ] Registrar modelo e versão no `LOG.md`
- [ ] Validar memória e CPU
- [ ] Executar teste básico de inferência
- [ ] Medir tempo aproximado de resposta
- [ ] Definir timeout do workflow
- [ ] Validar chamada do Ollama a partir do n8n

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

- [ ] Implementar leitura de PDFs com texto extraível
- [ ] Identificar PDFs sem conteúdo textual
- [ ] Não tratar falha de extração como ausência de informação
- [ ] Converter/normalizar conteúdo
- [ ] Gerar representação Markdown
- [ ] Preservar metadados básicos do documento
- [ ] Validar documentos de exemplo

**Observação:** OCR comercial pago está fora do escopo inicial.

**Gate de saída:** PDFs suportados geram conteúdo textual/Markdown consistente.

---

## 10. Fase 6 — Prompt e análise regulatória

**Objetivo:** produzir análise estruturada com IA local.

- [ ] Criar prompt base
- [ ] Definir campos estruturados
- [ ] Identificar status regulatório
- [ ] Identificar medicamentos
- [ ] Identificar suplementos alimentares
- [ ] Identificar ensaios clínicos
- [ ] Identificar exigências
- [ ] Identificar pendências
- [ ] Definir política de evidência insuficiente
- [ ] Definir controle de confiança
- [ ] Definir regra de conteúdo contraditório
- [ ] Definir regra de revisão humana
- [ ] Criar conjunto de documentos de validação

**Gate de saída:** saída estruturada consistente nos casos de referência.

---

## 11. Fase 7 — Relatório e PDF

**Objetivo:** transformar a análise em artefato final padronizado.

- [ ] Definir template do relatório
- [ ] Mapear dados estruturados para o relatório
- [ ] Diferenciar campos encontrados, ausentes e inconclusivos
- [ ] Gerar relatório
- [ ] Converter relatório para PDF
- [ ] Validar legibilidade do PDF
- [ ] Salvar PDF no Google Drive
- [ ] Associar relatório ao documento de origem

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

- [ ] Classificar tipos de erro
- [ ] Implementar log mínimo por execução
- [ ] Criar caminho de retry
- [ ] Criar caminho de revisão humana
- [ ] Criar status de baixa confiança
- [ ] Criar status de erro técnico
- [ ] Garantir que erro não seja interpretado como dado ausente
- [ ] Validar comportamento de retomada

**Gate de saída:** falhas e ambiguidades possuem destino claro.

---

## 14. Fase 10 — Testes integrados

**Objetivo:** validar o fluxo ponta a ponta.

### Casos mínimos

- [ ] PDF válido
- [ ] PDF com status regulatório
- [ ] PDF com medicamentos
- [ ] PDF com suplementos
- [ ] PDF com ensaios clínicos
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

- [ ] Atualizar `PRD.md`
- [ ] Atualizar `ROADMAP.md`
- [ ] Consolidar `LOG.md`
- [ ] Revisar `AGENTS.md`
- [ ] Documentar implantação
- [ ] Documentar operação
- [ ] Documentar credenciais necessárias sem expor segredos
- [ ] Documentar backup
- [ ] Documentar recuperação
- [ ] Documentar modelo Ollama utilizado
- [ ] Documentar workflow final
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
| EXT-001 | Acesso à VPS | Cliente | TODO | Bloqueia infraestrutura |
| EXT-002 | Acesso/credencial Google Drive | Cliente | TODO | Bloqueia integração |
| EXT-003 | Acesso/credencial Gmail | Cliente | TODO | Bloqueia envio |
| EXT-004 | PDFs reais/de exemplo | Cliente | TODO | Bloqueia validação |
| EXT-005 | Definição dos destinatários | Cliente | TODO | Bloqueia regra de envio |

---

## 18. Marcos

| Marco | Resultado esperado | Status |
|---|---|---|
| M1 | Governança criada | DONE |
| M2 | Ambiente Docker + n8n + Ollama operacional | TODO |
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
