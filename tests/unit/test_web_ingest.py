"""Testes RED para kb/web_ingest.py — ingestão de URLs.

Rastreabilidade SPEC:
  REQ-1: detecta URL automaticamente (http:// ou https://)
  REQ-2: faz download do HTML via requests
  REQ-3: converte HTML para Markdown via html2text
  REQ-4: salva raw/<slug>.md com frontmatter source_url, ingested_at, title
  REQ-5: erro HTTP (4xx/5xx) → exibe erro sem criar arquivo
  REQ-6: timeout → exibe erro sem criar arquivo
  REQ-7: .[web] não instalado → mensagem clara
  REQ-8: --no-commit suprime commit automático
  REQ-9: slug usa <title> da página; fallback: 8 primeiros chars da URL
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# RED: falha até ingest-url ser implementada
from kb.web_ingest import ingest_url, WebIngestError  # noqa: E402


HTML_SAMPLE = """
<html>
<head><title>XSS Attack Explained</title></head>
<body>
<h1>XSS Attack Explained</h1>
<p>Cross-Site Scripting (XSS) is a security vulnerability.</p>
</body>
</html>
"""

HTML_NO_TITLE = """
<html>
<body><p>Content without a title tag.</p></body>
</html>
"""


class TestIngestUrl:
    """Testa kb.web_ingest.ingest_url(url)."""

    def test_should_save_markdown_file_in_raw_dir(self, tmp_path, monkeypatch):
        """REQ-4: ingest_url deve salvar arquivo .md em raw/."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_SAMPLE
        mock_response.raise_for_status = MagicMock()

        with patch("kb.web_ingest.requests.get", return_value=mock_response), \
             patch("kb.web_ingest.commit"):
            out = ingest_url("https://example.com/xss")

        assert out.suffix == ".md"
        assert out.parent == raw_dir

    def test_should_include_required_frontmatter_fields(self, tmp_path, monkeypatch):
        """REQ-4: frontmatter deve ter source_url, ingested_at, title."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_SAMPLE
        mock_response.raise_for_status = MagicMock()

        url = "https://example.com/xss"
        with patch("kb.web_ingest.requests.get", return_value=mock_response), \
             patch("kb.web_ingest.commit"):
            out = ingest_url(url)

        content = out.read_text(encoding="utf-8")
        assert "source_url:" in content
        assert url in content
        assert "ingested_at:" in content
        assert "title:" in content

    def test_should_use_page_title_as_slug(self, tmp_path, monkeypatch):
        """REQ-9: slug do arquivo deve ser derivado do <title> da página."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_SAMPLE
        mock_response.raise_for_status = MagicMock()

        with patch("kb.web_ingest.requests.get", return_value=mock_response), \
             patch("kb.web_ingest.commit"):
            out = ingest_url("https://example.com/xss")

        # title "XSS Attack Explained" → slug "xss-attack-explained"
        assert "xss" in out.stem.lower()

    def test_should_use_url_fallback_when_page_has_no_title(self, tmp_path, monkeypatch):
        """REQ-9b: quando página não tem <title>, usa hash dos primeiros 8 chars da URL."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_NO_TITLE
        mock_response.raise_for_status = MagicMock()

        with patch("kb.web_ingest.requests.get", return_value=mock_response), \
             patch("kb.web_ingest.commit"):
            out = ingest_url("https://example.com/no-title")

        assert out.exists()
        assert out.suffix == ".md"

    def test_should_raise_on_http_error(self, tmp_path, monkeypatch):
        """REQ-5: HTTP 4xx/5xx deve levantar WebIngestError sem criar arquivo."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        import requests as _requests

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = _requests.HTTPError("404 Not Found")

        with patch("kb.web_ingest.requests.get", return_value=mock_response):
            with pytest.raises(WebIngestError, match="404"):
                ingest_url("https://example.com/not-found")

        assert list(raw_dir.iterdir()) == []

    def test_should_raise_on_timeout(self, tmp_path, monkeypatch):
        """REQ-6: timeout deve levantar WebIngestError sem criar arquivo."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        import requests as _requests

        with patch("kb.web_ingest.requests.get", side_effect=_requests.Timeout()):
            with pytest.raises(WebIngestError, match="[Tt]imeout"):
                ingest_url("https://example.com/slow")

        assert list(raw_dir.iterdir()) == []

    def test_should_suppress_commit_when_no_commit_is_true(self, tmp_path, monkeypatch):
        """REQ-8: no_commit=True deve suprimir o commit automático."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_SAMPLE
        mock_response.raise_for_status = MagicMock()

        with patch("kb.web_ingest.requests.get", return_value=mock_response), \
             patch("kb.web_ingest.commit") as mock_commit:
            ingest_url("https://example.com/xss", no_commit=True)

        assert not mock_commit.called

    def test_should_commit_automatically_by_default(self, tmp_path, monkeypatch):
        """REQ-8b: commit automático deve ser chamado por padrão."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_SAMPLE
        mock_response.raise_for_status = MagicMock()

        with patch("kb.web_ingest.requests.get", return_value=mock_response), \
             patch("kb.web_ingest.commit") as mock_commit:
            ingest_url("https://example.com/xss")

        assert mock_commit.called
