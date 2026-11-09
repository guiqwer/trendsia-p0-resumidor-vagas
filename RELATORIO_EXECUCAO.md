# Relatório de execução: P0, Resumidor de vagas

## 1. Evolução por nível

### Básico (tag `p0-basico`)

Programa de terminal em Python que lê o texto de uma vaga, envia para a API REST da Anthropic e mostra
um resumo com sete campos. A chave fica em variável de ambiente e as dependências estão travadas no
`requirements.txt`. A integração foi feita pelo pull request #1, com merge commit.

### Intermediário

A preencher.

### Avançado

A preencher.

## 2. Decisões

| Decisão | Alternativa considerada | Justificativa |
|---|---|---|
| Usar a Anthropic (`claude-sonnet-5-5`) | LLM institucional (Devel) | Quando comecei, a Devel apresentava erros relatados no fórum e meu acesso não estava liberado. Eu já tinha uma chave da Anthropic, uso Claude no dia a dia e queria aprender a API desse provedor. O enunciado permite outro LLM, com custo por minha conta |
| Chamar a API com `requests` | SDK oficial da Anthropic | A competência C03 pede o envio por API REST |
| Integrar com merge commit | Squash and merge | O enunciado pede evolução progressiva, e o squash juntaria os commits em um só |
| Fazer um resumo por vaga quando o anúncio trouxer mais de uma | Manter um resumo só, ou avisar e parar | Mantém o formato padronizado, que é o objetivo do programa, sem exigir que a pessoa separe o anúncio |
| Deduzir a senioridade quando a vaga der pistas, marcando como estimada | Escrever "não informado" | Variações como "3+ anos" são o motivo de usar um LLM, e a marcação deixa claro o que é dedução |

## 3. Testes

| Teste | Entrada ou situação | Resultado esperado | Resultado obtido |
|---|---|---|---|
| Anúncio real | Anúncio com duas vagas (AI Engineer e AI Builder) | Resumo com os sete campos | Campos preenchidos e dados conferidos com o anúncio, mas as duas vagas saíram em um resumo só |

## 4. Falhas e limitações

**Anúncio com mais de uma vaga.** O modelo juntou as duas vagas em um único resumo, com os campos
divididos por trilha. Identifiquei ao testar com um anúncio real. O tratamento planejado para o
Intermediário é pedir um resumo por vaga.

**Criação do ambiente virtual.** `python3 -m venv .venv` falhou porque faltava o pacote
`python3.14-venv`. Identifiquei pela mensagem de erro e resolvi instalando o pacote. O README vai
incluir esse passo.

## 5. Uso de IA

| Ferramenta | Tarefa delegada | Resultado aproveitado | Correções | Verificação |
|---|---|---|---|---|
| Claude Code (`claude-opus-5-5`) | Gerar a primeira versão de `resumidor.py` e do `.env.example` | Código do Básico | Modelo padrão trocado para Sonnet por decisão minha | Execução real e revisão da saída e do código no pull request |
| Claude Code (`claude-opus-5-5`) | Redigir este relatório a partir das decisões que informei | Estrutura e texto inicial | A preencher, se eu alterar algo | Revisão minha do texto |

## 6. Reflexão

A preencher na entrega.
