"""Solver for the Burr puzzle."""

import heapq
from typing import FrozenSet, List, NamedTuple, Tuple


from .astar import astar
from .piece import Piece
from .puzzle import Move, Puzzle, PuzzleState


def disassemble(puzzle: Puzzle) -> List[Tuple[PuzzleState, Move]]:
    start = puzzle.state()

    def distance(a: PuzzleState, b: PuzzleState) -> int:
        # Each puzzle state is separated by one move
        return 1

    def heuristic(a: PuzzleState) -> int:
        # This heuristic is accurate once the piece count is below 4,
        # but can be incorrect in early stages of a puzzle when pieces
        # may need to mov in groups. This is why the value is capped.
        return max(len(a.pieces), 4)

    def neighbors(a: PuzzleState):
        # Generate all possible moves from the current state
        puzzle_a = puzzle.to_state(a)
        for move in puzzle_a.valid_moves():
            yield move, puzzle_a.do_move(move).state()

    def is_goal(a: PuzzleState) -> bool:
        # The goal is to have no pieces left in the puzzle
        return len(a.pieces) == 0

    return astar(distance, heuristic, neighbors, is_goal, start)


Solution = NamedTuple("Solution", [("assembly", PuzzleState),
                                   ("moves", List[Tuple[PuzzleState, Move]]),
                                   ("num_iterations", int),
                                   ("num_checked", int)])


class AssemblyState(NamedTuple("AssemblyState",
                               [("puzzle", PuzzleState),
                                ("shapes", FrozenSet[int]),
                                ("places", FrozenSet[str])])):
    def add(self, place: str, piece: Piece) -> "AssemblyState":
        return AssemblyState(self.puzzle.add(piece),
                             self.shapes - set([piece.shape]),
                             self.places - set([place]))

    @property
    def num_remaining(self):
        return len(self.places)

    def remaining(self):
        for shape in self.shapes:
            for place in self.places:
                yield shape, place


def try_pieces(puzzle: Puzzle,
               state: AssemblyState,
               frontier: List[AssemblyState]):
    """Try to add pieces to the assembly."""
    voxels = frozenset(sum([puzzle.voxels_for(p)
                            for p in state.puzzle.pieces], tuple()))
    for shape, place in state.remaining():
        for piece in puzzle.pieces_at(shape, place):
            if voxels.isdisjoint(puzzle.voxels_for(piece)):
                new_state = state.add(place, piece)
                heapq.heappush(frontier, (new_state.num_remaining,
                                          new_state))


def solve(puzzle: Puzzle) -> Solution:
    """Solve the puzzle.

    The solver searches the space of potential assemblies. Once a
    valid assembly is found, the solver uses A* search to find the
    optimal disassembly. If there is no disassembly, the solver
    continues searching for a solution.
    """
    shapes = frozenset(range(6))
    places = frozenset(["A", "B", "C", "D", "E", "F"])
    start = AssemblyState(PuzzleState(()), shapes, places)
    frontier: List[Tuple[int, AssemblyState]] = []

    for s in shapes:
        if len(puzzle.shapes[s].orientations["A"]) > 2:
            continue

        state = start.add("A", puzzle.pieces_at(s, "A")[0])
        heapq.heappush(frontier, (state.num_remaining, state))

    num_checked = 0
    num_iterations = 0
    while frontier:
        num_iterations += 1
        _, state = heapq.heappop(frontier)
        if state.num_remaining == 0:
            # Found a valid assembly, now try to disassemble
            num_checked += 1
            puzzle = puzzle.to_state(state.puzzle)
            moves = disassemble(puzzle)
            if moves:
                return Solution(moves[0][0], moves, num_iterations, num_checked)

            continue

        try_pieces(puzzle, state, frontier)

    raise ValueError("No valid assembly found")
