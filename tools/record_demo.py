"""Record a real local desktop demonstration with an explicit capture label.

Requires ffmpeg on PATH. Use only the dedicated synthetic demo windows.
This is a recording run, not a controlled performance benchmark.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from office_twin.runner import RunConfig, run
from office_twin.report import generate_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sheet-url", required=True)
    parser.add_argument("--scenario", default="")
    parser.add_argument("--seed", type=int, default=73)
    parser.add_argument("--output", default="runs/demo")
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("ffmpeg must be installed and available on PATH")
    destination = Path(args.output).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    video = destination / f"office-twin-desktop-{stamp}.mp4"
    label = destination / "recording-label.txt"
    label.write_text("OFFICE TWIN  |  Real Chrome + Google Sheets + Notepad  |  Normal speed (1x)", encoding="utf-8")
    # textfile path and cwd avoid filter escaping of arbitrary user paths.
    filters = "scale=1920:-2,drawbox=x=0:y=0:w=iw:h=44:color=0x101b2d:t=fill,drawtext=textfile=recording-label.txt:fontfile='C\\:/Windows/Fonts/segoeui.ttf':fontcolor=white:fontsize=22:x=24:y=10,drawbox=x=0:y=ih-45:w=iw:h=45:color=0x101b2d:t=fill"
    command = [ffmpeg, "-y", "-hide_banner", "-loglevel", "warning", "-f", "gdigrab", "-framerate", "15", "-i", "desktop",
               "-vf", filters, "-c:v", "libx264", "-preset", "ultrafast", "-crf", "25", "-pix_fmt", "yuv420p", str(video)]
    with (destination / f"capture-{stamp}.log").open("wb") as log:
        capture = subprocess.Popen(command, cwd=destination, stdin=subprocess.PIPE, stdout=log, stderr=log,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        time.sleep(1)
        if capture.poll() is not None:
            raise RuntimeError("Screen capture did not start; inspect capture log")
        try:
            summary = run(RunConfig(mode="desktop", workflow="sheets", timing="contextual", seed=args.seed,
                                    sheet_url=args.sheet_url, scenario=args.scenario, output=str(destination)),
                          on_event=lambda event: print(event["label"], flush=True) if "label" in event else None)
            time.sleep(2)
        finally:
            if capture.poll() is None:
                try:
                    capture.communicate(b"q\n", timeout=15)
                except subprocess.TimeoutExpired:
                    capture.terminate()
                    capture.wait(timeout=5)
    summary["screen_recording"] = {"path": str(video), "fps": 15, "speed": "real time 1x",
                                   "scope": "Primary desktop with top and bottom task banners; no microphone",
                                   "benchmark_warning": "Screen capture was active. Do not compare performance with runs recorded under different conditions."}
    run_dir = Path(summary["run_directory"])
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    generate_report(run_dir)
    print(json.dumps({k: summary[k] for k in ["status", "success", "run_directory", "screen_recording"]}, indent=2))
    return 0 if summary["success"] and video.is_file() and capture.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
