#!/usr/bin/env bash
# Build a local CV page, refresh its PDF, then build the deployable site.
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash scripts/build-site.sh BASE_URL" >&2
  exit 2
fi

site_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
site_base_url="${1%/}/"
preview_port="${CV_PREVIEW_PORT:-8765}"
preview_url="http://127.0.0.1:${preview_port}/"
cd "$site_root"
mkdir -p tmp out

hugo --gc --minify --cleanDestinationDir \
  --baseURL "$preview_url" \
  --destination "$site_root/tmp/cv-preview" \
  --cacheDir "$site_root/tmp/hugo-cache"

python3 -m http.server "$preview_port" --bind 127.0.0.1 \
  --directory "$site_root/tmp/cv-preview" > out/cv-preview-server.log 2>&1 &
preview_pid=$!
trap 'kill "$preview_pid" 2>/dev/null || true; wait "$preview_pid" 2>/dev/null || true' EXIT

preview_ready=false
for attempt in {1..50}; do
  if ! kill -0 "$preview_pid" 2>/dev/null; then
    echo "CV preview failed to start. See out/cv-preview-server.log." >&2
    exit 1
  fi
  if curl --fail --silent --output /dev/null "${preview_url}cv/"; then
    preview_ready=true
    break
  fi
  sleep 0.1
done
if [[ "$preview_ready" != true ]]; then
  echo "CV preview did not become available. See out/cv-preview-server.log." >&2
  exit 1
fi

pdf_arguments=(--url "${preview_url}cv/")
if [[ -n "${CV_BROWSER:-}" ]]; then
  pdf_arguments+=(--browser "$CV_BROWSER")
fi
if [[ "${CV_BROWSER_NO_SANDBOX:-0}" == 1 ]]; then
  pdf_arguments+=(--no-sandbox)
fi
python3 scripts/render-cv-pdf.py "${pdf_arguments[@]}"

hugo --gc --minify --cleanDestinationDir \
  --baseURL "$site_base_url" \
  --cacheDir "$site_root/tmp/hugo-cache"
