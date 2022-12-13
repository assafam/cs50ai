import unittest

from crossword import Crossword, Variable
from generate import CrosswordCreator


class TestGenerateMethods(unittest.TestCase):
    def setUp(self):
        crossword_src = [
            ("data/structure0.txt", "data/words0.txt"),
            # ("data/structure1.txt", "data/words1.txt"),
            # ("data/structure2.txt", "data/words2.txt"),
            ]
        self.creators = []
        for structure, words in crossword_src:
            crossword = Crossword(structure, words)
            self.creators.append(CrosswordCreator(crossword))

    def test_enforce_node_consistency(self):
        for creator in self.creators:
            creator.enforce_node_consistency()
            for var, words in creator.domains.items():
                for word in words:
                    self.assertEqual(len(word), var.length)

    def test_revise(self):
        for creator in self.creators:
            creator.enforce_node_consistency()
            for x in creator.crossword.variables:
                for y in creator.crossword.variables:
                    if x == y:
                        continue

                    creator.revise(x, y)

                    # Verify that arc is consistent after revision
                    overlap = creator.crossword.overlaps[x, y]
                    for word_x in creator.domains[x]:
                        self.assertTrue(
                            overlap is None or
                            len({w for w in creator.domains[y] if w[overlap[1]] == word_x[overlap[0]]}) > 0
                            )

                    # No further revision is expected
                    self.assertFalse(creator.revise(x, y))

    def test_ac3(self):
        for creator in self.creators:
            creator.enforce_node_consistency()
            creator.ac3(None)

            # Verify that all arcs are consistent
            for x in creator.crossword.variables:
                for y in creator.crossword.variables:
                    if x == y:
                        continue

                    overlap = creator.crossword.overlaps[x, y]
                    for word_x in creator.domains[x]:
                        self.assertTrue(
                            overlap is None or
                            len({w for w in creator.domains[y] if w[overlap[1]] == word_x[overlap[0]]}) > 0
                            )

    def test_assignment_complete(self):
        creator = self.creators[0]
        self.assertTrue(creator.assignment_complete({v: "A" for v in creator.crossword.variables}))
        self.assertFalse(creator.assignment_complete({v: None for v in creator.crossword.variables}))
        self.assertFalse(creator.assignment_complete({Variable(0, 1, 'across', 3): "A"}))

    def test_consistent(self):
        creator = self.creators[0]
        assignment = dict()
        assignment[Variable(0, 1, 'across', 3)] = "ABC"
        assignment[Variable(4, 1, 'across', 4)] = "SAME"
        self.assertTrue(creator.consistent(assignment))
        assignment[Variable(1, 4, 'down', 4)] = "SAME"      # Non-distinct word
        self.assertFalse(creator.consistent(assignment))
        assignment[Variable(1, 4, 'down', 4)] = "WRONG_LENGTH"
        self.assertFalse(creator.consistent(assignment))
        assignment[Variable(0, 1, 'down', 5)] = "ABCDE"     # Conflicts
        self.assertFalse(creator.consistent(assignment))

    def test_order_domain_values(self):
        creator = self.creators[0]
        creator.enforce_node_consistency()
        # Conflict with two other variables, result dict: {'THREE': 5, 'SEVEN': 5, 'EIGHT': 7}
        assignment = dict()
        self.assertIn(creator.order_domain_values(Variable(0, 1, 'down', 5), assignment),
                      [["SEVEN", "THREE", "EIGHT"], ["THREE", "SEVEN", "EIGHT"]])
        # Conflict with one other variable, result dict: {'THREE': 3, 'SEVEN': 2, 'EIGHT': 3}
        assignment[Variable(0, 1, 'across', 3)] = "TEN"
        self.assertIn(creator.order_domain_values(Variable(0, 1, 'down', 5), assignment),
                      [["SEVEN", "THREE", "EIGHT"], ["SEVEN", "EIGHT", "THREE"]])
        # Conflict with no other variables, result dict: {'THREE': 0, 'SEVEN': 0, 'EIGHT': 0}
        assignment[Variable(4, 1, 'across', 4)] = "SAME"
        self.assertEqual(len(creator.order_domain_values(Variable(0, 1, 'down', 5), assignment)), 3)

    def test_select_unassigned_variable(self):
        creator = self.creators[0]
        creator.enforce_node_consistency()
        # Tie in remaining values and number of neighbours
        assignment = dict()
        self.assertIn(creator.select_unassigned_variable(assignment),
                      [Variable(0, 1, 'down', 5), Variable(4, 1, 'across', 4)])  # Both have 2 nighbours
        # One variable with more neighbours
        assignment[Variable(0, 1, 'down', 5)] = "ABCDE"
        self.assertEqual(creator.select_unassigned_variable(assignment),
                         Variable(4, 1, 'across', 4))
        # One variable with less remaining values
        assignment[Variable(4, 1, 'across', 4)] = "SAME"
        self.assertEqual(creator.select_unassigned_variable(assignment),
                         Variable(1, 4, 'down', 4))
        # Single unassigned variable
        assignment[Variable(0, 1, 'across', 3)] = "TEN"
        self.assertEqual(creator.select_unassigned_variable(assignment),
                         Variable(1, 4, 'down', 4))


if __name__ == "__main__":
    unittest.main()
