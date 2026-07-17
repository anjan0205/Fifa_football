"""Endpoint tests for the FastAPI application.

The app is exercised through ``TestClient`` with the database dependency
overridden to use SQLite and the AI modules replaced by lightweight stubs
(see ``conftest.py``).
"""


def _register(client, username="user1", role="fan"):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "pw",
            "role": role,
        },
    )


def test_root_status(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "online"
    assert body["version"] == "1.0.0"
    assert "timestamp" in body


def test_register_success(client):
    resp = _register(client, "alice")
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "alice"
    assert body["is_active"] is True
    assert "id" in body
    assert "hashed_password" not in body  # not exposed by UserResponse


def test_register_duplicate_username(client):
    _register(client, "bob")
    resp = _register(client, "bob")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Username already registered"


def test_login_success_returns_token(client):
    _register(client, "carol", role="operator")
    resp = client.post(
        "/api/auth/login", json={"username": "carol", "password": "pw"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"] == "mock_jwt_token_for_carol_operator"


def test_login_wrong_password(client):
    _register(client, "dave")
    resp = client.post(
        "/api/auth/login", json={"username": "dave", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/api/auth/login", json={"username": "ghost", "password": "pw"}
    )
    assert resp.status_code == 401


def _create_match(client):
    return client.post(
        "/api/matches/",
        json={
            "team_a": "ARG",
            "team_b": "FRA",
            "match_time": "2026-06-11T18:00:00",
        },
    )


def test_create_and_list_matches(client):
    assert client.get("/api/matches/").json() == []
    created = _create_match(client)
    assert created.status_code == 200
    assert created.json()["team_a"] == "ARG"

    listed = client.get("/api/matches/")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_issue_ticket_generates_qr(client):
    user = _register(client, "erin").json()
    match = _create_match(client).json()
    resp = client.post(
        "/api/matches/tickets",
        json={
            "user_id": user["id"],
            "match_id": match["id"],
            "seat_sector": "112",
            "seat_row": "R",
            "seat_number": "7",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["qr_code"] == "FIFA-2026-1-SEC112-RR-S7"
    assert body["status"] == "active"
    assert body["match"]["team_a"] == "ARG"


def _report_incident(client, title="Smoke", category="fire", status="open"):
    return client.post(
        "/api/incidents/",
        json={
            "title": title,
            "category": category,
            "location": "Sector 112",
            "status": status,
        },
    )


def test_report_and_list_incidents(client):
    resp = _report_incident(client)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Smoke"
    assert len(client.get("/api/incidents/").json()) == 1


def test_incident_status_filter(client):
    _report_incident(client, title="Open one", status="open")
    _report_incident(client, title="Closed one", status="closed")
    open_only = client.get("/api/incidents/", params={"status": "open"})
    assert open_only.status_code == 200
    titles = [i["title"] for i in open_only.json()]
    assert titles == ["Open one"]


def test_update_incident(client):
    inc = _report_incident(client).json()
    resp = client.patch(
        f"/api/incidents/{inc['id']}",
        json={"status": "dispatched", "severity": "high"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "dispatched"
    assert body["severity"] == "high"


def test_update_incident_not_found(client):
    resp = client.patch("/api/incidents/999", json={"status": "closed"})
    assert resp.status_code == 404


def test_add_and_list_sensor_data_with_filter(client):
    client.post(
        "/api/telemetry/sensors",
        json={"sensor_type": "crowd_count", "value": 100, "location": "A"},
    )
    client.post(
        "/api/telemetry/sensors",
        json={"sensor_type": "water", "value": 50, "location": "B"},
    )
    all_data = client.get("/api/telemetry/sensors")
    assert len(all_data.json()) == 2

    crowd = client.get(
        "/api/telemetry/sensors", params={"sensor_type": "crowd_count"}
    )
    assert len(crowd.json()) == 1
    assert crowd.json()[0]["sensor_type"] == "crowd_count"


def test_get_emissions_empty(client):
    resp = client.get("/api/telemetry/emissions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_ai_chat_returns_rag_contexts(client):
    resp = client.post(
        "/api/ai/chat", json={"query": "where is my seat", "top_k": 2}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["query"] == "where is my seat"
    # RAG pipeline is seeded at import time, so contexts are returned.
    assert isinstance(body["contexts_retrieved"], list)
    assert len(body["contexts_retrieved"]) == 2
    assert len(body["metadata"]) == 2


def test_ai_agent_workflow_response_shape(client):
    resp = client.post("/api/ai/agent", json={"prompt": "please evacuate now"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["input_prompt"] == "please evacuate now"
    assert set(body.keys()) == {
        "input_prompt",
        "agent_response",
        "agent_thoughts",
        "emergency_active",
    }
    assert isinstance(body["agent_thoughts"], list)
    assert len(body["agent_thoughts"]) >= 1


def test_ai_report_generation(client):
    _report_incident(client)
    resp = client.post("/api/ai/report", params={"report_type": "executive"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["report_type"] == "executive"
    assert "FIFA WORLD CUP 2026" in body["generated_content"]
    assert "1 active incidents" in body["generated_content"]
