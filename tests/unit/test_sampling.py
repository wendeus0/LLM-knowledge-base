"""RED — feature 022: perfis de sampling por tarefa.

Nenhuma das nove chamadas ao LLM declarava amostragem: todas rodavam a 0,8.
Na 021 isso produziu 36 índices fora de faixa no rerank e derrubou o resultado
abaixo de não reordenar. Ordenar índices e inventar perguntas não podem
compartilhar a mesma temperatura.
"""

import pytest

from kb import sampling


class TestProfiles:
    def test_deterministic_should_have_zero_temperature(self):
        assert sampling.params("deterministic")["temperature"] == 0.0

    def test_diverse_should_have_higher_temperature_than_analytical(self):
        assert (
            sampling.params("diverse")["temperature"]
            > sampling.params("analytical")["temperature"]
        )

    def test_generative_should_sit_between_analytical_and_diverse(self):
        analytical = sampling.params("analytical")["temperature"]
        generative = sampling.params("generative")["temperature"]
        diverse = sampling.params("diverse")["temperature"]

        assert analytical < generative < diverse

    def test_should_expose_top_p(self):
        assert "top_p" in sampling.params("deterministic")

    def test_should_reject_unknown_profile(self):
        with pytest.raises(ValueError) as exc:
            sampling.params("inexistente")

        assert "inexistente" in str(exc.value)

    def test_should_return_a_copy_so_callers_cannot_mutate_the_table(self):
        first = sampling.params("analytical")
        first["temperature"] = 99.0

        assert sampling.params("analytical")["temperature"] != 99.0


class TestOverride:
    def test_should_honour_env_override(self, monkeypatch):
        monkeypatch.setenv("KB_SAMPLING_ANALYTICAL_TEMP", "0.45")

        assert sampling.params("analytical")["temperature"] == 0.45

    def test_should_ignore_invalid_override(self, monkeypatch):
        monkeypatch.setenv("KB_SAMPLING_ANALYTICAL_TEMP", "nao-e-numero")

        assert isinstance(sampling.params("analytical")["temperature"], float)

    def test_override_should_be_per_profile(self, monkeypatch):
        monkeypatch.setenv("KB_SAMPLING_DIVERSE_TEMP", "0.11")

        assert sampling.params("diverse")["temperature"] == 0.11
        assert sampling.params("deterministic")["temperature"] == 0.0
