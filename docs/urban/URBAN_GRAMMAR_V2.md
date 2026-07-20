# Archive Urban Grammar V2

Status: `DESIGN_CONTRACT / NOT_CANONICAL / NOT_V3_APPLIED`

## 1. 목적과 참조 경계

Archive Urban Grammar V2는 세계 주요 CBD와 수변 도시에서 특정 형태가 아니라 **도시가 작동하는 원리**를 추출해 ArchiveOS–Ledger Core + Urban Stream에 적용하는 공간 계약이다.

> Reference is used only to understand abstract spatial, operational, and visual-quality principles. No identifiable building, bridge, waterway, plaza, lighting arrangement, landmark, or urban plan may be reproduced.

허용되는 변환 순서는 다음뿐이다.

`Reference evidence → Urban principle → Archive grammar → Archive-native geometry → Archive scene evidence`

사진의 과장된 노출, 채도, 광고 화면, 특정 스카이라인 또는 특정 교량 실루엣은 목표가 아니다. 야간 사진은 건물 점유 패턴, 중경의 겹침, 밝고 어두운 영역의 위계, 저층부 연속성을 읽는 자료로만 사용한다.

## 2. 현재 Archive 장면과 참조 방향의 실제 차이

평가는 V13 대표 WebGL 캡처 4장과 실제 GLB 보고서를 함께 사용했다. 아래의 화면 비율은 픽셀 정밀 계측값이 아니라 대표 캡처에 대한 보수적 육안 판정이다.

| 항목 | 현재 Archive 상태 | 참조에서 읽히는 원리 | V2 판정 |
| --- | --- | --- | --- |
| 도시 밀도 | 건물 수는 충분하지만 포디움 사이와 수변 전경에 큰 비활성 면이 남는다. | 고층 밀도보다 먼저 저층 도시벽과 중경 레이어가 연속된다. | `FAIL` |
| 깊이 레이어 | 주요 거리 장면이 전경 포장–수로–건물의 2~3개 층으로 단순하다. | 전경 활동, 수변, 저층부, 중층 도시벽, 고층 피크가 4~6개 층으로 겹친다. | `FAIL` |
| 건물 외피 | `detachedWindowCount=0`은 통과했지만 굵고 균일한 격자, 얕은 벽 반환부, 반복 비율 때문에 창이 구조체와 분리된 표면 장식처럼 읽힌다. | 창은 벽 두께, 스팬드럴, 슬래브, 실내 그림자와 결합해 하나의 외피로 읽힌다. | `VISUAL_FAIL` |
| 지상층 | 실제 로비 깊이 계약은 있으나 거리에서 긴 불투명 포디움과 낮은 점유 밀도가 더 강하게 보인다. | 출입구, 투명 로비, 상업/공공 베이, 캐노피와 실내 점유가 연속된 보행 경험을 만든다. | `FAIL` |
| 수변 단면 | 물, 하상, 단차와 교량은 실제 형상이나 장거리 직선 수면과 반복 난간이 지배한다. | 수변은 상부 도시 레벨–하부 산책로–물의 3단 단면이며 장소별 폭과 접근 방식이 달라진다. | `PARTIAL` |
| 스카이라인 | 가느다란 계단형 타워와 유사한 옥상 캡이 반복되고, 저·중층 배경 조직이 약하다. | 피크, 보조 피크, 중층 도시벽, 낮은 공공건물, 열린 축이 함께 리듬을 만든다. | `FAIL` |
| 식재 | 식재 위치는 있으나 근거리에서 동일한 로우폴리 수관과 규칙적 간격이 보인다. | 수관의 비대칭, 층위, 하부 식재가 공간을 감싸고 출입구와 시선을 조절한다. | `FAIL` |
| 사람/차량 | 개체는 존재하지만 실루엣이 작고 흩어져 장소의 용도를 설명하지 못한다. | 출입, 대기, 식사, 횡단, 환승 같은 활동 군집이 전경–중경–배경을 구성한다. | `FAIL` |
| 야간 | 선택적 발광은 시작됐지만 포디움 조명이 긴 띠로 읽히고, 로비·교량 접근·수변 경계의 위계가 약하다. | 밝은 지상층, 선택적 사무실 점유, 제한된 크라운, 보행 안전 조명이 서로 다른 밝기 층을 만든다. | `FAIL` |
| 재질/대기 | 흰색·회색 면과 균일한 유리색이 많고, 접촉 그림자와 습윤/건조 차이가 약하다. | 석재–유리–금속–수면이 거칠기, 색온도, 반사와 그림자로 분리된다. | `FAIL` |
| 성능 | 근거리 품질을 늘리기 전에 이미 headless 평균이 30 FPS Gate 아래다. | 보이는 구역에만 품질을 집중하고 반복 요소는 인스턴싱하며 원경은 도시 실루엣 역할만 유지한다. | `FAIL` |

