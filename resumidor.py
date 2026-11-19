"""Resume uma vaga de emprego colada no terminal, usando a API REST da Anthropic."""
import sys

from dotenv import load_dotenv

from src.cliente import ErroLLM, enviar
from src.config import Configuracao, ConfiguracaoInvalida, carregar
from src.entrada import EntradaVazia, ler_vaga
from src.pedido import montar_corpo
from src.resposta import extrair_texto


def resumir(vaga: str, config: Configuracao) -> str:
    corpo = montar_corpo(vaga, config)
    dados = enviar(corpo, config)
    return extrair_texto(dados)


def main() -> None:
    load_dotenv()
    try:
        config = carregar()  # Programa vai falhar aqui se não houver chave ou se houver algum erro de configuração
        vaga = ler_vaga()
        print(resumir(vaga, config))
    except (ConfiguracaoInvalida, EntradaVazia, ErroLLM) as erro:
        print(erro, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
