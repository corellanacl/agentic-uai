"""Herramientas disponibles para el agente demo."""

from langchain_core.tools import tool


@tool
def saludar(nombre: str) -> str:
    """Saluda a una persona por su nombre."""
    return f"Hola, {nombre}! Bienvenido/a."


TOOLS = [saludar]
