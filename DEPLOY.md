# Implantação da Automação Miller

## Checklist de liberação ao cliente

A instalação inicial foi verificada em 21/11/2026. A atualização para
download direto foi implantada e verificada na VPS em 23/11/2026.

### Concluído

- [x] Instalar o Miller na VPS do cliente e verificar os seis serviços Docker.
- [x] Publicar `reportai.info` com HTTPS e validar o redirecionamento de `www`.
- [x] Configurar o usuário `operador` e validar login, logout e acesso restrito.
- [x] Importar os quatro workflows inativos e vincular a credencial PostgreSQL.
- [x] Selecionar OpenRouter para o Anvisa V8 e preparar o comando de instalação da chave.
- [x] Instalar a chave da OpenRouter na VPS e verificar sua presença no renderizador saudável em 23/11/2026.
- [x] Criar o backup na VPS e conferir os hashes do banco e dos artefatos.
- [x] **Download direto.** Implantar `b006b7f`, aplicar a migração `006` e publicar as versões atualizadas dos workflows de processamento e de erros com a credencial PostgreSQL vinculada.
- [x] **n8n.** Verificar a execução contínua, o reinício automático e o acesso administrativo por túnel SSH.
- [x] **Novos uploads.** Liberar o acesso autenticado ao upload para o teste do cliente previsto para 24/11/2026.

### Pendente para concluir a homologação e a entrega