### 핵심 진단

현재 장면은 **오브젝트는 많지만 도시방이 적다**. 개선의 중심은 소품 수 증가가 아니라 다음 관계의 재구성이다.

1. 건물 본체와 포디움이 가로의 벽을 만든다.
2. 포디움 내부 점유가 외부 보행 공간으로 새어 나온다.
3. 수로 양안의 저층부가 서로 마주 보고 교량으로 연결된다.
4. 식재와 활동이 빈 공간을 가리는 장식이 아니라 공간의 경계와 용도를 만든다.
5. 고층은 반복 개체가 아니라 저·중층 도시벽 위의 선택적 피크가 된다.

## 3. 참조 도시에서 추출한 원리

| 참조 대상 | 관찰할 도시 원리 | Archive에 가져오지 않는 것 | Archive 변환 |
| --- | --- | --- | --- |
| Canary Wharf | 고밀도일수록 연결된 공공공간과 수변 접근의 중요성이 커진다. 광장·정원·수변 보행로가 개별 건물 사이를 연결한다. | 특정 부두 형상, 타워, 광장 배치 | Core의 각 블록을 `street room → lobby court → stream room`으로 연결한다. |
| Marina Bay | 연속적인 수변 보행축, 공개 공간, 보행·자전거 연결과 수변 쪽으로 낮아지는 스카이라인이 도시와 물의 관계를 읽게 한다. | 만의 형상, 특정 랜드마크, 교량 | Stream 양안의 연속 동선과 낮은 수변 저층부 뒤로 상승하는 Archive skyline을 만든다. |
| Roppongi Hills | 업무·문화·상업·주거 기능을 보행 범위에 겹치고, 고저차를 입체 보행으로 해결하며 지속적인 장소 운영으로 공간을 활성화한다. | 단지 배치, 특정 타워·정원 | Hero Zone마다 낮/저녁 활동 프로그램과 상·하부 동선을 함께 배치한다. |
| Otemachi–Marunouchi | 업무지구의 품질은 건물만 아니라 가로 운영, 계절 프로그램, 보행 우선 실험, 공공·민간 협력으로 완성된다. | 특정 거리 폭, 포장 패턴, 행사 | Ledger Boulevard에 시간대별 점유와 가변 좌석·행사 여지를 주되 브랜드를 넣지 않는다. |
| Songdo IBD | 수공간은 경관뿐 아니라 수질·안전·유지관리·생활 동선을 함께 가져야 한다. 동시에 큰 슈퍼블록과 비활성 전면은 경계해야 한다. | 수로 치수, 공원·교량 형태 | Stream에 유지관리·비상 접근을 유지하고 긴 블록은 통로와 저층 프로그램으로 잘게 나눈다. |
| Lujiazui / Huangpu waterfront | 단절된 수변을 보드워크·플랫폼·교량과 완행 이동망으로 연결하면 도시 전면이 공공 공간이 된다. | 강변 스카이라인과 특정 전망 구조 | Stream의 양안을 하나의 연속 공공 네트워크로 보고 끊김과 소유 중복을 허용하지 않는다. |
| Hudson Yards | 교통 접근, 고밀도 복합개발, 선형 공원이 함께 작동해야 밀도가 보행 가능성으로 전환된다. | 오브젝트형 랜드마크, 특정 데크·공원 | Transit Junction의 환승 동선이 plaza, frontage, stream promenade를 10분 생활권으로 묶는다. |
| Cheonggyecheon 주변 CBD | 수로 복원만으로 충분하지 않다. 보행·산업·커뮤니티 재생과 인접 저층부가 함께 바뀔 때 도시 촉매가 된다. 침수와 피난도 단면의 일부다. | 수로 폭·벽체·교량·조명 복제 | 물길보다 양안의 건물·보행·피난·프로그램을 먼저 검증한다. |
| Yeouido | 대형 업무지구에서 공원·수변·보행·자전거·대중교통의 연결이 도시 규모의 빈 공간을 완화한다. 넓은 도로로 인한 단절은 피해야 한다. | 특정 공원과 IFC 스카이라인 | Core boulevard를 건너는 횡단 빈도를 높이고 Stream–park 방향의 녹색 연결을 보존한다. |
| Busan Centum City | 업무·MICE·문화·상업의 혼합과 강변 공원, 보행교가 광역 시설 사이의 보행 연속성을 보완한다. | 특정 문화시설·교량·야경 | Transit·문화·수변 노드를 분리하지 않고 하나의 보행 시퀀스로 구성한다. |

