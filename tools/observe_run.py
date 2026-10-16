"""Observe Office Twin from a separate, read-only process polling application resources.

Example (start before the controller):
  python tools/observe_run.py --output runs/bench/observer --controller-file runs/bench/controller.json --stop-file runs/bench/observer.stop
Wait for observer-ready.json. Write {"pid": ..., "create_time": ...} to the
controller file after launch, then create the stop file when the task finishes.
This is sampled process telemetry, not a complete OS event trace.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from office_twin.observer import observe


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Fresh directory for observer evidence")
    parser.add_argument("--stop-file", type=Path, help="Stop after this marker exists")
    parser.add_argument("--controller-file", type=Path, help="JSON containing controller pid and create_time; may be created after observer readiness")
    parser.add_argument("--controller-pid", type=int, help="Already running controller PID; requires --controller-created")
    parser.add_argument("--controller-created", type=float, help="Exact controller creation timestamp from psutil")
    parser.add_argument("--interval", type=float, default=0.1, help="Target polling interval seconds (actual gaps are recorded)")
    parser.add_argument("--duration", type=float, default=1800, help="Safety time limit seconds; stops sooner on the stop file")
    args = parser.parse_args(argv)
    if (args.controller_pid is None) != (args.controller_created is None):
        parser.error("--controller-pid and --controller-created must be supplied together")
    if args.controller_file and args.controller_pid:
        parser.error("Choose a controller file or an explicit controller identity")
    controller = None if args.controller_pid is None else (args.controller_pid, args.controller_created)
    try:
        result = observe(args.output, stop_file=args.stop_file, controller_file=args.controller_file,
                         controller_identity=controller, interval=args.interval, duration=args.duration)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps({key: result[key] for key in ("status", "stop_reason", "duration_seconds", "snapshot_count", "process_count", "cadence", "scopes")}))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
