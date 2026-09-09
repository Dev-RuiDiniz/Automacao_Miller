#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

STACK_DIR="${STACK_DIR:-/opt/automacao-miller}"
BACKUP_DIR="${BACKUP_DIR:-/opt/backups/automacao-miller}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
VOLUME_NAME="${ARTIFACT_VOLUME_NAME:-automacao_miller_artifacts_data}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DB_DUMP="${BACKUP_DIR}/automacao-miller-${TIMESTAMP}.pgdump"
ARTIFACT_ARCHIVE="${BACKUP_DIR}/automacao-miller-${TIMESTAMP}.artifacts.tar.gz"
MANIFEST="${BACKUP_DIR}/automacao-miller-${TIMESTAMP}.manifest"

case "${RETENTION_DAYS}" in
  ''|*[!0-9]*) echo "BACKUP_RETENTION_DAYS deve ser um número inteiro." >&2; exit 2 ;;
esac

mkdir -p "${BACKUP_DIR}"
chmod 0700 "${BACKUP_DIR}"
cd "${STACK_DIR}"
REPOSITORY_VERSION="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
DATABASE_NAME="$(docker compose -f "${COMPOSE_FILE}" exec -T postgres sh -c 'printf %s "$POSTGRES_DB"' | tr -d '\\r\\n')"

docker compose -f "${COMPOSE_FILE}" exec -T postgres \
  sh -c 'pg_dump -Fc -U "$POSTGRES_USER" -d "$POSTGRES_DB"' > "${DB_DUMP}"

docker run --rm \
  -v "${VOLUME_NAME}:/data:ro" \
  -v "${BACKUP_DIR}:/backup" \
  alpine:3.20 \
  tar -czf "/backup/$(basename "${ARTIFACT_ARCHIVE}")" -C /data .

{
  printf 'created_at=%s\n' "${TIMESTAMP}"
  printf 'repository_version=%s\n' "${REPOSITORY_VERSION}"
  printf 'stack_dir=%s\n' "${STACK_DIR}"
  printf 'postgres_database=%s\n' "${DATABASE_NAME:-unknown}"
  printf 'postgres_volume_backup=%s\n' "$(basename "${DB_DUMP}")"
  printf 'artifact_volume=%s\n' "${VOLUME_NAME}"
  printf 'artifact_volume_backup=%s\n' "$(basename "${ARTIFACT_ARCHIVE}")"
  sha256sum "${DB_DUMP}" "${ARTIFACT_ARCHIVE}"
} > "${MANIFEST}"

find "${BACKUP_DIR}" -maxdepth 1 -type f \
  \( -name 'automacao-miller-*.pgdump' -o -name 'automacao-miller-*.artifacts.tar.gz' -o -name 'automacao-miller-*.manifest' \) \
  -mtime "+${RETENTION_DAYS}" -delete

echo "Backup concluído: ${MANIFEST}"
