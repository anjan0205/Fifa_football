"""Unit tests for the multi-agent LangGraph orchestration.

With no provider API keys configured, ``get_llm`` returns the in-process
MockLLM, so the graph runs deterministically without network access.
"""
from langchain_core.messages import AIMessage, HumanMessage

from app import ai_agents


def _state(text, **overrides):
    state = {
        "messages": [HumanMessage(content=text)],
        "current_agent": "User",
        "context": {},
        "recommendations": [],
        "emergency_active": False,
    }
    state.update(overrides)
    return state


def test_get_llm_falls_back_to_mock(monkeypatch):
    monkeypatch.setattr(ai_agents.settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(ai_agents.settings, "GEMINI_API_KEY", "")
    llm = ai_agents.get_llm()
    result = llm.invoke([HumanMessage(content="hi")])
    assert isinstance(result, AIMessage)
    assert "Mock LLM output" in result.content


def test_navigation_agent_node_appends_recommendation():
    out = ai_agents.navigation_agent_node(_state("find my seat"))
    assert out["current_agent"] == "NavigationAgent"
    assert out["recommendations"][-1]["agent"] == "Navigation"
    assert isinstance(out["messages"][0], AIMessage)


def test_crowd_agent_node():
    out = ai_agents.crowd_agent_node(_state("queue is congested"))
    assert out["current_agent"] == "CrowdAgent"
    assert out["recommendations"][-1]["agent"] == "Crowd"


def test_emergency_agent_node_sets_flag():
    out = ai_agents.emergency_agent_node(_state("evacuate now"))
    assert out["current_agent"] == "EmergencyAgent"
    assert out["emergency_active"] is True
    assert out["recommendations"][-1]["agent"] == "Emergency"


def test_transport_agent_node():
    out = ai_agents.transport_agent_node(_state("train schedule"))
    assert out["current_agent"] == "TransportAgent"
    assert out["recommendations"][-1]["agent"] == "Transport"


def test_volunteer_agent_node():
    out = ai_agents.volunteer_agent_node(_state("assign a task"))
    assert out["current_agent"] == "VolunteerAgent"
    assert out["recommendations"][-1]["agent"] == "Volunteer"


def test_operations_coordinator_node():
    out = ai_agents.operations_coordinator_node(_state("status report"))
    assert out["current_agent"] == "OperationsCoordinator"
    assert out["recommendations"][-1]["agent"] == "Operations"


def test_recommendations_accumulate():
    state = _state("evacuate", recommendations=[{"agent": "Prev"}])
    out = ai_agents.emergency_agent_node(state)
    assert len(out["recommendations"]) == 2
    assert out["recommendations"][0]["agent"] == "Prev"


def test_run_command_center_agents_returns_expected_shape():
    result = ai_agents.run_command_center_agents("please evacuate sector 5")
    assert set(result.keys()) == {"final_reply", "logs", "emergency_active"}
    assert isinstance(result["logs"], list)
    assert result["final_reply"]


# NOTE: The graph's AgentState.messages channel has no reducer, so the
# OperationsCoordinator node overwrites the human message with the LLM reply
# before route_decision inspects it. As a result the workflow currently always
# terminates at the coordinator and never dispatches to a specialist agent.
# These tests pin that actual behavior; see the PR description for the bug.
def test_run_command_center_agents_terminates_at_coordinator():
    for prompt in ("please evacuate now", "where is my seat", "hello there"):
        result = ai_agents.run_command_center_agents(prompt)
        assert result["emergency_active"] is False
        assert len(result["logs"]) == 1
        assert result["logs"][0]["agent"] == "Operations"


def test_create_agent_graph_is_compiled():
    graph = ai_agents.create_agent_graph()
    # A compiled LangGraph exposes an invoke method.
    assert hasattr(graph, "invoke")
