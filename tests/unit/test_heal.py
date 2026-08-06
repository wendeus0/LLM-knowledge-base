from unittest.mock import patch

from kb.heal import _is_stub, _stamp_reviewed, heal


class TestIsStub:
    """Testes unitários para _is_stub()"""

    def test_should_detect_empty_text_as_stub(self):
        """
        Dado um texto vazio,
        Quando _is_stub() é executado,
        Então deve retornar True
        """
        # RED: falha se _is_stub não detecta texto vazio
        assert _is_stub("") is True

    def test_should_detect_headers_only_as_stub(self):
        """
        Dado um texto com apenas headers e sem conteúdo,
        Quando _is_stub() é executado,
        Então deve retornar True
        """
        # RED: falha se não detecta header-only como stub
        stub_text = """---
title: Empty Article
---

# Title

## Subtítulo
"""
        assert _is_stub(stub_text) is True

    def test_should_not_mark_content_as_stub(self):
        """
        Dado um texto com conteúdo substantivo,
        Quando _is_stub() é executado,
        Então deve retornar False
        """
        # RED: falha se marca artigo com conteúdo como stub
        content = """---
title: Article
---

# Article

Isto é conteúdo substantivo sobre um tópico.
Tem várias linhas e informação real.
Mais linhas de conteúdo.
"""
        assert _is_stub(content) is False


class TestStampReviewed:
    """Testes para _stamp_reviewed()"""

    def test_should_add_reviewed_at_when_missing(self):
        """
        Dado um artigo sem reviewed_at,
        Quando _stamp_reviewed() é chamado,
        Então deve adicionar reviewed_at
        """
        article = """---
title: Test
topic: ai
---

# Test
"""
        # RED: falha se não adiciona reviewed_at
        result = _stamp_reviewed(article)
        assert "reviewed_at:" in result

    def test_should_update_reviewed_at_when_present(self):
        """
        Dado um artigo com reviewed_at antigo,
        Quando _stamp_reviewed() é chamado,
        Então deve atualizar timestamp
        """
        article = """---
title: Test
reviewed_at: 2026-01-01
---

# Test
"""
        # RED: falha se não atualiza timestamp
        result = _stamp_reviewed(article)
        assert "reviewed_at:" in result
        assert "2026-01-01" not in result


