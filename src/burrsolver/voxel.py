"""Voxel class."""

from functools import lru_cache
import math
from typing import NamedTuple

from .position import Axis, Direction, Position, SIZE


@lru_cache(maxsize=None)
def move_voxel(v: "Voxel", d: Direction, steps=1) -> "Voxel":
    """Move the voxel in the given direction.

    Description:
        Note the use of lru_cache to cache the results of the function.
        This is because there are only so many voxels (1331) and only
        so many ways to transition to them. As such, we can cache everything
        and speed up the process of moving voxels around considerably.

    Args:
        v: The voxel to move.
        d: The direction to move the voxel.
        steps: The number of steps to move the voxel.

    Returns:
        The result of moving the voxel.
    """
    match d:
        case Direction.UP:
            return Voxel(v.x, v.y + steps * SIZE, v.z)
        case Direction.DOWN:
            return Voxel(v.x, v.y - steps * SIZE, v.z)
        case Direction.LEFT:
            return Voxel(v.x - steps * SIZE, v.y, v.z)
        case Direction.RIGHT:
            return Voxel(v.x + steps * SIZE, v.y, v.z)
        case Direction.FORWARD:
            return Voxel(v.x, v.y, v.z + steps * SIZE)
        case Direction.BACKWARD:
            return Voxel(v.x, v.y, v.z - steps * SIZE)
        case _:
            raise ValueError("Invalid direction")


class Voxel(NamedTuple("Voxel", [("x", int), ("y", int), ("z", int)])):
    """A voxel in the puzzle."""

    def __add__(self, other: "Voxel") -> "Voxel":
        """Adds two voxels together."""
        return Voxel(self.x + other.x, self.y + other.y, self.z + other.z)

    def move(self, d: Direction, steps=1) -> "Voxel":
        """Move the voxel in the given direction.

        Args:
            d: The direction to move the voxel.
            steps: The number of steps to move the voxel.

        Returns:
            The result of moving the voxel.
        """
        return move_voxel(self, d, steps)

    def move_to(self, p: Position, n: int) -> "Voxel":
        """Move the voxel to a new position.

        Args:
            p: The new position to move the voxel to.
            n: The orientation of the piece.

        Returns:
            The new position of the voxel after moving.
        """
        x, y, z = self
        if n > 3:
            n -= 4
            if n > 3:
                raise ValueError("Invalid orientation")

            x, z = -x, -z       # rotate 180 deg/Y

        match n:
            case 1:
                x, y = -y, x    # rotate 90 deg/Z
            case 2:
                x, y, = -x, -y  # rotate 180 deg/Z
            case 3:
                x, y = y, -x    # rotate 270 deg/Z

        match p.axis:
            case Axis.Z:
                return Voxel(x + p.x, y + p.y, z + p.z)
            case Axis.Y:
                # rotate 90 deg/X
                return Voxel(x + p.x, -z + p.y, y + p.z)
            case Axis.X:
                # rotate 90 deg/Y
                return Voxel(z + p.x, y + p.y, -x + p.z)
            case _:
                raise ValueError("Invalid axis")

    def align(self) -> "Voxel":
        """Align the voxel to the grid."""
        return Voxel(math.floor(self.x), math.floor(self.y),
                     math.floor(self.z))

    def is_inside(self) -> bool:
        """Check if the voxel is inside the puzzle."""
        return not self.is_outside()

    def is_outside(self) -> bool:
        """Check if the voxel is outside the puzzle."""
        return self.x < -5 or self.x > 5 or self.y < -5 or self.y > 5 or self.z < -5 or self.z > 5

    def __str__(self) -> str:
        """Return a string representation of the voxel."""
        return f"({self.x},{self.y},{self.z})"
