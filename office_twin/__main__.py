import argparse
import importlib.util
import json
import platform
import sys


def main():
    parser = argparse.ArgumentParser(description="Office Twin — reproducible desktop work sessions")
    parser.add_argument("--mode", choices=["simulate", "desktop"], help="Omit to launch the control panel")
    parser.add_argument("--workflow", choices=["notepad", "sheets", "office"], default="notepad")
    parser.add_argument("--timing", choices=["contextual", "fixed"], default="contextual")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--scale", type=float, default=1.0, help="Timing multiplier; 0 is a fast plan/test mode")
    parser.add_argument("--output", help="Directory containing unique per-run folders")
    parser.add_argument("--sheet-url", default="", help="Dedicated scratch Google Sheet for visible UI editing")
    parser.add_argument("--scenario", default="", help="Optional synthetic procurement scenario JSON")
    parser.add_argument("--doctor", action="store_true", help="Read-only dependency check")
    args = parser.parse_args()
    if args.doctor:
        print(json.dumps({"python": sys.version.split()[0], "platform": platform.platform(),
                          "desktop_supported": sys.platform == "win32",
                          "dependencies": {p: importlib.util.find_spec(p) is not None for p in ["tkinter", "pywinauto", "psutil"]},
                          "note": "Dependency availability does not verify Office activation, browser login, or UI compatibility."}, indent=2))
        return 0
    if args.mode is None:
        from .gui import launch
        launch()
        return 0
    from .runner import RunConfig, run
    kwargs = {k: v for k, v in vars(args).items() if k not in {"doctor", "output"}}
    if args.output:
        kwargs["output"] = args.output
    try:
        summary = run(RunConfig(**kwargs), on_event=lambda e: print(e.get("label", ""), flush=True) if "label" in e else None)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps({key: summary[key] for key in ["status", "success", "steps_completed", "steps_total", "error", "verification", "run_directory", "report_path"] if key in summary}, indent=2, default=str))
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
