import pytest

from burrsolver.position import Axis, Direction, Position, SIZE


def expected(direction: Direction, steps: int):
    match direction:
        case Direction.UP:
            return Position(0, steps * SIZE, 0, Axis.Z)
        case Direction.DOWN:
            return Position(0, -steps * SIZE, 0, Axis.Z)
        case Direction.LEFT:
            return Position(-steps * SIZE, 0, 0, Axis.Z)
        case Direction.RIGHT:
            return Position(steps * SIZE, 0, 0, Axis.Z)
        case Direction.FORWARD:
            return Position(0, 0, steps * SIZE, Axis.Z)
        case Direction.BACKWARD:
            return Position(0, 0, -steps * SIZE, Axis.Z)
        case _:
            raise ValueError("Invalid direction")


@pytest.mark.parametrize("direction", list(Direction))
@pytest.mark.parametrize("steps", [1, 2, 3])
def test_move(direction: Direction, steps: int):
    p = Position(0, 0, 0, Axis.Z)
    actual = p.move(direction, steps)
    assert actual == expected(direction, steps)

# test serialization