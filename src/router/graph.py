"""Grafo del agente router (ecommerce)."""

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import Annotated, Literal, TypedDict

from src.router.prompts import (
    ROUTER_SYSTEM_PROMPT,
    AGENTE_PREVENTA_RESPUESTA,
    AGENTE_POSTVENTA_RESPUESTA,
    RESPUESTA_GENERICA,
)

load_dotenv()

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")


class Decision(BaseModel):
    ruta: Literal["preventa", "postventa", "generica"] = Field(
        description="A qué agente va el mensaje."
    )
    motivo: str = Field(description="Una frase: por qué esa ruta.")


class State(TypedDict):
    mensaje: str
    ruta: str
    motivo: str
    respuesta: str
    messages: Annotated[list, add_messages]


def _llm():
    llm = ChatGoogleGenerativeAI(model=MODELO, temperature=0)
    return llm.with_structured_output(Decision)


def _ultimo_mensaje_usuario(state: State) -> str:
    msgs = state.get("messages") or []
    if msgs:
        last = msgs[-1]
        content = getattr(last, "content", last)
        if isinstance(content, list):
            content = "".join(str(p) for p in content)
        if isinstance(last, (tuple, list)) and len(last) >= 2:
            content = last[1]
        return str(content)
    return state.get("mensaje", "") or ""


def router_node(state: State) -> dict:
    msg = _ultimo_mensaje_usuario(state)
    decision: Decision = _llm().invoke(
        [SystemMessage(content=ROUTER_SYSTEM_PROMPT), HumanMessage(content=msg)]
    )
    update = {"mensaje": msg, "ruta": decision.ruta, "motivo": decision.motivo}
    msgs = state.get("messages") or []
    if not msgs:
        update["messages"] = [HumanMessage(content=msg)]
    return update


def agente_preventa_node(state: State) -> dict:
    msg = state.get("mensaje") or _ultimo_mensaje_usuario(state)
    resp = AGENTE_PREVENTA_RESPUESTA.format(mensaje=msg)
    return {"respuesta": resp, "messages": [AIMessage(content=resp)]}


def agente_postventa_node(state: State) -> dict:
    msg = state.get("mensaje") or _ultimo_mensaje_usuario(state)
    resp = AGENTE_POSTVENTA_RESPUESTA.format(mensaje=msg)
    return {"respuesta": resp, "messages": [AIMessage(content=resp)]}


def respuesta_generica_node(state: State) -> dict:
    resp = RESPUESTA_GENERICA
    return {"respuesta": resp, "messages": [AIMessage(content=resp)]}


def _route(state: State) -> str:
    return state.get("ruta", "generica")


def build_graph():
    graph = StateGraph(State)
    graph.add_node("router", router_node)
    graph.add_node("agente_preventa", agente_preventa_node)
    graph.add_node("agente_postventa", agente_postventa_node)
    graph.add_node("respuesta_generica", respuesta_generica_node)

    graph.add_edge(START, "router")
    graph.add_conditional_edges(
        "router",
        _route,
        {
            "preventa": "agente_preventa",
            "postventa": "agente_postventa",
            "generica": "respuesta_generica",
        },
    )
    graph.add_edge("agente_preventa", END)
    graph.add_edge("agente_postventa", END)
    graph.add_edge("respuesta_generica", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


graph = build_graph()
app = graph
