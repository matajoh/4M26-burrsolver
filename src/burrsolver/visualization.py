"""Solution visualization code.

NB: Nothing in this module is in scope for the Tripos. Students do not
need to understand how this works, but may find it interesting as an
example of how to use ScenePic.
"""

from typing import List, Tuple

import numpy as np
import scenepic as sp


from .geometry import Mesh
from .puzzle import Puzzle, PuzzleState, Move
from .voxel import Voxel


"""Colors for each piece."""
COLORS = [sp.Colors.Red, sp.Colors.Green, sp.Colors.Blue,
          sp.Colors.Yellow, sp.Colors.Cyan, sp.Colors.Magenta]


def voxels_to_mesh(scene: sp.Scene, voxels: List[Voxel],
                   name="voxels", color=sp.Colors.White,
                   fill_triangles=True, add_wireframe=False,
                   merge_mesh=False) -> sp.Mesh:
    """Create a mesh from a list of voxels.

    Args:
        scene: The scene to add the mesh to.
        voxels: The list of voxels to create a mesh from.
        name: The name of the mesh (and its layer)
        color: The color of the mesh.

    Returns:
        The mesh created from the list of voxels.
    """
    mesh = scene.create_mesh(name, layer_id=name, shared_color=color)
    mesh_info = Mesh.from_voxels(voxels, merge_mesh)
    triangles = np.zeros((mesh_info.quads.shape[0] * 2, 3), dtype=np.int32)
    triangles[0::2] = mesh_info.quads[:, 0:3]
    triangles[1::2, :2] = mesh_info.quads[:, 2:]
    triangles[1::2, 2] = mesh_info.quads[:, 0]
    mesh.add_mesh_with_normals(mesh_info.vertices, mesh_info.normals, triangles,
                               fill_triangles=fill_triangles, add_wireframe=add_wireframe)
    return mesh


def cross_mesh(scene: sp.Scene):
    cross = scene.create_mesh("cross", layer_id="wireframe")
    cross.add_cube(transform=sp.Transforms.scale(
        [12, 4, 8]), add_wireframe=True, fill_triangles=False,
        color=sp.Colors.Red)
    cross.add_cube(transform=sp.Transforms.scale(
        [8, 12, 4]), add_wireframe=True, fill_triangles=False,
        color=sp.Colors.Green)
    cross.add_cube(transform=sp.Transforms.scale(
        [4, 8, 12]), add_wireframe=True, fill_triangles=False,
        color=sp.Colors.Blue)
    cross.add_coordinate_axes()
    return cross


def save_scenepic(path: str, puzzle: Puzzle,
                  disassembly: List[Tuple[PuzzleState, Move]], width: int, height: int):
    """Save the solution as a ScenePic HTML file."""
    piece_size = width // 6
    scene = sp.Scene()
    camera = sp.Camera([16, 4, 6], [0, 0, 0], [0, 1, 0], 60)
    shading = sp.Shading(bg_color=sp.Colors.White)
    meshes = [voxels_to_mesh(scene, shape.voxels, str(s), COLORS[s])
              for s, shape in enumerate(puzzle.shapes)]
    for i, mesh in enumerate(meshes):
        canvas = scene.create_canvas_3d("shape{}".format(i), width=piece_size,
                                        height=piece_size, camera=camera, shading=shading)
        frame = canvas.create_frame()
        frame.add_mesh(mesh)

    cross = cross_mesh(scene)
    camera.aspect_ratio = width / height
    canvas = scene.create_canvas_3d("solution", width=width, height=height,
                                    camera=camera, shading=shading)
    frames_per_step = 5
    num_frames = sum([move.steps
                      for _, move in disassembly[:-1]]) * frames_per_step
    freeze_frames = 60
    cameras = sp.Camera.orbit(num_frames + freeze_frames + num_frames, 20, 1, 0, 1,
                              [0, 1, 0], [0, 0, 1],
                              60, width / height, .1, 100)
    f = 0
    for state, move in reversed(disassembly[:-1]):
        puzzle = puzzle.to_state(state)
        move_steps = move.steps * frames_per_step
        for steps in range(move_steps, 0, -1):
            temp = puzzle.do_move(Move(move.pieces, move.direction, steps / frames_per_step))
            frame: sp.Frame3D = canvas.create_frame(camera=cameras[f])
            f += 1
            frame.add_mesh(cross)
            for piece in temp.pieces:
                mesh = meshes[piece.shape]
                transform = piece.to_transform()
                frame.add_mesh(mesh, transform)

    assembled = puzzle.to_state(disassembly[0][0])
    for _ in range(freeze_frames):
        frame = canvas.create_frame(camera=cameras[f])
        frame.add_mesh(cross)
        f += 1
        for piece in assembled.pieces:
            mesh = meshes[piece.shape]
            transform = piece.to_transform()
            frame.add_mesh(mesh, transform)

    for state, move in disassembly[:-1]:
        puzzle = puzzle.to_state(state)
        move_steps = move.steps * frames_per_step
        for steps in range(0, move_steps):
            temp = puzzle.do_move(Move(move.pieces, move.direction, steps / frames_per_step))
            frame: sp.Frame3D = canvas.create_frame(camera=cameras[f])
            f += 1
            frame.add_mesh(cross)
            for piece in temp.pieces:
                mesh = meshes[piece.shape]
                transform = piece.to_transform()
                frame.add_mesh(mesh, transform)

    scene.grid(width=f"{width}px", grid_template_rows=f"{piece_size}px {height}px",
               grid_template_columns=f"repeat(6, {piece_size}px)")

    for i in range(6):
        scene.place("shape{}".format(i), "1", str(i + 1))

    scene.place("solution", "2", "1 / span 6")
    scene.save_as_html(path)
