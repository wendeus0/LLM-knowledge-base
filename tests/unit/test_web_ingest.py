"""Testes RED para kb/web_ingest.py — ingestão de URLs.

Rastreabilidade SPEC:
  REQ-1: detecta URL automaticamente (http:// ou https://)
  REQ-2: faz download do HTML via requests
  REQ-3: converte HTML para Markdown via html2text
  REQ-4: salva raw/<slug>.md com frontmatter source_url, ingested_at, title
  REQ-5: erro HTTP (4xx/5xx) → exibe erro sem criar arquivo
  REQ-6: timeout → exibe erro sem criar arquivo
  REQ-7: .[web] não instalado → mensagem clara
REQ-8: write local é padrão; commit é explícito
  REQ-9: slug usa <title> da página; fallback: 8 primeiros chars da URL
"""

from unittest.mock import MagicMock, patch

import pytest

# RED: falha até ingest-url ser implementada
from kb.web_ingest import WebIngestError, ingest_url  # noqa: E402

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

_NAV_LINKS = "\n".join(
    f'<li><a href="/section/{i}">Section {i}</a></li>' for i in range(40)
)

HTML_JS_SHELL = f"""
<html>
<head><title>Google Hacking Database</title></head>
<body>
<nav><ul>{_NAV_LINKS}</ul></nav>
<div id="root">This site requires JavaScript to run.</div>
<footer><a href="/privacy">Privacy</a><a href="/cookies">Cookies</a></footer>
</body>
</html>
"""

HTML_JS_SHELL_MINIMAL = """
<html>
<head><title>App</title></head>
<body><div id="root">Please enable JavaScript to continue.</div></body>
</html>
"""

_PARAGRAPH = (
    "Cross-site scripting happens when an application takes data controlled by "
    "the attacker and writes it into the page without escaping, so the browser "
    "executes it as if it came from the origin itself. The fix is contextual "
    "output encoding at the point of interpolation, never a blocklist of tags."
)

HTML_REAL_ARTICLE = f"""
<html>
<head><title>XSS In Depth</title></head>
<body>
<nav><ul>{_NAV_LINKS}</ul></nav>
<article><p>{_PARAGRAPH}</p><p>{_PARAGRAPH}</p></article>
</body>
</html>
"""

HTML_SHORT_REAL = f"""
<html>
<head><title>Short But Real</title></head>
<body><p>{_PARAGRAPH[:300]}</p></body>
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

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit"),
        ):
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
        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit"),
        ):
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

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit"),
        ):
            out = ingest_url("https://example.com/xss")

        # title "XSS Attack Explained" → slug "xss-attack-explained"
        assert "xss" in out.stem.lower()

    def test_should_use_url_fallback_when_page_has_no_title(
        self, tmp_path, monkeypatch
    ):
        """REQ-9b: quando página não tem <title>, usa hash dos primeiros 8 chars da URL."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_NO_TITLE
        mock_response.raise_for_status = MagicMock()

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit"),
        ):
            out = ingest_url("https://example.com/no-title")

        assert out.exists()
        assert out.suffix == ".md"
        assert "example" in out.stem or "no-title" in out.stem

    def test_should_raise_on_http_error(self, tmp_path, monkeypatch):
        """REQ-5: HTTP 4xx/5xx deve levantar WebIngestError sem criar arquivo."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        import requests as _requests

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = _requests.HTTPError(
            "404 Not Found"
        )

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
        """REQ-8: no_commit=True deve manter a ingestão apenas local."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_SAMPLE
        mock_response.raise_for_status = MagicMock()

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit") as mock_commit,
        ):
            ingest_url("https://example.com/xss", no_commit=True)

        assert not mock_commit.called

    def test_should_not_commit_by_default(self, tmp_path, monkeypatch):
        """REQ-8b: commit não deve ocorrer por padrão."""
        # RED: falha até ingest-url ser implementada
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_SAMPLE
        mock_response.raise_for_status = MagicMock()

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit") as mock_commit,
        ):
            ingest_url("https://example.com/xss")

        mock_commit.assert_not_called()

    def test_should_commit_when_explicitly_requested(self, tmp_path, monkeypatch):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_SAMPLE
        mock_response.raise_for_status = MagicMock()

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit") as mock_commit,
        ):
            ingest_url("https://example.com/xss", no_commit=False)

        mock_commit.assert_called_once()


