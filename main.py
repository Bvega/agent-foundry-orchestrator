from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json

# NEW: yaml loader
try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# ---------------------------
# Models
# ---------------------------
class Constraints(BaseModel):
    deadline: Optional[str] = None
    audience: Optional[str] = None
    tone: Optional[str] = None
    budget: Optional[str] = None
    tools: Optional[List[str]] = None

class OrchestratePayload(BaseModel):
    task: str
    deliverables: Optional[List[str]] = None
    constraints: Optional[Constraints] = None
    notes: Optional[str] = None

# ---------------------------
# Helpers
# ---------------------------
def load_roles() -> List[Dict[str, Any]]:
    """
    M2: load roles from a vendored file (data/roles.yaml).
    M6: replace with a proper dependency on agent-foundry-agents.
    """
    roles_path = os.path.join(os.path.dirname(__file__), "data", "roles.yaml")
    if not os.path.exists(roles_path):
        raise FileNotFoundError(f"roles.yaml not found at {roles_path}")

    if yaml is None:
        # Fallback: provide minimal roles if PyYAML missing
        return [
            {"name": "Strategist", "charter": "Set objectives", "duties": ["scope", "tradeoffs", "constraints"]},
            {"name": "Creator", "charter": "Draft deliverables", "duties": ["outline", "write", "polish"]},
            {"name": "QA", "charter": "Sanity-check", "duties": ["risks", "edits", "next steps"]},
        ]

    with open(roles_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    # basic shape validation
    roles = []
    for r in data:
        roles.append({
            "name": r.get("name", "Unknown"),
            "charter": r.get("charter", ""),
            "duties": r.get("duties", []),
        })
    return roles

def pick_mode(deliverables: Optional[List[str]]) -> str:
    """
    Tiny heuristic: if user wants a plan/brief, use pipeline, else round-table.
    """
    if not deliverables:
        return "round-table"
    text = " ".join(deliverables).lower()
    if any(k in text for k in ["plan", "brief", "checklist", "outline"]):
        return "pipeline"
    return "round-table"

def synthesize(task: str, roster: List[Dict[str, Any]], mode: str) -> str:
    """
    Very small M2 synthesizer: produce a short markdown draft.
    """
    roles_line = ", ".join([r["name"] for r in roster])
    return (
        f"# Draft for: {task}\n\n"
        f"**Mode:** {mode}\n\n"
        f"**Agents:** {roles_line}\n\n"
        f"## Summary\n"
        f"- This is an M2 stub synthesis. In later milestones we’ll call real LLMs and merge.\n"
        f"- Next we’ll add adapters and smarter planning.\n"
    )

# ---------------------------
# Routes
# ---------------------------
@app.post("/orchestrate_task")
def orchestrate_task(payload: OrchestratePayload) -> Dict[str, Any]:
    try:
        roster = load_roles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load roles: {e}")

    mode = pick_mode(payload.deliverables)
    primary_md = synthesize(payload.task, roster, mode)

    return {
        "task_snapshot": {
            "task": payload.task,
            "deliverables": payload.deliverables or [],
            "constraints": payload.constraints.dict() if payload.constraints else {},
            "assumptions": ["M2 stub – planner/synthesizer are minimal"],
        },
        "agent_roster": roster,
        "collab_log": [
            f"Selected mode = {mode} based on deliverables",
            "Loaded roles from data/roles.yaml",
        ],
        "deliverables": {
            "primary": primary_md
        },
        "risks": ["Outputs are draft-level; planning is heuristic-only"],
        "next_steps": [
            "Implement planner (M2+)",
            "Add OpenAI adapter for one step (M3)",
            "Add auth & Docker (M3)"
        ],
    }
