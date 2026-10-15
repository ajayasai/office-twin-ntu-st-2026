"""Small desktop control panel. Work happens in a cancellable worker thread."""
import json
import os
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from .runner import RunConfig, run


class ControlPanel:
    def __init__(self, root):
        self.root = root
        root.title("Office Twin — Synthetic Work Sessions")
        root.geometry("960x740")
        root.minsize(840, 620)
        root.configure(bg="#101b2d")
        self.events = queue.Queue()
        self.cancel = threading.Event()
        self.worker = None
        self.last_summary = None
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#101b2d")
        style.configure("TLabel", background="#101b2d", foreground="#dbe8f8", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 27, "bold"), foreground="#ffffff")
        style.configure("Sub.TLabel", foreground="#97acc5", font=("Segoe UI", 11))
        style.configure("TButton", padding=(15, 9), font=("Segoe UI", 10))
        style.configure("TCombobox", padding=6)
        outer = ttk.Frame(root, padding=28)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="OFFICE TWIN", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="A work session you can inspect, measure, and reproduce.", style="Sub.TLabel").pack(anchor="w", pady=(4, 22))
        controls = ttk.Frame(outer)
        controls.pack(fill="x")
        try:
            settings = json.loads((Path(__file__).resolve().parent.parent / "local-settings.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            settings = {}
        self.mode = tk.StringVar(value="simulate")
        self.workflow = tk.StringVar(value=settings.get("workflow", "notepad"))
        self.timing = tk.StringVar(value="contextual")
        self.seed = tk.StringVar(value="42")
        self.sheet_url = tk.StringVar(value=settings.get("sheet_url", ""))
        for col, (label, var, values) in enumerate([
            ("Execution", self.mode, ["simulate", "desktop"]),
            ("Workflow", self.workflow, ["notepad", "sheets", "office"]),
            ("Timing policy", self.timing, ["contextual", "fixed"])]):
            ttk.Label(controls, text=label).grid(row=0, column=col, sticky="w", padx=(0, 18))
            ttk.Combobox(controls, textvariable=var, values=values, state="readonly", width=18).grid(row=1, column=col, sticky="w", padx=(0, 18), pady=(6, 16))
        ttk.Label(controls, text="Seed").grid(row=0, column=3, sticky="w")
        ttk.Entry(controls, textvariable=self.seed, width=10).grid(row=1, column=3, sticky="w", pady=(6, 16))
        ttk.Label(outer, text="Dedicated Google Sheet URL (Sheets workflow only)").pack(anchor="w")
        ttk.Entry(outer, textvariable=self.sheet_url).pack(fill="x", pady=(6, 10))
        ttk.Label(outer, text="Desktop mode types into your apps. Keep the desktop idle; press Escape to stop.", style="Sub.TLabel").pack(anchor="w", pady=(0, 15))
        buttons = ttk.Frame(outer)
        buttons.pack(fill="x")
        self.start_btn = ttk.Button(buttons, text="Start session", command=self.start)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(buttons, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=9)
        self.report_btn = ttk.Button(buttons, text="Open evidence report", command=self.open_report, state="disabled")
        self.report_btn.pack(side="right")
        self.status = tk.StringVar(value="Ready · Simulation performs no desktop input.")
        ttk.Label(outer, textvariable=self.status, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(23, 10))
        self.progress = ttk.Progressbar(outer, maximum=100, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 15))
        self.log = tk.Text(outer, bg="#0b1423", fg="#b9cee6", relief="flat", font=("Consolas", 10), wrap="word", padx=14, pady=14, height=12)
        self.log.pack(fill="both", expand=True)
        self.log.configure(state="disabled")
        ttk.Label(outer, text="Transparent by design · No cloud model calls · No fabricated human baseline", style="Sub.TLabel").pack(anchor="w", pady=(14, 0))
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(100, self.poll)

    def append(self, line):
        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        if int(self.log.index("end-1c").split(".")[0]) > 350:
            self.log.delete("1.0", "100.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self):
        if self.worker and self.worker.is_alive():
            return
        try:
            config = RunConfig(mode=self.mode.get(), workflow=self.workflow.get(), timing=self.timing.get(), seed=int(self.seed.get()), sheet_url=self.sheet_url.get().strip())
            config.validate()
        except ValueError as exc:
            messagebox.showerror("Check configuration", str(exc))
            return
        self.cancel.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.report_btn.configure(state="disabled")
        self.progress["value"] = 0
        self.status.set("Starting session…")
        self.append(f"\n{config.mode.upper()} / {config.workflow} / {config.timing} / seed {config.seed}")
        def work():
            try:
                result = run(config, self.cancel, self.events.put)
                self.events.put({"event": "gui_result", "summary": result})
            except Exception as exc:
                self.events.put({"event": "gui_error", "message": str(exc)})
        self.worker = threading.Thread(target=work, daemon=True)
        self.worker.start()

    def stop(self):
        self.cancel.set()
        self.status.set("Stopping at the next input boundary…")

    def poll(self):
        try:
            while True:
                e = self.events.get_nowait()
                kind = e.get("event")
                if kind in {"step_started", "countdown"}:
                    self.status.set(e.get("label", "Working"))
                    self.append(e.get("label", "Working"))
                elif kind == "step_completed":
                    self.progress["value"] = 100 * e["index"] / e["total"]
                elif kind in {"run_error", "gui_error"}:
                    self.append("ERROR: " + e.get("message", "Unknown error"))
                if kind == "gui_result":
                    self.last_summary = e["summary"]
                    self.status.set("Session " + self.last_summary["status"].replace("_", " "))
                    self.append("Evidence: " + self.last_summary["run_directory"])
                    if "error" in self.last_summary:
                        self.append(self.last_summary["error"])
                    self.start_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.report_btn.configure(state="normal" if self.last_summary.get("report_path") else "disabled")
                elif kind == "gui_error":
                    self.status.set("Session failed")
                    self.start_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def open_report(self):
        if self.last_summary and self.last_summary.get("report_path"):
            webbrowser.open(Path(self.last_summary["report_path"]).as_uri())

    def close(self):
        self.cancel.set()
        if self.worker and self.worker.is_alive():
            self.status.set("Stopping safely before closing…")
            self.root.after(150, self.close)
        else:
            self.root.destroy()


def launch():
    if os.name == "nt":
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            pass
    root = tk.Tk()
    ControlPanel(root)
    root.mainloop()
