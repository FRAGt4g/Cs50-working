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

        mine_locations = [(2, 3), (4, 3), (5, 5), (6, 1), (6, 3), (6, 4), (6, 6), (7, 0), (0,0)]
        small_locations = [
            (0, 1), (0, 2), (0, 3), (2, 2), (1, 3), (3, 2)
        ]
        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            # i, j = mine_locations[len(self.mines)]
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True
        with open("mines.txt", "w+") as f:
            for i, j in self.mines:
                f.write(f"{i} {j}\n")

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
                if (i, j) == cell: continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) in self.mines:
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
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
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
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

    def mark_all_mines(self, sentence):
        for cell in sentence.cells.copy():
            self.mark_mine(cell)
        
    def mark_all_safe(self, sentence):
        for cell in sentence.cells.copy():
            self.mark_safe(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

    def get_neighbors(self, cell):
        """
        Returns the list of neighbors of a cell.
        """
        neighbors = []
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.height and 0 <= j < self.width and (i, j) != cell:
                    neighbors.append((i, j))
        return neighbors
    
    def mines_in_neighbors(self, cell):
        count = 0
        for neighbor in self.get_neighbors(cell):
            if neighbor in self.mines:
                count += 1
        return count
    
    def unknown_neighbors(self, cell):
        nieghbors = self.get_neighbors(cell)
        for neighbor in nieghbors:
            if neighbor in self.mines or neighbor in self.safes:
                nieghbors.remove(neighbor)
        return nieghbors

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)
        self.mark_safe(cell)
        unknown_nieghbors = self.unknown_neighbors(cell)
        known_mines_around = self.mines_in_neighbors(cell)
        self.knowledge.append(Sentence(unknown_nieghbors, count - known_mines_around))
        for sentence in self.knowledge:
            if len(sentence.cells) == 0 or sentence.count < 0: #Invalid sentence
                self.knowledge.remove(sentence)
            elif sentence.count == 0:
                self.mark_all_safe(sentence)
            elif sentence.count == len(sentence.cells):
                self.mark_all_mines(sentence)
        for sentence1, sentence2 in itertools.combinations(self.knowledge, 2):
            if len(sentence1.cells) == len(sentence2.cells): continue

            if sentence1.cells.issubset(sentence2.cells):
                new_sentence = Sentence(
                    sentence2.cells - sentence1.cells, 
                    sentence2.count - sentence1.count
                )
                if new_sentence not in self.knowledge:
                    if new_sentence.count == 0: self.mark_all_safe(new_sentence)
                    else: self.knowledge.append(new_sentence)
            elif sentence2.cells.issubset(sentence1.cells):
                new_sentence = Sentence(
                    sentence1.cells - sentence2.cells, 
                    sentence1.count - sentence2.count
                )
                if new_sentence not in self.knowledge:
                    if new_sentence.count == 0: self.mark_all_safe(new_sentence)
                    else: self.knowledge.append(new_sentence)
        
        self.print_info()


    def print_info(self):
        print("***GENERAL INFO***")
        if len(self.knowledge) > 0:
            print("Knowledge base:")
            for fact in self.knowledge:
                print(f"  {len(fact.cells)} Cells with {fact.count} Mine{"s:" if fact.count > 1 else ":"}\t{fact.cells}")
        else: print("Knowledge base: Empty")

        print(f"Played cells ({len(self.moves_made)}): \n  [{", ".join([str(cell) for cell in sorted(self.moves_made)]) if len(self.moves_made) > 0 else "EMPTY"}]")
        print(f"Additional Safe cells ({len(self.safes - self.moves_made)}): \n  [{", ".join([str(cell) for cell in sorted(self.safes - self.moves_made)]) if len(self.safes) > 0 else "EMPTY"}]")
        print(f"Mine cells ({len(self.mines)}): \n  [{", ".join([str(cell) for cell in sorted(self.mines)]) if len(self.mines) > 0 else "EMPTY"}]")
        print("******************")

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        for cell in self.safes:
            if cell not in self.moves_made and cell not in self.mines:
                return cell

        return None
    

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        for _ in range(self.height * self.width * 10):
            random_move = (random.randint(0, self.height - 1), random.randint(0, self.width - 1))
            if random_move not in self.moves_made and random_move not in self.mines:
                return random_move
            
        
        return None
    




