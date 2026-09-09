# Implantação da stack de homologação

Esta stack usa n8n, PostgreSQL, Ollama, os serviços locais de conversão e
renderização e o gateway de upload, com volumes e rede próprios.

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

## Workflows

Importe os três exports internos descritos em `workflows/README.md`:
processamento, reconciliação e erros. Associe somente PostgreSQL e Gmail,
configure o webhook interno e valide uma execução completa antes de ativar os
workflows. Os exports que usam Drive devem permanecer inativos como histórico.

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
