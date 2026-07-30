"""RED — guarda de isolamento: nenhuma fixture pode deixar o vault real exposto.

Regressão real: `tmp_wiki` isolava WIKI_DIR mas não STATE_DIR. Quando a feature
015 acrescentou refresh de índice ao fim do `heal`, um teste de integração
passou a reconstruir o índice do vault do usuário a partir de um wiki
temporário de 1 artigo — 1.037 vetores viraram 1.
"""

import kb.config as config


class TestFixtureIsolation:
    def test_tmp_wiki_should_isolate_state_dir(self, tmp_wiki, tmp_path):
        assert str(config.STATE_DIR).startswith(str(tmp_path))

    def test_tmp_wiki_should_isolate_wiki_dir(self, tmp_wiki, tmp_path):
        assert str(config.WIKI_DIR).startswith(str(tmp_path))

    def test_tmp_raw_wiki_should_isolate_state_dir(self, tmp_raw_wiki, tmp_path):
        assert str(config.STATE_DIR).startswith(str(tmp_path))

    def test_tmp_wiki_should_isolate_tracking_db(self, tmp_wiki, tmp_path):
        from kb.core import tracking

        assert str(tracking.DB_PATH).startswith(str(tmp_path))

    def test_tmp_raw_wiki_should_isolate_tracking_db(self, tmp_raw_wiki, tmp_path):
        from kb.core import tracking

        assert str(tracking.DB_PATH).startswith(str(tmp_path))

    def test_tmp_raw_wiki_should_isolate_router_wiki_dir(self, tmp_raw_wiki, tmp_path):
        from kb import router

        assert str(router.WIKI_DIR).startswith(str(tmp_path))
