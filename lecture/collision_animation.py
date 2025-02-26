import json
import os

import scenepic as sp

from burrsolver.position import Direction
from burrsolver.puzzle import Puzzle
from burrsolver.visualization import COLORS, cross_mesh, voxels_to_mesh


def main(width=1440, height=1080, frames_per_step=25):
    path = os.path.join(os.path.dirname(__file__), "..", "puzzles.json")
    with open(path) as f:
        puzzle_info = json.load(f)

    puzzle = Puzzle.from_text(puzzle_info["puzzles"][5]["shapes"])

    a = puzzle.pieces_at(1, "F")[0]
    b = puzzle.pieces_at(4, "C")[0]

    scene = sp.Scene()

    cross = cross_mesh(scene)

    canvas: sp.Canvas3D = scene.create_canvas_3d(width=width, height=height)
    canvas.shading = sp.Shading(sp.Colors.White)

    canvas.camera = sp.Camera([15, 10, 20], aspect_ratio=width / height,
                              near_crop_distance=.1, far_crop_distance=100)

    a = a.move(Direction.DOWN, 5)

    meshes = []

    for i in range(8):
        a_voxels = set(puzzle.voxels_for(a))
        b_voxels = set(puzzle.voxels_for(b))
        collision = a_voxels.intersection(b_voxels)
        a_voxels -= collision
        b_voxels -= collision

        a_mesh = voxels_to_mesh(scene, a_voxels, f"a{i}", COLORS[a.shape])
        b_mesh = voxels_to_mesh(scene, b_voxels, f"b{i}", COLORS[b.shape])

        if collision:
            collision_mesh = voxels_to_mesh(scene, collision, f"collision{i}", sp.Colors.Red)
            meshes.append((a_mesh, b_mesh, collision_mesh))
        else:
            meshes.append((a_mesh, b_mesh))

        a = a.move(Direction.UP, 1)

    meshes = meshes + meshes[::-1]
    for frame_meshes in meshes:
        for _ in range(frames_per_step):
            frame: sp.Frame3D = canvas.create_frame(meshes=frame_meshes)
            frame.add_mesh(cross)

    scene.save_as_html("collision_animation.html")


if __name__ == "__main__":
    main()
