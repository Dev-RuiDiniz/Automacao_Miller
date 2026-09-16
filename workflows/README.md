# Workflows n8n

## Fluxo ativo

A origem oficial de novos documentos é a landing privada. Importe e mantenha
inativos até a validação no n8n:

1. `automacao-regulatoria-internal-v1.json` — recebe o protocolo, reivindica o
   documento no PostgreSQL, lê o PDF do volume, converte, analisa, grava os
   artefatos e deixa o documento em `aguardando_envio`, com alertas de qualidade
   e referências para conferência opcional;
2. `automacao-regulatoria-send-report-v1.json` — recebe a solicitação manual do
   painel, reivindica a entrega, lê o relatório do volume, envia pelo Gmail e
   marca `concluido` somente após sucesso;
3. `automacao-regulatoria-internal-reconcile-v1.json` — recupera documentos
   presos em processamento e redispara pendências;
4. `automacao-regulatoria-internal-error-v1.json` — registra categoria, etapa,
   execução, tentativa e mensagem no PostgreSQL.

Os exports `automacao-regulatoria-v1.json`, `automacao-regulatoria-intake-v1.json`,
`automacao-regulatoria-completion-v1.json` e
`automacao-regulatoria-error-v1.json` são históricos da homologação com Google
Drive. Permanecem versionados e inativos para auditoria e rollback, sem serem
parte do fluxo ativo.

## Repositório interno

O gateway e o n8n compartilham `/data/artifacts`, proveniente do volume Docker
`automacao_miller_artifacts_data`. A organização é determinística por SHA-256:

```text
/data/artifacts/objects/ab/cd/<sha256>/
  original.pdf
  markdown-v1.md
  analysis-v1.json
  report-v1.pdf
```

O PostgreSQL é a fonte de verdade. As tabelas principais são
`documents`, `artifacts`, `processing_attempts`, `analysis_results`,
`human_reviews`, `workflow_errors`, `report_recipients`, `document_recipients` e
`email_deliveries`. Os workflows devem gravar somente chaves
relativas, nunca caminhos absolutos.

Associe no n8n apenas as credenciais PostgreSQL e Gmail. Nenhum ID de credencial
é versionado neste repositório. A variável `ARTIFACTS_GID` deve representar o
grupo compartilhado que permite ao gateway e ao n8n ler e gravar no volume.
Além das permissões do volume, o n8n deve receber
`N8N_RESTRICT_FILE_ACCESS_TO=/data/artifacts`, que libera os nós de arquivo
somente dentro do repositório privado compartilhado.

## Reprocessamento e conferência opcional

A deduplicação é feita pelo SHA-256 no gateway e reforçada pela restrição única
do PostgreSQL. Para autorizar reprocessamento, registre a decisão em
`human_reviews`, mantenha o PDF no volume e devolva o documento ao estado
`recebido`; o workflow de reconciliação fará o despacho pelo webhook interno.

Resultados com baixa confiança, contradição ou evidência insuficiente seguem em
`aguardando_envio` com o alerta preservado no relatório. O download oficial só é
liberado quando o PostgreSQL indicar `concluido`. O operador pode visualizar o
PDF, Markdown e JSON pelo painel autenticado e confirmar as páginas quando
desejar, mas essa conferência não é obrigatória para solicitar o envio.

O PDF é apresentado como relatório executivo: começa com resumo dos achados,
leitura prática para acompanhamento operacional e comercial, pontos de atenção
e próximos passos. As seções detalhadas continuam exibindo os dados extraídos e
as evidências de página disponíveis; a linguagem comercial não substitui a
conferência opcional do documento original.
Cada achado exibe suas páginas de origem. Se a IA não conseguir comprovar a
referência, o relatório mostra essa pendência de forma explícita e mantém o caso
disponível para conferência, sem inventar a numeração da página.

## Painel e envio manual

