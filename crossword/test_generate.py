import unittest

from crossword import Variable
from generate import Crossword, CrosswordCreator


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
        assignment[Variable(0, 1, 'down', 5)] = "ABCDE"
        self.assertFalse(creator.consistent(assignment))    # Conflicts


if __name__ == "__main__":
    unittest.main()
