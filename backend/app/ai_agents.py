import logging
from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from .database import settings
from .rag_pipeline import rag_pipeline, RAGPipelineError

logger = logging.getLogger(__name__)


class AgentExecutionError(Exception):
    """Raised when the multi-agent workflow fails to produce a result."""

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

# Agent Node Functions
def navigation_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Navigation Agent: Focuses on seating pathfinding, accessibility, and corridor routing.
    """
    messages = state["messages"]
    last_msg = messages[-1].content
    
    # Query RAG context for navigation. Retrieval is supplementary here, so a
    # failure is logged and the agent continues without extra context rather
    # than aborting the whole workflow.
    try:
        context_data = rag_pipeline.query(last_msg, top_k=2)
        docs = context_data["documents"]
    except RAGPipelineError:
        logger.exception("RAG retrieval failed in navigation agent; continuing without context")
        docs = []
    
    prompt = (
        f"You are the Stadium Navigation Agent. Your job is to find optimal, safe, and wheelchair-accessible paths.\n"
        f"User Query: {last_msg}\n"
        f"Relevant Context: {' | '.join(docs)}\n"
        f"Generate a clear navigation path instruction. If wheelchair access is required, prioritize ramps and elevators."
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    recs = state["recommendations"] + [{"agent": "Navigation", "action": "Calculate seat path", "details": response.content}]
    
    return {
        "messages": [response],
        "current_agent": "NavigationAgent",
        "recommendations": recs
    }

def crowd_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Crowd Agent: Forecasts overcrowding risk and dynamically manages gate queues.
    """
    messages = state["messages"]
    last_msg = messages[-1].content
    
    prompt = (
        f"You are the Stadium Crowd Agent. Your job is to monitor crowd flow rates and predict bottlenecks.\n"
        f"Telemetry Input: {last_msg}\n"
        f"Identify if there is high density or scanner failure and recommend alternative entrances/exits."
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    recs = state["recommendations"] + [{"agent": "Crowd", "action": "Monitor congestion", "details": response.content}]
    
    return {
        "messages": [response],
        "current_agent": "CrowdAgent",
        "recommendations": recs
    }

def emergency_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Emergency Agent: Handles high-severity alert routing, disaster mapping, and PA audio scripts.
    """
    messages = state["messages"]
    last_msg = messages[-1].content
    
    prompt = (
        f"You are the Emergency Management Agent. Your job is to orchestrate stadium evacuation procedures.\n"
        f"Critical Signal: {last_msg}\n"
        f"Draft an emergency evacuation command sequence. Clearly define which sectors should exit which gates."
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    recs = state["recommendations"] + [{"agent": "Emergency", "action": "Evacuate sectors", "details": response.content}]
    
    return {
        "messages": [response],
        "current_agent": "EmergencyAgent",
        "recommendations": recs,
        "emergency_active": True
    }

def transport_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Transportation Agent: Coordinates subway arrivals, shuttle bus releases, and parking barriers.
    """
    messages = state["messages"]
    last_msg = messages[-1].content
    
    prompt = (
        f"You are the Transportation Agent. Your job is to align outbound transit with stadium flow rates.\n"
        f"Traffic data: {last_msg}\n"
        f"Provide suggestions on shuttle routes and train frequencies."
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    recs = state["recommendations"] + [{"agent": "Transport", "action": "Transit optimization", "details": response.content}]
    
    return {
        "messages": [response],
        "current_agent": "TransportAgent",
        "recommendations": recs
    }

def volunteer_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Volunteer Agent: Translates instructions, manages shifts, and generates dispatcher notifications.
    """
    messages = state["messages"]
    last_msg = messages[-1].content
    
    prompt = (
        f"You are the Volunteer Coordination Copilot. Your job is to assign shifts and generate task messages.\n"
        f"Operations Request: {last_msg}\n"
        f"Generate a clear, polite instruction for a volunteer squad to address this request."
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    recs = state["recommendations"] + [{"agent": "Volunteer", "action": "Assign task", "details": response.content}]
    
    return {
        "messages": [response],
        "current_agent": "VolunteerAgent",
        "recommendations": recs
    }

def operations_coordinator_node(state: AgentState) -> Dict[str, Any]:
    """
    Operations Agent: The master node that analyzes inputs, routes commands to sub-agents, 
    and generates unified dashboards reports.
    """
    messages = state["messages"]
    last_msg = messages[-1].content
    
    prompt = (
        f"You are the Master Operations Coordinator for the FIFA Stadium. Analyze this request and delegate it.\n"
        f"System Request: {last_msg}\n"
        f"Decide which department (Navigation, Crowd, Emergency, Transport, Volunteer) needs to act."
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    recs = state["recommendations"] + [{"agent": "Operations", "action": "Delegate workflow", "details": response.content}]
    
    return {
        "messages": [response],
        "current_agent": "OperationsCoordinator",
        "recommendations": recs
    }

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
    
    try:
        output_state = agent_orchestrator.invoke(initial_state)
    except Exception as exc:
        logger.exception("Multi-agent orchestration failed")
        raise AgentExecutionError("Multi-agent orchestration failed") from exc

    return {
        "final_reply": output_state["messages"][-1].content,
        "logs": output_state["recommendations"],
        "emergency_active": output_state["emergency_active"]
    }
