"""The Burr Solver Tool.

These files, in addition with the README, act as lecture notes and a
revision aid for the Tripos. Some files are not in scope for the Tripos
and will be marked as such in the module comments. Other files will have
commented methods or functions which correspond to those discussed in
lecture, and students should understand those thoroughly.

As a general note, anything to do with visualization is not in scope for the
Tripos. This includes the `visualization` module and any code for producing
meshes (e.g. for STL files).
"""

import argparse
import json


from .puzzle import Puzzle
from .solver import solve
from .visualization import save_scenepic


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--puzzle", "-p", type=int,
                        default=0, help="Puzzle number to solve")
    parser.add_argument("--stl", "-s", action="store_true",
                        help="Write out shapes as STL files")
    parser.add_argument("--sp-width", type=int, default=900,
                        help="Width of the ScenePic solution")
    parser.add_argument("--sp-height", type=int, default=600,
                        help="Height of the ScenePic solution")
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    with open("puzzles.json") as f:
        data = json.load(f)
        print("Solving puzzle", args.puzzle)
        print("Shapes:")
        shapes = data["puzzles"][args.puzzle]["shapes"]
        for line in shapes:
            print(line)

        print()
        puzzle = Puzzle.from_text(shapes)
        if args.stl:
            for i, shape in enumerate(puzzle.shapes):
                shape.save_as_stl(f"puzzle{args.puzzle}_shape{i}.stl")

    if puzzle.level() > 1:
        print("Puzzle is level", puzzle.level(), "(Higher levels can result in longer solve times)")

    solution = solve(puzzle)

    if solution is None:
        print("No solution found")
        return

    print("Valid assembly", solution.assembly, "found after checking", solution.num_checked,
          "assemblies" if solution.num_checked > 1 else "assembly", "over", solution.num_iterations,
          "iterations")
    print("Disassembly takes", len(solution.moves) - 1, "steps:")
    for i, step in enumerate(solution.moves[:-1]):
        print(f"{i}:", step[1])
    path = "solution{}.html".format(args.puzzle)
    save_scenepic(path, puzzle, solution.moves, args.sp_width, args.sp_height)
    print("View solution: ./solution{}.html".format(args.puzzle))
