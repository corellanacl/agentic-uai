"""Punto de entrada para ejecutar agentes.

Uso:
    python main.py {nombre_agente} "mensaje"
    python main.py {nombre_agente} "mensaje" --saltos
    python main.py {nombre_agente} --diagrama
"""

import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_graph(agent_name: str):
    module = importlib.import_module(f"src.{agent_name}.graph")
    for attr in ("build_graph",):
        factory = getattr(module, attr, None)
        if callable(factory):
            return factory()
    for attr in ("graph", "app", "compiled_graph"):
        obj = getattr(module, attr, None)
        if obj is not None:
            return obj
    raise RuntimeError(f"El agente '{agent_name}' no expone build_graph/graph/app")


def extract_final_text(result) -> str:
    """Extrae el texto final de un resultado de invocación."""
    messages = None
    if isinstance(result, dict):
        messages = result.get("messages")
    if not messages:
        return str(result)
    last = messages[-1]
    content = getattr(last, "content", None)
    if content is None and isinstance(last, dict):
        content = last.get("content")
    if isinstance(content, list):
        # Gemini puede devolver lista de partes
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text", ""))
            else:
                parts.append(str(part))
        content = "".join(parts)
    return str(content) if content is not None else str(last)


def run(agent_name: str, message: str, saltos: bool) -> None:
    graph = load_graph(agent_name)
    config = {"configurable": {"thread_id": "cli"}}
    visited: list[str] = []
    final_state = None
    try:
        stream = graph.stream({"messages": [("user", message)]}, config, stream_mode=["updates", "values"])
        for mode, payload in stream:
            if mode == "updates" and isinstance(payload, dict):
                for node_name in payload.keys():
                    visited.append(node_name)
            elif mode == "values" and isinstance(payload, dict):
                final_state = payload
    except TypeError:
        for chunk in graph.stream({"messages": [("user", message)]}, config, stream_mode="updates"):
            for node_name in chunk.keys():
                visited.append(node_name)
            final_state = chunk
    if final_state is None:
        try:
            snap = graph.get_state(config)
            if snap and snap.values:
                final_state = snap.values
        except Exception:
            pass

    if saltos:
        print("Saltos: " + " -> ".join(visited))
    if isinstance(final_state, dict):
        if final_state.get("motivo"):
            print(f"Motivo: {final_state['motivo']}")
        if final_state.get("ruta"):
            print(f"Ruta: {final_state['ruta']}")
    if final_state is not None:
        print(extract_final_text(final_state))
    elif visited:
        print(" -> ".join(visited))


def diagram(agent_name: str) -> None:
    graph = load_graph(agent_name)
    try:
        mermaid = graph.get_graph().draw_mermaid()
    except Exception:
        mermaid = graph.get_graph().draw_mermaid_png()  # fallback unlikely
    print(mermaid)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta un agente LangGraph")
    parser.add_argument("agent", help="Nombre del agente en src/{nombre}/")
    parser.add_argument("message", nargs="?", default="", help="Mensaje de entrada")
    parser.add_argument("--saltos", action="store_true", help="Imprime los nodos por los que pasó el grafo")
    parser.add_argument("--diagrama", action="store_true", help="Imprime el Mermaid del grafo sin ejecutarlo")
    args = parser.parse_args()

    if args.diagrama:
        diagram(args.agent)
        return
    if not args.message:
        parser.error("Se requiere un mensaje salvo con --diagrama")
    run(args.agent, args.message, args.saltos)


if __name__ == "__main__":
    main()
