import pytest

from kb.discover import registry, rules


@pytest.mark.parametrize("command, category", rules.INTERNAL_RULES)
def test_should_classify_command_when_command_is_declared_in_rules(command, category):
    """
    Dado um comando declarado nas regras internas,
    Quando o registry classifica o comando,
    Entao a categoria declarativa deve ser retornada.
    """
    assert registry.classify_internal_command(command) == category


def test_should_normalize_command_when_command_has_spaces_and_uppercase():
    """
    Dado um comando conhecido com espacos e maiusculas,
    Quando o registry classifica o comando,
    Entao a categoria deve considerar o nome normalizado.
    """
    assert registry.command_category("  COMPILE  ") == "pipeline"


def test_should_classify_job_command_when_job_name_maps_to_internal_command():
    """
    Dado um job canonico associado a um comando interno,
    Quando o registry classifica o job,
    Entao a categoria do comando associado deve ser retornada.
    """
    assert registry.classify_job_command("review") == "maintenance"
    assert registry.classify_job_command("metrics") == "operations"
    assert registry.classify_job_command("index-refresh") == "pipeline"


def test_should_return_unknown_when_command_is_not_declared():
    """
    Dado um comando desconhecido,
    Quando o registry classifica o comando,
    Entao a categoria default deve ser unknown.
    """
    assert registry.classify_internal_command("missing") == "unknown"
    assert registry.classify_job_command("missing") == "unknown"
