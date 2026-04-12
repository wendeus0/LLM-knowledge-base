"""Registry e regras de roteamento no estilo RTK."""

from kb.discover.registry import (
    classify_internal_command,
    classify_job_command,
    command_category,
)

__all__ = ["classify_internal_command", "classify_job_command", "command_category"]
