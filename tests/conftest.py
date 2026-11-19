"""Peças comuns dos testes. Nenhum teste chama a API de verdade."""
import pytest

from src.config import Configuracao


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch):
    """Remove as variáveis LLM_* do ambiente, para a configuração de quem roda não interferir."""
    for nome in ("LLM_API_KEY", "LLM_MODEL", "LLM_TIMEOUT", "LLM_MAX_TOKENS", "LLM_EFFORT"):
        monkeypatch.delenv(nome, raising=False)


@pytest.fixture
def config():
    return Configuracao("chave-de-teste", "claude-sonnet-5-5", timeout=30, max_tokens=1000, esforco="high")


@pytest.fixture
def resposta_api():
    """Monta uma resposta no formato da API de mensagens da Anthropic."""
    def montar(texto="Cargo: Desenvolvedor Python", stop_reason="end_turn", content=None):
        return {
            "id": "msg_teste",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-5-5",
            "content": [{"type": "text", "text": texto}] if content is None else content,
            "stop_reason": stop_reason,
            "usage": {"input_tokens": 120, "output_tokens": 40},
        }
    return montar
