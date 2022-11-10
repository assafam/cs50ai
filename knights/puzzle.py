from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

def puzzle_constraints(knight, knave):
    """Returns constaints given by puzzle definition."""
    return And(
    Or(knight, knave),
    Implication(knight, Not(knave)),
    Implication(knave, Not(knight))
    )

def knight_knave_implications(knight, knave, sentence):
    """Returns a positive implication for Knight and a negative implicatino for Knave"""
    return And(
        Implication(knight, sentence),
        Implication(knave, Not(sentence))
    )

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    puzzle_constraints(AKnight, AKnave),
    knight_knave_implications(AKnight, AKnave, And(AKnight, AKnave)),
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    puzzle_constraints(AKnight, AKnave),
    puzzle_constraints(BKnight, BKnave),
    knight_knave_implications(AKnight, AKnave, And(AKnave, BKnave)),
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    puzzle_constraints(AKnight, AKnave),
    puzzle_constraints(BKnight, BKnave),
    knight_knave_implications(AKnight, AKnave, Or(
        And(AKnight, BKnight),
        And(AKnave, BKnave),
    )),
    knight_knave_implications(BKnight, BKnave, Or(
        And(AKnight, BKnave),
        And(AKnave, BKnight),
    )),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    puzzle_constraints(AKnight, AKnave),
    puzzle_constraints(BKnight, BKnave),
    puzzle_constraints(CKnight, CKnave),
    Implication(AKnight, Or(AKnight, AKnave)),
    Implication(AKnave, Or(Not(AKnight), Not(AKnave))),
    # B is a knight so A said 'I am a knave'
    Implication(BKnight, knight_knave_implications(AKnight, AKnave, AKnave)),
    # B is a knave so A said 'I am a knight'
    Implication(BKnave, knight_knave_implications(AKnight, AKnave, AKnight)),
    knight_knave_implications(BKnight, BKnave, CKnave),
    knight_knave_implications(CKnight, CKnave, AKnight),
)

def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
