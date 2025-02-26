import random
import pytest

from burrsolver.position import Axis, Position
from burrsolver.voxel import Voxel


ROTATIONS = [
    (Voxel(1, 2, 3), 0, Axis.Z, Voxel(1, 2, 3)),
    (Voxel(1, 2, 3), 1, Axis.Z, Voxel(-2, 1, 3)),
    (Voxel(1, 2, 3), 2, Axis.Z, Voxel(-1, -2, 3)),
    (Voxel(1, 2, 3), 3, Axis.Z, Voxel(2, -1, 3)),
    (Voxel(1, 2, 3), 4, Axis.Z, Voxel(-1, 2, -3)),
    (Voxel(1, 2, 3), 5, Axis.Z, Voxel(-2, -1, -3)),
    (Voxel(1, 2, 3), 6, Axis.Z, Voxel(1, -2, -3)),
    (Voxel(1, 2, 3), 7, Axis.Z, Voxel(2, 1, -3)),

    (Voxel(1, 2, 3), 0, Axis.Y, Voxel(1, -3, 2)),
    (Voxel(1, 2, 3), 1, Axis.Y, Voxel(-2, -3, 1)),
    (Voxel(1, 2, 3), 2, Axis.Y, Voxel(-1, -3, -2)),
    (Voxel(1, 2, 3), 3, Axis.Y, Voxel(2, -3, -1)),
    (Voxel(1, 2, 3), 4, Axis.Y, Voxel(-1, 3, 2)),
    (Voxel(1, 2, 3), 5, Axis.Y, Voxel(-2, 3, -1)),
    (Voxel(1, 2, 3), 6, Axis.Y, Voxel(1, 3, -2)),
    (Voxel(1, 2, 3), 7, Axis.Y, Voxel(2, 3, 1)),

    (Voxel(1, 2, 3), 0, Axis.X, Voxel(3, 2, -1)),
    (Voxel(1, 2, 3), 1, Axis.X, Voxel(3, 1, 2)),
    (Voxel(1, 2, 3), 2, Axis.X, Voxel(3, -2, 1)),
    (Voxel(1, 2, 3), 3, Axis.X, Voxel(3, -1, -2)),
    (Voxel(1, 2, 3), 4, Axis.X, Voxel(-3, 2, 1)),
    (Voxel(1, 2, 3), 5, Axis.X, Voxel(-3, -1, 2)),
    (Voxel(1, 2, 3), 6, Axis.X, Voxel(-3, -2, -1)),
    (Voxel(1, 2, 3), 7, Axis.X, Voxel(-3, 1, -2)),
]


@pytest.mark.parametrize("voxel, orientation, axis, expected", ROTATIONS)
def test_rotate(voxel: Voxel, orientation: int, axis: Axis, expected: Voxel):
    assert voxel.move_to(Position(0, 0, 0, axis), orientation) == expected

    for i in range(10):
        x = random.randint(-10, 10)
        y = random.randint(-10, 10)
        z = random.randint(-10, 10)
        expected_move = expected + Voxel(x, y, z)
        assert voxel.move_to(Position(x, y, z, axis), orientation) == expected_move
