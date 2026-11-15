"""Resume uma vaga de emprego colada no terminal, usando a API REST da Anthropic."""
import sys

from dotenv import load_dotenv

from src.cliente import ErroLLM, enviar
from src.config import Configuracao, ConfiguracaoInvalida, carregar
from src.entrada import EntradaVazia, ler_vaga
from src.pedido import montar_corpo


def resumir(vaga: str, config: Configuracao) -> str:
    dados = enviar(montar_corpo(vaga, config), config)
    # A resposta é uma lista de blocos, e nem todo bloco é texto.
    blocos = dados["content"]
    return "".join(b["text"] for b in blocos if b["type"] == "text")


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
