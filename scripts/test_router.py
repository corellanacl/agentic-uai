"""Ejecuta los casos de tests/casos_router.json contra el grafo router."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.router.graph import build_graph

CASES_PATH = ROOT / "tests" / "casos_router.json"


def main() -> None:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    graph = build_graph()
    aciertos = 0
    fallados = []
    rows = []
    for i, caso in enumerate(cases, start=1):
        msg = caso["mensaje"]
        esperado = caso["esperado"]
        out = graph.invoke(
            {"mensaje": msg},
            config={"configurable": {"thread_id": f"caso-{i}"}},
        )
        obtenido = out.get("ruta", "")
        motivo = out.get("motivo", "")
        ok = obtenido == esperado
        if ok:
            aciertos += 1
        else:
            fallados.append((msg, esperado, obtenido, motivo))
        rows.append((msg, esperado, obtenido, "✔" if ok else "✘", motivo))

    # Tabla
    print(f"{'Mensaje':<45} {'Esp':<10} {'Obt':<10} {'':<3} Motivo")
    print("-" * 110)
    for msg, esp, obt, marca, motivo in rows:
        print(f"{msg[:44]:<45} {esp:<10} {obt:<10} {marca:<3} {motivo}")

    total = len(cases)
    pct = (aciertos / total * 100) if total else 0
    print()
    print(f"Aciertos: {aciertos}/{total} ({pct:.1f}%)")
    if fallados:
        print("\nFallados:")
        for msg, esp, obt, motivo in fallados:
            print(f"  - {msg!r}: esperado={esp}, obtenido={obt} ({motivo})")
    else:
        print("\nSin fallos.")


if __name__ == "__main__":
    main()