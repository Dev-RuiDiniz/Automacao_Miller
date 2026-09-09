# ROADMAP.md — Acompanhamento do Projeto

## 1. Projeto

**Nome:** Agente de Automação e Análise Regulatória  
**Stack principal:** n8n + Ollama + PostgreSQL + volume privado Docker + Gmail
**Prazo comercial de referência:** até 10 dias úteis, contado após aprovação, pagamento da entrada, disponibilização dos acessos e arquivos de exemplo.

> Este roadmap é o documento operacional de acompanhamento. Datas devem ser atualizadas conforme o início real do projeto e os bloqueios encontrados.

---

## 2. Status geral

**Estado atual:** homologação ponta a ponta aprovada; repositório interno e painel publicados; workflows internos ativos; produção permanece condicionada à revisão de segurança e ao aceite operacional final
**MVP:** definido  
**Infraestrutura:** VPS auditada; stack Docker isolada implantada em `/opt/automacao-miller`
**Dependências externas:** acessos do cliente, Gmail, VPS e arquivos de exemplo
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

**Status da fase:** preparação interna concluída. Os acessos de homologação foram validados; permanecem pendências de segurança, revisão humana e simulação de falhas.

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
- [x] Configurar credenciais fora do código
- [x] Validar acesso ao painel
- [x] Definir workflow principal
- [x] Definir tratamento de erros
- [x] Definir estratégia de retry
- [x] Definir rastreabilidade por documento
- [x] Integrar gate HTTP PDF → Markdown
- [x] Persistir Markdown no Google Drive antes da extração na homologação histórica
- [x] Impedir chamada ao Ollama antes da conversão validada

**Gate de saída:** n8n estável e pronto para receber integrações.

## Fase 2B — Repositório interno de documentos

**Objetivo:** substituir a organização operacional por pastas do Google Drive por
um repositório interno controlado pelo PostgreSQL e por volume privado do Docker.

- [x] Aprovar PostgreSQL como fonte de verdade operacional
- [x] Aprovar volume privado como armazenamento de PDFs e artefatos
- [x] Criar modelo de documentos, artefatos, tentativas, análises, revisões e erros
- [x] Criar volume `automacao_miller_artifacts_data` em `/data/artifacts`
- [x] Persistir PDF original, Markdown, análise JSON e relatório no volume interno
- [x] Alterar o gateway para hash, deduplicação e chaves relativas
- [x] Alterar o n8n para reivindicar documentos pendentes no PostgreSQL
- [x] Remover o Drive dos workflows ativos; exports antigos permanecem históricos
- [x] Criar reconciliação de documentos presos e workflow de erros interno
- [x] Criar rotina de backup conjunto e migração controlada do volume antigo
- [x] Validar upload, reprocessamento, revisão e download no repositório interno
- [x] Executar backup e cópia dos dados na VPS de homologação
- [x] Ativar workflows internos após associação das credenciais e desativação dos históricos

**Gate de saída:** o processamento completo ocorre sem depender do Google Drive
para armazenar ou organizar os arquivos.

**Status da fase:** concluída em homologação. O processamento interno, a
reconciliação, o tratamento de erros, o backup conjunto e a preservação do
volume legado foram validados.

## Fase 2A — Landing e gateway de upload

**Objetivo:** oferecer entrada privada por navegador, protocolo assíncrono e
download controlado do relatório.

- [x] Criar landing responsiva com seleção e arrastar/soltar
- [x] Criar API de upload, status e download
- [x] Validar token privado e token interno separado
- [x] Calcular SHA-256 e impedir duplicidade acidental
- [x] Persistir uploads e relatórios no volume privado dedicado
- [x] Criar workflow n8n de processamento iniciado pela landing
- [x] Criar workflow n8n de reconciliação e atualização de status
- [x] Criar página de acesso com usuário e senha
- [x] Criar sessão HttpOnly, expiração e logout
- [x] Configurar usuário, hash da senha e segredo da sessão no ambiente autorizado
- [x] Configurar tokens no ambiente autorizado
- [x] Configurar Caddy/HTTPS para a landing
- [x] Validar fluxo de homologação ponta a ponta

**Gate de saída:** um usuário autorizado consegue enviar um PDF, acompanhar o
protocolo e baixar o relatório final sem acesso às credenciais internas.

## Fase 2C — Painel operacional e envio manual

**Objetivo:** permitir que o operador autenticado acompanhe os protocolos,
confira os artefatos, mantenha destinatários e controle a entrega por Gmail.

