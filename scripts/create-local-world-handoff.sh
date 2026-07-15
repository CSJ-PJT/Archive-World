#!/usr/bin/env bash
# Build the non-Git input handoff needed to rebuild V3 without changing V2.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
output_root=${1:-/mnt/c/ArchiveTransfer}
stamp=$(date +%Y%m%d-%H%M)
name="Archive-World-Local-Handoff-${stamp}"
package_dir="$output_root/$name"
mkdir -p "$package_dir"

cd "$root"
refs=$(mktemp)
tracked=$(mktemp)
grep 'assets/runtime/v2/library/' assets/runtime/v3/asset-library.json \
  | grep -oE '[A-Za-z0-9_-]+\.glb' \
  | sed 's|^|assets/runtime/v2/library/|' \
  | sort -u > "$refs"
git ls-files assets/runtime/v2/library | sort > "$tracked"

{
  printf '%s\n' assets/runtime/v2/asset-library.json
  comm -23 "$refs" "$tracked"
} > "$package_dir/restore-paths.txt"

while IFS= read -r path; do
  [[ -f "$path" ]] || { echo "missing required local input: $path" >&2; exit 1; }
  mkdir -p "$package_dir/$(dirname "$path")"
  cp -p "$path" "$package_dir/$path"
done < "$package_dir/restore-paths.txt"

(cd "$package_dir" && sha256sum $(cat restore-paths.txt) > SHA256SUMS)
cat > "$package_dir/README-RESTORE.md" <<'EOF'
# Archive-World Local Input Restore

This package contains only V3 rebuild inputs that are intentionally not part of
the Git branch because V2 remains a legacy baseline. Restore from the clone
root, preserving relative paths:

```bash
tar -xzf Archive-World-Local-Handoff-<timestamp>.tar.gz -C /tmp/archive-world-handoff
cp -a /tmp/archive-world-handoff/assets/runtime/v2/. assets/runtime/v2/
sha256sum -c /tmp/archive-world-handoff/SHA256SUMS
```

Do not copy `.env`, credentials, caches, backups, `node_modules`, or build
output from another machine. This package contains no secrets.
EOF

tar -C "$output_root" -czf "$output_root/$name.tar.gz" "$name"
(cd "$output_root" && sha256sum "$name.tar.gz" > "$name.sha256")
printf 'LOCAL_HANDOFF_DIR=%s\nLOCAL_HANDOFF_ARCHIVE=%s\nLOCAL_HANDOFF_SHA=%s\n' \
  "$package_dir" "$output_root/$name.tar.gz" "$output_root/$name.sha256"

rm -f "$refs" "$tracked"
