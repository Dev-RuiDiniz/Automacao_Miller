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
concluido. Para reprocessar, o operador deve registrar a autorizacao no log
operacional, alterar o registro para status aguardando_revisao e etapa
reprocessamento_autorizado, devolver o arquivo para Entrada e executar
novamente. O historico permanece no banco; nenhuma senha ou credencial deve
ser registrada no Git.

## Documentos extensos

O Markdown integral continua sendo salvo no Drive. Para documentos com mais de
20 paginas, a primeira analise do modelo usa as paginas 71-75 e 79 definidas
para a homologacao. Esse recorte e marcado como baixa confianca e exige
revisao humana; ele nao autoriza status concluido. O relatorio e o e-mail
continuam sendo gerados para permitir a revisao.

## Compatibilidade n8n

O export versionado nao inclui IDs de credenciais. Depois de importar ou
atualizar o workflow, associe novamente as credenciais Google Drive, Gmail e
PostgreSQL no n8n. Na versao homologada do n8n, o Drive usa fileFolder para
busca, folderId e inputDataFieldName para upload, e o Gmail usa
options.attachmentsUi.attachmentsBinary.
