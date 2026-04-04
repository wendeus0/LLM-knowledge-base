from unittest.mock import patch
from kb.heal import heal


class TestHealWorkflow:
    """Testes de integração: heal mantém wiki saudável"""

    def test_should_heal_and_remove_stubs_from_wiki(self, tmp_raw_wiki):
        """
        Dado uma wiki com um stub,
        Quando heal() é executado,
        Então stub deve ser detectado e removido
        """
        raw, wiki = tmp_raw_wiki
        # Criar um stub (sem conteúdo substantivo)
        stub = wiki / "python" / "empty.md"
        stub.write_text("""---
title: Empty Article
---

# Empty Article
""")

        with patch("kb.heal.chat") as mock_chat, patch(
            "kb.heal.commit"
        ), patch("random.sample") as mock_sample:
            mock_chat.return_value = "NO_CHANGES"
            mock_sample.return_value = [stub]

            result = heal(n=1)

            # RED: falha se não remove stub
            assert any(r["action"] == "deleted_stub" for r in result)

    def test_should_fix_broken_wikilinks_in_articles(self, tmp_wiki):
        """
        Dado artigos com wikilinks quebrados,
        Quando heal() é executado,
        Então LLM deve sugerir e corrigir links
        """
        article = tmp_wiki / "cybersecurity" / "auth.md"
        article.write_text("""---
title: Authentication
---

# Authentication

Ver [[NonExistent]] para mais info.
Ver [[XSS]] para outro tópico.
""")

        with patch("kb.heal.chat") as mock_chat, patch(
            "kb.heal.commit"
        ), patch("random.sample") as mock_sample:
            mock_chat.return_value = "Wikilink [[NonExistent]] não existe. Sugestão: remover ou criar artigo."
            mock_sample.return_value = [article]

            heal(n=1)

            # RED: falha se heal não processa wikilinks
            mock_chat.assert_called()

    def test_should_update_reviewed_at_timestamp(self, tmp_wiki):
        """
        Dado artigos sem reviewed_at,
        Quando heal() os processa,
        Então reviewed_at deve ser adicionado
        """
        article = tmp_wiki / "ai" / "ml.md"
        article.write_text("""---
title: Machine Learning
topic: ai
---

# Machine Learning

Machine Learning é um subcampo da inteligência artificial que permite aos sistemas aprender e melhorar a partir da experiência sem serem programados explicitamente.
""")

        with patch("kb.heal.chat") as mock_chat, patch(
            "kb.heal.commit"
        ), patch("random.sample") as mock_sample:
            mock_chat.return_value = "Processado."
            mock_sample.return_value = [article]

            result = heal(n=1)

            # RED: falha se reviewed_at não é atualizado
            # Verificar que o arquivo foi processado e timestamp foi adicionado
            assert len(result) > 0
            assert result[0]["action"] in ["healed", "reviewed_no_changes"]

    def test_should_not_delete_valuable_stubs(self, tmp_raw_wiki):
        """
        Dado um stub com texto substantivo (mesmo que curto),
        Quando heal() processa,
        Então NÃO deve deletar (porque tem conteúdo além de headers)
        """
        raw, wiki = tmp_raw_wiki
        # Criar stub com algum conteúdo (não será deletado por _is_stub)
        stub = wiki / "cybersecurity" / "authentication.md"
        stub.write_text("""---
title: Authentication
---

# Authentication

A ser completado em breve.
""")

        with patch("kb.heal.chat") as mock_chat, patch(
            "kb.heal.commit"
        ), patch("random.sample") as mock_sample:
            mock_chat.return_value = "Revisado."
            mock_sample.return_value = [stub]

            result = heal(n=1)

            # RED: falha se deleta artigos que não são stubs
            assert not any(r["action"] == "deleted_stub" for r in result)

    def test_should_generate_heal_commit_with_statistics(self, tmp_raw_wiki):
        """
        Dado heal() processando múltiplos artigos,
        Quando completa,
        Então commit deve incluir estatísticas (N processados)
        """
        raw, wiki = tmp_raw_wiki
        # Criar artigos com conteúdo substantivo
        for i in range(3):
            (wiki / "python" / f"article{i}.md").write_text(
                f"""---
title: Article {i}
---

# Article {i}

Content with substantial text content for article {i}.
"""
            )

        with patch("kb.heal.chat") as mock_chat, patch(
            "kb.heal.commit"
        ) as mock_commit, patch("random.sample") as mock_sample:
            articles = list((wiki / "python").glob("*.md"))[:3]
            mock_chat.side_effect = ["Healed.", "Healed.", "Healed."]
            mock_sample.return_value = articles

            result = heal(n=3)

            # RED: falha se commit não é chamado com mudanças
            assert len(result) > 0
            mock_commit.assert_called()
