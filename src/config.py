import os
from dataclasses import dataclass, field

MODELO_PADRAO = "claude-sonnet-5-5"
TIMOUT_PADRAO = 120

class ConfiguracaoInvalida(Exception):
    """Alguma variável de ambiente está ausente ou com valor inválido."""

class CredencialAusente(ConfiguracaoInvalida):
    """A chave de acesso ao LLM não foi definida"""


@dataclass(frozen=True) # Imutável, para evitar alterações acidentais
class Configuracao:
    chave: str = field(repr=False) # Proteção para não exibir a chave em logs ou prints
    modelo: str
    timeout: int

def _ler_timeout() -> int:
    try:
        timeout = int(os.environ.get("LLM_TIMEOUT", TIMOUT_PADRAO))
    except ValueError:
        raise ConfiguracaoInvalida("LLM_TIMEOUT precisa ser número inteiro de segundos") from None
    if timeout <= 0:
        raise ConfiguracaoInvalida("LL_TIMEOUT precisa ser maior que zero.")
    return timeout

def carregar() -> Configuracao:
    chave = os.environ.get("LLM_API_KEY", "").strip()
    if not chave:
        raise CredencialAusente("LLM_API_KEY não definida. Copie .env.example para .env e preencha a chave.") 
    modelo = os.environ.get("LLM_MODEL", MODELO_PADRAO).strip()
    if not modelo:
        raise ConfiguracaoInvalida("LLM_MODEL está vazia. Informe o nome do modelo ou remova a variável.")
    return Configuracao(chave, modelo, _ler_timeout())       