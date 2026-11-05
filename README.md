# Ecommerce Router API

Proyecto de agente en LangGraph que actúa como router de un chat de ecommerce.
Clasifica cada mensaje del usuario en una de tres rutas (`preventa`, `postventa`
o `generica`) y lo enruta al agente correspondiente. Expone la funcionalidad
mediante una API FastAPI (con Swagger) y un webhook para Telegram.

## Qué hace el proyecto

- Agente `router` (`src/router/`) con salida estructurada (`Decision`: ruta + motivo).
- Tres agentes destino cascarón: preventa, postventa y respuesta genérica.
- Memoria por `thread_id` usando `MemorySaver`.
- API FastAPI (`api/app.py`) con `/health`, `/chat` y `/telegram`.
- Pruebas en `tests/` (pytest) y script de casos en `scripts/test_router.py`.

## Correr el router en local

```bash
.venv/bin/python main.py router "¿tienen la polera azul en talla M?" --saltos
.venv/bin/python main.py router --diagrama
```

## Levantar la API

```bash
uvicorn api.app:app --reload --port 8000
```

Documentación interactiva (Swagger): http://localhost:8000/docs

## Ejemplo de /chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "u1", "texto": "¿tienen la polera azul en talla M?"}'
```

Respuesta esperada:

```json
{"ruta":"preventa","motivo":"...","respuesta":"Soy el agente de preventa. ..."}
```

## Correr las pruebas

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/test_router.py
```

## Desplegar en Heroku

```bash
heroku create
git push heroku main
heroku config:set GOOGLE_API_KEY=tu_clave MODELO=gemini-3.5-flash-lite TELEGRAM_TOKEN=tu_token TELEGRAM_SECRET=cambiame PUBLIC_URL=https://tu-app.herokuapp.com
```

El `Procfile` ya define el comando web:

```
web: uvicorn api.app:app --host 0.0.0.0 --port $PORT
```

## Conectar Telegram

1. Crea un bot con BotFather y obtén `TELEGRAM_TOKEN`.
2. Despliega la API y obtén la URL pública (`PUBLIC_URL`).
3. Registra el webhook (reemplaza los valores):

```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://tu-app.herokuapp.com/telegram", "secret_token": "cambiame"}'
```

4. Asegúrate de que `TELEGRAM_SECRET` coincida con el `secret_token` enviado.