- [ ] **Teste final de análise.** Com autorização, enviar um PDF sintético pela landing. Conferir o protocolo, o Markdown paginado e persistido, a cobertura e as evidências do relatório, o PDF gerado e o status `concluido`.
- [ ] **Teste final de download.** Abrir o protocolo sintético autenticado e baixar o PDF pelo botão **Baixar relatório PDF**. Conferir a abertura do arquivo e o bloqueio sem sessão.
- [ ] **Falhas e retomada.** Verificar que falhas de conversão ou de análise interrompem o processamento na etapa correta. Testar a retomada e a prevenção de duplicidades antes de liberar reprocessamentos e reconciliação.
- [ ] **Protocolo do cliente no Anvisa V8.** Concluir o [checklist de migração e retomada](#migrar-o-checkpoint-anvisa-v8-antes-da-retomada), incluindo a conferência do checkpoint de destino, antes de autorizar o reprocessamento.
- [ ] **Recuperação.** Guardar uma cópia protegida do backup fora da VPS e testar a restauração em ambiente isolado.
- [ ] **Aceite.** Registrar os resultados dos testes finais e obter o aceite operacional antes de liberar o uso ao cliente.

## Estado verificado em 21/11/2026

| Item | Configuração da VPS do cliente |
| --- | --- |
| Hostinger | `srv2147368.hstgr.cloud`, IPv4 `2.25.172.95`, Ubuntu 26.04.1 LTS |
| Landing | [reportai.info](https://reportai.info/) com login e HTTPS pelo Caddy |
| DNS | Registro `A @` para `2.25.172.95`, TTL de 60 segundos. `www` é um CNAME para o domínio principal e recebe redirecionamento HTTPS |
| Código | `/opt/automacao-miller`, commit `3cac700` registrado em `DEPLOYED_COMMIT` |
| Docker | Engine 29.1.3 e Compose 2.40.3, projeto `automacao-miller` |
| Serviços | PostgreSQL, n8n, Ollama, conversor PDF, renderizador e gateway saudáveis |
| Portas locais na VPS | Gateway `127.0.0.1:8085` e n8n `127.0.0.1:25678` |
| Operação | Quatro workflows importados com PostgreSQL, todos inativos. Zero execuções e zero documentos |

O commit foi instalado a partir de um `git archive`. Use `DEPLOYED_COMMIT`
para identificar a versão no servidor. A fotografia da VPS de testes de
27/10/2026 está no [ROADMAP.md](ROADMAP.md).

Em 21/11 foram verificados certificado, redirecionamentos, acesso à área
privada, login, logout e cookie seguro. Os hashes dos backups do PostgreSQL e
dos artefatos foram conferidos.

## Atualização verificada em 23/11/2026

A VPS executa o commit `b006b7f` com a migração `006` aplicada. Os seis
serviços Docker estavam saudáveis. O n8n registrou o webhook de entrada,
as versões atuais de processamento e erros publicadas e zero execuções.
Os dez nós PostgreSQL desses dois workflows usam a credencial existente.

A página de novo upload foi liberada em 23/11, por autorização do usuário
para a simulação do cliente. A verificação confirmou HTTP `200` com a sessão
do operador e `403` sem sessão. O reprocessamento continua suspenso no
Caddy. Os backups anteriores à atualização estão em
`/opt/backups/automacao-miller/pre-b006b7f-20261124T020251Z`. A fotografia
anterior dos workflows está no arquivo `workflows.json` desse diretório.

## Atualização verificada em 25/11/2026

A VPS executa o commit `0894805` da `main`, com o hotfix de releitura do
Anvisa V8. A troca recriou somente o renderizador. Os seis serviços estavam
saudáveis e o webhook de entrada do n8n permaneceu registrado.

O checkpoint do protocolo interrompido foi migrado para a identidade nova,
com 7 lotes concluídos e 18 das 228 páginas concluídas. A conferência comparou
o estado completo de origem e destino e confirmou a integridade do original.
O login, a página de novo upload e o logout foram validados em HTTPS. Os
novos uploads voltaram à configuração anterior após a manutenção. A rota
pública de reprocessamento respondeu `503`. A retomada do documento depende
de autorização operacional.

O backup verificado está em
`/opt/backups/automacao-miller/pre-0894805-20261125T160734Z`. O diretório da
versão anterior para rollback é `/opt/automacao-miller-anterior-20261125T160734Z`.

## Revisão de segurança após a configuração

A revisão de 21/11/2026 usou consultas HTTPS sem credenciais e verificações
somente leitura na VPS do cliente, com o commit `3cac700` implantado.

- **Acesso público.** A página de login, o `/healthz` e os arquivos estáticos,
  incluindo o HTML do painel, responderam `200`. O HTML contém a estrutura da
  interface. A fila, os destinatários e as rotas de visualização e download de
  relatórios responderam `403` sem credenciais.
- **Serviços internos.** O Caddy devolveu `404` para as rotas internas e a
  documentação da API. O n8n e a porta direta do gateway estavam vinculados ao
  loopback da VPS. O n8n tinha quatro workflows importados, todos inativos.
- **PostgreSQL.** A porta `5432` estava sem publicação no host Docker e a
  tentativa de conexão externa expirou. O próprio host e o conversor PDF
  alcançaram a porta pela rede compartilhada da stack. As conexões por essa
  rede exigiam autenticação `SCRAM-SHA-256`. O gateway e o n8n usavam a mesma
  conta de superusuário. Uma credencial comprometida daria controle sobre toda
  a instância. [Configuração da stack](docker-compose.yml)

### Itens para avaliar após concluir a configuração

- [ ] **Isolar o PostgreSQL e reduzir privilégios.** Criar uma rede Docker para
  o banco e os serviços que precisam acessá-lo. Separar as contas do gateway e
  do n8n e conceder a cada uma apenas as permissões necessárias. Validar o
  processamento, a consulta e o download no painel com as novas contas.
- [ ] **Proteger o upload antes de ler o arquivo.** A versão do FastAPI
  implantada começa a processar o corpo antes de verificar a sessão e o Caddy
  ativo não aplicava limite de tamanho. Antecipar a autenticação e impor um
  limite ao corpo no proxy para reduzir o risco de indisponibilidade.
  [Gateway](infra/upload_gateway/app.py)
- [ ] **Revisar o token legado.** O token estava configurado e era aceito na
  URL. Esse uso pode deixar a credencial no histórico ou em logs. Confirmar
  se alguma integração depende dele e retirar o suporte pela URL.
  [Gateway](infra/upload_gateway/app.py)
- [ ] **Limitar tentativas de login.** O código do gateway e a configuração
  ativa do Caddy não apresentaram limite de tentativas. Aplicar o limite e
  conferir que o acesso legítimo continua funcionando.
- [ ] **Revalidar a exposição pública.** Após as mudanças, conferir o bloqueio
  das rotas privadas sem credenciais, a ausência de publicação da porta do
  PostgreSQL e a necessidade de manter o `/healthz` e o HTML do painel
  acessíveis publicamente.

## Acessos e arquivos locais

Use uma chave SSH autorizada com a identidade da VPS confirmada. A sessão
administrativa nesta implantação foi feita como `root`.

```bash
ssh root@2.25.172.95
cd /opt/automacao-miller
cat DEPLOYED_COMMIT
docker compose ps
```

- O `.env` contém as configurações e os segredos do ambiente e usa permissão
  `600`. O `docker-compose.override.yml` publica o gateway no loopback.
- O Caddy usa `/etc/caddy/Caddyfile`. O serviço encaminha a landing ao gateway
  e devolve `404` para as rotas internas e a documentação da API.
- A landing usa inicialmente o usuário `operador`. A senha inicial está em
  `/root/.automacao-miller-landing-inicial`, com permissão `600`. O administrador
  pode acessá-la pela sessão SSH e guardá-la no cofre aprovado.
- PostgreSQL, artefatos e diagnósticos usam volumes Docker persistentes. Mantenha
  a chave de criptografia do n8n no cofre administrativo para recuperação.
  Consulte [ACESSOS.md](ACESSOS.md).

## Configurar a chave OpenRouter e ativar o Anvisa V8

Em 23/11/2026, a presença da chave foi confirmada no renderizador antes e
depois da atualização para `b006b7f`. O `.env` manteve a permissão `600` e
o n8n está configurado para `openrouter`. Para instalar ou trocar a chave,
use um terminal com acesso SSH à VPS durante uma janela de manutenção:

```bash
ssh -t -o StrictHostKeyChecking=yes root@2.25.172.95 /usr/local/sbin/miller-configurar-openrouter --somente-chave
```

Insira a chave no prompt oculto do terminal. O comando consulta os metadados
da credencial na OpenRouter, atualiza o `.env` com permissão `600` e recria
somente o renderizador. Ao terminar, deve aparecer `Chave validada e aplicada ao renderizador.`
[Documentação da OpenRouter](https://openrouter.ai/docs/api/api-reference/api-keys/get-current-key)

Após implantar a versão para download direto, publique os workflows
atualizados `automacao-reg-error-handler` e `automacao-regulatoria-internal`
e confirme o estado no n8n. O modelo definido no código
é `openai/gpt-6.1-terra`. Com autorização operacional, use um PDF sintético
para confirmar a geração do Markdown e do PDF, conferir as evidências e
observar o status `concluido` e o botão de download. Para documento real, registre a
autorização para o documento e o destino e confira se os termos do provedor
permitem os dados. Consulte [PRD.md](PRD.md) e [workflows/README.md](workflows/README.md).

## Configurar o proprietário do n8n

Em 23/11/2026, foi confirmado que o Docker inicia com a VPS e o n8n está
saudável com a política `restart: unless-stopped`. O editor escuta em
`127.0.0.1:25678` na VPS. Abra o túnel SSH somente quando precisar usar o
editor:

```bash
ssh -N -L 25678:127.0.0.1:25678 root@2.25.172.95
```

No primeiro uso administrativo, o responsável indicado pelo cliente abre
`http://localhost:25678` pelo túnel e cadastra a conta proprietária. Confirme
no projeto pessoal o processamento, o tratamento de erros, a reconciliação
e a credencial `PostgreSQL Miller`. Ao fechar o túnel, o n8n continua
executando na VPS.

## Atualizar a versão na mesma VPS

Escolha um commit aprovado e leia o diff, o [ROADMAP.md](ROADMAP.md) e o
[LOG.md](LOG.md). Confirme as migrações necessárias e reserve uma janela de
atualização sem execuções em andamento. Prepare o backup descrito abaixo
antes de alterar os serviços.

No checkout local autorizado, empacote somente os arquivos rastreados:

```bash
git fetch origin
release=$(git rev-parse --verify refs/remotes/origin/main)
arquivo="$(mktemp -d)/miller-$release.tar"
git archive --format=tar "$release" > "$arquivo"
git get-tar-commit-id < "$arquivo"
sha256sum "$arquivo"
scp "$arquivo" "root@2.25.172.95:/root/miller-$release.tar"
```

Registre o commit e o hash exibidos. Na VPS, substitua os dois valores
indicados no bloco e execute-o no terminal administrativo:

```bash
(
  set -euo pipefail
  umask 077
  release='SUBSTITUA_PELO_COMMIT_COMPLETO'
  checksum='SUBSTITUA_PELO_SHA256_DO_ARQUIVO'
  [[ "$release" =~ ^[0-9a-f]{40}$ && "$checksum" =~ ^[0-9a-f]{64}$ ]]

  arquivo="/root/miller-$release.tar"
  printf '%s  %s\n' "$checksum" "$arquivo" | sha256sum --check
  atual=/opt/automacao-miller
  anterior="/opt/automacao-miller-anterior-$(date -u +%Y%m%dT%H%M%SZ)"
  candidato=$(mktemp -d /opt/.automacao-miller.XXXXXX)
  tar -xf "$arquivo" -C "$candidato" --no-same-owner
  install -m 0600 "$atual/.env" "$candidato/.env"
  install -m 0640 "$atual/docker-compose.override.yml" "$candidato/docker-compose.override.yml"
  printf '%s\n' "$release" > "$candidato/DEPLOYED_COMMIT"
  chmod 0750 "$candidato"
  (cd "$candidato" && docker compose -p automacao-miller config --quiet)

  cd /opt
  test ! -e "$anterior"
  mv -T "$atual" "$anterior"
  if ! mv -T "$candidato" "$atual"; then
    mv -T "$anterior" "$atual"
    exit 1
  fi
  printf 'Versão anterior em %s\n' "$anterior"

  cd "$atual"
  docker compose -p automacao-miller up -d --build --wait --wait-timeout 240
  docker compose -p automacao-miller ps
)
```

Preserve o nome do projeto Docker e os volumes. Se a versão alterar SQL ou
workflows, aplique somente a migração prevista para o banco existente. Os
scripts em `deploy/postgres/init/` inicializam bancos novos. Para atualizar
workflows, conserve a configuração anterior, confira os vínculos de
credenciais e valide o estado publicado depois da importação.
[Guia da stack](deploy/README.md) · [Operação dos workflows](workflows/README.md)

### Migrar o checkpoint Anvisa V8 antes da retomada

Use este roteiro para retomar o protocolo interrompido no limite de
releituras após atualizar o renderizador de `b006b7f` para a versão com a
rodada extra. A versão nova usa outra chave de checkpoint. Se o protocolo
for reprocessado antes da migração, o renderizador pode iniciar a análise
do zero, gerar novas cobranças e criar um destino que o migrador recusará
sobrescrever.

- [ ] Mantenha suspensos o reprocessamento público e os disparos manuais ou
  automáticos do protocolo. Aguarde o término das execuções em andamento.
  Confirme o commit de origem em `DEPLOYED_COMMIT`, o ID do protocolo, o
  SHA-256 do Markdown paginado persistido e a chave do diretório do
  checkpoint de origem. Use o Markdown vinculado à tentativa original.
- [ ] Faça e verifique o [backup](#backup-e-recuperação), incluindo o volume de
  diagnósticos com o checkpoint original. Registre os lotes e páginas
  concluídos na origem. Guarde a versão anterior para rollback.
- [ ] Atualize o renderizador preservando o volume de diagnósticos. Com a
  retomada ainda suspensa, execute o migrador dentro do renderizador que
  atenderá o protocolo. Use uma cópia privada do Markdown persistido,
  sem converter novamente o PDF ou editar o arquivo. Confira com
  `sha256sum` que a cópia corresponde ao artefato original.

  ```bash
  cd /opt/automacao-miller
  protocolo='SUBSTITUA_PELO_ID_DO_PROTOCOLO'
  chave_origem='SUBSTITUA_PELA_CHAVE_DO_DIRETORIO_DE_ORIGEM'
  markdown='/CAMINHO/PRIVADO/DO/MARKDOWN_PERSISTIDO.md'
  docker compose -p automacao-miller exec -T report-renderer \
    python -m infra.report_renderer.migrate_checkpoint \
    --markdown /dev/stdin --submission-id "$protocolo" --from-key "$chave_origem" \
    < "$markdown"
  ```

- [ ] Exija saída bem-sucedida com `status` igual a `migrado` ou
  `ja_migrado`. Confira `source_key`, registre a `destination_key` e
  confirme que ela difere da origem. Verifique `completed_lots` e
  `completed_pages` contra a origem. Se for uma repetição após avanço
  autorizado, confira que o destino mantém as páginas já concluídas na
  origem e o progresso posterior registrado. Confirme a presença dos dois
  arquivos `state.json` no mesmo volume privado. Em caso de erro, destino
  divergente ou progresso incompatível, mantenha a retomada suspensa e
  preserve ambos os estados para investigação.
- [ ] Após a conferência e com autorização, reprocesse uma única vez o
  mesmo protocolo pelo caminho que reutiliza o Markdown salvo. Acompanhe
  a tentativa. Ao gerar o pacote privado de verificação, confira
  `lotes_reutilizados` e `paginas_reutilizadas` em
  `processamento_incremental`. Verifique cobertura, status `concluido` e
  download autenticado do PDF. Registre a etapa e a referência do diagnóstico
  se falhar, mantendo a reconciliação suspensa até concluir a validação.

**Rollback do renderizador.** Suspenda os disparos e aguarde o encerramento
da tentativa antes de trocar a versão. Faça backup das duas identidades de
checkpoint e siga o roteiro para [voltar à versão anterior](#voltar-à-versão-anterior),
mantendo o volume de diagnósticos. Confirme o commit restaurado, a saúde do
renderizador e a presença do checkpoint original antes de qualquer nova
tentativa. A versão anterior usa o estado de origem, com o limite de três
releituras. O progresso posterior permanece no destino e fica disponível
para a versão nova. Mantenha o protocolo suspenso até decidir em qual
versão retomar. Preserve o banco e os demais artefatos quando o rollback
for apenas do renderizador.

### Atualizar para download direto

Em janela de manutenção, suspenda novos uploads e aguarde as execuções ativas.
Guarde um backup do banco, dos artefatos e dos workflows. Mantenha despublicados
o workflow legado de envio e os workflows em atualização até completar a troca.
No checkout da nova versão, aplique a migração ao volume PostgreSQL existente:

```bash
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1' \
  < deploy/postgres/init/006_report_download.sql
```

A migração conclui protocolos antigos que aguardavam envio ou falharam na
entrega, quando há um registro de PDF vinculado à tentativa. O gateway também
confere que o arquivo existe no volume antes de exibir o botão. As tabelas
legadas existentes ficam guardadas para auditoria.

Importe a versão atualizada do workflow de processamento selecionado e do
workflow de erros. Atualize a reconciliação antes de publicá-la. Revincule os
nós PostgreSQL, confira o vínculo com o tratamento de erros e valide um PDF
sintético autorizado. Em 23/11, o usuário autorizou a reabertura de novos
uploads para que o cliente fizesse a simulação. Para liberar reprocessamentos
após a validação de falhas e retomada, remova o matcher
`@reprocessamentoSuspensoDownload` e a regra `respond` correspondente de
`/etc/caddy/Caddyfile`. Valide com
`caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile` e aplique
com `systemctl reload caddy`.

### Validar após implantar

```bash
cd /opt/automacao-miller
cat DEPLOYED_COMMIT
docker compose config --quiet
docker compose ps
curl -fsS http://127.0.0.1:25678/healthz/readiness
curl -fsS -o /dev/null -w '%{http_code}\n' https://reportai.info/
curl -sS -o /dev/null -w '%{http_code}\n' https://reportai.info/upload
curl -sS -o /dev/null -w '%{http_code}\n' https://reportai.info/internal/verificacao
```

Espere seis serviços saudáveis, HTTPS `200` na página de login, `403` na área
privada sem sessão e `404` na rota interna. Confira login e logout e consulte
o estado dos workflows pelo túnel. Registre o commit implantado, as validações
executadas e as pendências no [LOG.md](LOG.md).

### Voltar à versão anterior

Se a instalação falhar, localize o diretório anterior exibido pelo roteiro,
verifique seu `DEPLOYED_COMMIT` e confirme a compatibilidade do banco e das
configurações. Preserve a versão problemática em outro diretório protegido,
recupere o diretório anterior como `/opt/automacao-miller` e reconstrua com
`docker compose -p automacao-miller up -d --build --wait`. Repita as validações.
Para divergência de esquema ou perda de dados, faça a recuperação com backup
validado e decisão explícita sobre as gravações posteriores ao ponto de
restauração.

## Backup e recuperação

Na janela de manutenção, suspenda a entrada de documentos e aguarde o
encerramento das execuções em andamento. Em seguida, a partir da raiz na VPS,
faça o backup conjunto e verifique as somas:

```bash
cd /opt/automacao-miller
./deploy/backup/backup.sh
manifesto=$(find /opt/backups/automacao-miller -maxdepth 1 -name '*.manifest' -type f | sort | tail -1)
grep -E '^[a-f0-9]{64}  ' "$manifesto" | sha256sum --check
```

Registre o `DEPLOYED_COMMIT` junto ao manifesto. O script cobre banco e
artefatos. Inclua também o volume `automacao-miller_automacao_miller_diagnostics_data`,
em especial `/data/diagnostics/checkpoints` durante operação com Anvisa V8.
Copie o conjunto para armazenamento protegido fora da VPS e teste a
restauração em ambiente isolado. Em 21/11, a restauração e a cópia externa
seguiram pendentes. Consulte [deploy/README.md](deploy/README.md).

Para outra VPS, instale Docker e Compose, gere segredos próprios, prepare
`.env` e as portas de loopback, suba os serviços e importe somente os
workflows internos em estado inativo com credenciais do ambiente. Publique a
landing com Caddy após definir o DNS e validar o HTTPS.
[Preparação da stack](deploy/README.md) · [HTTPS automático do Caddy](https://caddyserver.com/docs/automatic-https)
