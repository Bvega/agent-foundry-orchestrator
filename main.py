from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI()

@app.get('/healthz')
def healthz():
    return {'status': 'ok'}

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

@app.post('/orchestrate_task')
def orchestrate_task(payload: OrchestratePayload) -> Dict[str, Any]:
    roster = [
        {'name': 'Strategist', 'charter': 'Set objectives', 'duties': ['scope', 'tradeoffs', 'constraints']},
        {'name': 'Creator', 'charter': 'Draft deliverables', 'duties': ['outline', 'write', 'polish']},
        {'name': 'QA', 'charter': 'Sanity-check', 'duties': ['risks', 'edits', 'next steps']},
    ]
    return {
        'task_snapshot': {
            'task': payload.task,
            'deliverables': payload.deliverables or [],
            'assumptions': ['MVP stub – replace with planner in M2']
        },
        'agent_roster': roster,
        'collab_log': ['Chose pipeline mode (simple stub)'],
        'deliverables': {
            'primary': f"# Draft for: {payload.task}\n\n(Replace with real synthesis in M2)"
        },
        'risks': ['Early stub; outputs incomplete'],
        'next_steps': ['Implement planner', 'Implement synthesizer', 'Add adapters']
    }
