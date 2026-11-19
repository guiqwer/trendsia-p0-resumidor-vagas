import pytest

from src.cliente import ErroLLM
from src.resposta import extrair_texto


def test_devolve_o_texto(resposta_api):
    assert extrair_texto(resposta_api("Cargo: Dev")) == "Cargo: Dev"


def test_ignora_raciocinio_e_junta_os_blocos_de_texto(resposta_api):
    content = [
        {"type": "thinking", "thinking": ""},
        {"type": "text", "text": "Cargo: Dev\n"},
        {"type": "text", "text": "Senioridade: Pleno"},
    ]
    assert extrair_texto(resposta_api(content=content)) == "Cargo: Dev\nSenioridade: Pleno"


def test_recusa_do_modelo(resposta_api):
    with pytest.raises(ErroLLM, match="se recusou"):
        extrair_texto(resposta_api(content=[], stop_reason="refusal"))


def test_resposta_cortada_pelo_limite(resposta_api):
    with pytest.raises(ErroLLM, match="Aumente LLM_MAX_TOKENS"):
        extrair_texto(resposta_api("Cargo: Dev", stop_reason="max_tokens"))


@pytest.mark.parametrize(
    "content",
    [[], [{"type": "text", "text": "   "}], [{"type": "thinking", "thinking": ""}]],
)
def test_resposta_vazia(resposta_api, content):
    with pytest.raises(ErroLLM, match="resposta vazia"):
        extrair_texto(resposta_api(content=content))


@pytest.mark.parametrize("dados", [None, [], "texto", {"type": "message"}, {"content": "não é lista"}])
def test_formato_inesperado(dados):
    with pytest.raises(ErroLLM, match="formato inesperado"):
        extrair_texto(dados)
