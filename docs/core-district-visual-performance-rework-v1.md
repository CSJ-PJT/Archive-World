# Core District Visual & Performance Rework V1

V8의 68/C와 Headless Chrome 27.7 FPS를 고정 기준선으로 삼았다. V9는 11개 지원 Family의 glTF PBR 색상 계층, 지상층 출입구 요소, 다중 수관 식생, public-realm 그룹 배치, ACES 조명, GLB material batching을 적용한다.

최종 판정은 **PARTIAL**이다. 실제 WebGL 캡처에서 재질 구분과 aerial hierarchy는 개선됐지만, street-level podium·보행 공간·야간 로비/환승 조명은 B등급에 미달한다. Headless Chrome은 draw call 330으로 예산을 통과했으나 평균 FPS와 1% low가 목표에 미달했다. Hardware Chrome 측정은 유효 표본을 얻지 못해 UNKNOWN이다.

따라서 새 District 확장, canonical 승격, V3 적용은 허용하지 않는다. 다음 작업은 새로운 범위가 아니라 현재 District의 street-level geometry와 night-light fixture를 실제 geometry/material 단위로 다시 만드는 것이다.
