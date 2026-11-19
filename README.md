# Resumidor de vagas

Projeto P0 da capacitação TrendsIA (Instituto Hardware Br): uma aplicação de terminal em Python que usa
um LLM para resumir vagas de emprego.

> Nível atual: Intermediário.

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

## Como funciona

1. O programa lê o texto da vaga pelo terminal e recusa entrada vazia.
2. Monta o pedido com as instruções do resumo e envia para a API REST da Anthropic com `requests`.
3. Confere a resposta (recusa, texto cortado, resposta vazia ou fora do formato) e mostra só o resumo.

Se um anúncio trouxer mais de uma vaga, sai um resumo para cada uma. A senioridade pode ser deduzida
de pistas como anos de experiência, e nesse caso vem marcada como "(estimada)".

## Requisitos

- Python 3.10 ou mais novo. O projeto foi desenvolvido no 3.14.4, e os testes também passam no 3.10.21 e
  no 3.12.14.
- Bibliotecas, com versões travadas no `requirements.txt`: `requests` (chamada HTTP à API),
  `python-dotenv` (leitura do `.env`), `pytest` e `requests-mock` (testes simulados).
- Uma chave da API da Anthropic. O projeto usa o modelo `claude-sonnet-5-5`, e o custo das chamadas é
  de quem roda o programa.
- Acesso à internet.

## Instalação

```bash
git clone https://github.com/guiqwer/trendsia-p0-resumidor-vagas.git
cd trendsia-p0-resumidor-vagas
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

No Ubuntu e no Debian, se `python3 -m venv` disser que falta o `ensurepip`, instale o pacote do venv
da sua versão do Python (`sudo apt install python3-venv`, ou `python3.14-venv` para o 3.14) e repita
o comando.

Se o `pip` não for encontrado, ou se aparecer `error: externally-managed-environment`, o ambiente
virtual não está ativado: rode `source .venv/bin/activate` e repita. Não use `--break-system-packages`.

## Configuração do acesso ao LLM

1. Crie uma chave no Console da Anthropic (https://platform.claude.com), em **API Keys**.
2. Copie o modelo de configuração:

   ```bash
   cp .env.example .env             # no Windows: copy .env.example .env
   ```

3. Abra o `.env` em um editor de texto e cole a chave logo depois de `LLM_API_KEY=`. As outras
   variáveis já vêm com o valor padrão.

| Variável | Obrigatória | Padrão | Para quê |
|---|---|---|---|
| `LLM_API_KEY` | sim | | Chave da API da Anthropic |
| `LLM_MODEL` | não | `claude-sonnet-5-5` | Modelo usado |
| `LLM_TIMEOUT` | não | `120` | Segundos de espera pela resposta |
| `LLM_MAX_TOKENS` | não | `16000` | Limite de tokens da resposta, contando o raciocínio do modelo. No `claude-sonnet-5-5`, vai até 128000 |
| `LLM_EFFORT` | não | `high` | Esforço do modelo: `low`, `medium`, `high`, `xhigh` ou `max`. Mais esforço deixa a resposta mais cuidadosa, mais lenta e mais cara |

O `.env` está no `.gitignore` e nunca vai para o repositório.

## Execução

Todos os comandos deste README supõem o ambiente virtual ativado (`source .venv/bin/activate`, ou
`.venv\Scripts\activate` no Windows). Quando ele está ativo, aparece `(.venv)` no começo da linha do
terminal.

```bash
python resumidor.py
```

Cole o texto da vaga e termine com **Ctrl+D** (no Windows, **Ctrl+Z** e depois Enter). O programa lê
a vaga da entrada padrão: para usar um arquivo, redirecione com `<`. Passar o nome do arquivo como
argumento não funciona. Também dá para salvar o resumo em um arquivo com `>`:

```bash
python resumidor.py < exemplos/vaga-ficticia.txt
python resumidor.py < exemplos/duas-vagas-ficticias.txt > resumo.txt
```

O resumo sai no `stdout`. O aviso inicial e as mensagens de erro saem no `stderr`, então o arquivo
recebe só o resumo. Em caso de erro, o programa mostra uma mensagem curta e sai com código 1.

## Exemplos

Entrada (`exemplos/vaga-ficticia.txt`):

```text
Desenvolvedor Python Pleno - Empresa Fictícia Ltda.
Trabalho remoto. Requisitos: 3+ anos com Python, Django e PostgreSQL.
Desejável: Docker e AWS. Salário: R$ 8.000 a R$ 10.000.
```

Saída:

```text
Cargo: Desenvolvedor Python Pleno
Senioridade: Pleno
Stack obrigatória: Python, Django, PostgreSQL (3+ anos de experiência com Python)
Stack desejável: Docker, AWS
Modalidade: Remoto
Salário: R$ 8.000 a R$ 10.000
Pontos de atenção: não informado
```

Com `exemplos/duas-vagas-ficticias.txt` (AI Engineer e AI Builder no mesmo anúncio), saem dois resumos,
com a senioridade estimada em cada um: "Sênior (estimada)" e "Júnior (estimada)".

## Logs

Cada chamada ao LLM grava uma linha em `logs/resumidor.log`. A pasta é criada na primeira execução e
fica fora do Git. A linha traz só metadados: horário, modelo, esforço, tamanho da vaga em caracteres,
tempo de resposta, status HTTP, id da requisição, motivo de parada e tokens usados. A chave e o texto
da vaga nunca são gravados.

```text
2026-11-19 07:01:33,790 INFO modelo=claude-sonnet-5-5 esforco=high entrada_chars=177 latencia_ms=2245 status=200 request_id=req_011Ch... parada=end_turn tokens_entrada=418 tokens_saida=129
```

As falhas aparecem como `WARNING`, com o status HTTP ou com `falha=timeout` ou `falha=comunicacao`.

## Testes

### Testes simulados (automatizados, sem chamada real)

```bash
python -m pytest
```

São 55 testes em `tests/`, um arquivo para cada parte do programa. Eles rodam em menos de um segundo,
sem internet e sem chave, porque a API é simulada com `requests-mock` no formato de resposta da
Anthropic. Cobrem:

- entrada vazia e leitura pelo terminal;
- configuração: valores padrão, valores inválidos, credencial ausente e chave fora do `repr`;
- corpo do pedido, com modelo, limite de tokens, esforço e instruções;
- chamada: status 400, 401, 403, 404, 429 e 5xx, tempo esgotado, falha de conexão e corpo que não é
  JSON;
- resposta: recusa, resposta cortada, resposta vazia e formato inesperado;
- log: tem os metadados e não tem a chave nem o texto da vaga;
- o programa inteiro: resumo no `stdout` e código 1 nos erros, sem traceback.

### Testes reais (o programa de verdade)

Os casos 1 a 4 não chegam à API. O caso 3 é uma falha induzida: aponta o proxy para uma porta fechada.
Os casos 5 a 10 chamam a API da Anthropic e usam a sua chave.

| # | Situação | Comando | Mensagem esperada (saída 1) |
|---|---|---|---|
| 1 | Entrada vazia | `echo "" \| python resumidor.py` | Nenhum texto recebido… |
| 2 | Credencial ausente | `LLM_API_KEY= python resumidor.py < exemplos/vaga-ficticia.txt` | LLM_API_KEY não definida… |
| 3 | Falha de comunicação | `HTTPS_PROXY=http://127.0.0.1:9 python resumidor.py < exemplos/vaga-ficticia.txt` | Falha de comunicação com o LLM… |
| 4 | Configuração inválida | `LLM_TIMEOUT=abc python resumidor.py < exemplos/vaga-ficticia.txt` | LLM_TIMEOUT precisa ser número inteiro… |
| 5 | Credencial inválida | `LLM_API_KEY=chave-falsa python resumidor.py < exemplos/vaga-ficticia.txt` | Credencial inválida… |
| 6 | Modelo inexistente | `LLM_MODEL=modelo-inexistente python resumidor.py < exemplos/vaga-ficticia.txt` | Modelo não encontrado… |
| 7 | Tempo esgotado | `LLM_TIMEOUT=1 python resumidor.py < exemplos/vaga-ficticia.txt` | O LLM não respondeu no limite de 1 s… |
| 8 | Resposta cortada | `LLM_MAX_TOKENS=20 python resumidor.py < exemplos/vaga-ficticia.txt` | A resposta foi cortada pelo limite de tokens… |
| 9 | Uma vaga | `python resumidor.py < exemplos/vaga-ficticia.txt` | (saída 0) resumo com os sete campos |
| 10 | Duas vagas | `python resumidor.py < exemplos/duas-vagas-ficticias.txt` | (saída 0) um resumo por vaga |

