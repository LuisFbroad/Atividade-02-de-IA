# Campo Minado

> A versão mais recente do Python que você deve usar neste curso é o Python 3.12.

Implemente uma IA capaz de jogar Campo Minado.

![Jogo Campo Minado](https://cs50.harvard.edu/ai/projects/1/minesweeper/images/game.png)

## Contexto

### Campo Minado

Campo Minado é um jogo de lógica formado por uma grade de células, algumas das quais contêm "minas" escondidas. Clicar em uma célula que contém uma mina detona a mina e faz o jogador perder a partida. Clicar em uma célula "segura", isto é, uma célula que não contém uma mina, revela um número indicando quantas células vizinhas contêm minas. Uma célula é considerada vizinha quando está uma posição à esquerda, à direita, acima, abaixo ou na diagonal da célula em questão.

Neste exemplo de Campo Minado `3 x 3`, os três valores `1` indicam que cada uma dessas células possui uma célula vizinha que é uma mina. Os quatro valores `0` indicam que nenhuma delas possui uma mina vizinha.

![Exemplo de números em células seguras](https://cs50.harvard.edu/ai/projects/1/minesweeper/images/safe_cells.png)

Com essas informações, um jogador que raciocine logicamente pode concluir que deve existir uma mina na célula inferior direita e que não existe uma mina na célula superior esquerda. Somente assim os números mostrados nas demais células podem estar corretos.

O objetivo do jogo é sinalizar, isto é, identificar, cada uma das minas. Em muitas implementações, incluindo a deste projeto, o jogador pode sinalizar uma mina clicando em uma célula com o botão direito do mouse ou usando o gesto equivalente do computador.

### Lógica Proposicional

O objetivo deste projeto é construir uma IA capaz de jogar Campo Minado. Agentes baseados em conhecimento tomam decisões examinando sua base de conhecimento e realizando inferências a partir do que sabem.

Uma forma de representar o conhecimento de uma IA sobre uma partida de Campo Minado seria tratar cada célula como uma variável proposicional. A variável seria verdadeira se a célula contivesse uma mina e falsa caso contrário.

A IA sabe sempre que uma célula segura é selecionada e recebe o número exibido naquela célula. Considere o tabuleiro abaixo, no qual a célula central foi revelada e as demais células receberam letras apenas para facilitar a explicação.

![Célula central e suas vizinhas](https://cs50.harvard.edu/ai/projects/1/minesweeper/images/middle_safe.png)

Agora sabemos que uma das oito células vizinhas é uma mina. Poderíamos escrever a seguinte expressão lógica para representar que uma das células vizinhas contém uma mina:

```text
Or(A, B, C, D, E, F, G, H)
```

Entretanto, sabemos mais do que essa expressão afirma. A sentença acima diz apenas que pelo menos uma das oito variáveis é verdadeira. Podemos fazer uma afirmação mais forte: sabemos que **exatamente uma** das oito variáveis é verdadeira. Isso pode ser expresso pela seguinte sentença de lógica proposicional:

```text
Or(
    And(A, Not(B), Not(C), Not(D), Not(E), Not(F), Not(G), Not(H)),
    And(Not(A), B, Not(C), Not(D), Not(E), Not(F), Not(G), Not(H)),
    And(Not(A), Not(B), C, Not(D), Not(E), Not(F), Not(G), Not(H)),
    And(Not(A), Not(B), Not(C), D, Not(E), Not(F), Not(G), Not(H)),
    And(Not(A), Not(B), Not(C), Not(D), E, Not(F), Not(G), Not(H)),
    And(Not(A), Not(B), Not(C), Not(D), Not(E), F, Not(G), Not(H)),
    And(Not(A), Not(B), Not(C), Not(D), Not(E), Not(F), G, Not(H)),
    And(Not(A), Not(B), Not(C), Not(D), Not(E), Not(F), Not(G), H)
)
```

Essa é uma expressão bastante complexa apenas para representar o significado de uma célula que contém o número `1`. Se uma célula contivesse `2`, `3` ou outro valor, a expressão poderia ser ainda maior.

Realizar verificação de modelos nesse tipo de problema também se tornaria rapidamente inviável. Em uma grade `8 x 8`, tamanho usado pela Microsoft no nível iniciante, teríamos 64 variáveis e, portanto, `2^64` modelos possíveis para verificar. É uma quantidade grande demais para ser processada em tempo razoável. Precisamos de uma representação melhor para o conhecimento deste problema.

### Representação do Conhecimento

Em vez da fórmula proposicional completa, cada sentença da base de conhecimento da IA será representada da seguinte maneira:

```text
{A, B, C, D, E, F, G, H} = 1
```

Cada sentença lógica nessa representação possui duas partes: um conjunto de `cells` do tabuleiro envolvidas na sentença e um número `count`, que representa quantas dessas células são minas. A sentença acima afirma que, entre as células A, B, C, D, E, F, G e H, exatamente uma é uma mina.

Essa representação é útil porque permite realizar certos tipos de inferência de maneira simples. Considere o jogo abaixo.

![Jogo no qual células seguras podem ser inferidas](https://cs50.harvard.edu/ai/projects/1/minesweeper/images/infer_safe.png)

Usando o número localizado na parte inferior esquerda, podemos construir a sentença `{D, E, G} = 0`, indicando que, entre as células D, E e G, exatamente zero são minas. Intuitivamente, podemos concluir que todas essas células são seguras. De modo geral, sempre que uma sentença possuir `count` igual a `0`, todas as suas `cells` devem ser seguras.

Agora considere o jogo abaixo.

![Jogo no qual minas podem ser inferidas](https://cs50.harvard.edu/ai/projects/1/minesweeper/images/infer_mines.png)

A IA construiria a sentença `{E, F, H} = 3`. Podemos concluir que E, F e H são minas. De modo geral, sempre que a quantidade de `cells` for igual a `count`, todas as células da sentença devem ser minas.

Em geral, as sentenças devem conter apenas `cells` que ainda não sejam conhecidas como seguras ou como minas. Assim que o estado de uma célula for descoberto, as sentenças podem ser atualizadas e simplificadas, o que poderá permitir novas conclusões.

Por exemplo, se a IA conhecesse a sentença `{A, B, C} = 2`, ainda não haveria informação suficiente para concluir o estado de nenhuma dessas células. Mas, se fosse informado que C é segura, C poderia ser removida da sentença, resultando em `{A, B} = 2`. Essa nova sentença permite concluir que A e B são minas.

Da mesma forma, se a IA conhecesse a sentença `{A, B, C} = 2` e descobrisse que C é uma mina, poderia remover C da sentença e diminuir o valor de `count`, pois C era uma mina incluída naquela contagem. A sentença resultante seria `{A, B} = 1`. Isso é lógico: se duas entre A, B e C são minas e sabemos que C é uma mina, então exatamente uma entre A e B também deve ser uma mina.

Existe ainda outro tipo de inferência que pode ser realizado.

![Jogo no qual é possível inferir por subconjuntos](https://cs50.harvard.edu/ai/projects/1/minesweeper/images/subset_inference.png)

Considere apenas as duas sentenças que a IA construiria a partir das células centrais superior e inferior. A célula central superior produz `{A, B, C} = 1`. A célula central inferior produz `{A, B, C, D, E} = 2`. A partir dessas duas sentenças, podemos inferir uma nova informação: `{D, E} = 1`. Se duas entre A, B, C, D e E são minas, mas apenas uma entre A, B e C é uma mina, então exatamente uma entre D e E deve ser a outra mina.

De modo geral, sempre que existirem duas sentenças `set1 = count1` e `set2 = count2`, em que `set1` seja um subconjunto de `set2`, podemos construir a nova sentença:

```text
set2 - set1 = count2 - count1
```

Releia o exemplo anterior e certifique-se de compreender por que essa inferência é válida.

Usando essa forma de representar o conhecimento, podemos criar um agente de IA capaz de reunir informações sobre o tabuleiro de Campo Minado e escolher células que ele sabe serem seguras.

## Primeiros Passos

- Baixe o código.
- Depois de entrar no diretório do projeto, crie um ambiente virtual e execute:

```bash
pip install -r requirements.txt
```

Esse comando instala o pacote Python necessário, `pygame`.

## Entendendo o Projeto

Há dois arquivos principais neste projeto: `runner.py` e `minesweeper.py`.

O arquivo `minesweeper.py` contém toda a lógica do jogo e da IA que jogará Campo Minado. O arquivo `runner.py` já foi implementado e contém todo o código responsável pela interface gráfica.

Depois de concluir todas as funções exigidas em `minesweeper.py`, você deverá conseguir executar:

```bash
python runner.py
```

para jogar Campo Minado ou permitir que a IA jogue por você.

Abra o arquivo `minesweeper.py` para entender o que já foi fornecido. Três classes estão definidas:

- `Minesweeper`
- `Sentence`
- `MinesweeperAI`

A classe `Minesweeper` controla o funcionamento do jogo e já foi totalmente implementada. Cada célula é representada por uma tupla `(i, j)`, em que `i` é o número da linha, variando de `0` a `height - 1`, e `j` é o número da coluna, variando de `0` a `width - 1`.

A classe `Sentence` representa as sentenças lógicas descritas anteriormente. Cada sentença possui um conjunto de `cells` e um `count` indicando quantas dessas células são minas. A classe também contém os métodos `known_mines` e `known_safes`, usados para determinar se alguma célula da sentença pode ser reconhecida como mina ou como segura. Os métodos `mark_mine` e `mark_safe` atualizam uma sentença quando surge uma nova informação sobre uma célula.

A classe `MinesweeperAI` implementará uma IA capaz de jogar Campo Minado. A classe mantém os seguintes valores:

- `self.moves_made`: conjunto de todas as células que já foram selecionadas, para que a IA não volte a escolhê-las;
- `self.mines`: conjunto de todas as células que a IA sabe serem minas;
- `self.safes`: conjunto de todas as células que a IA sabe serem seguras;
- `self.knowledge`: lista de todas as sentenças `Sentence` que a IA sabe serem verdadeiras.

O método `mark_mine` adiciona uma célula a `self.mines`, permitindo que a IA saiba que ela é uma mina. Em seguida, percorre todas as sentenças de `self.knowledge` e informa a cada uma delas que a célula é uma mina, para que sejam atualizadas quando necessário. O método `mark_safe` faz o mesmo para células seguras.

Os métodos restantes, `add_knowledge`, `make_safe_move` e `make_random_move`, devem ser implementados por você.

## Especificação

Conclua a implementação das classes `Sentence` e `MinesweeperAI` no arquivo `minesweeper.py`.

Na classe `Sentence`, implemente `known_mines`, `known_safes`, `mark_mine` e `mark_safe`.

### `known_mines`

O método `known_mines` deve retornar um `set` contendo todas as células de `self.cells` que, de acordo com a sentença, são reconhecidamente minas.

### `known_safes`

O método `known_safes` deve retornar um `set` contendo todas as células de `self.cells` que, de acordo com a sentença, são reconhecidamente seguras.

### `mark_mine`

O método `mark_mine` deve primeiro verificar se `cell` está entre as células incluídas na sentença.

- Se `cell` estiver na sentença, o método deverá atualizá-la para que `cell` deixe de fazer parte dela, mas para que a sentença continue logicamente correta considerando que `cell` é uma mina.
- Se `cell` não estiver na sentença, nenhuma ação será necessária.

### `mark_safe`

O método `mark_safe` deve primeiro verificar se `cell` está entre as células incluídas na sentença.

- Se `cell` estiver na sentença, o método deverá atualizá-la para que `cell` deixe de fazer parte dela, mas para que a sentença continue logicamente correta considerando que `cell` é segura.
- Se `cell` não estiver na sentença, nenhuma ação será necessária.

Na classe `MinesweeperAI`, implemente `add_knowledge`, `make_safe_move` e `make_random_move`.

### `add_knowledge`

O método `add_knowledge` deve receber uma `cell`, representada por uma tupla `(i, j)`, e seu `count` correspondente. Em seguida, deverá atualizar `self.mines`, `self.safes`, `self.moves_made` e `self.knowledge` com todas as novas informações que a IA puder inferir, considerando que `cell` é uma célula segura que possui `count` minas vizinhas.

- O método deve marcar `cell` como uma jogada já realizada.
- O método deve marcar `cell` como uma célula segura, atualizando também todas as sentenças que contenham essa célula.
- O método deve adicionar uma nova sentença à base de conhecimento da IA com base em `cell` e `count`, indicando que `count` das células vizinhas de `cell` são minas. Inclua na sentença apenas células cujo estado ainda não tenha sido determinado.
- Se alguma sentença de `self.knowledge` permitir que novas células sejam identificadas como seguras ou como minas, o método deverá marcá-las adequadamente.
- Se for possível inferir novas sentenças a partir das sentenças de `self.knowledge`, usando o método dos subconjuntos descrito anteriormente, as novas sentenças deverão ser adicionadas à base de conhecimento.
- Sempre que o conhecimento da IA for alterado, novas inferências que antes não eram possíveis poderão surgir. Certifique-se de adicionar também essas novas inferências à base de conhecimento.

### `make_safe_move`

O método `make_safe_move` deve retornar uma jogada `(i, j)` que seja reconhecidamente segura.

- A jogada retornada deve ser conhecida como segura e ainda não pode ter sido realizada.
- Se nenhuma jogada puder ser garantida como segura, o método deverá retornar `None`.
- O método não deve modificar `self.moves_made`, `self.mines`, `self.safes` nem `self.knowledge`.

### `make_random_move`

O método `make_random_move` deve retornar uma jogada aleatória `(i, j)`.

- Esse método será chamado quando não houver uma jogada segura disponível. Se a IA não souber onde jogar, escolherá uma posição aleatoriamente.
- A jogada não pode ter sido realizada anteriormente.
- A jogada não pode ser uma célula conhecida como mina.
- Se nenhuma jogada desse tipo for possível, o método deverá retornar `None`.

Não modifique as declarações das funções fornecidas, inclusive a quantidade ou a ordem de seus argumentos.

Depois que todas as funções forem implementadas corretamente, você deverá conseguir executar:

```bash
python runner.py
```

Em seguida, poderá jogar Campo Minado e também solicitar que a IA faça uma jogada.

## Dicas

- Leia cuidadosamente a seção de contexto para compreender como o conhecimento é representado e como a IA realiza inferências.
- Caso ainda não se sinta confortável com programação orientada a objetos, consulte a [documentação de classes do Python](https://docs.python.org/3/tutorial/classes.html).
- Consulte também as [operações comuns de `set`](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset) disponíveis em Python.
- Ao implementar `known_mines` e `known_safes` na classe `Sentence`, pense: em que situação é possível saber com certeza que as células de uma sentença são seguras? Em que situação é possível saber com certeza que são minas?
- `add_knowledge` realiza várias tarefas e provavelmente será, de longe, o método mais longo que você escreverá neste projeto. Implemente seu comportamento uma etapa de cada vez.
- Você pode adicionar métodos auxiliares às classes, mas não deve modificar as definições nem os argumentos dos métodos existentes.
- A IA nem sempre vencerá. Em algumas situações, ela precisará arriscar porque não possuirá informação suficiente para garantir uma jogada segura. Isso é esperado. Ao clicar em "AI Move", `runner.py` informará no terminal se a IA está realizando uma jogada que considera segura ou uma jogada aleatória.
- Não modifique um `set` enquanto estiver iterando diretamente sobre ele. Isso pode causar erros.

## Testes

Para acompanhar o progresso da sua implementação, execute:

```bash
python test_minesweeper.py
```

O script apresenta os testes agrupados por função, mostra os valores esperados e obtidos e fornece dicas quando encontra uma falha. Esses testes são auxiliares e não garantem que todos os casos possíveis estejam corretos.

Além dos testes automatizados, execute o programa e teste cuidadosamente o comportamento da interface:

```bash
python runner.py
```

Você não deve importar módulos que não façam parte da biblioteca padrão do Python ou que não tenham sido expressamente autorizados pela especificação da atividade. Uma importação não permitida ou uma alteração indevida no código de distribuição poderá impedir a execução dos testes.

Existem ferramentas capazes de simplificar alguns destes projetos, mas esse não é o objetivo da atividade. O propósito é compreender e implementar os conceitos em um nível mais fundamental. Se o uso de uma ferramenta não foi autorizado, ela não deve ser utilizada.

---

## Atribuição e Licença

Material original: **CS50’s Introduction to Artificial Intelligence with Python — Minesweeper**, de CS50/Harvard University.

Este documento é uma tradução e adaptação do material original. As imagens permanecem hospedadas no site do CS50.

O material original está licenciado sob a [Licença Internacional Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
