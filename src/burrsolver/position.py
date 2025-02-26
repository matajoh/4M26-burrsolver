"""Position and direction classes for the burr puzzle."""

from enum import Enum, IntEnum
from typing import NamedTuple


SIZE = 2


class Direction(IntEnum):
    """Directions for moving pieces."""
    FORWARD = 0
    BACKWARD = 1
    UP = 2
    DOWN = 3
    LEFT = 4
    RIGHT = 5


class Axis(Enum):
    """Axis for piece alignment."""
    X = "X"
    Y = "Y"
    Z = "Z"


class Position(NamedTuple("Position", [("x", int), ("y", int), ("z", int),
                                       ("axis", Axis)])):
    """Position of a piece in the puzzle."""

    def move(self, d: Direction, steps: int) -> "Position":
        """Move the position in the given direction.

        Args:
            d: The direction to move the piece.
            steps: The number of steps to move the piece.

        Returns:
            The new position of the piece after moving.
        """
        match d:
            case Direction.UP:
                return self.up(steps)
            case Direction.DOWN:
                return self.down(steps)
            case Direction.LEFT:
                return self.left(steps)
            case Direction.RIGHT:
                return self.right(steps)
            case Direction.FORWARD:
                return self.forward(steps)
            case Direction.BACKWARD:
                return self.back(steps)
            case _:
                raise ValueError("Invalid direction")

    def up(self, steps: int) -> "Position":
        """Move the position up by the given number of steps."""
        return Position(self.x, self.y + steps * SIZE, self.z, self.axis)

    def down(self, steps: int) -> "Position":
        """Move the position down by the given number of steps."""
        return Position(self.x, self.y - steps * SIZE, self.z, self.axis)

    def left(self, steps: int) -> "Position":
        """Move the position left by the given number of steps."""
        return Position(self.x - steps * SIZE, self.y, self.z, self.axis)

    def right(self, steps: int) -> "Position":
        """Move the position right by the given number of steps."""
        return Position(self.x + steps * SIZE, self.y, self.z, self.axis)

    def forward(self, steps: int) -> "Position":
        """Move the position forward by the given number of steps."""
        return Position(self.x, self.y, self.z + steps * SIZE, self.axis)

    def back(self, steps: int) -> "Position":
        """Move the position back by the given number of steps."""
        return Position(self.x, self.y, self.z - steps * SIZE, self.axis)

    def __str__(self) -> str:
        """Return a string representation of the position."""
        return f"({self.x},{self.y},{self.z},{self.axis.value})"

    @staticmethod
    def from_string(value: str) -> "Position":
        """Create a position from a string representation."""
        parts = value.split(",")
        x = int(parts[0])
        y = int(parts[1])
        z = int(parts[2])
        axis = Axis(parts[3])
        return Position(x, y, z, axis)


"""Named locations in the puzzle."""
PLACES = {
    "A": Position(0, -2, 0, Axis.Z),
    "B": Position(0, 0, -2, Axis.X),
    "C": Position(-2, 0, 0, Axis.Y),
    "D": Position(0, 0, 2, Axis.X),
    "E": Position(2, 0, 0, Axis.Y),
    "F": Position(0, 2, 0, Axis.Z),
}