class TestHeal:
    """Testes para heal()"""

    def test_should_process_articles(self, tmp_raw_wiki):
        """
        Dado uma wiki com artigos,
        Quando heal(n=1) é executado,
        Então deve processar artigos
        """
        raw, wiki = tmp_raw_wiki

        # Criar artigo
        (wiki / "python" / "article.md").write_text("""---
title: Article
---

# Article

Content.
""")

        with patch("kb.heal.chat") as mock_chat, patch("kb.heal.commit"):
            mock_chat.return_value = "Healed."

            # RED: falha se heal não processa
            result = heal(n=1)
            assert result is not None

    def test_should_commit_after_healing(self, tmp_raw_wiki):
        """
        Dado que heal() processou e fez mudanças,
        Quando termina,
        Então deve fazer commit
        """
        raw, wiki = tmp_raw_wiki

        # Criar artigo não-stub para ser processado
        (wiki / "ai" / "test.md").write_text("""---
title: Test
---

# Test

Conteúdo substantivo sobre teste.
""")

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("kb.heal.commit") as mock_commit,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = """---
title: Test
---

# Test

Conteúdo substantivo sobre teste com link para [[Python]].
"""
            article_path = wiki / "ai" / "test.md"
            mock_sample.return_value = [article_path]

            heal(n=1, no_commit=False)

            # RED: falha se commit não foi chamado após mudanças
            mock_commit.assert_called()

    def test_should_return_list_of_dicts(self, tmp_raw_wiki):
        """
        Dado heal() completo,
        Quando retorna,
        Então deve ser list[dict] com resultados
        """
        raw, wiki = tmp_raw_wiki

        (wiki / "typescript" / "test.md").write_text("# Test\nContent")

        with patch("kb.heal.chat") as mock_chat, patch("kb.heal.commit"):
            mock_chat.return_value = "OK"

            # RED: falha se não retorna list[dict]
            result = heal(n=1)
            assert isinstance(result, list)

    def test_should_skip_invalid_output_without_frontmatter(self, tmp_raw_wiki):
        """
        Dado artigo com frontmatter,
        Quando LLM retorna markdown sem frontmatter,
        Então deve manter artigo intacto e logar skipped_invalid_output
        """
        raw, wiki = tmp_raw_wiki

        article_path = wiki / "ai" / "invalid.md"
        original = """---
title: Invalid
---

# Invalid

Conteúdo substantivo sobre teste com informação suficiente para não ser stub.
"""
        article_path.write_text(original)

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = "# Invalid\n\nConteúdo sem frontmatter."
            mock_sample.return_value = [article_path]

            result = heal(n=1)

            assert article_path.read_text() == original
            assert result == [{"file": "invalid.md", "action": "skipped_invalid_output"}]

    def test_should_skip_collapsed_output(self, tmp_raw_wiki):
        """
        Dado artigo com conteúdo longo,
        Quando LLM retorna saída muito menor,
        Então deve manter artigo intacto e logar skipped_invalid_output
        """
        raw, wiki = tmp_raw_wiki

        article_path = wiki / "ai" / "collapse.md"
        original = """---
title: Collapse
---

# Collapse

Conteúdo substantivo sobre teste com informação suficiente para não ser stub.
Esta segunda frase aumenta o tamanho original para validar colapso de conteúdo.
Esta terceira frase mantém o artigo grande o suficiente para a heurística.
"""
        article_path.write_text(original)

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = """---
title: Collapse
---

# Collapse
"""
            mock_sample.return_value = [article_path]

            result = heal(n=1)

            assert article_path.read_text() == original
            assert result == [{"file": "collapse.md", "action": "skipped_invalid_output"}]

    def test_should_backup_before_valid_heal_write(self, tmp_raw_wiki):
        """
        Dado saída válida do LLM,
        Quando heal escreve o artigo,
        Então deve criar backup em .heal_backup
        """
        raw, wiki = tmp_raw_wiki

        article_path = wiki / "ai" / "valid.md"
        original = """---
title: Valid
---

# Valid

Conteúdo substantivo sobre teste com informação suficiente para não ser stub.
"""
        article_path.write_text(original)

        response = """---
title: Valid
---

# Valid

Conteúdo substantivo sobre teste com informação suficiente para não ser stub e link para [[Python]].
"""

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = response
            mock_sample.return_value = [article_path]

            result = heal(n=1)

            assert result == [{"file": "valid.md", "action": "healed"}]
            assert "[[Python]]" in article_path.read_text()
            backups = list((wiki / ".heal_backup").glob("*valid.*.md"))
            assert len(backups) == 1
            assert backups[0].read_text() == original

    def test_should_archive_stub_instead_of_deleting(self, tmp_raw_wiki, monkeypatch):
        """029 C2 (V7 mínimo): stub vai para archive/ com hierarquia — nunca
        unlink. O conteúdo sobrevive no vault, recuperável por git e por path.
        """
        raw, wiki = tmp_raw_wiki
        archive_dir = wiki.parent / "archive"
        monkeypatch.setattr("kb.config.ARCHIVE_DIR", archive_dir)

        stub_path = wiki / "ai" / "stub.md"
        original = """---
title: Stub
---

# Stub
"""
        stub_path.write_text(original)

        with patch("random.sample") as mock_sample:
            mock_sample.return_value = [stub_path]

            result = heal(n=1)

            assert result == [{"file": "stub.md", "action": "archived_stub"}]
            assert not stub_path.exists()
            destino = archive_dir / "ai" / "stub.md"
            assert destino.is_file()
            assert destino.read_text() == original

    def test_should_commit_archived_stub_and_manifest_when_commit_enabled(
        self, tmp_raw_wiki, monkeypatch
    ):
        """Review PR #71 (3 bots): amostra só com stubs não populava `changed`
        e o --commit não versionava nem o move nem o manifest."""
        import subprocess

        import kb.config
        from kb.state import record_backfill

        raw, wiki = tmp_raw_wiki
        vault = wiki.parent
        archive_dir = vault / "archive"
        state = vault / "kb_state"
        monkeypatch.setattr("kb.config.ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(kb.config, "DATA_DIR", vault)
        monkeypatch.setattr("kb.config.MANIFEST_PATH", state / "manifest.json")
        monkeypatch.setattr("kb.state.MANIFEST_PATH", state / "manifest.json")
        monkeypatch.setattr("kb.state.STATE_DIR", state)
        fonte = raw / "05-stub.md"
        fonte.write_text("capítulo", encoding="utf-8")
        stub_path = wiki / "ai" / "stub.md"
        stub_path.write_text("---\ntitle: Stub\n---\n\n# Stub\n")
        record_backfill(source_path=fonte, article_path=stub_path, book=None, provenance="backfill-basename")
        for cmd in (
            ["git", "init", "-q"],
            ["git", "config", "user.email", "kb@test"],
            ["git", "config", "user.name", "kb"],
            ["git", "add", "-A"],
            ["git", "commit", "-qm", "seed"],
        ):
            subprocess.run(cmd, cwd=vault, check=True)

        with patch("random.sample") as mock_sample:
            mock_sample.return_value = [stub_path]
            heal(n=1, no_commit=False)

        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=vault, check=True, capture_output=True, text=True
        ).stdout
        sujos = [linha for linha in status.splitlines() if "_index" not in linha]
        assert sujos == [], f"move do stub e manifest devem estar commitados; sobrou: {sujos}"

    def test_should_mark_manifest_when_archiving_stub(self, tmp_raw_wiki, monkeypatch):
        """A entrada do stub no manifest vira archived — o guard de recompile
        não pode apontar para path que o heal moveu."""
        import kb.config
        from kb.state import find_compiled_entry, record_backfill

        raw, wiki = tmp_raw_wiki
        archive_dir = wiki.parent / "archive"
        monkeypatch.setattr("kb.config.ARCHIVE_DIR", archive_dir)
        monkeypatch.setattr(kb.config, "DATA_DIR", wiki.parent)
        fonte = raw / "05-stub.md"
        fonte.write_text("capítulo", encoding="utf-8")
        stub_path = wiki / "ai" / "stub.md"
        stub_path.write_text("---\ntitle: Stub\n---\n\n# Stub\n")
        record_backfill(source_path=fonte, article_path=stub_path, book=None, provenance="backfill-basename")

        with patch("random.sample") as mock_sample:
            mock_sample.return_value = [stub_path]
            heal(n=1)

        assert find_compiled_entry(fonte) is None

    def test_should_exclude_heal_backup_files_from_candidates(self, tmp_raw_wiki):
        """
        Dado arquivo dentro de .heal_backup,
        Quando heal coleta candidatos,
        Então backup não deve ser processado
        """
        raw, wiki = tmp_raw_wiki

        article_path = wiki / "ai" / "article.md"
        article_path.write_text("""---
title: Article
---

# Article

Conteúdo substantivo sobre teste com informação suficiente para não ser stub.
""")
        backup_dir = wiki / ".heal_backup"
        backup_dir.mkdir()
        backup_path = backup_dir / "article.20260709-120000.md"
        backup_path.write_text("""---
title: Backup
---

# Backup

Conteúdo substantivo de backup que nunca deve ser processado pelo heal.
""")

        def sample(candidates, count):
            assert backup_path not in candidates
            return [article_path]

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = "NO_CHANGES"
            mock_sample.side_effect = sample

            result = heal(n=10)

            assert result == [{"file": "article.md", "action": "reviewed_no_changes"}]


