# Workflows n8n

## Fluxo ativo

A origem oficial de novos documentos é a landing privada. Importe e mantenha
inativos até a validação no n8n:

1. `automacao-regulatoria-internal-v1.json` — recebe o protocolo, reivindica o
   documento no PostgreSQL, lê o PDF do volume, converte, analisa, grava os
   artefatos, envia o relatório por Gmail e atualiza o status;
2. `automacao-regulatoria-internal-reconcile-v1.json` — recupera documentos
   presos em processamento e redispara pendências;
3. `automacao-regulatoria-internal-error-v1.json` — registra categoria, etapa,
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
`human_reviews` e `workflow_errors`. Os workflows devem gravar somente chaves
relativas, nunca caminhos absolutos.

Associe no n8n apenas as credenciais PostgreSQL e Gmail. Nenhum ID de credencial
é versionado neste repositório. A variável `ARTIFACTS_GID` deve representar o
grupo compartilhado que permite ao gateway e ao n8n ler e gravar no volume.

## Reprocessamento e revisão

A deduplicação é feita pelo SHA-256 no gateway e reforçada pela restrição única
do PostgreSQL. Para autorizar reprocessamento, registre a decisão em
`human_reviews`, mantenha o PDF no volume e devolva o documento ao estado
`recebido`; o workflow de reconciliação fará o despacho pelo webhook interno.

Resultados com baixa confiança, contradição ou evidência insuficiente ficam em
`aguardando_revisao`. O relatório pode ser gerado para análise humana, mas o
download público só é liberado quando o PostgreSQL indicar `concluido`.

## Documentos extensos

Para documentos com mais de 20 páginas, a análise usa o recorte configurado no
workflow e registra a necessidade de revisão humana. O Markdown integral
continua preservado no volume e relacionado ao documento no PostgreSQL.

## Operação

Configure `LANDING_ACCESS_TOKEN`, `INTERNAL_API_TOKEN`,
`N8N_INTERNAL_PROCESSING_WEBHOOK_URL`, `ARTIFACT_STORAGE_DIR` e
`UPLOAD_GATEWAY_BASE_URL` no ambiente protegido. Gmail e PostgreSQL devem ser
associados após a importação dos exports.

Para consultar ou reprocessar, use o protocolo e as tabelas internas. Não use
pastas do Drive para representar estados. Arquivos antigos do Drive não são
apagados automaticamente e só podem entrar por procedimento de importação
controlada futuro.
