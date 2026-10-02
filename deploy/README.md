# Implantação da stack de homologação

Esta stack usa n8n, PostgreSQL, Ollama, os serviços locais de conversão e
renderização e o gateway de upload, com volumes e rede próprios. O serviço RAG
é legado e fica fora da inicialização padrão; somente o perfil optativo `rag`
o inicia.

## Teste no computador local

Para testar a landing em http://localhost:8085 sem expor a porta na rede,
combine o Compose principal com deploy/docker-compose.local.yml. O roteiro
completo, incluindo preparação da .env, credencial PostgreSQL no n8n, teste
com PDF e estado final aguardando_envio, está em
[docs/TESTE_LOCAL.md](../docs/TESTE_LOCAL.md). Não ative o envio Gmail durante
essa homologação local.

## Preparação no servidor

1. Copie o repositório para `/opt/automacao-miller`.
2. Crie `.env` a partir de `.env.example` no servidor.
3. Gere `POSTGRES_PASSWORD`, `N8N_ENCRYPTION_KEY` e os tokens da landing fora
   do Git.
4. Defina `ARTIFACT_STORAGE_DIR=/data/artifacts`, `ARTIFACTS_GID=10002`,
   `BACKUP_DIR=/opt/backups/automacao-miller` e `BACKUP_RETENTION_DAYS`.

A origem oficial de novos documentos é a landing privada. O Google Drive não é
necessário para a operação e aparece somente nos workflows históricos de
homologação.

## Inicialização

