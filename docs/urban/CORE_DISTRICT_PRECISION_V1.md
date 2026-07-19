# Core District Precision V1

Metropolitan Planning Foundation은 `PASS`, Metropolitan Visual City는 `NOT_IMPLEMENTED`로 동결한다. 이 브랜치는 1.2 km × 1.0 km ArchiveOS–Ledger 경계를 실제 GLB와 Generated 전용 WebGL 장면으로 구현한다. Office V5는 geometry, material, score를 변경하지 않고 anchor instance로만 참조한다.

`family contract`, `planning proxy`, `actual GLB family`, `block configuration`, `actual 3D block`, `instance configuration`, `actual Viewer instance`, `planning diagram`, `actual rendered scene`은 서로 다른 상태다. actual GLB 생성·Khronos validation·WebGL 로드·실측 FPS가 없는 항목은 Production PASS가 아니다.

출력은 `C:/ArchiveData/World/Generated/v8/core-district-precision-v1`에만 기록하며 canonical, V3 layout, Runtime, main을 변경하지 않는다.

## 구현 결과와 품질 경계

- 동결 Office V5 anchor와 신규 support family 11종으로 actual family 12종, LOD GLB 36개를 구성했다.
- actual 3D block 22개와 building instance 220개를 WebGL 장면에 배치했다. planning proxy ratio는 0%다.
- street/public-realm/transit 통합 GLB는 raised sidewalk, curb, crosswalk, median, plaza, station entrance, shelter, tree, vehicle, human geometry를 포함한다.
- Khronos validator strict 결과는 37 GLB, error/warning/info 0이다.
- WebGL은 family별 `InstancedMesh` batching 후 draw call을 7,344에서 476으로 줄였다. Headless 1920×1080 측정은 약 27.7 FPS로 30 FPS Gate를 통과하지 못했다.
- 37장 actual WebGL screenshot을 생성했으나 night emissive, street camera composition, vegetation/human detail이 부족하다. Visual score는 68/C이므로 Production PASS가 아니다.

다음 Gate는 night/public-realm 재질, street camera, support-family facade 다양성 및 hardware Chrome 성능을 보강해 District 80/B 이상을 다시 검수하는 것이다. actual V3 application과 canonical promotion은 계속 금지한다.
