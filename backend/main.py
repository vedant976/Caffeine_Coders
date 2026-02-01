from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.endpoints import router
from backend.app.agent.core import global_agent
import os

app = FastAPI(title="Smart Payment Operations Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Start Agent
@app.on_event("startup")
def start_agent():
    global_agent.start_loop()

# Serve Static Dashboard (Fallback since Node is missing)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
