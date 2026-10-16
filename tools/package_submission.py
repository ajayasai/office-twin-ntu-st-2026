"""Package source and selected videos with separately scoped validation records."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

if __package__:
    from .run_benchmark import code_digest
else:
    from run_benchmark import code_digest


ROOT = Path(__file__).resolve().parents[1]
SAMPLER_PATH = Path("docs/resource-sampling-fix/integration-summary.json")
SAMPLER_SOURCES = {"office_twin/evidence.py", "office_twin/observer.py"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_files(root):
    files = [root / name for name in
             ["README.md", "STRATEGY.md", "SUBMISSION.md", "requirements.txt", "Launch.cmd", ".gitignore"]]
    for directory in ["office_twin", "tests", "docs", "scenarios", "tools"]:
        files.extend(path for path in (root / directory).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc")
    return sorted(files)


def repository_path(root, path):
    path = Path(path)
    resolved = (path if path.is_absolute() else root / path).resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise RuntimeError(f"Evidence path must be a repository file: {path}")
    return resolved


def published_path(root, path):
    resolved = repository_path(root, path)
    if resolved not in {item.resolve() for item in source_files(root)}:
        raise RuntimeError("Validation evidence must be included in the source archive")
    return resolved


def read_object(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object: {path}")
    return value


def verify_source_hashes(root, hashes, label, required=()):
    if not isinstance(hashes, dict) or not hashes:
        raise RuntimeError(f"{label} has no source hashes")
    if not set(required).issubset(hashes):
        raise RuntimeError(f"{label} omits required source hashes")
    for relative, expected in hashes.items():
        if not isinstance(relative, str) or Path(relative).is_absolute():
            raise RuntimeError(f"{label} source paths must be repository-relative")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise RuntimeError(f"{label} contains an invalid source hash")
        if sha256(repository_path(root, relative)) != expected:
            raise RuntimeError(f"{label} source mismatch: {relative}")


def current_validation(root, validation_dir):
    validation_dir = Path(validation_dir)
    if not validation_dir.is_absolute():
        validation_dir = root / validation_dir
    provenance_path = published_path(root, validation_dir / "test-provenance.json")
    log_path = published_path(root, validation_dir / "tests.log")
    validation = read_object(provenance_path)
    runtime_digest = code_digest(root)
    if validation.get("passed") is not True or runtime_digest != validation.get("runtime_sha256"):
        raise RuntimeError("Packaged runtime does not match successful current validation")
    if type(validation.get("tests")) is not int or validation["tests"] < 1:
        raise RuntimeError("Current validation must report a positive test count")
    if sha256(log_path) != validation.get("published_log_sha256"):
        raise RuntimeError("Current test log does not match its provenance")
    required = {"requirements.txt"}
    for directory in ("office_twin", "tests", "tools"):
        required.update(path.relative_to(root).as_posix() for path in (root / directory).rglob("*")
                        if path.is_file() and path.suffix in {".py", ".ps1"}
                        and "__pycache__" not in path.parts)
    verify_source_hashes(root, validation.get("source_file_sha256"), "Tested", required)
    return {
        "tested_source_commit": validation["tested_source_commit"],
        "tested_runtime_sha256": validation["runtime_sha256"],
        "runtime_digest_algorithm": validation["runtime_digest_algorithm"],
        "test_count": validation["tests"],
        "test_log_path": log_path.relative_to(root).as_posix(),
        "test_log_sha256": validation["published_log_sha256"],
        "test_provenance_path": provenance_path.relative_to(root).as_posix(),
        "test_provenance_sha256": sha256(provenance_path),
        "scope": "Current automated software tests; historical native benchmark and sampler probe remain separately scoped",
        "native_workflow_rerun": False,
        "human_run": False,
        "input_delivery_validated": False,
    }


def historical_sampler_validation(root):
    path = published_path(root, SAMPLER_PATH)
    integration = read_object(path)
    checks = integration.get("checks")
    if (integration.get("passed") is not True or not isinstance(checks, dict)
            or not checks or any(value is not True for value in checks.values())):
        raise RuntimeError("Historical sampler verification did not pass every recorded check")
    hashes = integration.get("source_files_sha256")
    if not isinstance(hashes, dict) or set(hashes) != SAMPLER_SOURCES:
        raise RuntimeError("Historical sampler verification must identify its two measured modules")
    verify_source_hashes(root, hashes, "Historical sampler", SAMPLER_SOURCES)
    return {
        "evidence_path": path.relative_to(root).as_posix(),
        "evidence_sha256": sha256(path),
        "source_commit": integration["source_commit"],
        "source_worktree_had_uncommitted_fix": integration["source_worktree_had_uncommitted_fix"],
        "check_count": len(checks),
        "passed": True,
        "source_files_sha256": hashes,
        "listed_modules_match_packaged_sources": True,
        "scope": "Retained noninteractive sampler probe; compatibility is limited to the unchanged listed modules, not validation of a new timing mode",
        "probe_rerun": False,
        "native_workflow_rerun": False,
        "human_run": False,
    }


def timing_validation(root, path):
    """Validate the optional, separately generated aggregate-fit report."""
    path = published_path(root, path)
    report = read_object(path)
    checks = report.get("checks")
    if (report.get("schema_version") != 1
            or report.get("kind") != "offline-synthetic-key-timing-verification"
            or report.get("passed") is not True
            or not isinstance(checks, dict) or not checks
            or any(value is not True for value in checks.values())):
        raise RuntimeError("Timing-model verification did not pass every recorded check")
    verify_source_hashes(root, report.get("source_files_sha256"), "Timing verification",
                         {"office_twin/timing.py", "tools/verify_human_timing.py"})
    reference = report.get("reference")
    if not isinstance(reference, dict) or reference.get("path") != "docs/human-baseline/aggregate.json":
        raise RuntimeError("Timing verification must identify the retained human aggregate file")
    baseline_path = published_path(root, reference["path"])
    if reference.get("sha256") != sha256(baseline_path):
        raise RuntimeError("Timing verification baseline hash does not match the retained aggregates")
    claims = report.get("claims")
    expected_claims = {"synthetic_samples": True, "new_human_run": False,
                       "native_input_observed": False, "elapsed_task_duration_validated": False,
                       "human_distribution_tested": False, "official_score_claimed": False}
    if not isinstance(claims, dict) or any(claims.get(key) is not value for key, value in expected_claims.items()):
        raise RuntimeError("Timing verification must retain its synthetic-only claim boundaries")
    return {
        "evidence_path": path.relative_to(root).as_posix(),
        "evidence_sha256": sha256(path),
        "passed": True,
        "check_count": len(checks),
        "source_files_sha256": report["source_files_sha256"],
        "baseline_path": reference["path"],
        "baseline_sha256": reference["sha256"],
        "scope": "Synthetic requested-delay verification against participant-supplied aggregate targets; not independent human-similarity or OS input-delivery validation",
        "native_workflow_rerun": False,
        "human_run": False,
        "input_delivery_validated": False,
    }


def build_manifest(root, args):
    validation = current_validation(root, args.validation_dir)
    sampler = historical_sampler_validation(root)
    timing = timing_validation(root, args.timing_verification) if args.timing_verification else None
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip())
    frozen_commit = "051ec6871425ddaba9faeffed297a2168620e58c"
    changed_runtime_files = []
    for path in sorted((root / "office_twin").glob("*.py")):
        relative = path.relative_to(root).as_posix()
        frozen = subprocess.check_output(["git", "show", f"{frozen_commit}:{relative}"], cwd=root)
        if path.read_bytes().replace(b"\r\n", b"\n") != frozen.replace(b"\r\n", b"\n"):
            changed_runtime_files.append(relative)
    manifest = {
        "manifest_schema_version": 3,
        "project": "Office Twin",
        "source_commit": commit,
        "source_worktree_dirty": dirty,
        "status": "Updated evidence package for the submitted Office Twin entry",
        "packaged_runtime_sha256": validation["tested_runtime_sha256"],
        "runtime_digest_algorithm": validation["runtime_digest_algorithm"],
        "current_software_validation": validation,
        "historical_sampler_verification": sampler,
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
    }
    if timing is not None:
        manifest["timing_model_verification"] = timing
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--raw-video", type=Path, default=ROOT / "dist" / "office-twin-demo.mp4")
    parser.add_argument("--narrated-video", type=Path, default=ROOT / "dist" / "office-twin-submission.mp4")
    parser.add_argument("--validation-dir", type=Path, default=ROOT / "docs" / "resource-sampling-fix")
    parser.add_argument("--timing-verification", type=Path, help="Published aggregate-fit verification JSON")
    parser.add_argument("--video-url", default="https://youtu.be/oTTT0ECN25U")
    parser.add_argument("--video-scope", default="15 October functional demonstration; subsequent measurements are documented separately in the source archive")
    args = parser.parse_args(argv)
    # Complete validation before creating or overwriting any output artifact.
    manifest = build_manifest(ROOT, args)
    output_dir = args.output_dir.resolve()
    output = output_dir / "office-twin-source.zip"
    output_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in source_files(ROOT):
            archive.write(path, path.relative_to(ROOT))
    print(output)
    videos = [args.raw_video.resolve(), args.narrated_video.resolve()]
    if all(path.is_file() for path in videos):
        artifacts = [(output, "office-twin-source.zip"), (videos[0], "office-twin-demo.mp4"),
                     (videos[1], "office-twin-submission.mp4")]
        manifest["files"] = [{"name": name, "bytes": path.stat().st_size, "sha256": sha256(path)}
                             for path, name in artifacts]
        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        bundle = output_dir / "office-twin-review-pack.zip"
        with ZipFile(bundle, "w", ZIP_DEFLATED) as archive:
            for path, name in [*artifacts, (manifest_path, "manifest.json")]:
                archive.write(path, name)
        print(bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
