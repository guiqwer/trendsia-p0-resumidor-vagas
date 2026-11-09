"""Leitura e validação do texto da vaga"""
import sys 

class EntradaVazia(Exception):
    """Exceção para entrada de texto vazia"""


def validar(texto: str) -> str:
    vaga = texto.strip()
    if not vaga:
        raise EntradaVazia("Nenhum texto recebido. Cole o texto da vaga e termine com Ctrl+D.") 
    return vaga


def ler_vaga() -> str:
    print("Cole o texto da vaga e termine com Ctrl+D:")
    return validar(sys.stdin.read())
