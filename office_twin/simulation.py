"""Plan-only backend. Never represents generated events as desktop evidence."""
from pathlib import Path
from .fixtures import prepare_workspace


class SimulationDesktop:
    def __init__(self, workspace, cancel, emit, pause, workflow="notepad", **kwargs):
        self.workspace = Path(workspace)
        self.cancel, self.emit, self.pause = cancel, emit, pause
        self.workflow = "office" if workflow == "office" else "notepad"
        self.requested_workflow = workflow
        self.scenario_path = kwargs.get("scenario_path")

    def prepare(self):
        kwargs = {"scenario_path": self.scenario_path} if self.scenario_path else {}
        self.bundle = prepare_workspace(self.workspace, self.workflow, **kwargs)
        if self.requested_workflow == "sheets":
            self.bundle["workflow"] = "sheets"
            self.bundle["steps"][4:4] = [
                {"id": "sheets_open", "label": "Open the dedicated Google Sheet", "kind": "switch"},
                {"id": "sheets_data", "label": "Enter supplier quotations in Google Sheets", "kind": "typing"},
                {"id": "sheets_formulas", "label": "Calculate totals and delivery eligibility", "kind": "typing"},
                {"id": "sheets_save", "label": "Reload and read back the calculated results", "kind": "review"},
            ]
        return self.bundle

    def run_step(self, step):
        kind = step.get("kind", "think")
        self.pause({"browser": "read", "typing": "key"}.get(kind, kind), 1)
        self.emit({"event": "simulated_action", "step_id": step["id"],
                   "kind": step.get("kind", "think"), "native_action": False})
        return {"simulated": True, "native_action": False}

    def verify(self):
        return {"success": True, "plan_only": True, "native_verified": False,
                "explanation": "Plan replay completed. No desktop input occurred and output correctness was not tested."}

    def close(self):
        pass
