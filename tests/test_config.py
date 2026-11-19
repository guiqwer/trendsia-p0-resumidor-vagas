import pytest

from src.config import (
    ESFORCO_PADRAO,
    MAX_TOKENS_PADRAO,
    MODELO_PADRAO,
    TIMEOUT_PADRAO,
    ConfiguracaoInvalida,
    CredencialAusente,
    carregar,
)


def test_sem_chave_avisa_credencial_ausente():
    with pytest.raises(CredencialAusente, match="LLM_API_KEY não definida"):
        carregar()


def test_chave_so_com_espacos_conta_como_ausente(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "   ")
    with pytest.raises(CredencialAusente):
        carregar()


def test_usa_os_valores_padrao(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "chave-de-teste")
    config = carregar()
    assert config.modelo == MODELO_PADRAO
    assert config.timeout == TIMEOUT_PADRAO
    assert config.max_tokens == MAX_TOKENS_PADRAO
    assert config.esforco == ESFORCO_PADRAO


def test_le_os_valores_do_ambiente(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "chave-de-teste")
    monkeypatch.setenv("LLM_MODEL", "claude-haiku-5-5")
    monkeypatch.setenv("LLM_TIMEOUT", "30")
    monkeypatch.setenv("LLM_MAX_TOKENS", "2000")
    monkeypatch.setenv("LLM_EFFORT", "LOW")
    config = carregar()
    assert (config.modelo, config.timeout, config.max_tokens, config.esforco) == ("claude-haiku-5-5", 30, 2000, "low")


def test_repr_nao_mostra_a_chave(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "chave-secreta")
    assert "chave-secreta" not in repr(carregar())


@pytest.mark.parametrize(
    "nome, valor, mensagem",
    [
        ("LLM_TIMEOUT", "abc", "LLM_TIMEOUT precisa ser número inteiro de segundos"),
        ("LLM_TIMEOUT", "0", "LLM_TIMEOUT precisa ser maior que zero"),
        ("LLM_MAX_TOKENS", "muitos", "LLM_MAX_TOKENS precisa ser número inteiro de tokens"),
        ("LLM_MAX_TOKENS", "-5", "LLM_MAX_TOKENS precisa ser maior que zero"),
        ("LLM_EFFORT", "turbo", "LLM_EFFORT precisa ser um destes valores"),
        ("LLM_MODEL", "  ", "LLM_MODEL está vazia"),
    ],
)
def test_valor_invalido_gera_mensagem_clara(monkeypatch, nome, valor, mensagem):
    monkeypatch.setenv("LLM_API_KEY", "chave-de-teste")
    monkeypatch.setenv(nome, valor)
    with pytest.raises(ConfiguracaoInvalida, match=mensagem):
        carregar()
