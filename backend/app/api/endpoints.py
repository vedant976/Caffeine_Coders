from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from backend.app.core.metrics import global_metrics
from backend.app.agent.core import global_agent
from backend.simulator.engine import sim_state, process_transaction, generate_transaction_request
from backend.app.core.routing import global_routing
import time
import threading

router = APIRouter()

# Background Traffic Generator
def traffic_loop():
    while True:
        # Generate 1-5 tx per second
        req = generate_transaction_request()
        
        # Check Routing
        if global_routing.is_enabled(req["issuer_id"]):
            tx = process_transaction(req)
            global_metrics.add(tx)
        else:
            # Dropped/Rerouted logic would go here.
            # For sim, we just don't process it (equivalent to 'blocked' or '0 volume')
            # Or we could record it as 'blocked'
            pass
            
        time.sleep(0.2) 

# Start traffic on import/startup (lazy way for demo)
traffic_thread = threading.Thread(target=traffic_loop, daemon=True)
traffic_thread.start()

@router.get("/metrics")
def get_metrics():
    return global_metrics.get_stats()

@router.get("/agent/logs")
def get_agent_logs():
    return global_agent.logs

class ChatRequest(BaseModel):
    message: str

@router.post("/agent/chat")
def chat_agent(req: ChatRequest):
    response = global_agent.chat(req.message)
    return {"response": response}

@router.post("/simulation/fault")
def inject_fault(issuer_id: str, health: float):
    sim_state.set_issuer_health(issuer_id, health)
    return {"status": "ok", "msg": f"Set {issuer_id} health to {health}"}

@router.get("/config/routes")
def get_routes():
    return global_routing.routes

@router.post("/config/routes")
def set_route(issuer_id: str, enabled: bool):
    global_routing.set_route(issuer_id, enabled)
    return {"status": "ok"}
