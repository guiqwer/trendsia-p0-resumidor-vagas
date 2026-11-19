import logging

import pytest

from src import registro


@pytest.fixture
def log_temporario(tmp_path, monkeypatch):
    """Aponta o log para uma pasta temporária e desfaz a configuração no fim."""
    arquivo = tmp_path / "logs" / "resumidor.log"
    monkeypatch.setattr(registro, "ARQUIVO_LOG", arquivo)
    yield arquivo
    programa = logging.getLogger("src")
    for handler in programa.handlers[:]:
        programa.removeHandler(handler)
        handler.close()
    programa.setLevel(logging.NOTSET)


def test_cria_a_pasta_e_grava_no_arquivo(log_temporario):
    registro.configurar()
    logging.getLogger("src.cliente").info("linha de teste")
    assert log_temporario.parent.is_dir()
    assert "INFO linha de teste" in log_temporario.read_text(encoding="utf-8")


def test_registros_das_bibliotecas_ficam_de_fora(log_temporario):
    registro.configurar()
    logging.getLogger("urllib3").warning("aviso de biblioteca")
    assert "aviso de biblioteca" not in log_temporario.read_text(encoding="utf-8")
