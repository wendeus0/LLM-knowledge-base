"""Infraestrutura compartilhada inspirada na arquitetura do RTK."""

from kb.core.runner import CommandResult, run_command
from kb.core.tracking import track_command

__all__ = ["CommandResult", "run_command", "track_command"]
