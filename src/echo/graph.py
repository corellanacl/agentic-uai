"""Grafo del agente echo (sin LLM)."""

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict

class State(TypedDict):
    messages: Annotated[list, add_messages]


def echo_node(state: State) -> dict:
    last = state["messages"][-1]
    content = getattr(last, "content", last)
    if isinstance(content, list):
        content = "".join(str(p) for p in content)
    return {"messages": [AIMessage(content=f"Echo: {content}")]}


def build_graph():
    graph = StateGraph(State)
    graph.add_node("echo", echo_node)
    graph.add_edge(START, "echo")
    graph.add_edge("echo", END)
    return graph.compile()


graph = build_graph()
app = graph
