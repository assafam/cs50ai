"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    flat_board = [cell for row in board for cell in row]
    if flat_board.count(X) <= flat_board.count(O):
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()

    for row in range(3):
        for col in range(3):
            if board[row][col] == EMPTY:
                possible_actions.add((row, col))

    return possible_actions

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] != EMPTY or action[0] < 0 or action[0] > 2 or action[1] < 0 or action[1] > 2:
        raise RuntimeError('Invalid move')

    new_board = deepcopy(board)
    new_board[action[0]][action[1]] = player(board)
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check horizontal and vertical axes
    for i in range(3):
        if board[i][0] != EMPTY and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
        if board[0][i] != EMPTY and board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]

    # Check diagonal axes
    if board[0][0] != EMPTY and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] != EMPTY and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    # No winner found
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # If there's a winner, game is over
    if winner(board) is not None:
        return True

    # If there's any empty cell left and no winner, game is not over
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False

    # If there are no empty cells, game is over
    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    assert terminal(board) is True

    result = winner(board)
    if result == X:
        return 1
    elif result == O:
        return -1
    else:
        return 0

def extermum(board):
    """
    Returns the maximal or minimal utility for a given board
    """
    # For terminal boards, return utility
    if terminal(board):
        return utility(board)

    # Initialize best move and best utility
    next_player = player(board)
    if next_player == X:
        best_utility = -math.inf
    else:
        best_utility = math.inf

    # Iterate over all possible actions and keep best utility
    for action in actions(board):
        next_board = result(board, action)
        next_utility = extermum(next_board)
        if (next_player == X and next_utility > best_utility) or (
           (next_player == O and next_utility < best_utility)):
            best_utility = next_utility

    return best_utility

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # If game ended, return None
    if terminal(board):
        return None

    # Evaluate all possible actions
    action_scores = []
    for action in actions(board):
        action_scores.append((extermum(result(board, action)), action))

    # Return action with highest utility for maximizing player, or lowest utility for minimizing player
    action_scores.sort(reverse=(player(board) == X))
    return action_scores[0][1]
