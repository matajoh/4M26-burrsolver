"""Geometry classes.

NB: Nothing in this module is in scope for the Tripos. Students do not
need to understand how this works, but may find it interesting.
"""

from typing import List, Mapping, NamedTuple, Tuple

import numpy as np

from .position import SIZE
from .voxel import Voxel


class Vec3(NamedTuple("Vec3", [("x", int), ("y", int), ("z", int)])):
    """Simple class representing a 3D vector."""

    def __add__(self, other: "Vec3") -> "Vec3":
        """Adds two vectors together."""
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        """Subtracts two vectors."""
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def cross(self, other: "Vec3") -> "Vec3":
        """Cross product of two vectors."""
        return Vec3(self.y * other.z - self.z * other.y,
                    self.z * other.x - self.x * other.z,
                    self.x * other.y - self.y * other.x)

    def dot(self, other: "Vec3") -> int:
        """Dot product of two vectors."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __lt__(self, other: "Vec3") -> "Vec3":
        """Tests whether one vector is less than another."""
        if self.x < other.x:
            return True

        if self.x == other.x:
            if self.y < other.y:
                return True

            if self.y == other.y:
                if self.z < other.z:
                    return True

        return False

    def scale(self, scale: int) -> "Vec3":
        """Casts all values to ints."""
        return Vec3(self.x * scale, self.y * scale, self.z * scale)

    @staticmethod
    def from_array(v: np.ndarray) -> "Vec3":
        """Creates a Vec3 from a numpy array."""
        return Vec3(int(v[0]), int(v[1]), int(v[2]))


class Facet(NamedTuple("Facet", [("normal", Vec3), ("loop", Tuple[Vec3, Vec3, Vec3])])):
    """A facet (triangle) in an STL mesh."""

    def write(self, file) -> str:
        """Write the facet to an STL file."""
        file.write(f"facet normal {self.normal.x} {self.normal.y} {self.normal.z}\n")
        file.write("  outer loop\n")
        for v in self.loop:
            file.write(f"    vertex {v.x} {v.y} {v.z}\n")
        file.write("  endloop\n")
        file.write("endfacet\n")


Quad = NamedTuple("Quad", [("normal", Vec3), ("loop", Tuple[Vec3, Vec3, Vec3, Vec3])])


def remove_duplicate_quads(quads: List[Quad]) -> List[Quad]:
    dedup = {}
    for quad in quads:
        key = tuple(sorted(quad.loop))
        if key in dedup:
            del dedup[key]
        else:
            dedup[key] = quad

    return list(dedup.values())


def merge_quads(quads: List[Quad]) -> List[Quad]:
    quads_by_vertex: Mapping[Tuple[Vec3, Vec3], List[Quad]] = {}
    for quad in quads:
        for v in quad.loop:
            key = v, quad.normal
            if key not in quads_by_vertex:
                quads_by_vertex[key] = []

            quads_by_vertex[key].append(quad)

    keys_by_degree = sorted(quads_by_vertex.keys(), key=lambda k: len(quads_by_vertex[k]), reverse=True)
    merged = set()
    new_quads = []
    for key in keys_by_degree:
        quads_to_merge = quads_by_vertex[key]
        if len(quads_to_merge) == 1:
            break

        do_merge = True
        for quad in quads_to_merge:
            if quad in merged:
                do_merge = False
                break

        if not do_merge:
            continue

        normal = quads_to_merge[0].normal
        vert_counts = {}
        for quad in quads_to_merge:
            for v in quad.loop:
                if v not in vert_counts:
                    vert_counts[v] = 0
                vert_counts[v] += 1
        loop = [v for v in vert_counts if vert_counts[v] == 1]
        if len(loop) != 4:
            continue

        for quad in quads_to_merge:
            merged.add(quad)

        ab = loop[1] - loop[0]
        ac = loop[2] - loop[0]
        bd = loop[3] - loop[1]
        if ac == bd:
            loop = [loop[0], loop[1], loop[3], loop[2]]
            ac = loop[2] - loop[0]

        if ab.cross(ac).dot(normal) <= 0:
            loop.reverse()
            ab = loop[1] - loop[0]
            ac = loop[2] - loop[0]
            assert ab.cross(ac).dot(normal) > 0

        new_quads.append(Quad(normal, tuple(loop)))

    for quad in quads:
        if quad not in merged:
            new_quads.append(quad)

    return new_quads


class Mesh(NamedTuple("Mesh", [("vertices", np.ndarray), ("normals", np.ndarray), ("quads", np.ndarray)])):
    @staticmethod
    def from_voxels(voxels: List[Voxel], merge_mesh=False) -> "Mesh":
        s = SIZE // 2
        cube_vertices = [
            Vec3(-s, -s, -s),
            Vec3(-s, s, -s),
            Vec3(s, s, -s),
            Vec3(s, -s, -s),
            Vec3(-s, -s, s),
            Vec3(-s, s, s),
            Vec3(s, s, s),
            Vec3(s, -s, s)
        ]
        cube_normals = [
            Vec3(0, 0, -1),
            Vec3(0, 0, 1),
            Vec3(0, -1, 0),
            Vec3(0, 1, 0),
            Vec3(-1, 0, 0),
            Vec3(1, 0, 0)
        ]
        cube_quads = [
            (0, 1, 2, 3),
            (7, 6, 5, 4),
            (4, 0, 3, 7),
            (2, 1, 5, 6),
            (4, 5, 1, 0),
            (2, 6, 7, 3)
        ]

        faces = []
        for v in voxels:
            center = Vec3(v.x, v.y, v.z)
            for normal, (a, b, c, d) in zip(cube_normals, cube_quads):
                loop = (cube_vertices[a] + center,
                        cube_vertices[b] + center,
                        cube_vertices[c] + center,
                        cube_vertices[d] + center)
                faces.append(Quad(normal, loop))

        if merge_mesh:
            faces = remove_duplicate_quads(faces)
            merged_faces = merge_quads(faces)
            while len(merged_faces) < len(faces):
                faces = merged_faces
                merged_faces = merge_quads(faces)

        # assemble vertices, normals, and faces

        # cycle through facets
        vertex_indices: Mapping[Tuple[Vec3, Vec3], int] = {}
        quads = []
        for quad in faces:
            for v in quad.loop:
                key = v, quad.normal
                if key not in vertex_indices:
                    vertex_indices[key] = len(vertex_indices)

            a = vertex_indices[(quad.loop[0], quad.normal)]
            b = vertex_indices[(quad.loop[1], quad.normal)]
            c = vertex_indices[(quad.loop[2], quad.normal)]
            d = vertex_indices[(quad.loop[3], quad.normal)]
            quads.append([a, b, c, d])

        vertices = np.zeros((len(vertex_indices), 3), dtype=np.float32)
        normals = np.zeros((len(vertex_indices), 3), dtype=np.float32)
        for (v, n), i in vertex_indices.items():
            vertices[i] = v
            normals[i] = n

        quads = np.array(quads, dtype=np.int32)

        for a, b, c, d in quads:
            v0 = vertices[a]
            v1 = vertices[b]
            v2 = vertices[c]
            v3 = vertices[d]
            n0 = normals[a]
            n1 = normals[b]
            n2 = normals[c]
            n3 = normals[d]
            assert np.allclose(n0, n1)
            assert np.allclose(n1, n2)
            assert np.allclose(n2, n3)
            assert np.dot(np.cross(v1 - v0, v2 - v0), n0) > 0
            assert np.dot(np.cross(v3 - v2, v0 - v2), n0) > 0

        return Mesh(vertices, normals, quads)