- [x] Criar fila com indicadores, busca, filtros e estados vazios
- [x] Criar detalhe com metadados, linha do tempo, tentativas e erros
- [x] Criar visualização autenticada de PDF, Markdown e JSON
- [x] Criar cadastro de destinatários padrão e substituição por documento
- [x] Criar revisão humana com liberação ou reprocessamento
- [x] Criar tabelas de destinatários e entregas no PostgreSQL
- [x] Separar o envio manual em workflow n8n próprio
- [x] Bloquear download oficial antes da confirmação do Gmail
- [x] Aplicar schema e migrar destinatários na homologação
- [x] Validar envio real, falha, retry e auditoria no Gmail
- [x] Liberar o painel após backup e validação ponta a ponta em homologação

**Gate de saída:** operador autenticado consegue revisar um relatório, escolher
destinatários, solicitar uma única entrega, confirmar o resultado e baixar o
PDF somente após `concluido`.

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

## 8. Fase 4 — Integração Google Drive (histórico)

**Objetivo:** criar entrada automática e armazenamento dos resultados.

As atividades desta fase registram a integração validada na homologação
anterior. Os workflows desta fase estão inativos e não são origem, controle de
estado ou armazenamento dos fluxos atuais. O Drive não será usado para novos
documentos.

- [x] Configurar credenciais do Google Drive
- [x] Definir pasta de entrada
- [x] Definir pasta de processamento
- [x] Definir pasta de concluídos
- [x] Definir pasta de revisão
- [x] Definir pasta de erro
- [x] Configurar monitoramento de novos PDFs
- [x] Implementar controle contra duplicidade
- [x] Validar download do documento
- [x] Validar upload dos artefatos finais

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
- [x] Persistir o Markdown no Google Drive na homologação vigente
- [x] Persistir o Markdown no volume interno e registrar o artefato no PostgreSQL
- [x] Validar documentos de exemplo

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
- [x] Salvar PDF no Google Drive na homologação vigente
- [x] Salvar PDF no volume interno
- [x] Associar relatório ao documento de origem

**Gate de saída:** um documento processado produz PDF final válido e armazenado.

---

## 12. Fase 8 — Gmail

**Objetivo:** entregar o relatório mediante solicitação manual do operador.

- [x] Configurar credenciais Gmail
- [x] Definir remetente autorizado
- [x] Definir a estrutura de destinatários padrão e por documento
- [x] Criar assunto e corpo padrão
- [x] Anexar ou referenciar relatório conforme regra aprovada
- [x] Enviar e-mail de teste
- [ ] Tratar falha de envio
- [x] Impedir status `concluído` quando o envio solicitado falhar

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
- [x] PDF válido
- [ ] PDF com status regulatório
- [ ] PDF com medicamentos
- [ ] PDF com suplementos
- [ ] PDF com ensaios clínicos
- [x] PDF de referência DOU com 128 páginas
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
- [ ] Falha no armazenamento interno
- [ ] Falha no Gmail
- [ ] Documento duplicado
- [ ] Reprocessamento autorizado
- [ ] Entrada pela landing privada
- [ ] Atualização de status e download do relatório pela landing

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

- [x] Atualizar `PRD.md` com a decisão landing-only e repositório interno
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
- [x] Executar validação final técnica; aceite regulatório do DOU permanece em revisão humana

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
| EXT-002 | Acesso/credencial Google Drive | Cliente | DONE | OAuth validado e credencial configurada |
| EXT-003 | Acesso/credencial Gmail | Cliente | DONE | OAuth validado e envio testado |
| EXT-004 | PDFs reais/de exemplo | Cliente | DONE | Documentos recebidos; validação técnica segue na Fase 10 |
| EXT-005 | Definição dos destinatários | Cliente | DONE | Destinatário de homologação configurado |

---

## 18. Marcos

| Marco | Resultado esperado | Status |
|---|---|---|
| M1 | Governança criada | DONE |
| M2 | Ambiente Docker + n8n + Ollama operacional | DONE |
| M3 | Entrada pelo Drive funcionando na homologação histórica | DONE |
| M4 | Extração + Markdown funcionando | DONE |
| M5 | Análise estruturada funcionando | DONE |
| M6 | Relatório + PDF funcionando | DONE |
| M7 | Gmail funcionando na homologação histórica | DONE |
| M8 | Revisão humana + erros funcionando | DONE |
| M9 | Testes ponta a ponta aprovados em homologação | DONE |
| M10 | Documentação e entrega | DONE |
| M11 | Repositório interno landing-only implementado | DONE |
| M12 | Painel operacional e envio manual implementados | DONE |

## 19. Homologação operacional concluída — 2026-09-09

Validações realizadas na VPS de homologação:

- [x] Upload de PDF válido, protocolo, hash e deduplicação.
- [x] Processamento interno com PostgreSQL e volume privado, incluindo PDF,
  Markdown, análise JSON e relatório PDF.
