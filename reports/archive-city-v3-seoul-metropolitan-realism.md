# Archive City v3 — Seoul Metropolitan Realism Pass

## 최종 판정

**VISUAL REALISM PARTIAL**

V3의 구조·공간·경로·리소스·Viewer Gate는 통과했다. 다만 최종 1600×1000 렌더를 검토하면, 현재의 procedural low-poly 산지·지면·건물 모듈은 수도권형 대도시의 기능적 구분과 밀도를 표현하지만 재질 세부·가로망·건물 facade의 다양성은 아직 사실적 기준에 미달한다. 따라서 기술 Gate PASS를 시각 사실성 PASS로 표현하지 않는다.

## 1. 인스턴스 변화

| 항목 | 이전 | 현재 | 변화 |
| --- | ---: | ---: | ---: |
| 전체 instance | 1,061 | 1,633 | +572 |
| 건물 | 671 | 936 | +265 |
| 차량 | 60 | 160 | +100 |
| 수목·가로등·공공 소품 | 245 | 445 | +200 |
| road module | 55 | 59 | +4 |
| road node / edge | 24 / 30 | 24 / 32 | 0 / +2 |
| canonical asset library | 93 | 100 | +7 |

신규 7개 library는 CBD·Residential·Market·Nexus·Logistics·Ledger·Port의 procedural ground 모듈이다. 모든 배치는 linked collection instance로 유지했고, Meshy 원본을 수정하거나 외부 3D/이미지 자산을 내려받지 않았다.

## 2. District별 현황

| District | 건물 | 차량 | 소품·수목 | 로컬 도로 | 총 instance |
| --- | ---: | ---: | ---: | ---: | ---: |
| ArchiveOS CBD | 111 | 0 | 36 | 12 | 160 |
| Market | 130 | 25 | 38 | 12 | 206 |
| Nexus Industrial | 172 | 25 | 33 | 12 | 243 |
| Logistics | 158 | 45 | 37 | 12 | 253 |
| Ledger Financial | 114 | 15 | 34 | 12 | 176 |
| Residential | 197 | 40 | 56 | 12 | 306 |
| Infrastructure / West Sea / Port / mountains / plains | 54 | 10 | 211 | 0 | 289 |

CBD는 landmark 주변의 낮은 office ring과 광장·주차·가로등을, Market은 retail/mall/low-rise mix를, Nexus는 factory/utility/tank/pipe-rack/warehouse를, Logistics는 cross-dock/warehouse/container yard를, Residential은 slab/tower/mid-rise/학교/놀이터/근린상가/주차를 확장했다. Port에는 crane/warehouse/container/dock을 추가했고, district별 ground에는 서로 다른 procedural paving·yard·grass·pedestrian band를 사용했다.

## 3. 지구 중심과 거리

| 관계 | 거리 |
| --- | ---: |
| ArchiveOS CBD ↔ Residential | 2,242 m |
| ArchiveOS CBD ↔ Market | 3,775 m |
| Nexus ↔ Logistics | 2,085 m |
| Residential ↔ Nexus | 4,378 m |
| West Sea Port ↔ Port freight hub | 968 m |
| West Sea Port ↔ Logistics center | 6,293 m |

CBD/Residential, CBD/Market, Nexus/Logistics, Residential/Industrial 완충은 요구 최소거리 이상이다. Port는 해안 freight hub와 1 km 이내로 연결되며, hub → southHub → Logistics의 화물 고속축을 추가했다. Port 중심과 Logistics 중심의 직접 거리 자체는 1 km를 초과하므로, 이 점은 시각/도시계획 현실성 blocker로 남긴다.

## 4. 렌더 산출물

다음 12개 PNG는 모두 1600×1000이고 파일 존재·크기를 확인했다.

1. `assets/previews/v3/city-overview.png`
2. `assets/previews/v3/birds-eye-view.png`
3. `assets/previews/v3/archiveos-overview.png`
4. `assets/previews/v3/residential-overview.png`
5. `assets/previews/v3/market-overview.png`
6. `assets/previews/v3/nexus-overview.png`
7. `assets/previews/v3/logistics-overview.png`
8. `assets/previews/v3/ledger-overview.png`
9. `assets/previews/v3/west-sea-port-overview.png`
10. `assets/previews/v3/han-river-bridges-overview.png`
11. `assets/previews/v3/north-east-mountains-overview.png`
12. `assets/previews/v3/south-plains-overview.png`

