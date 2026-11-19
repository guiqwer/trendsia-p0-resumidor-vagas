"""Apresentação: o programa inteiro, com a API simulada."""
import io

import pytest

import resumidor
from src.cliente import URL_API


@pytest.fixture
def programa(monkeypatch, requests_mock):
    """Roda o main() sem ler o .env real, sem gravar log e com a API simulada."""
    monkeypatch.setattr(resumidor, "load_dotenv", lambda: None)
    monkeypatch.setattr(resumidor.registro, "configurar", lambda: None)
    monkeypatch.setenv("LLM_API_KEY", "chave-de-teste")

    def rodar(vaga):
        monkeypatch.setattr("sys.stdin", io.StringIO(vaga))
        resumidor.main()

    return rodar


def test_resumo_sai_no_stdout(programa, requests_mock, resposta_api, capsys):
    requests_mock.post(URL_API, json=resposta_api("Cargo: Desenvolvedor Python"))
    programa("Vaga de Dev Python")
    saida = capsys.readouterr()
    assert saida.out == "Cargo: Desenvolvedor Python\n"
    assert "Cole o texto da vaga" in saida.err


def test_entrada_vazia_sai_com_codigo_1_sem_chamar_a_api(programa, requests_mock, capsys):
    with pytest.raises(SystemExit) as saida:
        programa("   \n")
    assert saida.value.code == 1
    assert "Nenhum texto recebido" in capsys.readouterr().err
    assert not requests_mock.called


def test_credencial_ausente_sai_com_codigo_1(programa, monkeypatch, capsys):
    monkeypatch.delenv("LLM_API_KEY")
    with pytest.raises(SystemExit) as saida:
        programa("Vaga de Dev Python")
    assert saida.value.code == 1
    assert "LLM_API_KEY não definida" in capsys.readouterr().err


def test_credencial_invalida_sai_com_codigo_1_sem_traceback(programa, requests_mock, capsys):
    requests_mock.post(URL_API, status_code=401, json={"type": "error"})
    with pytest.raises(SystemExit) as saida:
        programa("Vaga de Dev Python")
    assert saida.value.code == 1
    erro = capsys.readouterr().err
    assert "Credencial inválida" in erro
    assert "Traceback" not in erro