- [x] Visualização autenticada dos artefatos e bloqueio do download antes de
  `concluido`.
- [x] Revisão humana, liberação para envio e histórico de tentativas/erros.
- [x] Envio manual real pelo Gmail, registro de falha, retry e sucesso.
- [x] Bloqueio de duas solicitações de envio concorrentes.
- [x] Webhook repetido sem criação de processamento concorrente duplicado.
- [x] PDF inválido rejeitado com erro de entrada.
- [x] Backup conjunto do PostgreSQL e do volume; manifesto, hashes, permissões,
  preservação do volume legado e leitura isolada dos arquivos de restauração
  conferidos.

Antes da ativação em produção ainda devem ser tratados o hardening do acesso
administrativo da VPS, o aceite formal do operador e a definição do procedimento
de restauração em janela de manutenção.

---

## 20. Regra de atualização deste roadmap

Ao concluir uma atividade:

1. marcar o item;
2. atualizar o status da fase;
3. registrar decisão relevante no `LOG.md`;
4. adicionar novos bloqueios, se surgirem;
5. não apagar itens históricos — usar `CANCELLED` quando removidos do escopo.

Este arquivo deve refletir a realidade do projeto, e não apenas a intenção inicial.

## 22. Documento real validado com revisão pendente — 2026-09-09

- [x] Receber o PDF real pela landing e preservar o original no volume interno.
- [x] Converter o documento de 128 páginas para Markdown com 1.585.605 bytes.
- [x] Gerar e persistir análise JSON e relatório PDF após correção do contexto do
      Ollama e da validação do schema.
- [x] Abrir e validar visualmente o relatório PDF gerado.
- [x] Bloquear o download oficial enquanto o documento não estiver concluído.
- [x] Classificar o resultado como `baixa_confianca` quando houver ocorrências
      sem evidência de página.
- [ ] Executar a revisão humana das classificações e evidências do documento real.
- [ ] Validar o envio manual e o download oficial após a revisão aprovada.
## 20. Fechamento da homologacao - 2026-08-26

Estado atualizado: stack Docker isolada operacional em /opt/automacao-miller,
n8n local em 127.0.0.1:25678, PostgreSQL proprio, Ollama qwen2.5:3b,
conversor e renderizador saudaveis. OAuth Drive/Gmail, pastas, destinatario,
credencial PostgreSQL e workflow de erros configurados fora do Git.

Concluido e validado:

- [x] PDF simples ponta a ponta, com Markdown e relatorio salvos no Drive.
- [x] PDF simples enviado ao Gmail com anexo PDF.
- [x] Status simples concluido gravado como email_enviado somente apos envio.
- [x] DOU convertido integralmente com page_count 128; paginas 71-75 e 79
      presentes no Markdown e conferidas por marcadores de conteudo.
- [x] DOU com relatorio PDF salvo no Drive e enviado ao Gmail com anexo.
- [x] DOU encaminhado para aguardando_revisao e pasta Revisao, pois o modelo
      retornou estrutura generica e a politica de confianca impediu conclusao.
- [x] Duplicidade bloqueada por documento/hash, com reprocessamento operacional
      autorizado sem apagar o historico.
- [x] Export versionado sem credenciais; credenciais permanecem somente no n8n/VPS.

Pendencias reais:

- [ ] Rotacionar imediatamente a senha root exposta e validar chave SSH alternativa.
- [ ] Executar a revisao humana do DOU e validar classificacoes e evidencias.
- [ ] Ajustar a inferencia para classificacao completa de documentos extensos.
- [ ] Simular falhas de Drive, Gmail, Ollama, PDF e renderizador e validar workflow_errors.
- [ ] Validar retomada apos falha e manter autorizacao de reprocessamento no log operacional.

## 21. Ativação do acesso da landing - 2026-09-08

Estado atualizado: login por usuário e senha configurado na VPS, com sessão
segura em HTTPS e compatibilidade mantida para o token legado.

Concluído e validado:

- [x] Credenciais aleatórias de homologação geradas e entregues em arquivo local protegido.
- [x] `.env` da VPS atualizado com backup restrito anterior à alteração.
- [x] Gateway reconstruído no commit `de93fb9`.
- [x] Login, sessão, logout e bloqueio pós-logout validados pelo domínio HTTPS.
- [x] n8n, gateway, conversor, renderer, PostgreSQL e Ollama saudáveis.

Pendências reais:

- [ ] Executar upload de um PDF de teste autorizado pela landing.
- [ ] Confirmar protocolo, processamento, relatório e download pela interface.
- [ ] Executar os cenários de falha externa e retomada já previstos.
