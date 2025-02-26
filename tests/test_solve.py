import os
import json

import pytest

from burrsolver.puzzle import Puzzle
from burrsolver.solver import solve

PUZZLES_PATH = os.path.join(os.path.dirname(__file__), "..", "puzzles.json")
with open(PUZZLES_PATH) as f:
    PUZZLES = json.load(f)["puzzles"]


@pytest.mark.parametrize("puzzle_info", PUZZLES)
def test_solve(puzzle_info):
    puzzle = Puzzle.from_text(puzzle_info["shapes"])
    solution = solve(puzzle)
    assert solution
    assembly = str(solution.assembly)
    assert assembly in puzzle_info["assemblies"]
    actual_disassembly = [str(move[1]) for move in solution.moves]
    expected_disassembly = puzzle_info["assemblies"][assembly]
    for actual, expected in zip(actual_disassembly, expected_disassembly):
        assert actual == expected
