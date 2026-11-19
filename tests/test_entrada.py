import io

import pytest

from src.entrada import EntradaVazia, ler_vaga, validar


@pytest.mark.parametrize("texto", ["", "   ", "\n\n", " \t \n"])
def test_recusa_entrada_vazia(texto):
    with pytest.raises(EntradaVazia, match="Nenhum texto recebido"):
        validar(texto)


def test_tira_os_espacos_das_pontas():
    assert validar("  Vaga de Dev Python \n") == "Vaga de Dev Python"


def test_le_do_stdin_e_avisa_no_stderr(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("Vaga de Dev Python\n"))
    assert ler_vaga() == "Vaga de Dev Python"
    saida = capsys.readouterr()
    assert saida.out == ""  # o stdout fica só para o resumo
    assert "Cole o texto da vaga" in saida.err
