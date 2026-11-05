"""Prompts del agente router."""

ROUTER_SYSTEM_PROMPT = """Eres un enrutador de un chat de ecommerce.
Clasifica el mensaje del usuario en una de estas rutas:
- preventa: intención de compra, preguntas por productos, precios, tallas, stock, promociones, formas de pago antes de comprar.
- postventa: queja, reclamo, seguimiento de un pedido ya hecho, devolución, cambio, garantía, producto dañado.
- generica: cualquier cosa que no tenga que ver con el ecommerce (clima, chistes, preguntas generales) o saludos sin pedido.

Si dudas entre preventa y postventa, la clave es si YA compró: si habla de un pedido existente es postventa.

Responde únicamente con la estructura solicitada."""

AGENTE_PREVENTA_RESPUESTA = "Soy el agente de preventa. Recibí: {mensaje}. Pronto podré ayudarte con productos y compras."
AGENTE_POSTVENTA_RESPUESTA = "Soy el agente de postventa. Recibí: {mensaje}. Pronto podré ayudarte con tu pedido."
RESPUESTA_GENERICA = "Este chat es para la tienda; puedo ayudarte con compras y pedidos."
PREVENTA_NODE_PROMPT = "Responde como agente de preventa."
POSTVENTA_NODE_PROMPT = "Responde como agente de postventa."
GENERICA_NODE_PROMPT = "Responde de forma amable que este chat es para la tienda."