"""
    Called when the Minesweeper board tells us, for a given
    safe cell, how many neighboring cells have mines in them.

    This function should:
        1) mark the cell as a move that has been made
        2) mark the cell as safe
        3) add a new sentence to the AI's knowledge base
            based on the value of `cell` and `count`
        4) mark any additional cells as safe or as mines
            if it can be concluded based on the AI's knowledge base
        5) add any new sentences to the AI's knowledge base
            if they can be inferred from existing knowledge
"""
"""
def add_knowledge(self, cell, count):
        print(f"\nMAKING MOVE: {cell} with count {count}\n")
        self.moves_made.add(cell)
        self.mark_safe(cell)
        new_cells = self.get_neighbors(cell)
        for cell in new_cells:
            if cell in self.safes:
                new_cells.remove(cell)
            elif cell in self.mines:
                new_cells.remove(cell)
                count -= 1
            elif cell in self.moves_made:
                new_cells.remove(cell)
        
        if count == 0: 
            for neighbor in new_cells:
                self.mark_safe(neighbor)
        else:
            self.knowledge.append(Sentence(new_cells, count))
        
        for fact in self.knowledge:
            if fact.cells == set():             #Is an empty fact
                self.knowledge.remove(fact)
            elif fact.count <= 0:               #All cells are safe
                for cell in list(fact.cells):
                    self.mark_safe(cell)
                if fact in self.knowledge: self.knowledge.remove(fact)
            elif fact.count == len(fact.cells): #All cells are mines
                for cell in list(fact.cells):
                    self.mark_mine(cell)
                if fact in self.knowledge: self.knowledge.remove(fact)

        length = len(self.knowledge)
        for index1 in range(length):
            fact1 = self.knowledge[index1]
            
            for index2 in range(index1 + 1, length):
                fact2 = self.knowledge[index2]
                if fact1 == fact2: continue
                
                # print(f"fact combination @ {index1}: {fact1.cells} and {fact2.cells} @ {index2}")
                # if fact1.cells.issubset(fact2.cells) and fact1.cells.intersection(fact2.cells) not in [fact.cells for fact in self.knowledge]:
                if fact1.cells.issubset(fact2.cells):
                        # Create inverse of the intersection
                        inverse = fact2.cells - fact1.cells
                        new_count = fact2.count - fact1.count
                        new_fact = Sentence(inverse, new_count)
                        if new_fact not in self.knowledge:
                            print(f"fact {index1} is subset of fact {index2}:\n  Fact #{index1} (len = {len(fact1.cells)}) w {fact1.count} mines: {fact1.cells}\n  Fact #{index2} (len = {len(fact2.cells)}) w {fact2.count} mines: {fact2.cells}\n  Inverse:\n    Count: {new_count}\n    Cells: {inverse}")
                            self.knowledge.append(new_fact)
                elif fact2.cells.issubset(fact1.cells):
                    # Create inverse of the intersection
                    inverse = fact1.cells - fact2.cells
                    new_count = fact1.count - fact2.count
                    new_fact = Sentence(inverse, new_count)
                    if new_fact not in self.knowledge:
                        print(f"fact {index2} is subset of fact {index1}:\n  Fact #{index2} (len = {len(fact2.cells)}) w {fact2.count} mines: {fact2.cells}\n  Fact #{index1} (len = {len(fact1.cells)}) w {fact1.count} mines: {fact1.cells}\n  Inverse:\n    Count: {new_count}\n    Cells: {inverse}")
                        self.knowledge.append(new_fact)
        
        for index, fact in enumerate(self.knowledge):
            if fact.cells == set():             #Is an empty fact
                self.knowledge.remove(fact)
                print(f"Removed empty fact {index}")
            elif fact.count <= 0:               #All cells are safe
                print(f"Removed all safe fact {index}: {fact.cells}")
                for cell in list(fact.cells):
                    self.mark_safe(cell)
                if fact in self.knowledge: self.knowledge.remove(fact)
            elif fact.count == len(fact.cells): #All cells are mines
                print(f"Removed all mine fact {index}: {fact.cells}")
                for cell in list(fact.cells):
                    self.mark_mine(cell)
                if fact in self.knowledge: self.knowledge.remove(fact)
        
        for fact in self.knowledge:
            for cell in list(fact.cells):
                if cell in self.safes:
                    fact.cells.remove(cell)
                elif cell in self.mines:
                    fact.count -= 1
                    fact.cells.remove(cell)
                elif cell in self.moves_made:
                    fact.cells.remove(cell)
        
        self.print_info()
"""