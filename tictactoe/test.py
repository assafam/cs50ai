from tictactoe import initial_state, player, actions, result, winner, terminal, utility, extermum
import unittest

class TestTTTMethods(unittest.TestCase):
    def setUp(self):
        self.board = initial_state()

    def test_player(self):
        self.assertEqual(player(self.board), "X")
        self.board[0][0] = "X"
        self.assertEqual(player(self.board), "O")

    def test_actions(self):
        self.assertEqual(len(actions(self.board)), 9)

    def test_result(self):
        self.board = result(self.board, (1, 0))
        for i in range(3):
            for j in range(3):
                if i == 1 and j == 0:
                    self.assertEqual(self.board[i][j], "X")
                else:
                    self.assertIsNone(self.board[i][j])
        with self.assertRaises(RuntimeError):
            self.board = result(self.board, (1, 0))

    def fill_top_row_with_x(self):
        for i in range(3):
            self.board[0][i] = "X"

    def fill_board_with_tie_result(self):
        for i in range(3):
            for j in range(3):
                if (i == 0 and j == 0) or (i == 1 and j != 0) or (i == 2 and j != 2):
                    self.board[i][j] = "X"
                else:
                    self.board[i][j] = "O"

    def test_winner_terminal_utility(self):
        self.assertIsNone(winner(self.board))
        self.assertFalse(terminal(self.board))
        self.fill_top_row_with_x()
        self.assertEqual(winner(self.board), "X")
        self.assertTrue(terminal(self.board))
        self.assertEqual(utility(self.board), 1)
        self.fill_board_with_tie_result()
        self.assertIsNone(winner(self.board))
        self.assertTrue(terminal(self.board))
        self.assertEqual(utility(self.board), 0)

    def test_extermum(self):
        self.assertEqual(extermum(self.board), 0)
        self.fill_board_with_tie_result()
        self.board[0][0] = None
        self.assertEqual(extermum(self.board), 0)


if __name__ == '__main__':
    unittest.main()
