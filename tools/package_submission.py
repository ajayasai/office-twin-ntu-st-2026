"""Package source and documentation without private settings or local evidence."""
from pathlib import Path
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