class TestHealBackupAndKeyPreservation:
    def test_should_create_distinct_backups_when_same_stem_in_different_topics(
        self, tmp_raw_wiki
    ):
        """
        Dado dois stubs com o mesmo stem em tópicos diferentes,
        Quando heal deleta ambos no mesmo run,
        Então deve criar dois backups distintos (sem sobrescrita)
        """
        raw, wiki = tmp_raw_wiki

        stub_a = wiki / "a" / "x.md"
        stub_b = wiki / "b" / "x.md"
        stub_a.parent.mkdir(parents=True, exist_ok=True)
        stub_b.parent.mkdir(parents=True, exist_ok=True)
        stub_a.write_text("---\ntitle: A\n---\n\n# A\n")
        stub_b.write_text("---\ntitle: B\n---\n\n# B\n")

        import kb.config

        archive_dir = wiki.parent / "archive"
        with patch.object(kb.config, "ARCHIVE_DIR", archive_dir):
            with patch("random.sample") as mock_sample:
                mock_sample.return_value = [stub_a, stub_b]

                result = heal(n=2)

        assert [r["action"] for r in result] == ["archived_stub", "archived_stub"]
        # hierarquia preservada: mesmo stem em topics distintos não colide
        assert (archive_dir / "a" / "x.md").is_file()
        assert (archive_dir / "b" / "x.md").is_file()

    def test_should_skip_output_when_frontmatter_key_is_dropped(self, tmp_raw_wiki):
        """
        Dado artigo com topic no frontmatter,
        Quando LLM devolve output válido mas sem a chave topic,
        Então deve manter o artigo intacto e logar skipped_invalid_output
        """
        raw, wiki = tmp_raw_wiki

        article_path = wiki / "ai" / "keys.md"
        original = """---
title: Keys
topic: ai
tags: [a]
---

# Keys

Conteúdo substantivo sobre teste com informação suficiente para não ser stub.
"""
        article_path.write_text(original)

        response = """---
title: Keys
tags: [a]
---

# Keys

Conteúdo substantivo sobre teste com informação suficiente para não ser stub e [[link]].
"""

        with (
            patch("kb.heal.chat") as mock_chat,
            patch("random.sample") as mock_sample,
        ):
            mock_chat.return_value = response
            mock_sample.return_value = [article_path]

            result = heal(n=1)

        assert article_path.read_text() == original
        assert result == [{"file": "keys.md", "action": "skipped_invalid_output"}]
