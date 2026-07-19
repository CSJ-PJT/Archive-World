# Archive Metropolitan Seed City V1

## 목적과 안전 경계

이 브랜치는 6 km × 5 km 규모의 **Generated planning pilot**을 재현한다. 기존 V3 1,633개 인스턴스, canonical library, Runtime 저장소와 production manifest는 입력도 출력도 아니다. Office V5와 Residential V6는 각각 82/B인 동결 PO 후보이며 Generated 도시에 희소 anchor로만 사용한다.

## 생성 파이프라인

```mermaid
flowchart LR
  A[Master Plan] --> B[Street / Transit / Green]
  B --> C[District DNA Massing]
  C --> D[84 Block Variants]
  D --> E[42 Family Contracts / 3942 Instances]
  E --> F[Public Realm]
  F --> G[Static Vehicle / Human Proxy]
  G --> H[LOD / Chunk / Streaming Contract]
  H --> I[Metropolitan Review]
  I --> P{PO Review}
  P -->|승인 전 금지| X[Canonical or V3 Application]
```

각 단계는 외부 Generated root에 JSON과 atomic checkpoint를 기록한다. `--stop-after`와 기본 resume로 실패 지점부터 이어갈 수 있다.

## 도시 구조

- 13개 공간 구역이 ArchiveOS, Ledger, Market, Nexus, Logistics, Residential, Civic 및 river/park/infrastructure transition을 구성한다.
- 572개 교차점과 1,096개 도로 edge는 vehicle/pedestrian/service/fire 모드에서 각각 단일 연결 성분이다.
- 3개 rail/metro skeleton, 24개 역, 18개 bus route, 96개 bus stop을 계획한다. 실제 simulation integration은 `false`다.
- riverfront promenade, central park, 12 neighborhood park, 30 pocket park, 4 green corridor와 128 green module을 제공한다. green/open-space proxy는 18.57%다.
- 42개 building family 계약과 84개 block variant가 3,942개 instance configuration을 만든다. support family는 65–75점 계획 prototype이며 canonical asset이 아니다.

## 상태 계약

`PO_REVIEW_CANDIDATE_FROZEN`, `CITY_SUPPORT_PROTOTYPE`, `BLOCKOUT`, `PLACEHOLDER`, `INFRASTRUCTURE_PROXY`를 Viewer와 보고서에서 구분한다. `PO_REVIEW_CANDIDATE_FROZEN` geometry/material/score는 이 브랜치에서 수정하지 않는다.

## 실행

```bash
cd /mnt/c/ArchivePJT/Archive-World
python3 -m scripts.metropolitan.build_metropolitan \
  --output-root /mnt/c/ArchiveData/World/Generated/v7/metropolitan-seed-city-v1
python3 scripts/test_metropolitan_validation.py
python3 -m scripts.metropolitan.render_review_package \
  --output /mnt/c/ArchiveData/World/Generated/v7/metropolitan-seed-city-v1/review
```

Windows Blender나 Windows 도구에는 `C:/ArchiveData/...`를 전달하고 `/mnt/c/...`를 직접 전달하지 않는다.

## Viewer와 성능

`?mode=metropolitan`은 `VITE_ARCHIVE_WORLD_METROPOLITAN_BASE_URL`이 있을 때만 시작한다. 항상 `GENERATED METROPOLITAN PILOT / NOT CANONICAL / NOT V3 APPLIED`를 표시한다. 기본 V3 시작 경로는 바뀌지 않는다.

500/1,000/2,500/3,942 instance JSON encode/decode와 메모리는 측정하지만 이는 Viewer FPS가 아니다. 실제 GPU FPS, draw call, chunk load/unload는 GLB support family가 제작된 후 별도 Gate에서 측정해야 한다.

## 알려진 제한과 다음 Gate

- 49개 1920×1080 이미지는 계획 검토 다이어그램이며 photoreal render가 아니다.
- 40개 support family는 grammar 기반 계약이지 공식 validator를 통과한 신규 GLB가 아니다. 따라서 Building/Family visual gate는 미완료다.
- 도시 graph와 계획 metrics는 법규·교통·구조 엔지니어링 인증이 아니다.
- PO가 도시 구조와 status boundary를 승인한 뒤에만 support family production geometry, 실제 Viewer FPS 측정, district별 photoreal review로 진행한다.
- actual V3 application과 canonical promotion은 별도 명시 승인 없이는 금지다.

