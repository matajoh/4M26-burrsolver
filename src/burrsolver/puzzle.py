"""A six-piece burr puzzle."""

from itertools import combinations
from typing import FrozenSet, List, NamedTuple, Tuple

from .piece import Piece
from .position import Direction, PLACES, Position
from .shape import Shape
from .voxel import Voxel


class PuzzleState(NamedTuple("PuzzleState", [("pieces", Tuple[Piece])])):
    """The state of the puzzle."""

    def add(self, piece: Piece) -> "PuzzleState":
        """Add a piece to the puzzle state."""
        return PuzzleState(self.pieces + (piece,))

    def __str__(self) -> str:
        """Return a string representation of the puzzle state."""
        return " ".join([str(p) for p in self.pieces])

    @staticmethod
    def from_string(text: str) -> "PuzzleState":
        """Create a puzzle state from a string representation."""
        parts = text.split(" ")
        pieces = []

        for part in parts:
            if part[0] in PLACES:
                place = PLACES[part[0]]
                start = 1
            else:
                length = part.find(")")
                place = Position.from_string(part[1:length])
                start = length + 1

            s = int(part[start]) - 1
            n = ord(part[start + 1]) - 97
            piece = Piece(s, place, n)
            pieces.append(piece)

        return PuzzleState(tuple(pieces))


class Move(NamedTuple("Move", [("pieces", FrozenSet[Piece]),
                               ("direction", Direction),
                               ("steps", int)])):
    """A move in the puzzle."""

    def __repr__(self) -> str:
        """Return a string representation of the move."""
        pieces = " ".join(sorted(str(p) for p in self.pieces))
        return f"{self.direction.name} {self.steps} [{pieces}]"


class Puzzle(NamedTuple("Puzzle", [("shapes", Tuple[Shape]),
                                   ("pieces", Tuple[Piece])])):
    """A six-piece burr puzzle."""

    @staticmethod
    def from_text(lines: List[str]) -> "Puzzle":
        """Create a puzzle from a list of shape strings."""
        shapes = []
        for line in lines:
            shapes.append(Shape.from_text(line))

        return Puzzle(tuple(shapes), [])

    def order_by_size(self) -> List[int]:
        """Order the shapes by size."""
        return sorted(range(len(self.shapes)),
                      key=lambda s: -len(self.shapes[s].voxels))

    def order_by_orientations(self) -> List[int]:
        """Order the shapes by the number of valid orientations."""
        return sorted(range(len(self.shapes)),
                      key=lambda s: len(self.shapes[s].orientations["A"]))

    def pieces_at(self, s: int, place: str) -> List[Piece]:
        """Return all valid piece states for a shape at a named location."""
        return [(Piece(s, PLACES[place], o))
                for o in self.shapes[s].orientations[place]]

    def state(self) -> PuzzleState:
        """Return the current state of the puzzle."""
        return PuzzleState(self.pieces)

    def to_state(self, state: PuzzleState) -> "Puzzle":
        """Return a new puzzle with the given state."""
        return Puzzle(self.shapes, state.pieces)

    def do_move(self, move: Move) -> "Puzzle":
        """Move the pieces in the puzzle."""
        new_pieces = []

        for piece in self.pieces:
            if piece in move.pieces:
                new_piece = piece.move(move.direction, move.steps)
                new_shape = self.shapes[piece.shape].move_to(new_piece)
                if new_shape.inside_count() > 0:
                    new_pieces.append(new_piece)
            else:
                new_pieces.append(piece)

        return Puzzle(self.shapes, tuple(new_pieces))

    def voxels_for(self, piece: Piece) -> List[Voxel]:
        """Return the voxels for a piece."""
        return self.shapes[piece.shape].move_to(piece).voxels

    def level(self) -> int:
        """Return the level of the puzzle.

        The level of a burr puzzle is indicated by the number of
        "voids" in the puzzle, that is, empty spaces in the hidden
        center. The level is 1 + the number of voids.
        """
        num_voxels = sum([len(s.voxels) for s in self.shapes])
        return 105 - num_voxels

    def valid_moves(self):
        """Return all valid moves for the puzzle."""
        sizes = [1]
        if len(self.pieces) > 3:
            sizes.append(2)
        if len(self.pieces) == 6:
            sizes.append(3)

        piece_voxels = {p: self.voxels_for(p) for p in self.pieces}
        voxels = frozenset(sum(piece_voxels.values(), tuple()))

        for size in sizes:
            for subset in combinations(self.pieces, size):
                # Find all voxels not occupied by the subset
                subset_voxels: Tuple[Voxel, ...] = sum(
                    [piece_voxels[p] for p in subset], tuple())

                # Remove them from the set of all voxels
                old_voxels = voxels.difference(subset_voxels)

                for d in Direction:
                    # Try moving the subset in the given direction
                    can_move = True
                    is_outside = False
                    steps = 0
                    while can_move:
                        any_inside = False
                        for v in subset_voxels:
                            vv = v.move(d, steps + 1)
                            if vv in old_voxels:
                                can_move = False
                                break

                            if not any_inside:
                                any_inside = vv.is_inside()

                        if can_move:
                            steps += 1
                            if not any_inside:
                                is_outside = True
                                break

                    if steps:
                        if not is_outside:
                            # If the pieces are still in the puzzle we have
                            # to go by a single step
                            steps = 1

                        yield Move(frozenset(subset), d, steps)

    def __str__(self) -> str:
        """Return a string representation of the puzzle."""
        return str(self.state())
