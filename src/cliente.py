"""Chamada HTTP à API REST da Anthropic."""
import logging
import time

import requests

from src.config import Configuracao

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())  # Sem o registro configurado, nada aparece no terminal

URL_API = "https://api.anthropic.com/v1/messages"
VERSAO_API = "2026-10-21"

MENSAGENS_POR_STATUS = {
    400: "A API recusou o pedido. Confira LLM_MODEL, LLM_MAX_TOKENS e o saldo da conta.",
    401: "Credencial inválida. Confira o valor de LLM_API_KEY no .env.",
    403: "A credencial não tem permissão para usar este modelo.",
    404: "Modelo não encontrado. Confira LLM_MODEL no .env.",
    429: "Limite de uso atingido. Aguarde um pouco e tente de novo.",
}


class ErroLLM(Exception):
    """Falha ao chamar o modelo, com mensagem pronta para mostrar."""


def _verificar_status(status: int) -> None:
    if status == 200:
        return
    if status >= 500:
        raise ErroLLM("O serviço do LLM está indisponível. Tente de novo em alguns minutos.")
    raise ErroLLM(MENSAGENS_POR_STATUS.get(status, f"A API respondeu com erro inesperado ({status})."))


def _registrar(corpo: dict, config: Configuracao, inicio: float, **campos) -> None:
    """Grava uma linha com metadados da chamada. Nunca grava a chave nem o texto da vaga."""
    linha = {
        "modelo": config.modelo,
        "esforco": config.esforco,
        "entrada_chars": len(corpo["messages"][0]["content"]),
        "latencia_ms": round((time.perf_counter() - inicio) * 1000),
        **campos,
    }
    nivel = logging.INFO if campos.get("status") == 200 else logging.WARNING
    log.log(nivel, " ".join(f"{nome}={valor}" for nome, valor in linha.items()))


def _metadados(resposta: requests.Response, dados) -> dict:
    """Status, id da requisição, motivo de parada e tokens usados: nada do conteúdo."""
    dados = dados if isinstance(dados, dict) else {}
    uso = dados.get("usage") if isinstance(dados.get("usage"), dict) else {}
    return {
        "status": resposta.status_code,
        "request_id": resposta.headers.get("request-id", "-"),
        "parada": dados.get("stop_reason") or "-",
        "tokens_entrada": uso.get("input_tokens", "-"),
        "tokens_saida": uso.get("output_tokens", "-"),
    }


def enviar(corpo: dict, config: Configuracao) -> dict:
    inicio = time.perf_counter()
    try:
        resposta = requests.post(
            URL_API,
            headers={
                "x-api-key": config.chave,
                "anthropic-version": VERSAO_API,
                "content-type": "application/json",
            },
            json=corpo,
            timeout=config.timeout,
        )
    except requests.Timeout:
        _registrar(corpo, config, inicio, falha="timeout")
        raise ErroLLM(f"O LLM não respondeu no limite de {config.timeout} s. Tente de novo ou aumente LLM_TIMEOUT no .env.") from None
    except requests.RequestException:
        _registrar(corpo, config, inicio, falha="comunicacao")
        raise ErroLLM("Falha de comunicação com o LLM. Verifique sua conexão.") from None

    try:
        dados = resposta.json()
    except ValueError:
        dados = None
    _registrar(corpo, config, inicio, **_metadados(resposta, dados))

    _verificar_status(resposta.status_code)
    if dados is None:
        raise ErroLLM("O LLM devolveu uma resposta em formato inesperado.")
    return dados
