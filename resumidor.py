"""Resume uma vaga de emprego colada no terminal, usando a API REST da Anthropic."""
from src.config import Configuracao, ConfiguracaoInvalida, carregar
import sys

import requests
from dotenv import load_dotenv
from src.entrada import EntradaVazia, ler_vaga
from src.pedido import montar_corpo

URL_API = "https://api.anthropic.com/v1/messages"
VERSAO_API = "2026-10-21"


def resumir(vaga: str, config: Configuracao) -> str:
    resposta = requests.post(
        URL_API,
        headers={
            "x-api-key": config.chave,
            "anthropic-version": VERSAO_API,
            "content-type": "application/json",
        },
        json=montar_corpo(vaga, config),
        timeout=config.timeout,
    )
    resposta.raise_for_status()
    # A resposta é uma lista de blocos, e nem todo bloco é texto.
    blocos = resposta.json()["content"]
    return "".join(b["text"] for b in blocos if b["type"] == "text")


def main() -> None:
    load_dotenv()
    try:
        config = carregar() # Programa vai falhar aqui se não houver chave ou se houver algum erro de configuração 
        vaga = ler_vaga()
    except (ConfiguracaoInvalida, EntradaVazia) as erro:
        print(erro, file=sys.stderr)
        sys.exit(1)
    print(resumir(vaga, config))

if __name__ == "__main__":
    main()