## 4. Archive Urban Grammar V2 핵심 문법

아래 수치는 외부 도시를 복사한 값이 아니라 현재 1.2 km × 1.0 km Pilot을 위한 **Archive 설계 범위**다. 법정 설계나 실제 시공 기준이 아니며, 실제 적용 전 지역 법규와 접근성 기준을 별도로 검증해야 한다.

### G1. Urban room first

- 개별 건물보다 먼저 `street room`, `plaza room`, `stream room`, `transit room`, `service room`을 정의한다.
- 모든 건물은 최소 한 개의 공공 room을 형성하고, 반대편에 service room을 가진다.
- Hero Camera에서 건물 사이의 남은 공간이 아니라 **의도된 경계, 입구, 중심, 출구**가 읽혀야 한다.
- 30 m 이상 연속되는 무표정한 포디움, 20 m 이상 출입구 없는 Hero frontage, 용도 없는 포장 면은 금지한다.

### G2. Three-layer building

모든 주요 건물은 다음 세 층을 독립적으로 설계한다.

1. **Inhabited base**: 3~6층, clear ground-floor 4.5~6.5 m, interior depth 6~12 m.
2. **Urban body**: 반복 리듬을 가지되 4~8층마다 zone 변화, 실제 벽 반환부와 창 recess 0.25~0.9 m.
3. **Sky termination**: 기계실·스크린·테라스·parapet가 몸체와 통합된 옥상. 단순 상자 캡 금지.

창은 독립 판이 아니라 `wall return + sill + head + spandrel/slab + room-back shadow`로 닫힌 외피를 만든다. 기술적으로 detached mesh가 0이어도 다음 중 하나면 시각 실패다.

- 프레임 두께가 창 폭의 12%를 넘고 모든 층에서 동일함.
- 실내 그림자나 벽 두께가 보이지 않아 유리가 외벽 앞에 떠 보임.
- 같은 bay가 8개 층 이상 변화 없이 반복됨.
- facade grid와 massing setback의 기준선이 충돌함.

### G3. Inhabited frontage

