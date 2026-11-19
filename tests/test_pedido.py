from src.pedido import INSTRUCOES, montar_corpo


def test_usa_modelo_limite_e_esforco_da_configuracao(config):
    corpo = montar_corpo("Vaga de Dev Python", config)
    assert corpo["model"] == "claude-sonnet-5-5"
    assert corpo["max_tokens"] == 1000
    assert corpo["output_config"] == {"effort": "high"}


def test_vaga_vai_como_mensagem_e_instrucoes_no_system(config):
    corpo = montar_corpo("Vaga de Dev Python", config)
    assert corpo["messages"] == [{"role": "user", "content": "Vaga de Dev Python"}]
    assert corpo["system"] == INSTRUCOES


def test_nao_envia_parametros_de_amostragem(config):
    # A versão 2026-10-21 da API recusa temperature, top_p e top_k.
    corpo = montar_corpo("Vaga de Dev Python", config)
    assert not {"temperature", "top_p", "top_k"} & corpo.keys()


def test_instrucoes_pedem_os_sete_campos():
    for campo in ("Cargo:", "Senioridade:", "Stack obrigatória:", "Stack desejável:",
                  "Modalidade:", "Salário:", "Pontos de atenção:"):
        assert campo in INSTRUCOES
