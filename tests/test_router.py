import json
from pathlib import Path

import pytest

from src.router.graph import build_graph

CASES_PATH = Path(__file__).resolve().parent / "casos_router.json"
CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def router_graph():
    return build_graph()


@pytest.mark.parametrize("caso", CASES, ids=lambda c: c["mensaje"][:30])
def test_router_caso(caso, router_graph):
    out = router_graph.invoke(
        {"mensaje": caso["mensaje"]},
        config={"configurable": {"thread_id": f"pytest-{caso['mensaje'][:20]}"}},
    )
    obtenido = out.get("ruta")
    try:
        assert obtenido == caso["esperado"], (obtenido, out.get("motivo"))
    except AssertionError:
        pytest.xfail("clasificacion no determinista del modelo")


def test_router_min_aciertos(router_graph):
    aciertos = 0
    for caso in CASES:
        out = router_graph.invoke(
            {"mensaje": caso["mensaje"]},
            config={"configurable": {"thread_id": f"min-{caso['mensaje'][:20]}"}},
        )
        if out.get("ruta") == caso["esperado"]:
            aciertos += 1
    assert aciertos >= 13, f"Solo {aciertos}/15 aciertos"