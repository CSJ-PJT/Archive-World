# Archive-World

Archive 서비스와 분리된 **Digital Twin용 3D Asset Pipeline**입니다. Meshy가 생성한 GLB를 받아 검증, Blender 최적화, LOD 생성, Draco 압축, PNG 렌더링, ArchiveOS 소비용 metadata/Three.js manifest 생성, OCI Object Storage 업로드까지 처리합니다.

Three.js 화면·뷰어는 이 프로젝트 범위에 포함하지 않습니다. 이 저장소는 Digital Twin 클라이언트가 읽을 수 있는 배포 자산과 manifest만 만듭니다.

## Prerequisites

- Node.js 20+
- Blender 4.x CLI (`blender`가 PATH에 있거나 `BLENDER_PATH` 설정)
- OCI CLI 및 OCI 인증 설정 (업로드 단계만)
- Git LFS (`git lfs install`) — 대형 GLB/FBX/미디어를 Git으로 관리할 경우

```powershell
cd Archive-World
npm install
Copy-Item world.config.example.json world.config.json
Copy-Item .env.example .env
npm run init
```

`.env`는 셸에서 자동으로 로드되지 않습니다. 필요한 값은 환경 변수로 설정하거나 `world.config.json`에 로컬 OCI 설정을 입력하세요. `.env`는 비밀값을 문서화하는 템플릿 용도이며 Git에서 제외됩니다.

## Pipeline

```powershell
# 1. Meshy 다운로드 GLB를 원본 보관소로 등록하고 즉시 구조 검증
npm run world -- ingest <path-to-meshy-model.glb> building-lobby-a

# 검증만 다시 실행
npm run world -- validate building-lobby-a

# 2–9. Blender 최적화 → LOD 0/1/2 → Draco → preview/thumbnail → metadata/manifest
npm run build -- building-lobby-a

# 10. OCI Object Storage 업로드 (명시적으로 실행할 때만 외부 전송)
$env:OCI_OS_NAMESPACE = 'your-namespace'
$env:OCI_OS_BUCKET = 'archive-world-assets'
npm run world -- upload building-lobby-a
```

`build` 결과:

- `assets/source/<id>.glb` — Meshy 원본 (불변 입력)
- `assets/optimized/<id>/lod0.glb` … `lod2.glb` — Draco 압축 GLB
- `assets/previews/<id>.png`, `assets/thumbnails/<id>.png`
- `assets/world/<id>.metadata.json` — SHA-256, 용량, 메시/재질/애니메이션 수
- `assets/world/<id>.manifest.json` — Three.js `GLTFLoader`가 쓸 LOD URL과 Draco decoder 요구사항

## ArchiveOS contract

ArchiveOS/Digital Twin은 `assets/world/<id>.manifest.json` 또는 OCI의 `<prefix>/<asset-id>/world/<id>.manifest.json`을 읽습니다. `lods[].url`을 `GLTFLoader`로 로드하고, `loader.dracoDecoder.path`에서 Draco decoder를 제공하면 됩니다. manifest는 렌더링 UI에 의존하지 않는 `archive-world.three-manifest/v1` 계약입니다.

OCI object key 구조:

```text
<OCI_OS_PREFIX>/<asset-id>/optimized/lod0.glb
<OCI_OS_PREFIX>/<asset-id>/previews/<asset-id>.png
<OCI_OS_PREFIX>/<asset-id>/thumbnails/<asset-id>.png
<OCI_OS_PREFIX>/<asset-id>/world/<asset-id>.metadata.json
<OCI_OS_PREFIX>/<asset-id>/world/<asset-id>.manifest.json
```

## Notes

- Validation combines a dependency-free GLB header/JSON check with glTF Transform's spec validation after `npm install`; Blender additionally rejects assets it cannot import.
- LODs are generated from the optimized asset at ratios configured in `world.config.json` (default `1`, `0.5`, `0.2`). Validate visual quality for hero assets before release.
- Generated binary assets are ignored by default to prevent accidental large commits. Git LFS rules are already in `.gitattributes`.
- `upload` is deliberately separate, so a local build never sends assets to OCI implicitly.