```bash
cd /opt/automacao-miller
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Ao atualizar uma instalação antiga que já está executando RAG, pare o
container antes de usar o perfil padrão:

```bash
docker compose --profile rag stop rag-service
docker compose up -d --build
```

Isso preserva o container e os volumes; para voltar a iniciar o serviço, use o
perfil `rag` explicitamente.

Sem perfil adicional, os limites máximos declarados somam 6.912 MiB (6,75 GiB),
incluindo até 3 GiB para o Ollama. Em uma VPS de referência com 8 GiB, isso
deixa 1,25 GiB para o sistema e outros processos. Esses valores são tetos do
Compose, não consumo esperado. O perfil opcional RAG acrescenta 512 MiB ao
limite total; habilite-o somente para trabalho específico com essa capacidade.

O modelo inicial definido para a homologação é `qwen2.5:3b`:

```bash
docker compose exec ollama ollama pull qwen2.5:3b
```

O schema interno é aplicado automaticamente em um banco novo. Em uma stack
existente, aplique a migração depois que o gateway inicializar o schema legado:

```bash
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < deploy/postgres/init/002_internal_repository.sql
```

Em uma instalação já existente, aplique também
`deploy/postgres/init/003_panel_operations.sql` para criar destinatários,
destinatários por documento, entregas de e-mail e o status `aguardando_envio`.

## Repositório e permissões

O volume novo `automacao_miller_artifacts_data` é montado em
`/data/artifacts` no gateway e no n8n. O entrypoint do gateway cria `incoming`
e `objects`; os objetos são gravados com permissões privadas e organizados por
SHA-256. O grupo numérico definido em `ARTIFACTS_GID` deve existir nos serviços
e permitir leitura e escrita controladas entre gateway e n8n.

O volume antigo `automacao_miller_submission_data` permanece declarado para
rollback e migração. Antes de ativar o workflow interno, execute:

```bash
cd /opt/automacao-miller
./deploy/backup/migrate-artifacts.sh
```

O script faz o backup antes da cópia, preserva o volume antigo, replica os
arquivos em `legacy/submissions` e aplica a migração do PostgreSQL. Arquivos do
Google Drive não são apagados.

O n8n aplica uma restrição adicional aos nós de leitura e escrita de arquivos:
`N8N_RESTRICT_FILE_ACCESS_TO=/data/artifacts`. Essa variável precisa permanecer
alinhada ao ponto de montagem do volume; sem ela, o n8n recusa o acesso ao
repositório e mantém o documento em erro.

## Workflows

Importe os quatro exports internos descritos em `workflows/README.md`:
processamento, envio manual, reconciliação e erros. Associe somente PostgreSQL
e Gmail, configure os webhooks `N8N_SUBMISSION_WEBHOOK_URL` e
`N8N_REPORT_EMAIL_WEBHOOK_URL` e valide uma execução completa antes de ativar os
workflows. Os exports que usam Drive devem permanecer inativos como histórico.

O processamento termina em `aguardando_envio`. O operador confere os artefatos
no painel, escolhe os destinatários e solicita o envio. O download oficial fica
bloqueado até o workflow registrar a confirmação do Gmail e `concluido`.

## Operação e backup

Não remova volumes durante atualizações e não exponha portas internas na
Internet. O backup oficial inclui o dump do PostgreSQL e uma cópia do volume de
artefatos na mesma execução. O script versionado usa o diretório protegido
`/opt/backups/automacao-miller` por padrão:

```bash
cd /opt/automacao-miller
BACKUP_DIR=/opt/backups/automacao-miller ./deploy/backup/backup.sh
```

Cada execução gera `*.pgdump`, `*.artifacts.tar.gz` e um manifesto com data,
volume e SHA-256 dos dois arquivos. A retenção é controlada por
`BACKUP_RETENTION_DAYS`. Proteja o diretório com `chmod 700` e replique os
backups para uma mídia segura conforme a política da VPS.

Para restaurar, pare o processamento, restaure o dump em um banco vazio com
`pg_restore --clean --if-exists` e extraia o arquivo de artefatos na raiz do
volume `automacao_miller_artifacts_data`. Valide os hashes do manifesto antes
de reativar o n8n.

## Acesso ao n8n e landing

O n8n fica exposto somente em `127.0.0.1:25678`; use um túnel SSH:

```bash
ssh -L 25678:127.0.0.1:25678 root@SERVIDOR
```

Configure `LANDING_USERNAME`, `LANDING_PASSWORD_HASH` e
`AUTH_SESSION_SECRET` somente na VPS. Mantenha `SESSION_COOKIE_SECURE=true`
atrás de HTTPS. O gateway deve ser publicado por HTTPS/Caddy, sem expor
diretamente a porta 8085.

Gere o hash sem registrar a senha no Git:

```bash
docker compose run --rm upload-gateway python -m infra.upload_gateway.password_hash
```

O valor de `LANDING_PASSWORD_HASH` contém `$`; mantenha-o entre aspas simples
no `.env` da VPS.

## Perfil legado opcional de RAG

O workflow ativo não chama RAG, embeddings ou `quality_checks`. A inicialização
normal do Compose não inicia `rag-service` e o n8n não depende dele.

Para investigar essa capacidade legada de forma explícita, inicie apenas o
serviço no perfil dedicado:

```bash
docker compose --profile rag up -d rag-service
docker compose --profile rag exec ollama ollama pull nomic-embed-text
```

Em banco já existente, faça o backup conjunto antes de aplicar
`deploy/postgres/init/004_rag_and_training.sql`; arquivos de inicialização não
são reaplicados automaticamente. O serviço permanece apenas na rede Docker e
não expõe o volume nem seus caminhos ao navegador. Variáveis e configuração
específicas estão identificadas como opcionais no `.env.example`. Ativar o perfil
não conecta RAG ao workflow ativo. O dataset de treinamento exportado deve
permanecer em diretório protegido fora do Git.

## Coleta do DOU em staging

O coletor usa a sessão autenticada do INLABS e não salva a senha em arquivos do
projeto. Configure `DOU_INLABS_EMAIL` e `DOU_INLABS_PASSWORD` como secrets e
execute a coleta no staging protegido, preferencialmente fora da VPS para não
consumir o volume operacional:

```bash
python scripts/download_dou_corpus.py --start 2026-08-12 --end 2026-09-10 \
  --output /opt/staging/dou-2026-08-12_2026-09-10
python scripts/prepare_dou_review_queue.py \
  --staging /opt/staging/dou-2026-08-12_2026-09-10 --generate-candidates
python scripts/build_dou_report_package.py \
  --staging /opt/staging/dou-2026-08-12_2026-09-10 \
  --output /opt/dou-packages/dou-2026-08-12_2026-09-10
```

O script considera `do1`, `do2` e `do3` em PDF; os pacotes XML consideram
`DO1`, `DO2`, `DO3`, `DO1E`, `DO2E` e `DO3E`. Respostas 404 ficam registradas
como ausentes e não são tratadas como erro de conversão. O manifesto preserva
status, data, seção, tamanho e SHA-256. O ZIP não inclui os PDFs brutos.