| 구역 | 활성 전면 최소치 | 입구 간격 | 필수 점유 |
| --- | ---: | ---: | --- |
| Archive Water Plaza | 80% | 20~35 m | civic lobby, public bay, pavilion, café/community |
| Ledger Stream Terrace | 75% | 25~40 m | office lobby, café/meeting, retail/public bay |
| Transit Stream Junction | 75% | 15~30 m | station entry, waiting, kiosk, mobility service |
| Mixed Stream Corridor | 65% | 25~45 m | lobby + public/retail mix |
| General Core Boulevard | 60% | 30~50 m | lobby + public bay |

- frontage bay 폭은 4~9 m, 깊이는 6~12 m를 기본으로 한다.
- 근거리 frontage는 floor, ceiling, rear wall, column grid, door, mullion, furniture silhouette와 night state를 가진다.
- 동일 lobby/canopy module이 한 카메라에 2회 넘게 보이지 않게 한다.
- service frontage는 공공 전면과 같은 재질·조명으로 위장하지 않고 rear/service room에 배치한다.

### G4. Road and movement section

| Archive street type | 총 폭 범위 | 핵심 구성 | 실패 조건 |
| --- | ---: | --- | --- |
| Civic boulevard | 34~44 m | 4 vehicle lanes, median/turn pocket, protected cycle segment, 6~9 m pedestrian edges | 보행 횡단 120 m 초과, 양측 비활성 frontage |
| Ledger active street | 24~32 m | 2~4 lanes, drop-off pocket, 5~8 m sidewalks, tree/furniture zone | taxi와 보행 대기 충돌, 빈 석재 전면 |
| Transit frontage | 26~36 m | bus/taxi separation, cycle parking, sheltered wait, direct crossings | station entry가 차량 뒤에 숨음 |
| Local active street | 16~24 m | 2 lanes, 4~7 m pedestrian edges, loading by time window | 상시 loading이 active edge 점유 |
| Service street | 12~18 m | loading, fire access, utility, protected pedestrian strip | plaza freight intrusion, dead-end fire route |
| Stream promenade | 물 제외 양안 각 5~10 m | clear walk, furniture/planting band, lower access, emergency egress | 80 m 이상 접근 없음, 50 m 이상 동일 edge 반복 |

- 보행의 실제 clear width와 가구/식재 영역을 분리한다.
- 횡단보도는 블록 입구, transit, bridge landing의 desire line과 일치시킨다.
- 차도 폭을 넓혀 비어 보이는 문제를 해결하지 않는다. 필요 없는 아스팔트는 중간 섬, 식재, 보도 또는 활동 pocket으로 환원한다.

### G5. Block porosity and composition

- 일반 block frontage: 70~120 m. 120 m를 넘으면 45~70 m마다 passage, courtyard opening 또는 public lobby를 둔다.
- open-space proxy는 block 면적의 18~32% 범위에서 목적 있는 room으로 구성한다.
- tower는 podium 뒤로 6~15 m 물러나 보행 레벨의 하늘과 일조를 확보한다.
- Hero Zone tower-to-tower clear gap은 22~45 m를 기본으로 하되 view corridor는 30 m 이상 유지한다.
- 동일 family와 동일 orientation의 직접 인접을 금지하고, 한 카메라에서 동일 roofline이 2회 넘게 연속되지 않게 한다.
- 각 block은 `primary mass + secondary mass + low-rise edge + public void + rear service`의 다섯 역할 중 최소 네 개를 가진다.

### G6. Stream as an urban section

Stream은 물 표면이 아니라 다음의 결합체다.

`upper street → occupied frontage → terrace/steps/ramp → lower promenade → wet/dry edge → water → opposite edge → opposite frontage`

