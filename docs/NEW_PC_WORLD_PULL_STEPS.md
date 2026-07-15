# Archive-World 새 PC Pull 및 복원 절차

Ubuntu/WSL에서 실행한다.

```bash
mkdir -p /mnt/c/ArchivePJT
cd /mnt/c/ArchivePJT
git clone https://github.com/CSJ-PJT/Archive-World.git Archive-World
cd Archive-World

git fetch origin --prune
git checkout feat/archive-world-v1
git pull --ff-only origin feat/archive-world-v1
git lfs pull
git status --short --branch
```

기대하는 V3 기준 커밋은 `5c59346` 이상이다. `git lfs ls-files`로 LFS 파일을 확인한다.

## 로컬 이전 패키지 복원

별도 전달된 패키지와 checksum 파일을 같은 전송 폴더에 둔다.

```bash
cd /mnt/c/ArchiveTransfer
sha256sum -c Archive-World-Local-Handoff-20260715-2100.sha256

tmpdir="$(mktemp -d)"
tar -xzf Archive-World-Local-Handoff-20260715-2100.tar.gz -C "$tmpdir"
cp -a "$tmpdir/assets/." /mnt/c/ArchivePJT/Archive-World/assets/
rm -rf "$tmpdir"
```

복원 후 확인한다.

```bash
cd /mnt/c/ArchivePJT/Archive-World
test -f assets/runtime/v2/asset-library.json
find assets/runtime/v2/library -type f -name '*.glb' | wc -l
```

## Viewer 검증

```bash
cd /mnt/c/ArchivePJT/Archive-World/web
npm ci
npm run typecheck
npm test
npm run build
```

## Blender 확인 및 재현

Scene 재생성·렌더가 필요한 경우에만 Blender 실행 파일을 찾고 `BLENDER_PATH`를 설정한다. 프로젝트 파일에는 로컬 절대경로를 쓰지 않는다.

```bash
cd /mnt/c/ArchivePJT/Archive-World
node src/validate-world-v3.mjs
node src/validate-world-v3-spatial.mjs
node src/validate-world-v2.mjs
```

Git add, commit, push, main merge는 검증 작업 중 수행하지 않는다.
