# Relatório de execução: P0, Resumidor de vagas

## 1. Evolução por nível

### Básico (tag `p0-basico`)

Programa de terminal em Python que lê o texto de uma vaga, envia para a API REST da Anthropic e mostra
um resumo com sete campos. A chave fica em variável de ambiente e as dependências estão travadas no
`requirements.txt`. A integração foi feita pelo pull request #1, com merge commit.

### Intermediário (tag `p0-intermediario`)

O código foi dividido em um módulo por responsabilidade do enunciado: entrada (`src/entrada.py`),
configuração (`src/config.py`), preparo do pedido (`src/pedido.py`), chamada ao modelo
(`src/cliente.py`), tratamento da resposta (`src/resposta.py`) e apresentação (`resumidor.py`). Cada
falha prevista vira uma exceção com a mensagem pronta (`EntradaVazia`, `ConfiguracaoInvalida`,
`ErroLLM`). O `resumidor.py` mostra essa mensagem no `stderr` e sai com código 1, sem traceback. O
prompt passou a pedir um resumo por vaga e a permitir deduzir a senioridade, marcada como estimada. O
README ganhou instalação, configuração, execução, exemplos e os comandos dos testes. A integração foi
feita pelo pull request #2, com merge commit.

### Avançado

A preencher.

## 2. Decisões

| Decisão | Alternativa considerada | Justificativa |
|---|---|---|
| Usar a Anthropic (`claude-sonnet-5-5`) | LLM institucional (Devel) | Quando comecei, a Devel apresentava erros relatados no fórum e meu acesso não estava liberado. Eu já tinha uma chave da Anthropic, uso Claude no dia a dia e queria aprender a API desse provedor. O enunciado permite outro LLM, com custo por minha conta |
| Chamar a API com `requests` | SDK oficial da Anthropic | A competência C03 pede o envio por API REST. Com o SDK, a montagem da requisição e o tratamento dos status HTTP ficariam escondidos |
| Um módulo para cada responsabilidade do enunciado (seis no total) | Dois arquivos, `app.py` e `client.py`, como no vídeo de demonstração do Acervo | Cada parte fica pequena e testável isoladamente, e o código segue a lista do enunciado do Intermediário |
| Fazer um resumo por vaga quando o anúncio trouxer mais de uma | Manter um resumo só, ou avisar e parar | Mantém o formato padronizado, que é o objetivo do programa, sem exigir que a pessoa separe o anúncio |
| Tratar recusa e resposta cortada como erro, sem trocar de modelo | Mostrar o resumo parcial, ou ligar o *fallback* da API, que repete o pedido em outro modelo quando há recusa | Um resumo cortado perde os últimos campos, e quem lê pode achar que eles não existiam. O enunciado limita o P0 a um único LLM |

## 3. Testes

Os testes do Intermediário são execuções reais do programa, feitas em 15/11/2026 com
`claude-sonnet-5-5`. Os testes 3 a 6 terminam antes de chamar a API. O teste 5 é uma falha induzida
(proxy apontando para uma porta fechada). Os comandos estão no README.

| Teste | Entrada ou situação | Resultado esperado | Resultado obtido |
|---|---|---|---|
| 1. Anúncio real (Básico) | Anúncio com duas vagas (AI Engineer e AI Builder) | Resumo com os sete campos | Campos preenchidos e dados conferidos com o anúncio, mas as duas vagas saíram em um resumo só |
| 2. Uma vaga | `exemplos/vaga-ficticia.txt` | Resumo com os sete campos | Sete campos corretos, "Pontos de atenção: não informado". Saída 0, 2,3 s |
| 3. Entrada vazia | `echo ""` | Bloqueia e orienta | "Nenhum texto recebido. Cole o texto da vaga e termine com Ctrl+D." Saída 1 |
| 4. Credencial ausente | `LLM_API_KEY` vazia | Informa sem expor dado sensível | "LLM_API_KEY não definida. Copie .env.example para .env e preencha a chave." Saída 1 |
| 5. Falha de comunicação | `HTTPS_PROXY=http://127.0.0.1:9` | Mensagem compreensível | "Falha de comunicação com o LLM. Verifique sua conexão." Saída 1 |
| 6. Configuração inválida | `LLM_TIMEOUT=abc` | Mensagem compreensível | "LLM_TIMEOUT precisa ser número inteiro de segundos" Saída 1 |
| 7. Credencial inválida | `LLM_API_KEY=chave-falsa` (API responde 401) | Termina de forma controlada | "Credencial inválida. Confira o valor de LLM_API_KEY no .env." Saída 1 |
| 8. Modelo inexistente | `LLM_MODEL=modelo-inexistente` (API responde 404) | Mensagem compreensível | "Modelo não encontrado. Confira LLM_MODEL no .env." Saída 1 |
| 9. Tempo esgotado | `LLM_TIMEOUT=1` | Mensagem compreensível | "O LLM não respondeu no limite de 1 s. Tente de novo ou aumente LLM_TIMEOUT no .env." Saída 1 |
| 10. Duas vagas | `exemplos/duas-vagas-ficticias.txt` | Um resumo por vaga | Dois resumos completos, com "Sênior (estimada)" e "Júnior (estimada)". Saída 0, 3,7 s |
| 11. Fora do escopo | Anúncio real de atendimento ao cliente (fora de TI) | Resumir e sinalizar que não é TI | Resumiu e avisou "não é uma vaga técnica de TI", mas com campos menos padronizados (ver a seção 4). Saída 0, 4,5 s |
| 12. Saída para arquivo | `> resumo.txt` | Arquivo só com o resumo | O aviso inicial ficou no terminal e o arquivo recebeu só o resumo |

