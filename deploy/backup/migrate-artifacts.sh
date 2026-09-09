#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

STACK_DIR="${STACK_DIR:-/opt/automacao-miller}"
OLD_VOLUME="${OLD_ARTIFACT_VOLUME_NAME:-automacao_miller_submission_data}"
NEW_VOLUME="${ARTIFACT_VOLUME_NAME:-automacao_miller_artifacts_data}"
BACKUP_DIR="${BACKUP_DIR:-/opt/backups/automacao-miller}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

mkdir -p "${BACKUP_DIR}"
chmod 0700 "${BACKUP_DIR}"
cd "${STACK_DIR}"

"${STACK_DIR}/deploy/backup/backup.sh"

docker run --rm \
  -v "${OLD_VOLUME}:/source:ro" \
  -v "${NEW_VOLUME}:/target" \
  alpine:3.20 \
  sh -ec 'mkdir -p /target/legacy/submissions && cp -a /source/. /target/legacy/submissions/'

for migration in 002_internal_repository.sql 003_panel_operations.sql; do
  docker compose -f "${COMPOSE_FILE}" exec -T postgres \
    sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
    < "${STACK_DIR}/deploy/postgres/init/${migration}"
done

echo "Migração inicial concluída. O volume antigo foi preservado: ${OLD_VOLUME}"
