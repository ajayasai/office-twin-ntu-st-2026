"""Package source and selected demo videos without private settings or raw logs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED
from run_benchmark import code_digest

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=root / "dist")
parser.add_argument("--raw-video", type=Path, default=root / "dist" / "office-twin-demo.mp4")
parser.add_argument("--narrated-video", type=Path, default=root / "dist" / "office-twin-submission.mp4")
parser.add_argument("--video-url", default="https://youtu.be/oTTT0ECN25U")
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
    validation_dir = root / "docs" / "resource-sampling-fix"
    validation = json.loads((validation_dir / "test-provenance.json").read_text(encoding="utf-8"))
    integration_path = validation_dir / "integration-summary.json"
    integration = json.loads(integration_path.read_text(encoding="utf-8"))
    runtime_digest = code_digest(root)
    if not validation["passed"] or not integration["passed"] or runtime_digest != validation["runtime_sha256"]:
        raise RuntimeError("Packaged runtime does not match successful current validation")
    if hashlib.sha256((validation_dir / "tests.log").read_bytes()).hexdigest() != validation["published_log_sha256"]:
        raise RuntimeError("Current test log does not match its provenance")
    for relative, expected_hash in validation["source_file_sha256"].items():
        if hashlib.sha256((root / relative).read_bytes()).hexdigest() != expected_hash:
            raise RuntimeError(f"Tested source mismatch: {relative}")
    for relative, expected_hash in integration["source_files_sha256"].items():
        if hashlib.sha256((root / relative).read_bytes()).hexdigest() != expected_hash:
            raise RuntimeError(f"Integration evidence source mismatch: {relative}")
    frozen_commit = "051ec6871425ddaba9faeffed297a2168620e58c"
    changed_runtime_files = []
    for path in sorted((root / "office_twin").glob("*.py")):
        relative = path.relative_to(root).as_posix()
        frozen = subprocess.check_output(["git", "show", f"{frozen_commit}:{relative}"], cwd=root)
        if path.read_bytes().replace(b"\r\n", b"\n") != frozen.replace(b"\r\n", b"\n"):
            changed_runtime_files.append(relative)
    manifest = {
        "manifest_schema_version": 2,
        "project": "Office Twin",
        "source_commit": commit,
        "source_worktree_dirty": dirty,
        "status": "Updated evidence package for the submitted Office Twin entry",
        "packaged_runtime_sha256": runtime_digest,
        "runtime_digest_algorithm": validation["runtime_digest_algorithm"],
        "current_software_validation": {
            "tested_source_commit": validation["tested_source_commit"],
            "tested_runtime_sha256": validation["runtime_sha256"],
            "test_count": validation["tests"],
            "test_log_sha256": validation["published_log_sha256"],
            "test_provenance_sha256": hashlib.sha256((validation_dir / "test-provenance.json").read_bytes()).hexdigest(),
            "integration_evidence_sha256": hashlib.sha256(integration_path.read_bytes()).hexdigest(),
            "scope": "Automated software tests and a noninteractive resource-sampler check; historical native benchmark not rerun",
            "native_workflow_rerun": False,
            "human_run": False,
        },
        "historical_native_benchmark": {
            "source_commit": frozen_commit,
            "runtime_sha256": "ddc6560bcddd3a3a3074138525c121e3d75c58eda2ea1519e2dacad3319c8876",
            "applies_to_packaged_runtime": not changed_runtime_files,
            "runtime_files_changed_since_benchmark": changed_runtime_files,
            "comparison": "Source contents compared after CRLF-to-LF normalization; raw-byte runtime digest is recorded separately",
            "resource_measurements_recomputed": False,
        },
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
