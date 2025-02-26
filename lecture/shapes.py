import json
import os

import matplotlib.pyplot as plt
import scenepic as sp

from burrsolver.piece import Piece
from burrsolver.position import PLACES, Direction
from burrsolver.puzzle import Puzzle
from burrsolver.visualization import COLORS, voxels_to_mesh


def shapes(width=800, height=800):
    path = os.path.join(os.path.dirname(__file__), "..", "puzzles.json")
    with open(path) as f:
        puzzle_info = json.load(f)

    puzzle = Puzzle.from_text(puzzle_info["puzzles"][3]["shapes"])
    scene = sp.Scene()
    meshes = [voxels_to_mesh(scene, shape.voxels, str(s), COLORS[s])
              for s, shape in enumerate(puzzle.shapes)]
    camera = sp.Camera([10, 7, 12], aspect_ratio=width / height,
                       near_crop_distance=.1, far_crop_distance=100)

    for mesh in meshes:
        canvas: sp.Canvas3D = scene.create_canvas_3d(width=width, height=height)
        canvas.shading = sp.Shading(sp.Colors.White)
        canvas.camera = camera
        frame: sp.Frame3D = canvas.create_frame()
        frame.add_mesh(mesh, sp.Transforms.translate([1, 1, 0]))

    scene.save_as_html("shapes.html")


def orientations(width=800, height=800, shape_id=2):
    path = os.path.join(os.path.dirname(__file__), "..", "puzzles.json")
    with open(path) as f:
        puzzle_info = json.load(f)

    puzzle = Puzzle.from_text(puzzle_info["puzzles"][3]["shapes"])

    scene = sp.Scene()

    mesh = voxels_to_mesh(scene, puzzle.shapes[shape_id].voxels, str(shape_id), COLORS[shape_id])

    camera = sp.Camera([10, 7, 12], aspect_ratio=width / height,
                       near_crop_distance=.1, far_crop_distance=100)
    for o in range(8):
        piece = Piece(shape_id, PLACES["A"], o).move(Direction.RIGHT, 1).move(Direction.UP, 2)
        canvas: sp.Canvas3D = scene.create_canvas_3d(width=width, height=height)
        canvas.shading = sp.Shading(sp.Colors.White)
        canvas.camera = camera
        frame: sp.Frame3D = canvas.create_frame()
        frame.add_mesh(mesh, piece.to_transform())

    scene.save_as_html("orientations.html")


def create_figures(portrait=False, dpi=75):
    if portrait:
        fig = plt.figure(figsize=(4, 6))
    else:
        fig = plt.figure(figsize=(6, 4))

    for i in range(6):
        if portrait:
            ax = fig.add_subplot(3, 2, i + 1)
        else:
            ax = fig.add_subplot(2, 3, i + 1)

        image = plt.imread(os.path.join("shapes", f"Canvas-{i}", "frame_0000.png"))
        ax.imshow(image)
        ax.axis("off")
        ax.set_title(f"{i}")

    fig.tight_layout()
    fig.savefig("shapes.png", dpi=dpi)

    if portrait:
        fig = plt.figure(figsize=(4, 8))
    else:
        fig = plt.figure(figsize=(8, 4))

    for i, o in enumerate([0, 4, 1, 5, 2, 6, 3, 7]):
        if portrait:
            ax = fig.add_subplot(4, 2, i + 1)
        else:
            ax = fig.add_subplot(2, 4, i + 1)

        image = plt.imread(os.path.join("orientations", f"Canvas-{o}", "frame_0000.png"))
        ax.imshow(image)
        ax.axis("off")
        ax.set_title(f"{o}")

    fig.tight_layout()
    fig.savefig("orientations.png", dpi=dpi)


if __name__ == "__main__":
    shapes()
    orientations()
    create_figures()