class TestEmptyContentDetection:
    """Página que não renderiza conteúdo real não pode ser ingerida em silêncio."""

    def test_should_raise_when_page_is_only_navigation_chrome(
        self, tmp_path, monkeypatch
    ):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_JS_SHELL
        mock_response.raise_for_status = MagicMock()

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit"),
        ):
            with pytest.raises(WebIngestError, match="não rendeu conteúdo"):
                ingest_url("https://example.com/ghdb")

        assert list(raw_dir.iterdir()) == []

    def test_should_mention_javascript_and_manual_save_in_error(
        self, tmp_path, monkeypatch
    ):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_JS_SHELL_MINIMAL
        mock_response.raise_for_status = MagicMock()

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit"),
        ):
            with pytest.raises(WebIngestError) as exc_info:
                ingest_url("https://example.com/app")

        message = str(exc_info.value)
        assert "JavaScript" in message
        assert "salve" in message.lower()

    def test_should_accept_page_with_real_article(self, tmp_path, monkeypatch):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_REAL_ARTICLE
        mock_response.raise_for_status = MagicMock()

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit"),
        ):
            out = ingest_url("https://example.com/xss-in-depth")

        assert out.exists()

    def test_should_accept_short_but_real_page(self, tmp_path, monkeypatch):
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        monkeypatch.setattr("kb.config.RAW_DIR", raw_dir)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = HTML_SHORT_REAL
        mock_response.raise_for_status = MagicMock()

        with (
            patch("kb.web_ingest.requests.get", return_value=mock_response),
            patch("kb.web_ingest.commit"),
        ):
            out = ingest_url("https://example.com/short")

        assert out.exists()

    def test_should_accept_legitimate_short_line_content(self):
        """
        Dado conteúdo real de linha curta (glossário, FAQ, tabela),
        Quando o gate de conteúdo vazio avalia,
        Então aceita — o piso por linha derrubava conteúdo legítimo, e quem
        descarta menu é o link-ratio, não o comprimento da linha
        """
        from kb.web_ingest import _reject_empty_content

        glossario = "\n".join(f"- Termo {i}: definição breve." for i in range(30))
        faq = "\n".join(
            f"## Como faço a coisa {i}?\n\nVocê usa o comando numero {i} assim."
            for i in range(15)
        )
        tabela = "\n".join(f"| campo{i} | valor{i} | nota{i} |" for i in range(40))

        for body in (glossario, faq, tabela):
            _reject_empty_content(body, "https://example.com/x")

    def test_should_reject_menu_only_page_without_javascript_notice(self):
        """
        Dado uma página que é só barra de navegação, sem aviso de JavaScript,
        Quando o gate avalia,
        Então rejeita pelo volume de chrome — o aviso é sinal adicional, não a
        única evidência
        """
        from kb.web_ingest import _reject_empty_content

        so_menu = "\n".join(f"[Categoria numero {i}](/cat/{i})" for i in range(80))

        with pytest.raises(WebIngestError, match="não rendeu conteúdo"):
            _reject_empty_content(so_menu, "https://example.com/menu")


class TestSSRFProtection:
    def test_should_reject_localhost_url(self, monkeypatch):
        monkeypatch.setattr(
            "kb.web_ingest.socket.getaddrinfo",
            lambda *a, **kw: [(2, 1, 6, "", ("127.0.0.1", 0))],
        )
        with pytest.raises(WebIngestError, match="rede interna"):
            ingest_url("http://127.0.0.1/admin")

    def test_should_reject_private_network(self, monkeypatch):
        monkeypatch.setattr(
            "kb.web_ingest.socket.getaddrinfo",
            lambda *a, **kw: [(2, 1, 6, "", ("10.0.0.1", 0))],
        )
        with pytest.raises(WebIngestError, match="rede interna"):
            ingest_url("http://10.0.0.1/secret")

    def test_should_reject_172_private_range(self, monkeypatch):
        monkeypatch.setattr(
            "kb.web_ingest.socket.getaddrinfo",
            lambda *a, **kw: [(2, 1, 6, "", ("172.16.0.1", 0))],
        )
        with pytest.raises(WebIngestError, match="rede interna"):
            ingest_url("http://172.16.0.1/secret")

    def test_should_reject_192_168_private_range(self, monkeypatch):
        monkeypatch.setattr(
            "kb.web_ingest.socket.getaddrinfo",
            lambda *a, **kw: [(2, 1, 6, "", ("192.168.1.1", 0))],
        )
        with pytest.raises(WebIngestError, match="rede interna"):
            ingest_url("http://192.168.1.1/secret")

    def test_should_reject_link_local_169(self, monkeypatch):
        monkeypatch.setattr(
            "kb.web_ingest.socket.getaddrinfo",
            lambda *a, **kw: [(2, 1, 6, "", ("169.254.169.254", 0))],
        )
        with pytest.raises(WebIngestError, match="rede interna"):
            ingest_url("http://169.254.169.254/metadata")

    def test_should_reject_ipv6_loopback(self, monkeypatch):
        monkeypatch.setattr(
            "kb.web_ingest.socket.getaddrinfo",
            lambda *a, **kw: [(10, 1, 6, "", ("::1", 0, 0, 0))],
        )
        with pytest.raises(WebIngestError, match="rede interna"):
            ingest_url("http://[::1]/admin")

    def test_should_reject_ipv6_ula(self, monkeypatch):
        monkeypatch.setattr(
            "kb.web_ingest.socket.getaddrinfo",
            lambda *a, **kw: [(10, 1, 6, "", ("fd00::1", 0, 0, 0))],
        )
        with pytest.raises(WebIngestError, match="rede interna"):
            ingest_url("http://[fd00::1]/admin")

    def test_should_reject_file_scheme(self):
        with pytest.raises(WebIngestError, match="Esquema não permitido"):
            ingest_url("file:///etc/passwd")

    def test_should_reject_no_scheme(self):
        with pytest.raises(WebIngestError, match="Esquema não permitido"):
            ingest_url("example.com/page")
