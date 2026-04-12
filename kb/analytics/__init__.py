"""Camada analytics para métricas de execução."""

from kb.analytics.gain import render_gain_summary
from kb.analytics.history import get_history_summary

__all__ = ["render_gain_summary", "get_history_summary"]
