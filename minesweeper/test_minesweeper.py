"""
Script de verificacao das funcoes de minesweeper.py.

Este script NAO usa o modulo unittest de proposito: a ideia e que qualquer
aluno consiga executar ``python test_minesweeper.py`` e entender
imediatamente, em portugues, o que foi testado, o que era esperado e o que
o codigo realmente retornou.

Os testes ajudam a acompanhar o progresso, mas nao substituem a leitura da
especificacao nem garantem que todos os casos possiveis foram cobertos.

Como executar:
    cd minesweeper
    python test_minesweeper.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from minesweeper import MinesweeperAI, Sentence  # noqa: E402


class Reporter:
    """Coleta e exibe os resultados dos testes de forma explicativa."""

    def __init__(self):
        self.section_name = None
        self.sections_order = []
        self.sections = {}  # nome -> [passou, total]
        self.failures = []  # (secao, descricao, esperado, obtido, dica)

    def section(self, name):
        self.section_name = name
        self.sections_order.append(name)
        self.sections[name] = [0, 0]
        print()
        print("=" * 72)
        print(f" Testando: {name}")
        print("=" * 72)

    def _register(self, ok, description, expected, actual, hint):
        self.sections[self.section_name][1] += 1
        if ok:
            self.sections[self.section_name][0] += 1
            print(f"  [OK]     {description}")
        else:
            self.failures.append(
                (self.section_name, description, expected, actual, hint)
            )
            print(f"  [FALHOU] {description}")
            print(f"           esperado: {expected}")
            print(f"           obtido:   {actual}")
            if hint:
                print(f"           dica: {hint}")

    def check(self, description, actual_fn, expected, hint=None):
        """Executa actual_fn() e compara o resultado com ``expected``."""
        try:
            actual = actual_fn()
            ok = actual == expected
        except Exception as error:
            actual = f"{type(error).__name__}: {error}"
            ok = False
        self._register(ok, description, expected, actual, hint)

    def check_condition(
        self,
        description,
        actual_fn,
        condition,
        expected_description,
        hint=None,
    ):
        """Executa actual_fn() e valida o resultado usando ``condition``."""
        try:
            actual = actual_fn()
            ok = condition(actual)
        except Exception as error:
            actual = f"{type(error).__name__}: {error}"
            ok = False
        self._register(
            ok,
            description,
            expected_description,
            actual,
            hint,
        )

    def summary(self):
        print()
        print("=" * 72)
        print(" RESUMO POR FUNCAO")
        print("=" * 72)
        total_passed = 0
        total_all = 0

        for name in self.sections_order:
            passed, total = self.sections[name]
            total_passed += passed
            total_all += total
            status = "OK" if passed == total else "COM FALHAS"
            print(f"  {name:<24} {passed}/{total} testes passaram  [{status}]")

        print()
        print("-" * 72)
        print(f" TOTAL GERAL: {total_passed}/{total_all} testes passaram")
        print("-" * 72)

        if self.failures:
            print()
            print(f" {len(self.failures)} teste(s) falharam. Detalhe:")
            for section, description, _expected, _actual, _hint in self.failures:
                print(f"  - [{section}] {description}")
            print()
            print(" Revise as funcoes listadas acima. Role para cima para ver")
            print(" o motivo detalhado de cada falha (esperado x obtido).")
            return False

        print()
        print(" Parabens! Todas as funcoes passaram em todos os testes.")
        return True


def sentence_after_mark_mine(cells, count, cell):
    """Retorna o estado de uma sentenca depois de marcar uma mina."""
    sentence = Sentence(cells, count)
    sentence.mark_mine(cell)
    return sentence.cells, sentence.count


def sentence_after_mark_safe(cells, count, cell):
    """Retorna o estado de uma sentenca depois de marcar uma celula segura."""
    sentence = Sentence(cells, count)
    sentence.mark_safe(cell)
    return sentence.cells, sentence.count


def knowledge_contains(ai, cells, count):
    """Verifica se a base da IA contem uma sentenca especifica."""
    expected_cells = set(cells)
    return any(
        sentence.cells == expected_cells and sentence.count == count
        for sentence in ai.knowledge
    )


r = Reporter()


# ---------------------------------------------------------------------------
# Sentence.known_mines()
# ---------------------------------------------------------------------------
r.section("Sentence.known_mines")

r.check(
    "Se count for igual ao numero de celulas, todas devem ser minas",
    lambda: Sentence({(0, 0), (0, 1), (1, 0)}, 3).known_mines(),
    {(0, 0), (0, 1), (1, 0)},
    hint="Compare count com len(cells).",
)

r.check(
    "Se apenas parte das celulas for mina, nenhuma mina e conhecida ainda",
    lambda: Sentence({(0, 0), (0, 1), (1, 0)}, 2).known_mines(),
    set(),
)

r.check(
    "Uma sentenca com count 0 nao deve identificar nenhuma mina",
    lambda: Sentence({(0, 0), (0, 1)}, 0).known_mines(),
    set(),
)


# ---------------------------------------------------------------------------
# Sentence.known_safes()
# ---------------------------------------------------------------------------
r.section("Sentence.known_safes")

r.check(
    "Se count for 0, todas as celulas da sentenca devem ser seguras",
    lambda: Sentence({(0, 0), (0, 1), (1, 0)}, 0).known_safes(),
    {(0, 0), (0, 1), (1, 0)},
    hint="Uma sentenca com zero minas torna todas as suas celulas seguras.",
)

r.check(
    "Se a sentenca ainda contiver minas possiveis, nenhuma segura e certa",
    lambda: Sentence({(0, 0), (0, 1), (1, 0)}, 1).known_safes(),
    set(),
)


# ---------------------------------------------------------------------------
# Sentence.mark_mine()
# ---------------------------------------------------------------------------
r.section("Sentence.mark_mine")

r.check(
    "Marcar uma mina deve remover a celula e diminuir count",
    lambda: sentence_after_mark_mine(
        {(0, 0), (0, 1), (1, 0)},
        2,
        (0, 0),
    ),
    ({(0, 1), (1, 0)}, 1),
    hint="A mina removida ja foi contabilizada; diminua count em 1.",
)

r.check(
    "Marcar uma celula ausente nao deve modificar a sentenca",
    lambda: sentence_after_mark_mine(
        {(0, 0), (0, 1)},
        1,
        (2, 2),
    ),
    ({(0, 0), (0, 1)}, 1),
)


# ---------------------------------------------------------------------------
# Sentence.mark_safe()
# ---------------------------------------------------------------------------
r.section("Sentence.mark_safe")

r.check(
    "Marcar uma segura deve remover a celula sem diminuir count",
    lambda: sentence_after_mark_safe(
        {(0, 0), (0, 1), (1, 0)},
        2,
        (0, 0),
    ),
    ({(0, 1), (1, 0)}, 2),
    hint="Uma celula segura nao contribuia para a quantidade de minas.",
)

r.check(
    "Marcar uma celula ausente nao deve modificar a sentenca",
    lambda: sentence_after_mark_safe(
        {(0, 0), (0, 1)},
        1,
        (2, 2),
    ),
    ({(0, 0), (0, 1)}, 1),
)


# ---------------------------------------------------------------------------
# MinesweeperAI.add_knowledge()
# ---------------------------------------------------------------------------
r.section("MinesweeperAI.add_knowledge")


def center_knowledge_state():
    ai = MinesweeperAI(height=3, width=3)
    ai.add_knowledge((1, 1), 1)
    neighbors = {
        (0, 0), (0, 1), (0, 2),
        (1, 0),         (1, 2),
        (2, 0), (2, 1), (2, 2),
    }
    return (
        (1, 1) in ai.moves_made,
        (1, 1) in ai.safes,
        knowledge_contains(ai, neighbors, 1),
    )


r.check(
    "Deve registrar a jogada, marca-la segura e criar a sentenca vizinha",
    center_knowledge_state,
    (True, True, True),
    hint="A celula revelada nao deve aparecer entre suas proprias vizinhas.",
)


def corner_knowledge_state():
    ai = MinesweeperAI(height=3, width=3)
    ai.add_knowledge((0, 0), 1)
    return knowledge_contains(ai, {(0, 1), (1, 0), (1, 1)}, 1)


r.check(
    "Uma celula no canto deve considerar apenas as 3 vizinhas validas",
    corner_knowledge_state,
    True,
    hint="Verifique os limites de linha e coluna antes de incluir a vizinha.",
)


def excludes_known_safe():
    ai = MinesweeperAI(height=3, width=3)
    ai.mark_safe((0, 1))
    ai.add_knowledge((0, 0), 1)
    return knowledge_contains(ai, {(1, 0), (1, 1)}, 1)


r.check(
    "Celulas seguras ja conhecidas nao devem entrar na nova sentenca",
    excludes_known_safe,
    True,
)


def adjusts_for_known_mine():
    ai = MinesweeperAI(height=3, width=3)
    ai.mark_mine((0, 1))
    ai.add_knowledge((0, 0), 1)
    return {(1, 0), (1, 1)} <= ai.safes


r.check(
    "Uma mina vizinha conhecida deve ser descontada de count",
    adjusts_for_known_mine,
    True,
    hint=(
        "Se a unica mina vizinha ja e conhecida, as demais vizinhas "
        "desconhecidas devem formar uma sentenca com count 0."
    ),
)


def infers_all_safe_neighbors():
    ai = MinesweeperAI(height=3, width=3)
    ai.add_knowledge((1, 1), 0)
    return ai.safes


r.check(
    "Uma celula central com count 0 deve tornar toda a grade 3 x 3 segura",
    infers_all_safe_neighbors,
    {(i, j) for i in range(3) for j in range(3)},
)


def infers_all_mine_neighbors():
    ai = MinesweeperAI(height=2, width=2)
    ai.add_knowledge((0, 0), 3)
    return ai.mines


r.check(
    "No canto de uma grade 2 x 2, count 3 deve identificar 3 minas",
    infers_all_mine_neighbors,
    {(0, 1), (1, 0), (1, 1)},
)


def subset_inference_finds_safe():
    ai = MinesweeperAI(height=5, width=5)
    a, b, c = (0, 0), (0, 1), (0, 2)
    ai.knowledge = [
        Sentence({a, b}, 1),
        Sentence({a, b, c}, 1),
    ]

    # A celula revelada fica longe das sentencas preparadas acima. A chamada
    # serve para disparar a atualizacao completa da base de conhecimento.
    ai.add_knowledge((4, 4), 0)
    return c in ai.safes


r.check(
    "{A, B}=1 e {A, B, C}=1 devem permitir concluir que C e segura",
    subset_inference_finds_safe,
    True,
    hint="Subtraia a sentenca subconjunto da sentenca superconjunto.",
)


def repeated_inference_reaches_fixed_point():
    ai = MinesweeperAI(height=5, width=5)
    a, b, c, d, e = [(0, column) for column in range(5)]
    ai.knowledge = [
        Sentence({a, b}, 1),
        Sentence({a, b, c}, 1),
        Sentence({c, d}, 1),
        Sentence({d, e}, 1),
    ]

    ai.add_knowledge((4, 4), 0)
    return c in ai.safes, d in ai.mines, e in ai.safes


r.check(
    "Novas conclusoes devem ser propagadas ate nao haver mais inferencias",
    repeated_inference_reaches_fixed_point,
    (True, True, True),
    hint=(
        "Uma inferencia pode alterar outra sentenca. Repita o processo "
        "enquanto o conhecimento continuar mudando."
    ),
)


# ---------------------------------------------------------------------------
# MinesweeperAI.make_safe_move()
# ---------------------------------------------------------------------------
r.section("MinesweeperAI.make_safe_move")


def only_available_safe_move():
    ai = MinesweeperAI(height=3, width=3)
    ai.safes = {(0, 0), (1, 1)}
    ai.moves_made = {(0, 0)}
    return ai.make_safe_move()


r.check(
    "Deve escolher uma celula segura que ainda nao foi selecionada",
    only_available_safe_move,
    (1, 1),
)

r.check(
    "Deve retornar None quando nenhuma jogada segura estiver disponivel",
    lambda: MinesweeperAI(height=3, width=3).make_safe_move(),
    None,
)


def safe_move_without_mutation():
    ai = MinesweeperAI(height=3, width=3)
    ai.moves_made = {(0, 0)}
    ai.mines = {(2, 2)}
    ai.safes = {(0, 0), (1, 1)}
    ai.knowledge = [Sentence({(0, 1), (0, 2)}, 1)]

    before = (
        ai.moves_made.copy(),
        ai.mines.copy(),
        ai.safes.copy(),
        [(sentence.cells.copy(), sentence.count) for sentence in ai.knowledge],
    )
    move = ai.make_safe_move()
    after = (
        ai.moves_made.copy(),
        ai.mines.copy(),
        ai.safes.copy(),
        [(sentence.cells.copy(), sentence.count) for sentence in ai.knowledge],
    )
    return move, before == after


r.check(
    "Escolher uma jogada segura nao deve alterar o conhecimento da IA",
    safe_move_without_mutation,
    ((1, 1), True),
)


# ---------------------------------------------------------------------------
# MinesweeperAI.make_random_move()
# ---------------------------------------------------------------------------
r.section("MinesweeperAI.make_random_move")


def only_available_random_move():
    ai = MinesweeperAI(height=2, width=3)
    ai.moves_made = {(0, 0), (0, 1), (1, 0)}
    ai.mines = {(0, 2), (1, 1)}
    return ai.make_random_move()


r.check(
    "Deve escolher a unica celula que nao foi jogada nem e mina conhecida",
    only_available_random_move,
    (1, 2),
)


def random_moves_are_valid():
    ai = MinesweeperAI(height=3, width=4)
    ai.moves_made = {(0, 0), (1, 1)}
    ai.mines = {(0, 3), (2, 2)}
    allowed = {
        (i, j)
        for i in range(ai.height)
        for j in range(ai.width)
        if (i, j) not in ai.moves_made and (i, j) not in ai.mines
    }
    returned_moves = [ai.make_random_move() for _ in range(40)]
    return returned_moves, allowed


r.check_condition(
    "Varias escolhas aleatorias devem permanecer dentro das opcoes validas",
    random_moves_are_valid,
    lambda result: all(move in result[1] for move in result[0]),
    "40 jogadas pertencentes ao conjunto de celulas permitidas",
    hint="Exclua de antemao moves_made e mines das opcoes aleatorias.",
)


def no_random_move_available():
    ai = MinesweeperAI(height=2, width=2)
    ai.moves_made = {(0, 0), (0, 1)}
    ai.mines = {(1, 0), (1, 1)}
    return ai.make_random_move()


r.check(
    "Deve retornar None quando nenhuma jogada aleatoria for possivel",
    no_random_move_available,
    None,
)


if __name__ == "__main__":
    ok = r.summary()
    sys.exit(0 if ok else 1)
