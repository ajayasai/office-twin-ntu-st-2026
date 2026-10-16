"""Package source and selected demo videos without private settings or raw logs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=root / "dist")
parser.add_argument("--raw-video", type=Path, default=root / "dist" / "office-twin-demo.mp4")
parser.add_argument("--narrated-video", type=Path, default=root / "dist" / "office-twin-submission.mp4")
parser.add_argument("--video-url", default="https://youtu.be/0OpIetkSomM")
parser.add_argument("--video-scope", default="15 October functional demonstration; subsequent measurements are documented separately in the source archive")
args = parser.parse_args()
output_dir = args.output_dir.resolve()
output = output_dir / "office-twin-source.zip"
output.parent.mkdir(parents=True, exist_ok=True)
files = [root / name for name in ["README.md", "STRATEGY.md", "SUBMISSION.md", "requirements.txt", "Launch.cmd", ".gitignore"]]
for directory in ["office_twin", "tests", "docs", "scenarios", "tools"]:
    files.extend(p for p in (root / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
with ZipFile(output, "w", ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path, path.relative_to(root))
print(output)

# Build a reproducible handoff containing only this explicit artifact allowlist.
videos = [args.raw_video.resolve(), args.narrated_video.resolve()]
if all(path.is_file() for path in videos):
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=root, text=True).strip())
    artifacts = [(output, "office-twin-source.zip"),
                 (videos[0], "office-twin-demo.mp4"),
                 (videos[1], "office-twin-submission.mp4")]
    manifest = {
        "project": "Office Twin",
        "source_commit": commit,
        "source_worktree_dirty": dirty,
        "status": "Updated evidence package for the submitted Office Twin entry",
        "tested_runtime_commit": "051ec6871425ddaba9faeffed297a2168620e58c",
        "packaged_video_scope": args.video_scope,
        "repository": "https://github.com/ajayasai/office-twin-ntu-st-2026",
        "video": args.video_url,
        "files": [
            {"name": archive_name, "bytes": path.stat().st_size,
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path, archive_name in artifacts
        ],
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    bundle = output_dir / "office-twin-review-pack.zip"
    with ZipFile(bundle, "w", ZIP_DEFLATED) as archive:
        for path, archive_name in [*artifacts, (manifest_path, "manifest.json")]:
            archive.write(path, archive_name)
    print(bundle)
