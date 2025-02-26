import json
import math
import os

import numpy as np
import scenepic as sp

from burrsolver.puzzle import Puzzle


def main(width=1440, height=1080, num_frames=120, freeze_frames=240, max_scale=math.sqrt(2)):
    path = os.path.join(os.path.dirname(__file__), "..", "puzzles.json")
    with open(path) as f:
        puzzle_info = json.load(f)

    puzzle = Puzzle.from_text(puzzle_info["puzzles"][5]["shapes"])
    voxels = puzzle.shapes[5].voxels

    scene = sp.Scene()

    positions = np.stack([v for v in voxels])
    positions = positions.astype(np.float32) * 0.5
    rotate_around_y = sp.Transforms.rotation_about_y(math.pi / 2)[:3, :3]
    positions = positions @ rotate_around_y.T

    mesh = scene.create_mesh()
    mesh.add_cube(sp.Colors.Magenta, add_wireframe=True)
    mesh.enable_instancing(positions)

    canvas: sp.Canvas3D = scene.create_canvas_3d(width=width, height=height)
    canvas.shading = sp.Shading(sp.Colors.White)

    cameras = sp.Camera.orbit(num_frames + freeze_frames + num_frames, 10, 2, 0, 1,
                              [0, 1, 0], [0, 0, 1],
                              60, width / height, .1, 100)

    scale_up = np.linspace(1, max_scale, num_frames)
    scale_down = np.linspace(max_scale, 1, num_frames)

    for i in range(num_frames):
        frame = canvas.create_frame(camera=cameras[i])
        mesh_update = scene.update_instanced_mesh(mesh.mesh_id, positions * scale_up[i])
        frame.add_mesh(mesh_update)

    voxel_labels = []
    for v in voxels:
        label = scene.create_label(text=str(v), color=sp.Colors.Black, size_in_pixels=64, horizontal_align="center")
        pos = np.array(v, np.float32) * 0.5
        pos[1] += 0.5
        pos = pos @ rotate_around_y.T
        voxel_labels.append((pos, label))

    mesh_update = scene.update_instanced_mesh(mesh.mesh_id, positions * max_scale)
    for i in range(freeze_frames):
        frame = canvas.create_frame(camera=cameras[i + num_frames])
        frame.add_mesh(mesh_update)
        for pos, label in voxel_labels:
            frame.add_label(label, pos * max_scale)

    for i in range(num_frames):
        frame = canvas.create_frame(camera=cameras[i + num_frames + freeze_frames])
        mesh_update = scene.update_instanced_mesh(mesh.mesh_id, positions * scale_down[i])
        frame.add_mesh(mesh_update)

    scene.save_as_html("voxel_animation.html")


if __name__ == "__main__":
    main()
