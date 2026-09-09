#!/bin/sh
set -eu

storage_dir="${ARTIFACT_STORAGE_DIR:-/data/artifacts}"
mkdir -p "$storage_dir/incoming" "$storage_dir/objects"
chown -R appuser:appuser "$storage_dir"
find "$storage_dir" -type d -exec chmod 2770 {} +
find "$storage_dir" -type f -exec chmod 0660 {} +

exec su appuser -s /bin/sh -c 'exec uvicorn infra.upload_gateway.app:app --host 0.0.0.0 --port 8085'
