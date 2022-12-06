import unittest

from generate import Crossword, CrosswordCreator


class TestGenerateMethods(unittest.TestCase):
    def setUp(self):
        crossword_src = [
            ("data/structure0.txt", "data/words0.txt"),
            ("data/structure1.txt", "data/words1.txt"),
            ("data/structure2.txt", "data/words2.txt"),
            ]
        self.crosswords = []
        self.creators = []
        for structure, words in crossword_src:
            self.crosswords.append(Crossword(structure, words))
            self.creators.append(CrosswordCreator(self.crosswords[-1]))

    def test_enforce_node_consistency(self):
        for creator in self.creators:
            creator.enforce_node_consistency()
            for var, words in creator.domains.items():
                for word in words:
                    self.assertEqual(len(word), var.length)


if __name__ == "__main__":
    unittest.main()
