"""Registro de execução em logs/resumidor.log, só com metadados das chamadas."""
import logging
from pathlib import Path

# Caminho a partir da pasta do projeto, para funcionar de qualquer diretório e em qualquer sistema.
ARQUIVO_LOG = Path(__file__).resolve().parent.parent / "logs" / "resumidor.log"


def configurar() -> None:
    """Liga a gravação dos registros do programa. Se não der para criar o arquivo, segue sem log."""
    try:
        ARQUIVO_LOG.parent.mkdir(exist_ok=True)
        arquivo = logging.FileHandler(ARQUIVO_LOG, encoding="utf-8")
    except OSError:
        return
    arquivo.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    # Só os registros dos módulos em src/; os das bibliotecas (requests, urllib3) ficam de fora.
    programa = logging.getLogger("src")
    programa.addHandler(arquivo)
    programa.setLevel(logging.INFO)
