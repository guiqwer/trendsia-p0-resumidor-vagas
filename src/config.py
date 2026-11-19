import os
from dataclasses import dataclass, field

MODELO_PADRAO = "claude-sonnet-5-5"
TIMEOUT_PADRAO = 120
MAX_TOKENS_PADRAO = 16000
ESFORCO_PADRAO = "high"
NIVEIS_ESFORCO = ("low", "medium", "high", "xhigh", "max")

class ConfiguracaoInvalida(Exception):
    """Alguma variável de ambiente está ausente ou com valor inválido."""

class CredencialAusente(ConfiguracaoInvalida):
    """A chave de acesso ao LLM não foi definida"""


@dataclass(frozen=True) # Imutável, para evitar alterações acidentais
class Configuracao:
    chave: str = field(repr=False) # Proteção para não exibir a chave em logs ou prints
    modelo: str
    timeout: int
    max_tokens: int = MAX_TOKENS_PADRAO
    esforco: str = ESFORCO_PADRAO

def _ler_inteiro_positivo(nome: str, padrao: int, unidade: str) -> int:
    try:
        valor = int(os.environ.get(nome, padrao))
    except ValueError:
        raise ConfiguracaoInvalida(f"{nome} precisa ser número inteiro de {unidade}") from None
    if valor <= 0:
        raise ConfiguracaoInvalida(f"{nome} precisa ser maior que zero.")
    return valor

def _ler_esforco() -> str:
    esforco = os.environ.get("LLM_EFFORT", ESFORCO_PADRAO).strip().lower()
    if esforco not in NIVEIS_ESFORCO:
        raise ConfiguracaoInvalida(f"LLM_EFFORT precisa ser um destes valores: {', '.join(NIVEIS_ESFORCO)}.")
    return esforco

def carregar() -> Configuracao:
    chave = os.environ.get("LLM_API_KEY", "").strip()
    if not chave:
        raise CredencialAusente("LLM_API_KEY não definida. Copie .env.example para .env e preencha a chave.")
    modelo = os.environ.get("LLM_MODEL", MODELO_PADRAO).strip()
    if not modelo:
        raise ConfiguracaoInvalida("LLM_MODEL está vazia. Informe o nome do modelo ou remova a variável.")
    return Configuracao(
        chave,
        modelo,
        timeout=_ler_inteiro_positivo("LLM_TIMEOUT", TIMEOUT_PADRAO, "segundos"),
        max_tokens=_ler_inteiro_positivo("LLM_MAX_TOKENS", MAX_TOKENS_PADRAO, "tokens"),
        esforco=_ler_esforco(),
    )
