"""Chamada à API com respostas simuladas pelo requests-mock: nada sai para a rede."""
import logging

import pytest
import requests

from src.cliente import URL_API, VERSAO_API, ErroLLM, enviar

VAGA = "Desenvolvedor Python Pleno na Empresa Fictícia"


@pytest.fixture
def corpo():
    return {"model": "claude-sonnet-5-5", "max_tokens": 1000, "messages": [{"role": "user", "content": VAGA}]}


def test_sucesso_devolve_o_json(requests_mock, config, corpo, resposta_api):
    requests_mock.post(URL_API, json=resposta_api())
    assert enviar(corpo, config) == resposta_api()


def test_envia_chave_versao_corpo_e_timeout(requests_mock, config, corpo, resposta_api):
    requests_mock.post(URL_API, json=resposta_api())
    enviar(corpo, config)
    pedido = requests_mock.last_request
    assert pedido.headers["x-api-key"] == "chave-de-teste"
    assert pedido.headers["anthropic-version"] == VERSAO_API
    assert pedido.json() == corpo
    assert pedido.timeout == 30


@pytest.mark.parametrize(
    "status, mensagem",
    [
        (400, "A API recusou o pedido"),
        (401, "Credencial inválida"),
        (403, "não tem permissão"),
        (404, "Modelo não encontrado"),
        (429, "Limite de uso atingido"),
        (500, "indisponível"),
        (529, "indisponível"),
        (418, r"erro inesperado \(418\)"),
    ],
)
def test_status_de_erro_vira_mensagem_clara(requests_mock, config, corpo, status, mensagem):
    requests_mock.post(URL_API, status_code=status, json={"type": "error", "error": {"type": "teste"}})
    with pytest.raises(ErroLLM, match=mensagem):
        enviar(corpo, config)


@pytest.mark.parametrize(
    "excecao, mensagem",
    [
        (requests.Timeout, "não respondeu no limite de 30 s"),
        (requests.ConnectTimeout, "não respondeu no limite de 30 s"),  # é Timeout e ConnectionError ao mesmo tempo
        (requests.ConnectionError, "Falha de comunicação"),
    ],
)
def test_falha_de_rede_vira_mensagem_clara(requests_mock, config, corpo, excecao, mensagem):
    requests_mock.post(URL_API, exc=excecao)
    with pytest.raises(ErroLLM, match=mensagem):
        enviar(corpo, config)


def test_corpo_que_nao_e_json(requests_mock, config, corpo):
    requests_mock.post(URL_API, text="<html>erro</html>")
    with pytest.raises(ErroLLM, match="formato inesperado"):
        enviar(corpo, config)


def test_log_tem_metadados_e_nao_tem_chave_nem_vaga(requests_mock, config, corpo, resposta_api, caplog):
    caplog.set_level(logging.INFO, logger="src")
    requests_mock.post(URL_API, json=resposta_api(), headers={"request-id": "req_teste"})
    enviar(corpo, config)
    linha = caplog.records[-1].getMessage()
    for trecho in ("modelo=claude-sonnet-5-5", "esforco=high", f"entrada_chars={len(VAGA)}", "status=200",
                   "request_id=req_teste", "parada=end_turn", "tokens_entrada=120", "tokens_saida=40"):
        assert trecho in linha
    assert "chave-de-teste" not in caplog.text
    assert "Empresa Fictícia" not in caplog.text


def test_log_registra_falha_como_aviso(requests_mock, config, corpo, caplog):
    caplog.set_level(logging.INFO, logger="src")
    requests_mock.post(URL_API, exc=requests.Timeout)
    with pytest.raises(ErroLLM):
        enviar(corpo, config)
    assert caplog.records[-1].levelname == "WARNING"
    assert "falha=timeout" in caplog.records[-1].getMessage()
