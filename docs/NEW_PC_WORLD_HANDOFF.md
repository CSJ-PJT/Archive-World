# Archive-World 새 PC 인계 문서

## 기준 정보

- 저장소: `https://github.com/CSJ-PJT/Archive-World.git`
- 브랜치: `feat/archive-world-v1`
- V3 기준 커밋: `5c59346`
- 권장 WSL 작업 경로: `/mnt/c/ArchivePJT/Archive-World`
- Git LFS: 사용
- V2: Legacy Baseline으로 보존하며 수정하지 않는다.

## 현재 V3 상태

- Archive City v3 Seoul Metropolitan Realism Pass
- 인스턴스: 1,633
- 건물: 936
- 차량: 160
- 공공 소품: 445
- 도로 그래프: 24 nodes / 32 edges
- canonical V3 library: 100
- Meshy checksum: 46/46 일치
- V2 regression, V3 layout, Viewer typecheck/test/build: 통과
- 시각 품질 판정: `VISUAL REALISM PARTIAL`

남은 시각 품질 과제는 저폴리 자산의 반복 노출을 더 낮추는 일이며, 현재 배포 및 Viewer 실행을 막지는 않는다.

## 요구 도구

- Git
- Git LFS
- Node.js 및 npm
- Blender (Scene 재생성·렌더·Blender 검증을 수행하는 경우)
- Python (Blender build script를 수행하는 경우)

Blender는 먼저 `BLENDER_PATH` 환경변수를 확인하고, 없으면 Windows 설치 경로 또는 `blender` 명령을 탐색한다. 절대경로를 프로젝트 파일에 기록하지 않는다.

## 기본 복원과 검증

`docs/NEW_PC_WORLD_PULL_STEPS.md`의 순서대로 clone, Git LFS pull, 로컬 이전 패키지 복원, Viewer 검증을 수행한다.

주요 검증 명령은 다음과 같다.

```bash
node src/validate-world-v3.mjs
node src/validate-world-v3-spatial.mjs
node src/validate-world-v2.mjs

cd web
npm ci
npm run typecheck
npm test
npm run build
```

## 재현 가능한 World build

V3 layout과 asset library, external relative texture 구조를 사용한다. master scene에는 layout, link, camera, light만 유지하고 packed texture를 사용하지 않는다.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run-world-build-v3.ps1
```

이 작업은 Blender가 필요하며, 기존 결과만 확인하는 경우에는 실행하지 않는다.

## 로컬 이전 패키지

Git/LFS에 포함되지 않은 호환 보조 자료는 다음 패키지로 별도 전달한다.

- `Archive-World-Local-Handoff-20260715-2100.tar.gz`
- `Archive-World-Local-Handoff-20260715-2100.sha256`

복원 대상은 아래 상대 경로다.

- `assets/runtime/v2/asset-library.json`
- `assets/runtime/v2/library/*.glb` 중 패키지 manifest에 기재된 17개 파일

패키지에는 secret, 환경 파일, node_modules, dist, cache, log, autosave, backup Blend, 원본 Meshy 자료가 포함되지 않는다.

## 렌더 프리뷰

다음 렌더는 `assets/previews/v3/`에 있다.

- `city-overview.png`
- `birds-eye-view.png`
- `archiveos-overview.png`
- `residential-overview.png`
- `market-overview.png`
- `nexus-overview.png`
- `logistics-overview.png`
- `ledger-overview.png`
- `west-sea-port-overview.png`
- `han-river-bridges-overview.png`
- `north-east-mountains-overview.png`
- `south-plains-overview.png`

## 환경변수

환경변수 이름만 사용한다.

- `BLENDER_PATH`
- `VITE_ARCHIVEOS_BASE_URL`
- `VITE_ARCHIVE_WORLD_ASSET_BASE_URL`
- `VITE_RUNTIME_DATA_MODE`
