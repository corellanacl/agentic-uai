"""API FastAPI del router de ecommerce."""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")
TELEGRAM_SECRET = os.getenv("TELEGRAM_SECRET", "cambiame")

logger = logging.getLogger("ecommerce_router")
logging.basicConfig(level=logging.INFO)


class HealthResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"ok": True, "modelo": "gemini-3.5-flash-lite"}})
    ok: bool = Field(..., description="Indica si el servicio está vivo")
    modelo: str = Field(..., description="Modelo configurado", examples=["gemini-3.5-flash-lite"])


class ChatRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"user_id": "u1", "texto": "¿tienen la polera azul en talla M?"}
        }
    )
    user_id: str = Field(..., description="Identificador del usuario (thread_id)", examples=["u1"])
    texto: str = Field(..., description="Mensaje del usuario", examples=["¿tienen la polera azul en talla M?"])


class ChatResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ruta": "preventa",
                "motivo": "El usuario pregunta por disponibilidad de producto.",
                "respuesta": "Soy el agente de preventa. Recibí: ...",
            }
        }
    )
    ruta: str = Field(..., description="Ruta elegida: preventa, postventa o generica", examples=["preventa"])
    motivo: str = Field(..., description="Motivo de la clasificación", examples=["El usuario pregunta por disponibilidad."])
    respuesta: str = Field(..., description="Respuesta del agente destino", examples=["Soy el agente de preventa..."])


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.router.graph import build_graph

    app.state.graph = build_graph()
    yield
    app.state.graph = None


app = FastAPI(
    title="Ecommerce Router API",
    version="1.0.0",
    description=(
        "API del router de chat de ecommerce. Clasifica cada mensaje en una de tres rutas "
        "(preventa, postventa o generica) y lo enruta al agente correspondiente."
    ),
    lifespan=lifespan,
)


@app.get("/health", tags=["salud"], response_model=HealthResponse, summary="Salud del servicio")
def health() -> HealthResponse:
    return HealthResponse(ok=True, modelo=MODELO)


@app.post(
    "/chat",
    tags=["chat"],
    response_model=ChatResponse,
    summary="Enviar un mensaje al router",
    responses={
        200: {"description": "Clasificación y respuesta del router", "model": ChatResponse},
        422: {"description": "Body inválido o falta el campo texto"},
        502: {"description": "Error al invocar el modelo"},
    },
)
def chat(req: ChatRequest) -> ChatResponse:
    graph = getattr(app.state, "graph", None)
    if graph is None:
        from src.router.graph import build_graph

        graph = build_graph()
        app.state.graph = graph
    try:
        out = graph.invoke(
            {"mensaje": req.texto},
            config={"configurable": {"thread_id": req.user_id}},
        )
    except Exception:
        logger.exception("Error al invocar el router/modelo")
        raise HTTPException(status_code=502, detail="El modelo no está disponible en este momento. Intenta nuevamente.")
    return ChatResponse(
        ruta=out.get("ruta", ""),
        motivo=out.get("motivo", ""),
        respuesta=out.get("respuesta", ""),
    )


@app.post("/telegram", include_in_schema=False, tags=["telegram"], summary="Webhook de Telegram")
async def telegram(request: Request):
    await request.json()
    return {"ok": True}