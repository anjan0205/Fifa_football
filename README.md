# FIFA World Cup AI Command Center ⚽🏆

A production-grade, hackathon-winning Generative AI Platform and Digital Twin ecosystem for the **FIFA World Cup 2026**. Designed to optimize stadium operations, emergency evacuation planning, volunteer task management, crowd logistics, public transit systems, and the overall inclusive fan experience.

This platform represents a startup-ready solution tailored to the requirements of the world’s largest sporting event.

---

## 🏗️ System Architecture & Folder Structure

The project is structured as a full-stack, enterprise-grade application:

```
├── D:/Stadium Management/
│   ├── README.md                     # High-level overview, architecture, & setup
│   ├── docker-compose.yml            # Docker orchestration file for development/production
│   ├── frontend/                     # Interactive high-fidelity prototype (directly runnable)
│   │   ├── index.html                # Main SPA file containing all 11 views
│   │   ├── style.css                 # Custom glassmorphism, responsive grids, dark/light styles
│   │   └── app.js                    # In-memory RAG, speech-to-text, maps, multi-agent engine
│   ├── backend/                      # Production-ready Python FastAPI service
│   │   ├── requirements.txt          # Python dependencies (LangGraph, FastAPI, SQLAlchemy)
│   │   └── app/
│   │       ├── main.py               # Main application router and API configurations
│   │       ├── models.py             # SQLAlchemy models (User, Incident, Emissions, etc.)
│   │       ├── schemas.py            # Pydantic validation schemas
│   │       ├── database.py           # PostgreSQL/Supabase engine setup
│   │       ├── ai_agents.py          # Multi-agent system orchestration (LangGraph + OpenAI/Gemini)
│   │       └── rag_pipeline.py       # Retrieval Augmented Generation pipeline with vector DB
│   ├── database/                     # SQL scripts
│   │   ├── schema.sql                # PostgreSQL table definitions
│   │   └── seed.sql                  # Complete seed data including sensors, matches, and logs
│   ├── docker/                       # Deploy configurations
│   │   ├── Dockerfile.backend        # FastAPI Dockerfile
│   │   └── Dockerfile.frontend       # Static frontend Nginx Dockerfile
│   └── docs/                         # Platform Documentation
│       ├── api_documentation.md      # OpenAPI / REST endpoints documentation
│       ├── architecture_guide.md     # Sequence & ER diagrams in Mermaid, agent workflows
│       └── pitch_deck_assets.md      # Pitch slides, marketing highlights, and ROI calculations
```

---

## 🌟 Core Modules & GenAI Capabilities

### 1. AI Stadium Assistant (Fan Dashboard)
- **Natural Language & Voice UI**: Voice-to-text navigation, text-to-speech rule explainers, and instant translations using Web Speech APIs.
- **RAG Guide Q&A**: Resolves search queries regarding lost-and-found items, accessibility ramps, seat listings, matches, and ticket inquiries.

### 2. Operations Command Center (Admin View)
- **Digital Twin & Live Analytics**: Real-time monitoring of crowd counts, parking slots, carbon emissions, and electricity grids.
- **Predictive AI Recommendations**: Provides automated corrective actions, such as rerouting metro buses, dispatching volunteers, or optimizing gate configurations.

### 3. Crowd & Navigation Agentic AI
- **Multi-Agent Simulation**: Dedicated LangGraph agents coordinate live crowd control, dynamic path navigation, security dispatch, and emergency routing.
- **Dynamic Evacuation Planner**: Instantly triggers and maps emergency routing (e.g., active shooter, localized fire, structural overload) with optimal egress exit planning.

### 4. Accessibility AI
- **Universal Design**: Sign language avatar animation, high-contrast and color-blind CSS modes, Text-to-Speech screen reader, and wheelchair-accessible indoor pathfinding.

### 5. Sustainability AI
- **Carbon Footprint Monitoring**: Visualizes real-time metrics for electricity usage, water reserves, trash build-up, and recommends localized recycling programs.

---

## 🚀 Running the Project

### Interactive Frontend Prototype
You can run and test the UI immediately in any modern web browser:
1. Open the [frontend/index.html](file:///D:/Stadium%20Management/frontend/index.html) file directly in Google Chrome.
2. Switch between different dashboard interfaces using the sidebar: **Fan, Operations, or Volunteer Command Panels**.
3. Interact with the chat assistant, run crowd/evacuation simulations, speak to the voice assistant, or trigger accessibility modes.

### FastAPI Production Backend (Development Setup)
Once Python and PostgreSQL are configured in your local path:
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/fifa_stadium
   OPENAI_API_KEY=your-api-key
   GEMINI_API_KEY=your-gemini-key
   ```
4. Start the live reload server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Running with Docker Compose
To run both the backend API and frontend Nginx container together:
```bash
docker-compose up --build
```
The Command Center Dashboard will launch at `http://localhost:80` and the API documentation at `http://localhost:8000/docs`.