`infrastructure-overview.png`와 `topography-overview.png`는 보조 검토 이미지로 추가 유지한다.

## 5. 시각 개선 및 반복 노출

- 곡선 강, 3개 교량, 서해/항만, 남부 평야, 북·동 산지 및 녹지 완충을 유지했다.
- 단색 회색 ground를 district별 procedural urban/industrial/residential/port surface로 교체했다.
- 건물 군집은 방향·footprint·rotation·setback과 복수 모듈을 조합했다.
- 동일 real GLB는 링크 instance로만 반복했다.

그러나 원본 GLB의 linked material을 instance별로 변조하지 않았고, 일부 industrial/residential module은 여전히 일정한 높이·색·그리드 감을 보인다. 반복 노출 수준은 **중간~높음**이며, facade material override, roof accessory variation, 더 세분화된 local street/curb/crosswalk mesh가 다음 시각 품질 단계의 우선 항목이다.

## 6. 파일 크기 및 배포

| 대상 | 크기 |
| --- | ---: |
| `scenes/archive-city-v3.blend` | 402,950 B |
| 최대 district Blend (`infrastructure`) | 1,356,306 B |
| V3 scene/library/relative texture (backup 제외) | 1,212,190,417 B |
| 외부 texture directory | 646,073,871 B |
| V3 runtime GLB directory | 468,436,250 B |
| V3 previews | 21,293,420 B |
| Git LFS 후보 총량 (V3, ignored backup 제외) | 1,702,323,037 B |
| 최대 runtime GLB (`nexus.glb`) | 101,604,204 B |

100개 library, master 및 모든 district Blend는 500 MB 미만이다. 2 GiB 이상 추적 후보는 0개다. `.blend1/.blend2` backup 107개(약 1.21 GB)는 `.gitignore`로 제외한다. 기존 `archive-city-v1.blend` 2.417 GiB도 Git 배포 대상이 아니다.

Viewer build는 초기 `index` 4.93 kB (gzip 2.32 kB), lazy `viewer-runtime` 410.25 kB (gzip 26.03 kB), `three-core` 556.78 kB (gzip 139.38 kB), `three-extras` 63.97 kB (gzip 17.33 kB)로 분리됐다. Three.js/GLTF loader는 initial overview에서 내려받지 않는다.

## 7. 검증 결과

- V3 layout: **PASS** — 1,633 instances, 24 nodes, 32 edges.
- Road topology: **PASS** — 모든 핵심 district가 ArchiveOS graph에 연결됨.
- Spatial proxy validation: **PASS** — building overlap 0, ground-aligned 1,633/1,633, vehicle near route 160/160.
- V2 regression: **PASS** — 219 instances, 17 nodes, 20 edges. V2는 수정하지 않았다.
- Meshy checksum: **PASS** — 46/46, mismatch 0.
- Relative linked asset / packed texture: **PASS** — master + 7 districts, missing link 0, packed image 0.
- glTF validator: **PASS_WITH_WARNINGS** — runtime V3 GLB error 0, missing resource 0. 기존 generated tangent/sampler 관련 경고는 남음.
- Distribution validation: **PASS** — 500 MB 초과 Blend 0, 2 GiB 초과 후보 0.
- Viewer: **PASS** — TypeScript typecheck, Node test 1/1, production build.

## 8. 남은 blocker

1. Port 중심과 Logistics 중심의 실제 직접 거리는 6.29 km다. 현재는 coast freight hub와 고속 화물축으로 연결했으며, 1 km 직접 축 요구를 충족하려면 Logistics satellite 또는 도시 배치 재설계가 필요하다.
2. 현재 렌더는 low-poly 테스트 시각 언어가 강하다. facade/rooftop/curb/crosswalk/park/terrain variation과 더 자연스러운 산 능선·도로 연결을 추가하기 전에는 VISUAL REALISM PASS로 판정할 수 없다.
3. 이번 범위에서 clean-clone 재현은 지시대로 실행하지 않았다.

OCI upload, git add, commit, push, merge, Docker/Runtime 변경, Meshy 원본 수정은 수행하지 않았다.
