"""Guardrails operacionais para conteúdo sensível."""

from __future__ import annotations

import re
from dataclasses import dataclass


SENSITIVE_PATTERNS = {
    "api_key": re.compile(r"(?i)(api[_-]?key\s*[:=]\s*|sk-[a-z0-9]{10,})"),
    "token": re.compile(r"(?i)(token\s*[:=]\s*[a-z0-9_\-]{8,})"),
    "password": re.compile(r"(?i)(password\s*[:=])"),
    "secret": re.compile(r"(?i)(secret\s*[:=])"),
    "private_key": re.compile(r"-----BEGIN (RSA|EC|OPENSSH|DSA)? ?PRIVATE KEY-----"),
}


@dataclass(frozen=True)
class SensitiveFinding:
    label: str
    sample: str


class SensitiveContentError(RuntimeError):
    def __init__(self, findings: list[SensitiveFinding], source: str):
        self.findings = findings
        self.source = source
        labels = ", ".join(sorted({finding.label for finding in findings}))
        super().__init__(f"Conteúdo potencialmente sensível detectado em {source}: {labels}")


def _redact_match(value: str) -> str:
    clipped = value[:80]
    if len(clipped) <= 8:
        return "[redacted]"
    return f"{clipped[:4]}…{clipped[-4:]}"



def detect_sensitive_content(text: str) -> list[SensitiveFinding]:
    findings: list[SensitiveFinding] = []
    for label, pattern in SENSITIVE_PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append(SensitiveFinding(label=label, sample=_redact_match(match.group(0))))
    return findings


def assert_safe_for_provider(text: str, source: str, allow_sensitive: bool = False) -> None:
    findings = detect_sensitive_content(text)
    if findings and not allow_sensitive:
        raise SensitiveContentError(findings, source)


def summarize_findings(error: SensitiveContentError) -> str:
    bullets = "\n".join(f"- {finding.label}: `{finding.sample}`" for finding in error.findings[:5])
    return f"{error}\n{bullets}"
