# WSL and Windows Path Handling

- WSL tools use `/mnt/c/ArchivePJT/Archive-World` and `/mnt/c/ArchiveData/World/Generated`.
- Windows Blender receives native paths such as `C:/ArchiveData/World/Generated`; never pass `/mnt/c/...` directly to `blender.exe`.
- Convert repository and output paths at the process boundary, not inside tracked contracts.
- Do not record user-home paths, previous-PC paths, or `ArchiveTransfer` paths in source or generated manifests.
- Prefer WSL-local temporary files for Linux-side atomic generation, then publish to the final Windows Generated root.
- Generated outputs, logs, GLBs, Blend files, textures, and high-resolution renders stay outside Git.
