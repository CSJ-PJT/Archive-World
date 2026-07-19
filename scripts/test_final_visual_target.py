from pathlib import Path

text = Path("docs/core-urban-stream-final-visual-target.md").read_text(encoding="utf-8")
assert "CONCEPT TARGET" in text
assert "No direct reproduction" in text
assert "ARCHIVE_NATIVE_PROCEDURAL_NO_DIRECT_COPY" in text
assert "lower promenade" in text and "transparent lobby" in text
print("final visual target contract: PASS")
