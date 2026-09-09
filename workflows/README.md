# Workflows n8n

## Importacao

Na homologação vigente, importe primeiro `automacao-regulatoria-v1.json` e
depois `automacao-regulatoria-error-v1.json` no n8n local. Esses exports ainda
usam o Google Drive para entrada, movimentação e armazenamento de artefatos.
O workflow principal deve permanecer inativo até que as credenciais Google
Drive, Gmail e PostgreSQL sejam associadas aos nós correspondentes.

A arquitetura aprovada para a próxima implementação usará o PostgreSQL como
fonte de verdade e o volume privado do Docker como repositório dos arquivos.
Os workflows atuais não devem ser considerados migrados enquanto essa etapa
estiver pendente.

Associe o workflow de erro ao workflow principal nas configuracoes do n8n.
Nenhum ID de credencial e versionado neste repositorio.

## Credenciais necessarias

- Google Drive OAuth2 para a homologação vigente e a importação temporária.
- Gmail OAuth2 para envio do relatorio.
- PostgreSQL para a tabela `automacao_miller.document_processing`.
- PostgreSQL para a tabela `automacao_miller.workflow_errors`.
- Volume privado compartilhado para PDFs, Markdown e relatórios após a migração.

## Reprocessamento autorizado

O controle de duplicidade ignora um documento com o mesmo ID e SHA-256 já
concluído. Na homologação vigente, o reprocessamento autorizado devolve o
arquivo para a pasta Entrada do Drive. Após a migração, o operador deverá
alterar o registro interno para `aguardando_revisao` e
`reprocessamento_autorizado`, mantendo o arquivo no volume privado. O histórico
permanece no banco; nenhuma senha ou credencial deve ser registrada no Git.

## Documentos extensos

Na homologação vigente, o Markdown integral continua sendo salvo no Drive. Após
a migração, ele será salvo no volume privado e registrado no PostgreSQL. Para documentos com mais de
20 paginas, a primeira analise do modelo usa as paginas 71-75 e 79 definidas
para a homologacao. Esse recorte e marcado como baixa confianca e exige
revisao humana; ele nao autoriza status concluido. O relatorio e o e-mail
continuam sendo gerados para permitir a revisao.

## Compatibilidade n8n

O export versionado não inclui IDs de credenciais. Depois de importar ou
atualizar o workflow vigente, associe novamente as credenciais Google Drive,
Gmail e PostgreSQL no n8n. Na versão homologada do n8n, o Drive usa fileFolder para
busca, folderId e inputDataFieldName para upload, e o Gmail usa
options.attachmentsUi.attachmentsBinary.

## Landing privada

Importe `automacao-regulatoria-intake-v1.json` e
`automacao-regulatoria-completion-v1.json`. O intake atual salva o PDF recebido
na pasta de entrada do Drive e o workflow de conclusão consulta o vínculo por
SHA-256, copia o relatório para o volume compartilhado e atualiza o protocolo
da landing. Na arquitetura aprovada, o intake deverá persistir diretamente no
volume privado e no PostgreSQL, sem usar pastas do Drive para representar
estados. Mantenha ambos inativos até associar as credenciais e configurar
`LANDING_ACCESS_TOKEN`, `INTERNAL_API_TOKEN` e as URLs internas no ambiente.

A landing possui uma página de acesso com usuário e senha. Configure
`LANDING_USERNAME`, `LANDING_PASSWORD_HASH` e `AUTH_SESSION_SECRET` somente na
VPS; a senha é verificada por hash e a sessão usa cookie `HttpOnly`. O acesso
por token continua disponível para compatibilidade e testes automatizados.
