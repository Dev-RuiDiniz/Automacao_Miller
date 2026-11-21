# Implantação da Automação Miller

## Checklist de liberação ao cliente

Status baseado na verificação da VPS em 21/11/2026.

### Concluído

- [x] Instalar o Miller na VPS do cliente e verificar os seis serviços Docker.
- [x] Publicar `reportai.info` com HTTPS e validar o redirecionamento de `www`.
- [x] Configurar o usuário `operador` e validar login, logout e acesso restrito.
- [x] Importar os quatro workflows inativos e vincular a credencial PostgreSQL.
- [x] Selecionar OpenRouter para o Anvisa V8 e preparar o comando de instalação da chave.
- [x] Criar o backup na VPS e conferir os hashes do banco e dos artefatos.

### Pendente para liberar

- [ ] **OpenRouter.** Receber a chave do cliente, instalá-la na VPS e confirmar a publicação dos workflows de processamento e de erros.
- [ ] **n8n.** Cadastrar a conta proprietária com o administrador indicado pelo cliente.
- [ ] **Gmail.** Confirmar a conta de produção com o cliente ou líder técnico, autorizar o OAuth no n8n e vincular a credencial ao workflow de envio manual.
- [ ] **Teste final de análise.** Com autorização, enviar um PDF sintético pela landing. Conferir o protocolo, o Markdown paginado e persistido, a cobertura e as evidências do relatório, o PDF gerado e o status `aguardando_envio`.
- [ ] **Teste final de envio.** Enviar o relatório sintético pelo painel a um destinatário autorizado. Confirmar o recebimento pelo Gmail, o registro da entrega, o status `concluido` e a liberação do download após a conclusão.
- [ ] **Falhas e retomada.** Verificar que falhas de conversão ou de análise interrompem o processamento na etapa correta. Testar a retomada e a prevenção de duplicidades antes de liberar a reconciliação.
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
dos artefatos foram conferidos. A análise de ponta a ponta aguarda a chave
OpenRouter e a autorização para executar o teste.

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

## Ativar Anvisa V8 quando chegar a chave OpenRouter

A configuração `ANVISA_REPORT_PROVIDER=openrouter` já está aplicada. Os
workflows importados continuam inativos e `OPENROUTER_API_KEY` está vazio.
Quando o cliente disponibilizar a chave pelo canal aprovado, o administrador
deve executar, a partir de um terminal com acesso SSH à VPS:

```bash
ssh -t root@2.25.172.95 /usr/local/sbin/miller-configurar-openrouter
```

Insira a chave no prompt do terminal. O comando valida a credencial na API
da OpenRouter, atualiza o `.env` com permissão `600`, aplica a configuração ao
renderizador e publica os workflows de erro e de processamento. A validação
da chave consulta metadados, sem documento e sem chamada de inferência.
[Documentação da OpenRouter](https://openrouter.ai/docs/api/api-reference/api-keys/get-current-key)

Confirme no n8n que `automacao-reg-error-handler` e
`automacao-regulatoria-internal` estão publicados. O modelo definido no código
é `openai/gpt-6.1-terra`. Com autorização operacional, use um PDF sintético
para confirmar a geração do Markdown e do PDF, conferir as evidências e
observar o status `aguardando_envio`. Para documento real, registre a
autorização para o documento e o destino e confira se os termos do provedor
permitem os dados. Consulte [PRD.md](PRD.md) e [workflows/README.md](workflows/README.md).

## Configurar o proprietário do n8n e o Gmail

O administrador indicado pelo cliente deve concluir a criação da conta
proprietária do n8n. Em seu computador, abra o túnel SSH:

```bash
ssh -N -L 25678:127.0.0.1:25678 root@2.25.172.95
```

Com o túnel ativo, acesse `http://localhost:25678` e conclua o cadastro.
Confirme no projeto pessoal a presença dos quatro workflows e da credencial
`PostgreSQL Miller`.

O Gmail ficou para uma etapa posterior, a partir da indicação da conta pelo
cliente ou pelo líder técnico.

1. No projeto Google Cloud autorizado pelo cliente, habilite a Gmail API,
   configure o consentimento e crie o cliente OAuth do tipo **Aplicativo da
   Web**. Use a conta de produção aprovada. [OAuth para serviços Google no n8n](https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service)
2. Abra a credencial **Gmail OAuth2 API** no n8n e copie exatamente a URL de
   redirecionamento exibida para o cliente OAuth no Google. Com o túnel atual,
   confira se o n8n apresenta `http://localhost:25678/rest/oauth2-credential/callback`.
   Mantenha o túnel aberto durante a autorização. [URIs de redirecionamento do Google](https://developers.google.com/identity/protocols/oauth2/web-server)
3. Informe o Client ID e o Client Secret diretamente na credencial do n8n.
   O responsável autentica a conta pelo Google e autoriza o acesso. Guarde as
   credenciais no cofre do n8n.
4. Vincule a credencial ao nó Gmail de `automacao-regulatoria-send-report`.
   Cadastre o destinatário de homologação na landing e publique o workflow
   durante a janela do teste. Com autorização para o envio, use um relatório
   sintético em `aguardando_envio`, solicite o envio no painel e confirme o
   recebimento, o registro da entrega e o status `concluido`.
5. Avalie a publicação de `automacao-reg-internal-reconcile` após homologar os
   fluxos que ele pode despachar. Confira a retomada e a prevenção de duplicidade.

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
