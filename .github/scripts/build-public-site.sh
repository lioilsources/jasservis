#!/usr/bin/env bash
set -euo pipefail

source_dir="${1:-jasservis.cz}"
output_dir="${2:-.pages-dist}"

rm -rf "$output_dir"
mkdir -p "$output_dir"

# The repository can contain authoring data, but a deployable artifact must contain
# only customer-facing files. Keep this allow/copy boundary in both preview and
# production workflows.
tar \
  --exclude='./_warnings' \
  --exclude='./_media' \
  --exclude='*/kontrolky-a-vystrazna-hlaseni/revize.html' \
  --exclude='*/kontrolky-a-vystrazna-hlaseni/revize-kapitol.html' \
  --exclude='*/kontrolky-a-vystrazna-hlaseni/druha-kontrola.html' \
  --exclude='*/kontrolky-a-vystrazna-hlaseni/zdroje.html' \
  --exclude='*/kontrolky-a-vystrazna-hlaseni/evidence.json' \
  -C "$source_dir" -cf - . | tar -C "$output_dir" -xf -

forbidden="$output_dir/_warnings
$output_dir/_media
$output_dir/kontrolky-a-vystrazna-hlaseni/revize.html
$output_dir/kontrolky-a-vystrazna-hlaseni/zdroje.html
$output_dir/en/kontrolky-a-vystrazna-hlaseni/revize.html
$output_dir/en/kontrolky-a-vystrazna-hlaseni/zdroje.html
$output_dir/de/kontrolky-a-vystrazna-hlaseni/revize.html
$output_dir/de/kontrolky-a-vystrazna-hlaseni/zdroje.html
$output_dir/kontrolky-a-vystrazna-hlaseni/revize-kapitol.html
$output_dir/en/kontrolky-a-vystrazna-hlaseni/druha-kontrola.html
$output_dir/de/kontrolky-a-vystrazna-hlaseni/evidence.json"

while IFS= read -r path; do
  if [[ -e "$path" ]]; then
    echo "Forbidden internal path in public artifact: $path" >&2
    exit 1
  fi
done <<< "$forbidden"

if find "$output_dir" -type f \( -name '*review*.json' -o -name '*review*.csv' -o -name '*inventory*.csv' -o -name 'catalog.json' \) -print -quit | grep -q .; then
  echo 'Internal catalogue, review or inventory material found in public artifact.' >&2
  exit 1
fi

test -f "$output_dir/kontrolky-a-vystrazna-hlaseni/index.html"
test -f "$output_dir/wp-content/themes/theme53985/js/warning-lights.js"