- water width는 8~16 m 안에서 구간별로 변한다.
- 상부 도시 레벨과 하부 promenade의 높이 차이는 1.8~4.5 m 범위에서 장소별로 달라진다.
- lower promenade clear width는 Hero Zone 5~8 m, green/service 구간 3.5~6 m를 기본으로 한다.
- barrier-free connection은 최대 80 m 간격, 일반 접근은 최대 60 m 간격을 목표로 한다.
- 동일 edge section은 50 m 이상 연속하지 않는다.
- bridge/crossing은 평균 80~150 m 간격으로 배치하되 실제 desire line과 연결한다.
- water material은 shallow edge, darker center, wet stone, dry stone을 분리하되 reflection으로 형상 부족을 숨기지 않는다.
- 유지관리·피난 경로가 끊긴 수변은 시각적으로 좋아도 실패다.

### G7. Skyline as a field, not a collection

| Tier | 상대 높이 | 역할 |
| --- | ---: | --- |
| 1 | district 95~100 percentile | Office V5 단일 main peak와 제한된 civic marker |
| 2 | 78~94 percentile | Ledger secondary peak, transit/stream framing |
| 3 | 55~77 percentile | 일반 high-rise urban wall |
| 4 | 25~54 percentile | 중층 배경 조직과 podium transition |
| 5 | 0~24 percentile | civic relief, pavilion, service edge, open-space frame |

- main peak와 secondary peak 사이에는 적어도 한 개의 mid-rise trough를 둔다.
- skyline 평가 시 높이뿐 아니라 width, crown, setback, facade orientation이 함께 달라야 한다.
- 동일한 가느다란 계단형 tower를 scale만 바꿔 반복하지 않는다.
- 수변에서는 낮은 foreground–중층 wall–고층 peak가 동시에 읽혀야 한다.

### G8. Activity before population

사람은 좌표 scatter가 아니라 다음 activity cluster로 배치한다.

- office arrival / lobby exit
- café queue / lunch terrace
- pair walking / group conversation
- stream sitting / bridge crossing
- transit wait / boarding / bicycle stop
- maintenance / delivery / service access
- dusk social / night walk

Hero street camera는 foreground 2~5명, midground 6~20명, background density를 갖고 최소 두 종류의 활동을 보여야 한다. 사람 수가 아니라 `행동–가구–입구–동선`의 관계를 검증한다.

### G9. Night occupancy hierarchy

야간은 건물 전체를 밝히지 않고 다음 네 층을 구분한다.

1. **Primary civic/transit rooms**: Archive Plaza, Ledger Terrace, Transit Junction.
2. **Occupied edge**: lobby, café/public frontage, bridge landing, main promenade.
3. **Orientation layer**: pocket node, tree/step light, wayfinding.
4. **Safety layer**: rear/service/fire route.

- ground-floor active frontage의 65~85%가 공간별로 다른 warm light를 가진다.
- tower window occupancy는 일반적으로 18~35% 범위의 군집 패턴을 사용하고 층별·zone별로 끊는다.
- lobby/public interior는 2700~3300 K, 일반 보행은 3000~3800 K, Archive identity accent는 제한된 4000~5000 K 범위를 사용한다.
- 모든 창 발광, 균일한 크라운 발광, 수면 자체 emissive, 청색 네온 과다는 금지한다.
- 밝은 점의 수보다 `입구 → 보행로 → 교량 → 목적지`가 연속적으로 읽히는지를 검증한다.

### G10. Landscape as spatial structure

- 근거리 나무는 trunk taper, primary branch, 3개 이상 crown lobe, 비대칭 silhouette를 가진다.
- 같은 variant의 직접 인접은 2개 이하로 제한한다.
- canopy는 entrance frame, shade room, service screen, view corridor 중 하나의 역할을 명시한다.
- groundcover와 shrub는 빈 포장 채우기가 아니라 edge, threshold, seating enclosure를 만든다.
- entrance, bridge approach, service/fire clear zone을 가리는 식재는 0이어야 한다.

### G11. Material and atmosphere

