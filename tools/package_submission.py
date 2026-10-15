"""Package source and selected demo videos without private settings or raw logs."""
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
output = root / "dist" / "office-twin-source.zip"
output.parent.mkdir(exist_ok=True)
files = [root / name for name in ["README.md", "STRATEGY.md", "SUBMISSION.md", "requirements.txt", "Launch.cmd", ".gitignore"]]
for directory in ["office_twin", "tests", "docs", "scenarios", "tools"]:
    files.extend(p for p in (root / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
with ZipFile(output, "w", ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path, path.relative_to(root))
print(output)

# Build a reproducible handoff containing only this explicit artifact allowlist.
videos = [root / "dist" / name for name in
          ("office-twin-demo.mp4", "office-twin-submission.mp4")]
if all(path.is_file() for path in videos):
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=root, text=True).strip())
    artifacts = [output, *videos]
    manifest = {
        "project": "Office Twin",
        "source_commit": commit,
        "source_worktree_dirty": dirty,
        "status": "Review package; Devpost draft held until two teammates join",
        "repository": "https://github.com/ajayasai/office-twin-ntu-st-2026",
        "video": "https://youtu.be/0OpIetkSomM",
        "files": [
            {"name": path.name, "bytes": path.stat().st_size,
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in artifacts
        ],
    }
    manifest_path = root / "dist" / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    bundle = root / "dist" / "office-twin-review-pack.zip"
    with ZipFile(bundle, "w", ZIP_DEFLATED) as archive:
        for path in [*artifacts, manifest_path]:
            archive.write(path, path.name)
    print(bundle)
