import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_diagrama_demo():
    r = subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "main.py", "demo", "--diagrama"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "graph" in r.stdout.lower() or "agent" in r.stdout.lower() or "mermaid" in r.stdout.lower() or "flowchart" in r.stdout.lower()


def test_saltos_echo():
    r = subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "main.py", "echo", "hola", "--saltos"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "Saltos: echo" in r.stdout


def test_main_requires_message():
    r = subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "main.py", "demo"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