Os casos de resposta vazia, recusa, texto cortado, JSON sem o campo `content`, corpo que não é JSON e
status 403, 413, 429, 500 e 529 não são fáceis de provocar com a API real. Eles foram verificados com
respostas simuladas por um script fora do repositório e viram testes automatizados no nível Avançado.

## 4. Falhas e limitações

**Anúncio com mais de uma vaga.** No Básico, o modelo juntou as duas vagas de um anúncio real em um
único resumo, com os campos divididos por trilha. Identifiquei ao testar. No Intermediário, as
instruções passaram a pedir um resumo por vaga. Como não guardei o anúncio original, refiz o teste com
um anúncio fictício parecido (`exemplos/duas-vagas-ficticias.txt`), e saíram dois resumos completos
(teste 10).

**Anúncio fora de TI.** Com um anúncio real de atendimento ao cliente (teste 11), o programa resumiu e
avisou que a vaga não é de TI, mas o formato ficou frouxo: comentários entre parênteses nos campos,
endereço, contrato e escala dentro de "Modalidade" e a lista de benefícios dentro de "Salário". Além
disso, um "vagas2" que sobrou da página copiada virou "o anúncio menciona 2 vagas". Identifiquei
comparando a saída com o anúncio. Ficou como limitação documentada, porque o público do programa é quem
procura vaga em TI e o aviso já aparece nos pontos de atenção.

**Criação do ambiente virtual.** `python3 -m venv .venv` falhou porque faltava o pacote
`python3.14-venv`. Identifiquei pela mensagem de erro e resolvi instalando o pacote. O README traz esse
passo.

## 5. Uso de IA

Estou aprendendo enquanto desenvolvo o projeto, então utilizei o Claude também como ferramenta de aprendizagem. As alterações eram acompanhadas de explicações no chat, e eu procurava entender cada implementação antes de prosseguir, perguntando sempre que surgiam dúvidas. Alguns exemplos foram: por que o `resumidor.py` fica na raiz do projeto em vez de `src/`, por que o programa recebe a vaga pela entrada padrão (`<`) em vez de pelo nome do arquivo e por que o `pip` precisa ser executado com o ambiente virtual ativado. As dúvidas que poderiam dificultar o uso do programa também serviram de referência para melhorar as instruções do README.

| Ferramenta | Tarefa delegada | Resultado aproveitado | Correções | Verificação |
|---|---|---|---|---|
| Claude Code (`claude-opus-5-5`) | Auxílio na criação da primeira versão de `resumidor.py` e do `.env.example`, com explicações sobre a implementação | Estrutura inicial e código do Básico | Revisei a implementação e troquei o modelo padrão para Sonnet por decisão própria | Execução real e revisão da saída e do código no pull request |
| Claude Code (`claude-opus-5-5`) | Apoio na organização e redação deste relatório e do README, com base nas decisões e nos testes realizados | Sugestões de estrutura e texto | Revisei o conteúdo e ajustei as informações para refletir o desenvolvimento real | Conferência com as execuções e com o histórico do projeto |
| Claude Code (`claude-opus-5-5`) | Intermediário: explicações e orientação para implementar a entrada (`src/entrada.py`), a configuração (`src/config.py`) e a chamada ao modelo (`src/cliente.py`). O código foi digitado por mim, com correções pontuais de erros de digitação no `cliente.py`, a meu pedido | Código implementado por mim a partir das explicações | Acrescentei a informação "no .env" à mensagem de timeout | Execução dos casos de erro e 14 casos simulados sem rede para o `cliente.py` |
| Claude Code (`claude-opus-5-5`) | Intermediário: auxílio na implementação do preparo do pedido (`src/pedido.py`), tratamento da resposta (`src/resposta.py`), integração dos módulos no `resumidor.py` e criação de exemplos fictícios. Algumas partes foram solicitadas diretamente nos arquivos. Desde 15/11, devido ao prazo, passei a utilizar esse formato para todo o código, mantendo a revisão, as decisões técnicas e os commits sob minha responsabilidade | Código integrado, revisado e commitado por mim, em commits separados por assunto | Revisei os trechos gerados, ajustei o que foi necessário e validei o comportamento das implementações | Execuções reais (seção 3) e 10 respostas simuladas para o `resposta.py` |

## 6. Reflexão

A preencher na entrega.
