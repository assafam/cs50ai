import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains.keys():
            self.domains[var] = {word for word in self.domains[var] if len(word) == var.length}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False

        revised = False

        for word_x in self.domains[x].copy():
            conflict = True
            for word_y in self.domains[y]:
                if word_x[overlap[0]] == word_y[overlap[1]]:
                    conflict = False
                    break
            if conflict:
                self.domains[x].remove(word_x)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = [vars for vars, overlap in self.crossword.overlaps.items() if overlap is not None]

        while len(arcs):
            (x, y) = arcs.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for v in self.crossword.variables:
            if v not in assignment or assignment[v] is None:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Verify that all values are distinct
        words = assignment.values()
        if len(words) > len(set(words)):
            return False

        for v1, word in assignment.items():
            # Verify that every value has the correct length
            if v1.length != len(word):
                return False
            # Verify no conflicts between neighbouring variables
            for v2 in self.crossword.neighbors(v1):
                overlap = self.crossword.overlaps[v1, v2]
                try:
                    if assignment[v1][overlap[0]] != assignment[v2][overlap[1]]:
                        return False
                except KeyError:
                    # Incomplete assignment is acceptable
                    pass

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        assert var not in assignment
        values = {v: 0 for v in self.domains[var]}

        for var2 in self.crossword.neighbors(var):
            # Variables already assigned should not be counted
            if var2 in assignment:
                continue
            # Candidate values for all neighbours should have the correct length (node consistency)
            for val2 in self.domains[var2]:
                assert var2.length == len(val2)
            overlap = self.crossword.overlaps[var, var2]
            for val1 in values:
                # Candidate values for neighbours are ruled out (not consistent) if they are non distinct,
                # or if there's a conflict between letters in a common position (overlap)
                for val2 in self.domains[var2]:
                    if val1 == val2 or (overlap is not None and val1[overlap[0]] != val2[overlap[1]]):
                        values[val1] += 1

        return sorted(values, key=values.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Create a dict of variables with number of remaining values, filter out variables already in assignment
        vars = {v: len(self.domains[v]) for v in self.crossword.variables if v not in assignment}
        assert len(vars) > 0
        # Filter items which have more than the minimum number of remaining items
        vars = {k: v for k, v in vars.items() if v == min(vars.values())}
        if len(vars) == 1:
            return list(vars.keys())[0]

        # For remaining variables, sort according to number of neighbours
        num_neighbours = {v: len(self.crossword.neighbors(v)) for v in vars.keys()}
        return sorted(num_neighbours, key=num_neighbours.get, reverse=True)[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var, assignment):
            if self.consistent(assignment | {var: val}):
                assignment[var] = val
                res = self.backtrack(assignment)
                if res is not None:
                    return res
                assignment.pop(var)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
