# Archive City v3 — 재현 가능한 빌드

## 구조

- `scenes/v3/libraries/<assetId>.blend`: 자산별 canonical Blender library
- `scenes/v3/libraries/textures/`: library가 참조하는 외부 상대경로 텍스처
- `scenes/v3/<district>.blend`: linked collection instance만 보유하는 지구 scene
- `scenes/archive-city-v3.blend`: 7개 district scene link, camera, lighting만 보유하는 master
- `assets/runtime/v3/<district>.glb`: 웹용 자체 포함 GLB
- `assets/world/archive-city-v3-layout.json`: 배치·지구·도로 topology의 단일 소스

원본 Meshy 파일과 `assets/runtime/v2`는 입력/Legacy Baseline이며 빌드가 수정하지 않는다.

## 새 PC에서의 재현

```powershell
git clone <Archive-World repository URL>
Set-Location Archive-World
npm ci
$env:BLENDER_PATH = 'C:\Path\To\blender.exe'
.\scripts\run-world-build-v3.ps1
```

모든 link와 texture path는 저장소 기준 상대 경로다. `BLENDER_PATH`는 로컬 환경변수이며 source file에 기록하지 않는다.

## 검증

```powershell
node src/validate-world-v3.mjs
node src/validate-world-v3-distribution.mjs
& $env:BLENDER_PATH --background --python-exit-code 1 --python scripts/blender/validate_v3_blend_links.py -- --repo $PWD
Set-Location web
npm run typecheck
npm test
npm run build
```

## Viewer runtime

초기 화면은 overview PNG만 표시한다. 사용자가 **Load 3D district viewer** 또는 district preset을 선택하면 Three.js runtime과 해당 district GLB를 지연 로드한다.

로컬/배포 asset endpoint는 `VITE_ARCHIVE_WORLD_ASSET_BASE_URL`에 `runtime/` 디렉터리를 제공하는 asset root를 설정한다. 예시는 다음과 같다.

```text
VITE_ARCHIVE_WORLD_ASSET_BASE_URL=https://assets.example/archive-world/assets
```

`web/dist`, `.env`, cache, `*.blend1`, `*.blend2`, autosave, logs는 배포 source 커밋 대상이 아니다.
