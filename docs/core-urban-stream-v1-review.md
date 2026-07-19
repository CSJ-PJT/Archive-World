# Archive Core District + Urban Stream V1 Review

이 문서는 특정 실제 수로를 복제하지 않은 Generated 전용 3D Pilot의 검수 경계를 기록한다.

## 구현 결과

- 785.88m 실제 수면·하상·수변 geometry
- 실제로 인스턴스화된 edge section 10종
- 보행교 5개, service crossing 1개, street crossing 1개
- Archive Water Plaza, Ledger Stream Terrace, Transit Stream Junction
- pocket node 4개와 accessible access 8개
- Stream-facing micro-architecture 18개: door, glazing, canopy, blank signage, tactile approach 포함
- 기존 12 family, 22 block, 220 building instance 및 Office V5 anchor 불변
- 24 camera × day/dusk/night = 실제 WebGL screenshot 72장

## 판정 경계

기술 계약과 GLB 검증은 통과했지만, close-range vegetation, 일부 빈 포장, 야간 조명 위계 및 Headless Chrome 성능이 목표에 미달한다. 따라서 이 결과는 `PARTIAL`, `73/C`이며 canonical 또는 V3 적용 후보가 아니다.

## 성능 및 시각 한계

- LOD1 Headless: day 26.3 FPS / 1% low 13.9, night 27.5 / 15.6
- LOD2 Headless: day 26.6 FPS / 15.3, night 26.5 / 11.9
- draw calls 360(LOD1), 358(LOD2), 400 이하 계약은 통과
- Hardware Chrome: 측정하지 못했으므로 `UNKNOWN`

다음 Gate는 지상층/조경 geometry 재작업, Stream 전용 야간 조명, 성능 병목 profiling 후 같은 카메라에서 재검수하는 것이다.