- ArchiveOS: warm light stone + neutral concrete + blue-gray glass + cool restrained metal + warm occupied interior.
- Ledger: limestone/granite base + neutral curtain wall + bronze/charcoal accent + warm lobby.
- Stream: shallow blue-gray water + dark bed + wet/dry stone difference + sparse timber accent + planted edge.
- facade base, recess, glass, frame의 luminance가 한 값으로 수렴하지 않게 한다.
- 접촉 그림자, wall return, sill/head shadow를 재질보다 우선한다. 색상 변경만으로 깊이를 만들지 않는다.
- day는 재질 구분, dusk는 실내외 전환, night는 점유와 동선을 평가한다.

### G12. Performance-aware detail

| 거리 | 품질 역할 | 구현 정책 |
| --- | --- | --- |
| Hero / 0~120 m | wall depth, ground floor, tree branch, activity, light fixture | LOD0, camera-visible detail 집중, shadow caster 선택 |
| Mid / 120~350 m | facade zone, podium, crown, canopy silhouette | LOD1, geometry instancing, consolidated materials |
| Far / 350 m+ | skyline, major light cluster, urban wall | LOD2, facade micro-detail 제거, no individual furniture |

- draw calls 350 이하를 목표로 하고 400 이상은 실패다.
- screenshot capture와 FPS 측정을 분리한다.
- vegetation, public realm, human, vehicle은 family별 instancing을 사용한다.
- 모든 조명은 거리와 camera corridor에 따라 cull한다.
- 수면은 1~3개 material family로 통합하고 중복 투명면을 금지한다.
- 성능을 위해 사람·식재·그림자를 전부 제거하는 것은 품질 실패다.

## 5. Archive-native identity

Archive City의 정체성은 특정 랜드마크 모사가 아니라 반복되는 관계에서 나온다.

1. **Civic datum**: 4.5~6.0 m 높이의 깊은 공공 캐노피·로비 수평선이 plaza와 stream을 연결한다.
2. **Deep frame**: 0.35~1.2 m의 석재/금속 frame과 recess가 유리 외피를 실제 벽 안에 넣는다.
3. **Warm interior / cool civic exterior**: 따뜻한 점유 공간과 절제된 청회색 외부가 대비한다.
4. **Water seam**: 물은 중심 오브젝트가 아니라 양안의 공공 room을 연결하는 연속 seam이다.
5. **Quiet technology**: 읽을 수 없는 blank information panel, 제한된 light line, 투명 civic lobby로 ArchiveOS를 표현한다. 로고와 SF 네온은 사용하지 않는다.
6. **Ledger gravity**: 더 무거운 base, 좁고 깊은 bay, 정돈된 terrace와 따뜻한 lobby로 금융지구의 안정감을 만든다.

## 6. 구현 우선순위

1. **도시방 재구성**: 빈 포장과 고립된 포디움을 제거하고 양측 저층부가 마주 보는 단면을 만든다.
2. **건물 외피 재구성**: 창 개수보다 wall–window–room의 결합과 facade zone 변화를 먼저 고친다.
3. **지상층 점유**: 실제 깊이와 실내 그림자가 보이는 로비·공공·상업 frontage를 연속시킨다.
4. **Stream section**: 폭·높이·접근·edge를 장소별로 바꾸고 양안을 동선으로 묶는다.
5. **중경 도시벽과 skyline**: Hero foreground 뒤에 2~3개의 중경 레이어를 만든 뒤 peak를 배치한다.
6. **활동과 식재**: 용도와 시선에 따라 cluster를 구성한다.
7. **야간 점유**: base, path, bridge, selective tower occupancy를 독립 설계한다.
8. **성능 회수**: 시각적으로 승인된 구성에서 instancing, LOD, light/shadow culling을 적용한다.

## 7. 장면 수용 기준

### Street camera

- eye height 1.60~1.75 m, 기본 focal length 28~35 mm.
- blank pavement 15% 이하, foreground obstruction 12% 이하.
- 최소 4개 depth layer: foreground activity, stream/street, occupied base, mid/high skyline.
- active frontage, 실제 entrance, human scale, material depth와 light source가 한 장에서 확인되어야 한다.
- 벽만 보이는 장면, 수로만 보이는 장면, 건물 상층만 보이는 장면은 실패다.

