import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        return set()

    def known_safes(self):
        if self.count  == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):

        self.moves_made.add(cell)

        self.mark_safe(cell)

        neighbors = set()
        loop_count = count

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignora a própria célula
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) in self.mines:
                        loop_count -= 1
                    elif (i, j) not in self.safes:
                        neighbors.add((i, j))

        if len(neighbors) > 0:
            new_sentence = Sentence(neighbors, loop_count)
            self.knowledge.append(new_sentence)

        while True:
            mines_to_mark = set()
            safes_to_mark = set()

            for sentence in self.knowledge:
                safes_to_mark.update(sentence.known_safes())
                mines_to_mark.update(sentence.known_mines())

            for safe in safes_to_mark:
                self.mark_safe(safe)
            for mine in mines_to_mark:
                self.mark_mine(mine)

            self.knowledge = [s for s in self.knowledge if s.cells != set()]

            new_inferences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 != s2 and s1.cells.issubset(s2.cells):
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        inferred_sentence = Sentence(diff_cells, diff_count)
                        if inferred_sentence not in self.knowledge and inferred_sentence not in new_inferences:
                            new_inferences.append(inferred_sentence)

            if not new_inferences and not safes_to_mark and not mines_to_mark:
                break

            self.knowledge.extend(new_inferences)

    def make_safe_move(self):
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        possible_moves = []
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                # Não pode ter sido escolhida e não pode ser uma mina conhecida
                if cell not in self.moves_made and cell not in self.mines:
                    possible_moves.append(cell)
        
        if possible_moves:
            return random.choice(possible_moves)
        return None