O gateway oferece `/upload` para a fila, `/new` para upload,
`/submissions/{id}/view` para o detalhe e `/settings/recipients` para a lista
de destinatários. As APIs autenticadas mantêm os destinatários padrão e o
snapshot específico de cada envio no PostgreSQL. O workflow de envio recebe
`submission_id` e `delivery_id`; não consulta pastas do Drive e não usa
`REPORT_RECIPIENTS` como fonte operacional.

## Documentos extensos

Para documentos com mais de 20 páginas, a análise usa o recorte configurado no
workflow e registra o recorte e suas limitações. O Markdown integral
continua preservado no volume e relacionado ao documento no PostgreSQL.

## Operação

Configure `LANDING_ACCESS_TOKEN`, `INTERNAL_API_TOKEN`,
`N8N_INTERNAL_PROCESSING_WEBHOOK_URL`, `ARTIFACT_STORAGE_DIR` e
`UPLOAD_GATEWAY_BASE_URL` no ambiente protegido. Gmail e PostgreSQL devem ser
associados após a importação dos exports.

Para consultar ou reprocessar, use o painel, o protocolo e as tabelas internas. Não use
pastas do Drive para representar estados. Arquivos antigos do Drive não são
apagados automaticamente e só podem entrar por procedimento de importação
controlada futuro.

## RAG e validação de citações — capacidade opcional, fora do fluxo ativo

**Nota de vigência:** os parágrafos abaixo descrevem a capacidade legada de RAG
e não o caminho operacional atual. O workflow ativo não chama esse serviço, não
gera JSON estruturado e não cria `quality_checks`; ele usa o fluxo linear descrito
acima.

Depois de persistir o Markdown, o workflow chama o serviço interno
`RAG_SERVICE_BASE_URL` para indexar chunks por página, executar busca híbrida e
registrar os chunks recuperados. O contexto enviado ao Ollama contém o marcador
`## Página N`, o protocolo e a instrução de copiar evidência curta.

O nó `RAG - Validate citations` confere o resultado contra os chunks do mesmo
documento, incluindo páginas existentes, trecho literal normalizado, status
permitido e classificação de dispositivos. O resultado segue com avisos e
limitações quando houver falha de qualidade, sem bloquear a disponibilização do
relatório quando não houver falha técnica.

O contrato histórico de análise estruturada é o `regulatory-extraction-v3`. O
contrato ativo é o `regulatory-extraction-v4`, orientado a inteligência
regulatória e impacto de mercado. Ele responde, em ordem, a nove perguntas:
o que aconteceu; quem é afetado; qual é o status regulatório; qual é o impacto
direto no negócio; qual é o impacto potencial de mercado; se existe urgência ou
prazo; o que a empresa deve fazer agora; o que ainda não foi comprovado; e qual
é a prioridade executiva. O Ollama retorna Markdown com seções obrigatórias,
plano de ação e referências de páginas. A análise não é parecer regulatório
definitivo e a conferência humana é opcional.

Para reconstruir a base de embeddings, execute a indexação somente para os
Markdowns já persistidos e mantenha os workflows antigos do Drive inativos.

## Fluxo simplificado vigente

O workflow interno ativo segue uma cadeia linear para reduzir latência e
instabilidades em documentos extensos:

```text
PDF -> Markdown com marcadores de página -> prompt do especialista sênior
    -> relatório Markdown -> PDF comercial -> aguardando_envio
```

O artefato `report_markdown` é preservado junto do `report_pdf`. O prompt
`regulatory-extraction-v4` recebe um recorte compacto e rastreável do Markdown,
responde perguntas de negócio estabelecidas, produz somente Markdown e é
instruído a não inventar páginas ou fatos. JSON,
RAG, embeddings e `quality_checks` não são executados no caminho ativo; ficam
como capacidade legada/opcional. O envio, a reconciliação, o tratamento de erros
e o download oficial continuam operacionais.