### Aerial camera

- main peak, secondary peak, mid-rise wall, civic relief, stream corridor가 동시에 읽힌다.
- 동일 family/orientation 3개 연속, 반복 roofline 3개 연속, 의미 없는 대형 공백은 실패다.
- 야간은 광도 과장이 아니라 district별 점유 패턴으로 구분한다.

### Hero Zone

- Archive Water Plaza, Ledger Stream Terrace, Transit Stream Junction 각각 architecture, ground floor, stream relation, public realm, landscape, activity, night, camera, performance를 독립 통과한다.
- technical validator PASS가 visual PASS를 대체하지 않는다.
- current screenshots와 나란히 보았을 때 도시방, 점유, 깊이, 활동, 조명에서 명확한 질적 도약이 없으면 점수와 무관하게 실패다.

## 8. 금지되는 지름길

- 건물 수, 창 수, 사람 수 또는 조명 수만 늘리기
- 동일 tower의 높이·폭·색만 바꿔 family로 세기
- 포디움 앞에 작은 box를 붙여 active frontage로 보고하기
- 거대한 비어 있는 plaza를 civic scale로 해석하기
- 전체 창을 발광시켜 도시 활동으로 보이게 하기
- 수면 반사와 bloom으로 수변 형상 부족을 숨기기
- 항공 카메라로 근거리 결함을 가리기
- reference 도시의 교량, 건물, 수로, 광장 또는 조명 배치를 직접 복제하기

## 9. 근거 자료

- [Canary Wharf public realm and masterplan material](https://group.canarywharf.com/wp-content/uploads/2021/04/NQ.PA_.07_Design-Access-Statement_Part-3-July-2020.pdf)
- [Canary Wharf Middle Dock and green spine consultation](https://group.canarywharf.com/wp-content/uploads/2024/04/240408-MSWS-Consultation-content_For_Web.pdf)
- [URA Marina South urban-design guidance](https://www.ura.gov.sg/guidelines/urban-design/marina-south/)
- [URA Marina Bay planning history](https://www.ura.gov.sg/land-planning/shaping-our-city/marina-bay/)
- [Mori Building Roppongi Hills project](https://www.mori.co.jp/en/projects/roppongihills/)
- [Otemachi–Marunouchi–Yurakucho area management](https://tokyo-omy.jp/)
- [IFEZ Songdo waterfront guidance](https://www.ifez.go.kr/world/content/view.do?sn=511)
- [Shanghai Huangpu River waterfront public-space plan](https://www.shanghai.gov.cn/shssswzxgh/20200820/0001-22403_50731.html)
- [NYC Hudson Yards special district purpose](https://zr.planning.nyc.gov/node/19454)
- [NYC Hudson Yards planning overview](https://www.nyc.gov/assets/planning/download/pdf/plans/hudson-yards/hyards.pdf)
- [Seoul Cheonggyecheon official overview](https://english.seoul.go.kr/service/amusement/stream/1-cheonggyecheon/)
- [Seoul Yeouido Park](https://english.seoul.go.kr/yeouido-park/)
- [Busan Suyeonggang pedestrian connection](https://www.busan.go.kr/bige/daily-busan/view?bbsNo=10&dataNo=72514&srchCl=Daily+Busan)

## 10. 적용 상태

- 이 문서는 구현 방향과 수용 기준을 정의한다.
- canonical, V3 layout, Runtime, main을 변경하지 않는다.
- Office V5 geometry/material/score를 변경하지 않는다.
- 특정 참조의 직접 복제 상태는 `0`이어야 한다.
- 다음 geometry rework는 이 문서의 `G1 → G3 → G6 → G7 → G8/G9 → G12` 순서를 따른다.
