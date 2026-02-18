import os
from pathlib import Path

def ensure_logs_dir():
    """Ensure logs directory exists"""
    base_dir = Path(__file__).resolve().parent.parent
    logs_dir = base_dir / 'logs'
    logs_dir.mkdir(exist_ok=True, parents=True)  # parents=True creates parent directories too

# Call this function when the project loads
ensure_logs_dir()