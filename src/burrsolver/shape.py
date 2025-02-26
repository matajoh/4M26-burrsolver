"""Shape class for the burr puzzle."""

from typing import List, Mapping, NamedTuple, Tuple

from .piece import Piece
from .position import PLACES
from .geometry import Facet, Mesh, Vec3
from .voxel import Voxel


"""Voxels required for a piece orientation to be valid."""
REQUIRED = {
    "A": [Voxel(-1, -3, -5), Voxel(1, -3, -5),
          Voxel(-1, -3, -3), Voxel(1, -3, -3),
          Voxel(-1, -3, 3), Voxel(1, -3, 3),
          Voxel(-1, -3, 5), Voxel(1, -3, 5)],
    "B": [Voxel(-5, -1, -3), Voxel(-5, 1, -3),
          Voxel(-3, -1, -3), Voxel(-3, 1, -3),
          Voxel(3, -1, -3), Voxel(3, 1, -3),
          Voxel(5, -1, -3), Voxel(5, 1, -3)],
    "C": [Voxel(-3, -5, -1), Voxel(-3, -5, 1),
          Voxel(-3, -3, -1), Voxel(-3, -3, 1),
          Voxel(-3, 3, -1), Voxel(-3, 3, 1),
          Voxel(-3, 5, -1), Voxel(-3, 5, 1)],
    "D": [Voxel(-5, -1, 3), Voxel(-5, 1, 3),
          Voxel(-3, -1, 3), Voxel(-3, 1, 3),
          Voxel(3, -1, 3), Voxel(3, 1, 3),
          Voxel(5, -1, 3), Voxel(5, 1, 3)],
    "E": [Voxel(3, -5, -1), Voxel(3, -5, 1),
          Voxel(3, -3, -1), Voxel(3, -3, 1),
          Voxel(3, 3, -1), Voxel(3, 3, 1),
          Voxel(3, 5, -1), Voxel(3, 5, 1)],
    "F": [Voxel(-1, 3, -5), Voxel(1, 3, -5),
          Voxel(-1, 3, -3), Voxel(1, 3, -3),
          Voxel(-1, 3, 3), Voxel(1, 3, 3),
          Voxel(-1, 3, 5), Voxel(1, 3, 5)],
}


Orientations = Mapping[str, List[int]]


class Shape(NamedTuple("Shape", [("voxels", Tuple[Voxel, ...]),
                                 ("orientations", Orientations)])):
    """A shape in the puzzle.

    Consists of a list of voxels centered around the origin and a mapping of
    valid orientations for this shape at each named location in the puzzle.
    """

    def move_to(self, p: Piece) -> "Shape":
        """Return the shape with its voxels aligned to the grid for the given piece."""
        voxels = tuple(v.move_to(p.position, p.orientation)
                       for v in self.voxels)
        return Shape(voxels, self.orientations)

    def inside_count(self) -> int:
        """Return the number of voxels inside the puzzle."""
        return sum(v.is_inside() for v in self.voxels)

    @staticmethod
    def from_text(text: str) -> "Shape":
        """Create a shape from a string representation.

        The string representation consists of a series of lines with "/" separating
        each line. Each line contains "x" for a voxel and "." for empty space, for
        example:

        xxxxxx/xx..xx/x..xxx/x...xx
        """
        lines = text.split("/")
        shape_voxels: List[Voxel] = []
        for i, line in enumerate(lines):
            x = i % 2
            y = i // 2
            for z, v in enumerate(line):
                if v == "x":
                    voxel = Voxel(2 * x - 1, 2 * y - 1, 5 - 2 * z)
                    shape_voxels.append(voxel)

        valid_orientations = {}
        s = Shape(tuple(shape_voxels), valid_orientations)
        for name, place in PLACES.items():
            valid_orientations[name] = []
            # this set is used to filter orientations which result in
            # duplicate voxel layouts due to symmetry
            orientation_voxels = set()
            for o in range(8):
                piece = Piece(0, place, o)
                voxels = tuple(sorted(s.move_to(piece).voxels))
                if voxels not in orientation_voxels:
                    orientation_voxels.add(voxels)
                    num_req = len(set(voxels).intersection(REQUIRED[name]))
                    if num_req == 8:
                        valid_orientations[name].append(o)

        return s

    def save_as_stl(self, path: str, scale=10):
        """Save this shape as an STL file."""
        mesh = Mesh.from_voxels(self.voxels, True)
        facets: List[Facet] = []
        for a, b, c, d in mesh.quads:
            v0 = Vec3.from_array(mesh.vertices[a]).scale(scale)
            v1 = Vec3.from_array(mesh.vertices[b]).scale(scale)
            v2 = Vec3.from_array(mesh.vertices[c]).scale(scale)
            v3 = Vec3.from_array(mesh.vertices[d]).scale(scale)
            n = Vec3.from_array(mesh.normals[a])
            facets.append(Facet(n, (v0, v1, v2)))
            facets.append(Facet(n, (v2, v3, v0)))

        with open(path, "w") as file:
            file.write("solid burr_piece\n")
            for facet in facets:
                facet.write(file)
            file.write("endsolid")
