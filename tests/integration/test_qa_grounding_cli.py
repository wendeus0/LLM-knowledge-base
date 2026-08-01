"""Superfícies de saída da verificação de ancoragem (T-005, T-006).

Três adaptadores sobre o mesmo resultado: bloco humano no terminal, documento
JSON exclusivo em stdout e seção Markdown no file-back.

Sem rede: `kb.qa.chat` e `kb.grounding.verify` são as fronteiras mockadas.
Veredito negativo nunca bloqueia — a anotação é aviso, nunca gate (RF-06).
"""

import json

from typer.testing import CliRunner

from kb import grounding
from kb.cli import app

runner = CliRunner()

RESPOSTA = "O circuit breaker abre após falhas consecutivas."


def _resultado(status="verified", verdict="ancorada"):
    return grounding.GroundingResult(
        status=status,
        claims=[
            grounding.ClaimVerdict(
                claim="O circuit breaker abre após falhas consecutivas.",
                verdict=verdict,
                evidence="Após falhas consecutivas, o circuit breaker abre.",
                scores={"entailment": 0.91, "contradiction": 0.04, "neutral": 0.05},
            )
        ],
    )


def _preparar(tmp_path, monkeypatch, resultado=None):
    wiki = tmp_path / "wiki"
    outputs = tmp_path / "outputs"
    state = tmp_path / "kb_state"
    for caminho in (wiki, outputs, state):
        caminho.mkdir(parents=True, exist_ok=True)
    (wiki / "cybersecurity").mkdir(exist_ok=True)
    (wiki / "cybersecurity" / "circuit-breaker.md").write_text(
        "# Circuit breaker\nApós falhas consecutivas, o circuit breaker abre."
    )
    monkeypatch.setenv("KB_WIKI_DIR", str(wiki))
    monkeypatch.setenv("KB_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("KB_STATE_DIR", str(state))
    monkeypatch.setattr("kb.qa.chat", lambda **kwargs: RESPOSTA)
    monkeypatch.setattr(
        grounding,
        "verify",
        lambda response, context, max_pairs=None: resultado or _resultado(),
    )
    return wiki, outputs


class TestHumanOutput:
    def test_should_show_the_verdict_block_after_the_answer(self, tmp_path, monkeypatch):
        _preparar(tmp_path, monkeypatch)

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?"])

        assert resultado.exit_code == 0
        assert RESPOSTA in resultado.stdout
        assert "ancorada" in resultado.stdout.lower()

    def test_should_show_the_evidence_next_to_the_verdict(self, tmp_path, monkeypatch):
        _preparar(tmp_path, monkeypatch)

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?"])

        assert "Após falhas consecutivas" in resultado.stdout


class TestJsonOutput:
    def test_should_print_a_single_parseable_json_document(self, tmp_path, monkeypatch):
        _preparar(tmp_path, monkeypatch)

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?", "--json"])

        assert resultado.exit_code == 0
        payload = json.loads(resultado.stdout)
        assert payload["answer"] == RESPOSTA
        assert payload["grounding"]["status"] == "verified"

    def test_should_expose_the_documented_json_shape(self, tmp_path, monkeypatch):
        _preparar(tmp_path, monkeypatch)

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?", "--json"])
        assert resultado.exit_code == 0
        payload = json.loads(resultado.stdout)

        assert set(payload) >= {"answer", "grounding", "saved_path"}
        assert set(payload["grounding"]) >= {
            "status",
            "checked_claims",
            "unverified_due_to_limit",
            "claims",
        }
        primeira = payload["grounding"]["claims"][0]
        assert set(primeira) >= {"claim", "verdict", "evidence", "scores"}

    def test_should_report_null_saved_path_when_there_is_no_file_back(
        self, tmp_path, monkeypatch
    ):
        _preparar(tmp_path, monkeypatch)

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?", "--json"])

        assert resultado.exit_code == 0
        assert json.loads(resultado.stdout)["saved_path"] is None

    def test_should_keep_stdout_free_of_progress_text_in_json_mode(self, tmp_path, monkeypatch):
        _preparar(tmp_path, monkeypatch)

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?", "--json"])

        assert resultado.exit_code == 0
        json.loads(resultado.stdout)


class TestFileBack:
    def test_should_write_the_grounding_section_in_the_archived_file(
        self, tmp_path, monkeypatch
    ):
        _wiki, outputs = _preparar(tmp_path, monkeypatch)

        resultado = runner.invoke(
            app, ["qa", "O que faz o circuit breaker?", "--file-back", "--no-commit"]
        )

        assert resultado.exit_code == 0
        arquivos = list(outputs.rglob("*.md"))
        assert arquivos
        conteudo = arquivos[0].read_text()
        assert "Verificação de ancoragem" in conteudo
        assert "ancorada" in conteudo.lower()


class TestNonBlocking:
    def test_should_not_block_the_answer_on_a_contradita_verdict(self, tmp_path, monkeypatch):
        _preparar(tmp_path, monkeypatch, _resultado(verdict="contradita"))

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?"])

        assert resultado.exit_code == 0
        assert RESPOSTA in resultado.stdout

    def test_should_not_block_the_file_back_on_a_contradita_verdict(
        self, tmp_path, monkeypatch
    ):
        _wiki, outputs = _preparar(tmp_path, monkeypatch, _resultado(verdict="contradita"))

        resultado = runner.invoke(
            app, ["qa", "O que faz o circuit breaker?", "--file-back", "--no-commit"]
        )

        assert resultado.exit_code == 0
        assert list(outputs.rglob("*.md"))

    def test_should_keep_the_answer_when_the_service_is_degraded(self, tmp_path, monkeypatch):
        _preparar(tmp_path, monkeypatch, grounding.GroundingResult(status="degraded"))

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?"])

        assert resultado.exit_code == 0
        assert RESPOSTA in resultado.stdout


class TestNoGrounding:
    def test_should_not_touch_the_service_when_no_grounding_is_passed(
        self, tmp_path, monkeypatch
    ):
        _preparar(tmp_path, monkeypatch)

        def _nao_deve_chamar(response, context, max_pairs=None):
            raise AssertionError("--no-grounding não deve alcançar o serviço NLI")

        monkeypatch.setattr(grounding, "verify", _nao_deve_chamar)

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?", "--no-grounding"])

        assert resultado.exit_code == 0
        assert RESPOSTA in resultado.stdout

    def test_should_report_skipped_status_in_json_with_no_grounding(
        self, tmp_path, monkeypatch
    ):
        _preparar(tmp_path, monkeypatch)
        monkeypatch.setattr(
            grounding,
            "verify",
            lambda response, context, max_pairs=None: (_ for _ in ()).throw(
                AssertionError("não deve ser chamado")
            ),
        )

        resultado = runner.invoke(
            app, ["qa", "O que faz o circuit breaker?", "--no-grounding", "--json"]
        )

        assert resultado.exit_code == 0
        assert json.loads(resultado.stdout)["grounding"]["status"] == "skipped"


class TestHumanOutputEmptyBlock:
    def test_should_not_print_an_empty_human_block_without_claims(self, tmp_path, monkeypatch):
        _preparar(tmp_path, monkeypatch, grounding.GroundingResult(status="skipped"))

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?"])

        assert resultado.exit_code == 0
        assert "Verificação de ancoragem" not in resultado.stdout

    def test_should_not_print_an_empty_human_block_when_degraded(self, tmp_path, monkeypatch):
        _preparar(tmp_path, monkeypatch, grounding.GroundingResult(status="degraded"))

        resultado = runner.invoke(app, ["qa", "O que faz o circuit breaker?"])

        assert resultado.exit_code == 0
        assert "Verificação de ancoragem" not in resultado.stdout
