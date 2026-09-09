#!/bin/sh
set -eu

storage_dir="${ARTIFACT_STORAGE_DIR:-/data/artifacts}"
mkdir -p "$storage_dir/incoming" "$storage_dir/objects"
chown -R appuser:appuser "$storage_dir"
chmod 0770 "$storage_dir" "$storage_dir/incoming" "$storage_dir/objects"

exec su appuser -s /bin/sh -c 'exec uvicorn infra.upload_gateway.app:app --host 0.0.0.0 --port 8085'
