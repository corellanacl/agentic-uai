"""Grafo del agente demo."""

import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import Annotated, TypedDict

from src.demo.prompts import SYSTEM_PROMPT, AGENT_NODE_PROMPT
from src.demo.tools import TOOLS

load_dotenv()

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")


class State(TypedDict):
    messages: Annotated[list, add_messages]


def _llm():
    llm = ChatGoogleGenerativeAI(model=MODELO, temperature=0.3)
    return llm.bind_tools(TOOLS)


def agent_node(state: State) -> dict:
    llm = _llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        SystemMessage(content=AGENT_NODE_PROMPT),
    ] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: State) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


def build_graph():
    graph = StateGraph(State)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


# Alias para compatibilidad con cargadores genéricos.
graph = build_graph()
app = graph
