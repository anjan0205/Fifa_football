from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import datetime

from .database import get_db, settings
from . import models, schemas, crud
from .rag_pipeline import rag_pipeline
from .ai_agents import run_command_center_agents

app = FastAPI(
    title="FIFA World Cup 2026 AI Command Center API",
    description="Production-grade API endpoints for stadium operations, digital twin telemetry, and multi-agent AI execution pipelines.",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Endpoint
@app.get("/")
def read_root():
    return {
        "status": "online",
        "platform": "FIFA World Cup AI Command Center",
        "version": "1.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# =============================================================
# Auth Endpoints
# =============================================================
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=schemas.UserResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # In production, hash the password (mock hashing for fast setup)
    hashed_pwd = f"pbkdf2:{user_data.password}"
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd,
        role=user_data.role
    )
    return crud.save(db, new_user)

@auth_router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == login_data.username).first()
    if not user or user.hashed_password != f"pbkdf2:{login_data.password}":
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Generate mock JWT Token
    return {
        "access_token": f"mock_jwt_token_for_{user.username}_{user.role}",
        "token_type": "bearer"
    }

# =============================================================
# Matches & Tickets Endpoints
# =============================================================
match_router = APIRouter(prefix="/api/matches", tags=["Matches & Tickets"])

@match_router.get("/", response_model=List[schemas.MatchResponse])
def get_matches(db: Session = Depends(get_db)):
    return db.query(models.Match).all()

@match_router.post("/", response_model=schemas.MatchResponse)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    db_match = models.Match(**match.model_dump())
    return crud.save(db, db_match)

@match_router.post("/tickets", response_model=schemas.TicketResponse)
def issue_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    # Generate mock QR code value
    qr_val = f"FIFA-2026-{ticket.match_id}-SEC{ticket.seat_sector}-R{ticket.seat_row}-S{ticket.seat_number}"
    db_ticket = models.Ticket(
        user_id=ticket.user_id,
        match_id=ticket.match_id,
        seat_sector=ticket.seat_sector,
        seat_row=ticket.seat_row,
        seat_number=ticket.seat_number,
        qr_code=qr_val
    )
    return crud.save(db, db_ticket)

# =============================================================
# Incident Command Endpoints
# =============================================================
incident_router = APIRouter(prefix="/api/incidents", tags=["Operations Incident Control"])

@incident_router.get("/", response_model=List[schemas.IncidentResponse])
def get_incidents(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Incident)
    if status:
        query = query.filter(models.Incident.status == status)
    return query.all()

@incident_router.post("/", response_model=schemas.IncidentResponse)
def report_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    db_inc = models.Incident(**incident.model_dump())
    return crud.save(db, db_inc)

@incident_router.patch("/{incident_id}", response_model=schemas.IncidentResponse)
def update_incident(incident_id: int, updates: schemas.IncidentUpdate, db: Session = Depends(get_db)):
    db_inc = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not db_inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    update_data = updates.model_dump(exclude_unset=True)
    return crud.apply_updates(db, db_inc, update_data)

# =============================================================
# Telemetry Sensors & Sustainability Endpoints
# =============================================================
sensor_router = APIRouter(prefix="/api/telemetry", tags=["Digital Twin Telemetry"])

@sensor_router.get("/sensors", response_model=List[schemas.SensorDataResponse])
def get_sensor_data(sensor_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.SensorData)
    if sensor_type:
        query = query.filter(models.SensorData.sensor_type == sensor_type)
    return query.order_by(models.SensorData.recorded_at.desc()).limit(100).all()

@sensor_router.post("/sensors", response_model=schemas.SensorDataResponse)
def add_sensor_data(data: schemas.SensorDataCreate, db: Session = Depends(get_db)):
    db_data = models.SensorData(**data.model_dump())
    return crud.save(db, db_data)

@sensor_router.get("/emissions", response_model=List[schemas.EmissionsResponse])
def get_emissions(db: Session = Depends(get_db)):
    return db.query(models.Emissions).all()

# =============================================================
# Generative AI, RAG & Agents Endpoints
# =============================================================
ai_router = APIRouter(prefix="/api/ai", tags=["Generative AI Operations"])

class ChatPayload(BaseModel):
    query: str
    top_k: Optional[int] = 3

class AgentPayload(BaseModel):
    prompt: str

@ai_router.post("/chat")
def semantic_chat_rag(payload: ChatPayload):
    """
    Standard semantic Q&A that searches loaded vector documents (RAG).
    """
    search_results = rag_pipeline.query(payload.query, top_k=payload.top_k)
    return {
        "query": payload.query,
        "contexts_retrieved": search_results["documents"],
        "metadata": search_results["metadatas"],
        "distances": search_results["distances"]
    }

@ai_router.post("/agent")
def run_multi_agent_workflow(payload: AgentPayload):
    """
    Orchestrate state-graph multi-agent coordination via LangGraph.
    """
    result = run_command_center_agents(payload.prompt)
    return {
        "input_prompt": payload.prompt,
        "agent_response": result["final_reply"],
        "agent_thoughts": result["logs"],
        "emergency_active": result["emergency_active"]
    }

@ai_router.post("/report")
def generate_compliance_report(report_type: str = "executive", db: Session = Depends(get_db)):
    """
    Compile database records and sensor counts to output GenAI operational summaries.
    """
    incident_count = db.query(models.Incident).count()
    sensor_counts = db.query(models.SensorData).count()
    
    # In production, we'd query settings.DATABASE_URL values, compile standard strings,
    # and feed them to LLM. Invoking a mock summarizing report builder:
    summary_text = (
        f"### FIFA WORLD CUP 2026 - AI Generated Operational Status\n"
        f"Report Type: {report_type.upper()}\n"
        f"Database Metrics: {incident_count} active incidents logged, {sensor_counts} active sensor nodes reporting.\n\n"
        f"AI Operational Efficacy Assessment:\n"
        f"- Scanner bottleneck triggers successfully mitigated via automated volunteer Copilot prompts.\n"
        f"- Carbon footprint offsets stabilized at 98.2 CO₂e tons via HVAC micro-zoning automation."
    )
    return {
        "report_type": report_type,
        "generated_content": summary_text,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# Register all Routers
app.include_router(auth_router)
app.include_router(match_router)
app.include_router(incident_router)
app.include_router(sensor_router)
app.include_router(ai_router)
