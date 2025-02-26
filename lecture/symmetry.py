import json
import os
import numpy as np
import scenepic as sp
from scipy.spatial.transform import Rotation, Slerp

from burrsolver.puzzle import Puzzle, PuzzleState
from burrsolver.visualization import COLORS, voxels_to_mesh


def main(width=1440, height=1080, num_frames=90, freeze_frames=15):
    path = os.path.join(os.path.dirname(__file__), "..", "puzzles.json")
    with open(path) as f:
        puzzle_info = json.load(f)["puzzles"]

    puzzle = Puzzle.from_text(puzzle_info[1]["shapes"])
    assembly = list(puzzle_info[1]["assemblies"].keys())[0]
    puzzle = puzzle.to_state(PuzzleState.from_string(assembly))

    scene = sp.Scene()

    meshes = [voxels_to_mesh(scene, shape.voxels, str(s), COLORS[s], merge_mesh=True)
              for s, shape in enumerate(puzzle.shapes)]

    rot_x = Rotation.from_rotvec([np.pi / 2, 0, 0])
    rot_x2 = Rotation.from_rotvec([np.pi, 0, 0])
    rot_x3 = Rotation.from_rotvec([-np.pi / 2, 0, 0])
    rot_y = Rotation.from_rotvec([0, np.pi / 2, 0])
    rot_y3 = Rotation.from_rotvec([0, 3 * np.pi / 2, 0])
    rot_z = Rotation.from_rotvec([0, 0, np.pi / 2])
    quat = Rotation.identity()
    key_rots = [
        quat,
        rot_z * quat,
        rot_x,
        rot_y * rot_x,
        rot_x2,
        rot_z * rot_x2,
        rot_x3,
        rot_y * rot_x3,
        rot_y,
        rot_x3 * rot_y,
        rot_y3,
        rot_x * rot_y3,
        quat
    ]
    key_rots = Rotation.concatenate(key_rots)

    slerp = Slerp(np.arange(len(key_rots)), key_rots)

    # idea: animate rotation and layer settings
    def get_settings(opacity):
        return {
            "1": {"opacity": opacity},
            "2": {"opacity": opacity},
            "3": {"opacity": opacity},
            "4": {"opacity": opacity},
            "5": {"opacity": opacity},
        }

    camera = sp.Camera([15, 7, 20], near_crop_distance=0.1, far_crop_distance=100, aspect_ratio=width / height)
    canvas = scene.create_canvas_3d(width=width, height=height, camera=camera)
    canvas.shading = sp.Shading(bg_color=sp.Colors.White)
    canvas.set_layer_settings(get_settings(0))
    for i in range(len(key_rots) - 1):
        transform = sp.Transforms.quaternion_to_matrix(key_rots[i].as_quat())
        for j in range(freeze_frames):
            frame = canvas.create_frame()
            for p in puzzle.pieces:
                mesh = meshes[p.shape]
                frame.add_mesh(mesh, transform @ p.to_transform())
                frame.set_layer_settings(get_settings(0))

        interp = np.linspace(i, i + 1, num_frames)
        rots = slerp(interp)
        for j, r in enumerate(rots):
            q = r.as_quat()
            transform = sp.Transforms.quaternion_to_matrix(q)
            frame = canvas.create_frame()
            frame.set_layer_settings(get_settings(1))
            for p in puzzle.pieces:
                mesh = meshes[p.shape]
                frame.add_mesh(mesh, transform @ p.to_transform())

    scene.save_as_html("symmetry.html")


if __name__ == "__main__":
    main()
