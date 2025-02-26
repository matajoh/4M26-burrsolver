from itertools import combinations
import random

import pytest

from burrsolver.piece import Piece
from burrsolver.position import Axis, Position
from burrsolver.puzzle import PuzzleState


def random_position():
    """Generate a random position."""
    return Position(
        x=random.randint(-10, 10),
        y=random.randint(-10, 10),
        z=random.randint(-10, 10),
        axis=random.choice([Axis.X, Axis.Y, Axis.Z]),
    )


def random_orientation():
    """Generate a random orientation."""
    return random.randint(0, 5)


@pytest.mark.parametrize("num_pieces", [1, 2, 3, 4, 5, 6])
def test_state_random_positions(num_pieces: int):
    for shapes in combinations(range(6), num_pieces):
        pieces = [
            Piece(shape, random_position(), random_orientation()) for shape in shapes
        ]

        state = PuzzleState(pieces)
        expected = str(state)
        print(expected)
        state = PuzzleState.from_string(expected)
        actual = str(state)
        assert expected == actual
