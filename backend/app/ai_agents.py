import os
from typing import Callable, Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from .database import settings
from .rag_pipeline import rag_pipeline

# Define shared Multi-Agent state
class AgentState(TypedDict):
    messages: List[BaseMessage]
    current_agent: str
    context: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    emergency_active: bool

# Initialize Chat LLM
def get_llm():
    if settings.OPENAI_API_KEY:
        return ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4-turbo", temperature=0.2)
    elif settings.GEMINI_API_KEY:
        return ChatGoogleGenerativeAI(google_api_key=settings.GEMINI_API_KEY, model="gemini-1.5-pro", temperature=0.2)
    else:
        # Return fallback mock wrapper for testing
        class MockLLM:
            def invoke(self, messages):
                content = "Mock LLM output: Processing commands."
                return AIMessage(content=content)
        return MockLLM()

llm = get_llm()

# Agent Node Factory
def make_agent_node(
    node_name: str,
    log_agent: str,
    action: str,
    build_prompt: Callable[[str], str],
    extra_state: Optional[Dict[str, Any]] = None,
) -> Callable[[AgentState], Dict[str, Any]]:
    """
    Build a LangGraph node that runs a single-turn LLM step.

    Each agent shares the same shape: read the latest message, render a role
    specific prompt, invoke the shared LLM, and append a recommendation entry.
    ``build_prompt`` receives the last message content and returns the prompt;
    ``extra_state`` is merged into the returned state (e.g. ``emergency_active``).
    """
    def node(state: AgentState) -> Dict[str, Any]:
        last_msg = state["messages"][-1].content

        response = llm.invoke([HumanMessage(content=build_prompt(last_msg))])
        recs = state["recommendations"] + [
            {"agent": log_agent, "action": action, "details": response.content}
        ]

        result: Dict[str, Any] = {
            "messages": [response],
            "current_agent": node_name,
            "recommendations": recs,
        }
        if extra_state:
            result.update(extra_state)
        return result

    return node


def _navigation_prompt(last_msg: str) -> str:
    # Navigation is the only agent that grounds its prompt in RAG context.
    docs = rag_pipeline.query(last_msg, top_k=2)["documents"]
    return (
        f"You are the Stadium Navigation Agent. Your job is to find optimal, safe, and wheelchair-accessible paths.\n"
        f"User Query: {last_msg}\n"
        f"Relevant Context: {' | '.join(docs)}\n"
        f"Generate a clear navigation path instruction. If wheelchair access is required, prioritize ramps and elevators."
    )


navigation_agent_node = make_agent_node(
    "NavigationAgent", "Navigation", "Calculate seat path", _navigation_prompt
)

crowd_agent_node = make_agent_node(
    "CrowdAgent",
    "Crowd",
    "Monitor congestion",
    lambda last_msg: (
        f"You are the Stadium Crowd Agent. Your job is to monitor crowd flow rates and predict bottlenecks.\n"
        f"Telemetry Input: {last_msg}\n"
        f"Identify if there is high density or scanner failure and recommend alternative entrances/exits."
    ),
)

emergency_agent_node = make_agent_node(
    "EmergencyAgent",
    "Emergency",
    "Evacuate sectors",
    lambda last_msg: (
        f"You are the Emergency Management Agent. Your job is to orchestrate stadium evacuation procedures.\n"
        f"Critical Signal: {last_msg}\n"
        f"Draft an emergency evacuation command sequence. Clearly define which sectors should exit which gates."
    ),
    extra_state={"emergency_active": True},
)

transport_agent_node = make_agent_node(
    "TransportAgent",
    "Transport",
    "Transit optimization",
    lambda last_msg: (
        f"You are the Transportation Agent. Your job is to align outbound transit with stadium flow rates.\n"
        f"Traffic data: {last_msg}\n"
        f"Provide suggestions on shuttle routes and train frequencies."
    ),
)

volunteer_agent_node = make_agent_node(
    "VolunteerAgent",
    "Volunteer",
    "Assign task",
    lambda last_msg: (
        f"You are the Volunteer Coordination Copilot. Your job is to assign shifts and generate task messages.\n"
        f"Operations Request: {last_msg}\n"
        f"Generate a clear, polite instruction for a volunteer squad to address this request."
    ),
)

operations_coordinator_node = make_agent_node(
    "OperationsCoordinator",
    "Operations",
    "Delegate workflow",
    lambda last_msg: (
        f"You are the Master Operations Coordinator for the FIFA Stadium. Analyze this request and delegate it.\n"
        f"System Request: {last_msg}\n"
        f"Decide which department (Navigation, Crowd, Emergency, Transport, Volunteer) needs to act."
    ),
)

# Build LangGraph Workflow
def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Register Nodes
    workflow.add_node("OperationsCoordinator", operations_coordinator_node)
    workflow.add_node("NavigationAgent", navigation_agent_node)
    workflow.add_node("CrowdAgent", crowd_agent_node)
    workflow.add_node("EmergencyAgent", emergency_agent_node)
    workflow.add_node("TransportAgent", transport_agent_node)
    workflow.add_node("VolunteerAgent", volunteer_agent_node)
    
    # Define routing rules (edges)
    def route_decision(state: AgentState) -> str:
        last_msg_content = state["messages"][-1].content.lower()
        if "evacuate" in last_msg_content or "emergency" in last_msg_content or "alarm" in last_msg_content:
            return "EmergencyAgent"
        elif "seat" in last_msg_content or "where is" in last_msg_content or "navigation" in last_msg_content:
            return "NavigationAgent"
        elif "queue" in last_msg_content or "crowd" in last_msg_content or "congest" in last_msg_content:
            return "CrowdAgent"
        elif "bus" in last_msg_content or "train" in last_msg_content or "transit" in last_msg_content:
            return "TransportAgent"
        elif "task" in last_msg_content or "volunteer" in last_msg_content or "assign" in last_msg_content:
            return "VolunteerAgent"
        else:
            return END

    # Operations Coordinator acts as the orchestrator entrypoint
    workflow.set_entry_point("OperationsCoordinator")
    
    # Conditional Edges from coordinator
    workflow.add_conditional_edges(
        "OperationsCoordinator",
        route_decision,
        {
            "EmergencyAgent": "EmergencyAgent",
            "NavigationAgent": "NavigationAgent",
            "CrowdAgent": "CrowdAgent",
            "TransportAgent": "TransportAgent",
            "VolunteerAgent": "VolunteerAgent",
            END: END
        }
    )
    
    # End node transitions
    workflow.add_edge("EmergencyAgent", END)
    workflow.add_edge("NavigationAgent", END)
    workflow.add_edge("CrowdAgent", END)
    workflow.add_edge("TransportAgent", END)
    workflow.add_edge("VolunteerAgent", END)
    
    return workflow.compile()

agent_orchestrator = create_agent_graph()

# Execution Wrapper
def run_command_center_agents(user_prompt: str) -> Dict[str, Any]:
    initial_state = {
        "messages": [HumanMessage(content=user_prompt)],
        "current_agent": "User",
        "context": {},
        "recommendations": [],
        "emergency_active": False
    }
    
    output_state = agent_orchestrator.invoke(initial_state)
    return {
        "final_reply": output_state["messages"][-1].content,
        "logs": output_state["recommendations"],
        "emergency_active": output_state["emergency_active"]
    }
