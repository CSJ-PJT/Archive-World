# Official glTF Validation Runbook

The project pins Khronos `gltf-validator@2.0.0-dev.3.10` under `tools/gltf-validator`.

```bash
npm ci --prefix tools/gltf-validator
export ARCHIVE_GLTF_VALIDATOR_DIR="$PWD/tools/gltf-validator"
node scripts/validate_gltf.mjs --report /tmp/report.json path/to/file.glb
node scripts/validate_gltf.mjs --strict path/to/glb-directory
npm test --prefix tools/gltf-validator
```

Exit `0` is valid, `1` is validation failure (or warning under `--strict`), and
`2` is a blocked/missing tool or invalid invocation. Reports separate error,
warning, and informational messages. Generated validation reports remain
outside Git unless a deliberately small fixture report is approved.
