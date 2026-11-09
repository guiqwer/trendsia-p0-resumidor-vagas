# Resumidor de vagas

Projeto P0 da capacitação TrendsIA (Instituto Hardware Br): uma aplicação de terminal em Python que usa
um LLM para resumir vagas de emprego.

> Em construção: nível Básico.

## Problema

Uma pessoa que está procurando emprego em TI precisa transformar o texto de uma vaga (copiado do
LinkedIn, da Gupy ou de um e-mail) em um resumo padronizado (cargo, senioridade, stack obrigatória e
desejável, modalidade, salário e pontos de atenção), porque hoje perde tempo lendo descrições longas,
cada uma escrita de um jeito, para decidir se vale se candidatar.

## Por que usar um LLM

Cada empresa escreve a vaga de um jeito: "pleno", "mid-level" e "3+ anos de experiência" querem dizer
a mesma coisa, e a stack às vezes aparece só no meio de um parágrafo. Uma regra fixa ou uma expressão
regular não daria conta dessa variação. O LLM interpreta o texto, e o programa pede o resultado sempre
no mesmo formato.
