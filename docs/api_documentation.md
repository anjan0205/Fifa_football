# FIFA World Cup AI Command Center - API Documentation

The FIFA World Cup AI Command Center exposes RESTful APIs for database management, IoT sensor inputs, and Generative AI state-graph actions.

- **Base URL:** `http://localhost:8000`
- **Content-Type:** `application/json`

---

## 🔐 1. Authentication Service

### 1.1 User Registration
Registers a new system profile (Fan, Volunteer, Operator).

- **Method:** `POST`
- **Path:** `/api/auth/register`
- **Request Body:**
```json
{
  "username": "volunteer_sarah",
  "email": "sarah.connor@fifa.org",
  "password": "securepassword123",
  "role": "volunteer"
}
```
- **Response (200 OK):**
```json
{
  "id": 2,
  "username": "volunteer_sarah",
  "email": "sarah.connor@fifa.org",
  "role": "volunteer",
  "is_active": true
}
```

### 1.2 User Login
Authenticates and returns a secure JWT Token.

- **Method:** `POST`
- **Path:** `/api/auth/login`
- **Request Body:**
```json
{
  "username": "volunteer_sarah",
  "password": "securepassword123"
}
```
- **Response (200 OK):**
```json
{
  "access_token": "mock_jwt_token_for_volunteer_sarah_volunteer",
  "token_type": "bearer"
}
```

---

## ⚽ 2. Matches & Tickets Service

### 2.1 Retrieve Matches List
Lists all scheduled, live, and completed matches at the venue.

- **Method:** `GET`
- **Path:** `/api/matches`
- **Response (200 OK):**
```json
[
  {
    "id": 1,
    "team_a": "USA",
    "team_b": "England",
    "match_time": "2026-07-16T20:00:00Z",
    "status": "scheduled",
    "risk_level": "medium"
  }
]
```

### 2.2 Issue Digital Seating Ticket
Allocates a ticket to a user and generates a security QR Code.

- **Method:** `POST`
- **Path:** `/api/matches/tickets`
- **Request Body:**
```json
{
  "user_id": 4,
  "match_id": 1,
  "seat_sector": "112",
  "seat_row": "12",
  "seat_number": "4"
}
```
- **Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 4,
  "match_id": 1,
  "seat_sector": "112",
  "seat_row": "12",
  "seat_number": "4",
  "qr_code": "FIFA-2026-1-SEC112-R12-S4",
  "status": "active",
  "match": {
    "id": 1,
    "team_a": "USA",
    "team_b": "England",
    "match_time": "2026-07-16T20:00:00Z",
    "status": "scheduled",
    "risk_level": "medium"
  }
}
```

---

## 🚨 3. Operations & Incidents Control

### 3.1 Fetch Incidents Feed
Returns a history of reported stadium incidents, with optional status filters.

- **Method:** `GET`
- **Path:** `/api/incidents?status=dispatched`
- **Response (200 OK):**
```json
[
  {
    "id": 2,
    "title": "Scanner Congestion at Gate B Entrance",
    "description": "Ticket reader scanners running extremely slowly causing backlog.",
    "category": "crowd",
    "status": "dispatched",
    "location": "Gate B Scanners",
    "severity": "medium",
    "assigned_volunteer_id": 2,
    "created_at": "2026-07-16T19:53:34Z"
  }
]
```

### 3.2 Report New Incident
Files a new hazard, medical request, or security concern.

- **Method:** `POST`
- **Path:** `/api/incidents`
- **Request Body:**
```json
{
  "title": "Spilled water in stairs Sector 104",
  "description": "Slipping hazard detected near access ramp.",
  "category": "technical",
  "location": "Sector 104 Access Stairs",
  "severity": "low"
}
```
- **Response (200 OK):**
```json
{
  "id": 4,
  "title": "Spilled water in stairs Sector 104",
  "description": "Slipping hazard detected near access ramp.",
  "category": "technical",
  "status": "open",
  "location": "Sector 104 Access Stairs",
  "severity": "low",
  "assigned_volunteer_id": null,
  "created_at": "2026-07-16T20:13:34Z"
}
```

### 3.3 Update Incident Status
Modifies the status (e.g. dispatched/closed) or assigns a volunteer.

- **Method:** `PATCH`
- **Path:** `/api/incidents/2`
- **Request Body:**
```json
{
  "status": "closed"
}
```
- **Response (200 OK):**
```json
{
  "id": 2,
  "title": "Scanner Congestion at Gate B Entrance",
  "status": "closed",
  "assigned_volunteer_id": 2
}
```

---

## 📈 4. Telemetry & Sustainability IoT

### 4.1 Log Telemetry Metric
Inserts a new sensor reading.

- **Method:** `POST`
- **Path:** `/api/telemetry/sensors`
- **Request Body:**
```json
{
  "sensor_type": "electricity",
  "value": 418.5,
  "location": "Stadium Main Grid (kW)"
}
```
- **Response (200 OK):**
```json
{
  "id": 7,
  "sensor_type": "electricity",
  "value": 418.5,
  "location": "Stadium Main Grid (kW)",
  "recorded_at": "2026-07-16T20:14:00Z"
}
```

---

## 🤖 5. Generative AI, RAG & Agents

### 5.1 RAG Semantic Search
Searches the loaded Vector Database for matches, returning document chunks.

- **Method:** `POST`
- **Path:** `/api/ai/chat`
- **Request Body:**
```json
{
  "query": "Is there a bag policy?",
  "top_k": 2
}
```
- **Response (200 OK):**
```json
{
  "query": "Is there a bag policy?",
  "contexts_retrieved": [
    "Bag Policy: Only clear bags smaller than 12x6x12 inches are allowed inside MetLife Stadium. Small clutch bags (4.5x6.5 inches) do not need to be clear."
  ],
  "metadata": [
    {
      "source": "stadium_rules.pdf",
      "category": "rules"
    }
  ],
  "distances": [
    0.114
  ]
}
```

### 5.2 Invoke LangGraph Agents
Orchestrates state-graph multi-agent coordination based on a system prompt.

- **Method:** `POST`
- **Path:** `/api/ai/agent`
- **Request Body:**
```json
{
  "prompt": "Elevator breakdown near Sector 112. Volunteer needed."
}
```
- **Response (200 OK):**
```json
{
  "input_prompt": "Elevator breakdown near Sector 112. Volunteer needed.",
  "agent_response": "Support task created. Dispatching Volunteer Team 3 to guide fans with mobility issues from Sector 112 to Sector 114 escalators.",
  "agent_thoughts": [
    {
      "agent": "Operations",
      "action": "Delegate workflow",
      "details": "Routing elevator incident to Navigation and Volunteer Agents."
    },
    {
      "agent": "Navigation",
      "action": "Calculate seat path",
      "details": "Checking wheelchair access routes bypassing Sector 112 Elevator. Active alternate path: West ramp."
    },
    {
      "agent": "Volunteer",
      "action": "Assign task",
      "details": "Creating dispatch card for volunteer crew at Sector 112."
    }
  ],
  "emergency_active": false
}
```

### 5.3 Generate Operational ESG Summary
Compiles sensor statistics to draft a GenAI report summary.

- **Method:** `POST`
- **Path:** `/api/ai/report?report_type=sustain`
- **Response (200 OK):**
```json
{
  "report_type": "sustain",
  "generated_content": "### FIFA ESG Sustainability compliance Report\nRenewable Energy Share: 64%\nWater consumption: 18,450 gallons (92% recycled greywater)\nEnergy saved: 420 kWh\n...",
  "timestamp": "2026-07-16T20:15:34Z"
}
```
