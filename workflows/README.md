# Workflows n8n

## Importacao

Importe primeiro `automacao-regulatoria-v1.json` e depois
`automacao-regulatoria-error-v1.json` no n8n local. O workflow principal deve
permanecer inativo ate que as credenciais Google Drive, Gmail e PostgreSQL
sejam associadas aos nos correspondentes.

Associe o workflow de erro ao workflow principal nas configuracoes do n8n.
Nenhum ID de credencial e versionado neste repositorio.

## Credenciais necessarias

- Google Drive OAuth2 para busca, download, upload e movimentacao de arquivos.
- Gmail OAuth2 para envio do relatorio.
- PostgreSQL para a tabela `automacao_miller.document_processing`.
- PostgreSQL para a tabela `automacao_miller.workflow_errors`.

## Reprocessamento autorizado

O controle de duplicidade ignora um documento com o mesmo ID e SHA-256 ja
concluido. Para reprocessar, o operador deve remover o registro correspondente
da tabela de rastreabilidade somente com autorizacao registrada e executar
novamente o documento. O registro removido e a autorizacao devem ser mantidos
no log operacional fora do Git.
