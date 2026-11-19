"""Tratamento da resposta da API: extrai o texto e reconhece os desvios."""
from src.cliente import ErroLLM

FORMATO_INESPERADO = "O LLM devolveu uma resposta em formato inesperado."


def extrair_texto(dados: dict) -> str:
    if not isinstance(dados, dict) or not isinstance(dados.get("content"), list):
        raise ErroLLM(FORMATO_INESPERADO)

    motivo = dados.get("stop_reason")
    if motivo == "refusal":
        raise ErroLLM("O modelo se recusou a resumir este texto. Confira se o que foi colado é uma vaga de emprego.")
    if motivo == "max_tokens":
        raise ErroLLM("A resposta foi cortada pelo limite de tokens antes de terminar. Aumente LLM_MAX_TOKENS no .env.")

    # A resposta é uma lista de blocos, e nem todo bloco é texto (o raciocínio do modelo vem em blocos "thinking").
    texto = "".join(
        bloco.get("text", "")
        for bloco in dados["content"]
        if isinstance(bloco, dict) and bloco.get("type") == "text"
    ).strip()
    if not texto:
        raise ErroLLM("O LLM devolveu uma resposta vazia. Tente de novo.")
    return texto
