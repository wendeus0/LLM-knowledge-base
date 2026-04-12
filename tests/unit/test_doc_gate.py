from kb.doc_gate import evaluate_doc_gate


def test_doc_gate_should_pass_when_no_code_changes():
    result = evaluate_doc_gate(["README.md", "docs/adr/0001.md"])
    assert result.ok is True
    assert result.code_files == []


def test_doc_gate_should_fail_when_code_changes_without_docs():
    result = evaluate_doc_gate(["kb/cli.py", "kb/jobs.py"])
    assert result.ok is False
    assert "Mudança de código detectada" in result.reason


def test_doc_gate_should_pass_when_code_and_handoff_change_together():
    result = evaluate_doc_gate(["kb/cli.py", "docs/handoffs/2026-04-12-2300.md"])
    assert result.ok is True
    assert "kb/cli.py" in result.code_files
    assert "docs/handoffs/2026-04-12-2300.md" in result.doc_files


def test_doc_gate_should_pass_when_code_and_spec_change_together():
    result = evaluate_doc_gate(["kb/compile.py", "features/llm-wiki-v2-foundation/SPEC.md"])
    assert result.ok is True
    assert "features/llm-wiki-v2-foundation/SPEC.md" in result.doc_files