As variáveis passadas na frente do comando valem só para aquela execução e têm prioridade sobre o
`.env`. A sintaxe é de terminal Linux ou macOS. Os resultados obtidos estão no
[relatório](RELATORIO_EXECUCAO.md#3-testes).

O LLM indisponível (5xx), o excesso de pedidos (429), a recusa, a resposta vazia e a resposta fora do
formato não dá para provocar sob demanda com a API real. Por isso eles estão só nos testes simulados.

## Limitações conhecidas

- Depende de um serviço pago e externo (Anthropic) e de internet. Não usa o LLM institucional (ver o
  relatório).
- O texto da vaga é enviado à Anthropic: não cole dados pessoais junto com o anúncio.
- Um anúncio fora de TI ainda é resumido, com um aviso nos pontos de atenção, mas os campos ficam menos
  padronizados.
- A senioridade estimada é uma dedução do modelo e pode errar. Sobras da página copiada (como contadores
  de vagas) podem ser lidas como informação.
- Uma resposta cortada pelo limite de tokens vira erro, sem resumo parcial.
- Não há nova tentativa automática quando a API está sobrecarregada (429 ou 5xx).

## Estrutura

```text
resumidor.py          ponto de entrada: junta as partes e mostra o resultado
src/entrada.py        leitura e validação do texto da vaga
src/config.py         leitura e validação das variáveis de ambiente
src/pedido.py         instruções do resumo e montagem do corpo da requisição
src/cliente.py        chamada HTTP à API e mensagens por tipo de erro
src/resposta.py       extração do texto e tratamento de recusa, corte e resposta vazia
src/registro.py       configuração do log em logs/resumidor.log
tests/                testes simulados, um arquivo por parte do programa
pytest.ini            configuração do pytest
exemplos/             anúncios fictícios para testar
logs/                 registros de execução (criada ao rodar, fora do Git)
requirements.txt      dependências, com as versões travadas
.env.example          modelo das variáveis de ambiente, sem valores reais
RELATORIO_EXECUCAO.md decisões, testes, falhas e uso de IA
```

## Links

- [Relatório de execução](RELATORIO_EXECUCAO.md)
- Tags dos níveis: [`p0-basico`](https://github.com/guiqwer/trendsia-p0-resumidor-vagas/tree/p0-basico) ·
  [`p0-intermediario`](https://github.com/guiqwer/trendsia-p0-resumidor-vagas/tree/p0-intermediario)
- Vídeo: será publicado na entrega final.
