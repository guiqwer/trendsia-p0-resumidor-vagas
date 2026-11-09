"""Resume uma vaga de emprego colada no terminal, usando a API REST da Anthropic."""
import os
import sys

import requests
from dotenv import load_dotenv

URL_API = "https://api.anthropic.com/v1/messages"
VERSAO_API = "2026-10-21"

INSTRUCOES = """Você recebe o texto de uma vaga de emprego em TI e devolve um resumo em português, \
exatamente neste formato:

Cargo:
Senioridade:
Stack obrigatória:
Stack desejável:
Modalidade:
Salário:
Pontos de atenção:

Use só o que está no texto. Se uma informação não aparecer, escreva "não informado"."""


def resumir(vaga: str) -> str:
    resposta = requests.post(
        URL_API,
        headers={
            "x-api-key": os.environ["LLM_API_KEY"],
            "anthropic-version": VERSAO_API,
            "content-type": "application/json",
        },
        json={
            "model": os.environ.get("LLM_MODEL", "claude-sonnet-5-5"),
            "max_tokens": 16000,
            "system": INSTRUCOES,
            "messages": [{"role": "user", "content": vaga}],
        },
        timeout=120,
    )
    resposta.raise_for_status()
    # A resposta é uma lista de blocos, e nem todo bloco é texto.
    blocos = resposta.json()["content"]
    return "".join(b["text"] for b in blocos if b["type"] == "text")


def main() -> None:
    load_dotenv()
    print("Cole o texto da vaga e termine com Ctrl+D:")
    vaga = sys.stdin.read()
    print(resumir(vaga))


if __name__ == "__main__":
    main()
