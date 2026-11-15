"""Chamada HTTP à API REST da Anthropic."""
import requests

from src.config import Configuracao

URL_API = "https://api.anthropic.com/v1/messages"
VERSAO_API = "2026-10-21"

MENSAGENS_POR_STATUS = {
    400: "A API recusou o pedido. Confira LLM_MODEL e o saldo da conta.",
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


def enviar(corpo: dict, config: Configuracao) -> dict:
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
        raise ErroLLM(f"O LLM não respondeu em {config.timeout} segundos. Tente de novo ou aumente LLM_TIMEOUT no .env.") from None
    except requests.RequestException:
        raise ErroLLM("Falha de comunicação com o LLM. Verifique sua conexão.") from None

    _verificar_status(resposta.status_code)

    try:
        return resposta.json()
    except ValueError:
        raise ErroLLM("O LLM devolveu uma resposta em formato inesperado.") from None
