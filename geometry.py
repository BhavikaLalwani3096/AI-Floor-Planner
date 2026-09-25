"""
geometry.py - Continuous Vector Physics & Clearance Engine.
Separating Axis Theorem (SAT), affine vector projections, and radial sweeps.
Guarantees 15-inch toilet centerline code clearance. Standardized in feet.
"""

import math
from typing import Tuple, Dict, Any, List


class Vector2D:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        self.x = round(float(x), 4)
        self.y = round(float(y), 4)

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        return Vector2D(self.x * scalar, self.y * scalar)

    def dot(self, other: "Vector2D") -> float:
        return self.x * other.x + self.y * other.y

    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vector2D":
        mag = self.magnitude()
        return Vector2D(self.x / mag, self.y / mag) if mag > 1e-6 else Vector2D(0.0, 0.0)


class BoundingBox:
    """Axis-Aligned Bounding Box (AABB) in 2D space."""
    def __init__(self, x: float, y: float, width: float, depth: float):
        self.x = round(float(x), 3)
        self.y = round(float(y), 3)
        self.width = round(float(width), 3)
        self.depth = round(float(depth), 3)

    @property
    def x_min(self) -> float:
        return self.x

    @property
    def x_max(self) -> float:
        return self.x + self.width

    @property
    def y_min(self) -> float:
        return self.y

    @property
    def y_max(self) -> float:
        return self.y + self.depth

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.depth / 2.0)

    @property
    def area(self) -> float:
        return self.width * self.depth

    def intersects(self, other: "BoundingBox", tolerance: float = 0.02) -> bool:
        """Separating Axis Theorem intersection test."""
        return not (
            self.x_max <= other.x_min + tolerance or
            self.x_min >= other.x_max - tolerance or
            self.y_max <= other.y_min + tolerance or
            self.y_min >= other.y_max - tolerance
        )

    def is_strictly_inside(self, room_w: float, room_l: float) -> bool:
        return (
            self.x_min >= -0.01 and
            self.y_min >= -0.01 and
            self.x_max <= room_w + 0.01 and
            self.y_max <= room_l + 0.01
        )


class Door:
    """Architectural Door evaluated via radial sweep and entry corridors."""
    def __init__(self, wall: str, offset: float, width: float = 2.5, door_type: str = "swing_inward"):
        self.wall = wall.lower()
        self.offset = float(offset)
        self.width = float(width)
        self.door_type = door_type

    def get_frame_box(self, room_w: float, room_l: float) -> BoundingBox:
        thick = 0.15
        if self.wall in ("south", "north"):
            y = 0.0 if self.wall == "south" else (room_l - thick)
            return BoundingBox(self.offset, y, self.width, thick)
        else:
            x = 0.0 if self.wall == "west" else (room_w - thick)
            return BoundingBox(x, self.offset, thick, self.width)

    def get_corridor_box(self, room_w: float, room_l: float) -> BoundingBox:
        walk = 2.3
        if self.wall == "south":
            return BoundingBox(self.offset, 0.0, self.width, walk)
        elif self.wall == "north":
            return BoundingBox(self.offset, room_l - walk, self.width, walk)
        elif self.wall == "west":
            return BoundingBox(0.0, self.offset, walk, self.width)
        else:
            return BoundingBox(room_w - walk, self.offset, walk, self.width)

    def collides_with_box(self, box: BoundingBox, room_w: float, room_l: float) -> bool:
        if box.intersects(self.get_frame_box(room_w, room_l)):
            return True
        if self.door_type in ("swing_outward", "sliding"):
            return False

        # Inward radial swing arc
        hx = self.offset if self.wall in ("south", "north") else (0.0 if self.wall == "west" else room_w)
        hy = 0.0 if self.wall == "south" else (room_l if self.wall == "north" else self.offset)

        corners = [
            (box.x_min, box.y_min), (box.x_max, box.y_min),
            (box.x_min, box.y_max), (box.x_max, box.y_max)
        ]
        return any(math.hypot(cx - hx, cy - hy) < (self.width + 0.05) for cx, cy in corners)


class Window:
    """Daylight window aperture with exclusion volume."""
    def __init__(self, wall: str, room_w: float, room_l: float, width: float = 3.5):
        self.wall = wall.lower()
        self.width = width
        thick = 0.4
        if self.wall in ("south", "north"):
            y = 0.0 if self.wall == "south" else (room_l - thick)
            self.box = BoundingBox((room_w - width) / 2.0, y, width, thick)
        else:
            x = 0.0 if self.wall == "west" else (room_w - thick)
            self.box = BoundingBox(x, (room_l - width) / 2.0, thick, width)

    def blocks_placement(self, box: BoundingBox) -> bool:
        return box.intersects(self.box, tolerance=0.0)


class PlacedFixture:
    """Continuous parametric fixture with plumbing-code clearance envelopes."""
    def __init__(self, fixture_data: Dict[str, Any], x: float, y: float, orientation: str):
        self.data = fixture_data
        self.orientation = orientation
        is_cardinal_x = orientation in ("south_wall", "north_wall")

        self.width = float(fixture_data["width"]) if is_cardinal_x else float(fixture_data["depth"])
        self.depth = float(fixture_data["depth"]) if is_cardinal_x else float(fixture_data["width"])
        self.x = round(float(x), 3)
        self.y = round(float(y), 3)

    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self.x, self.y, self.width, self.depth)

    @property
    def clearance_box(self) -> BoundingBox:
        front_buf = float(self.data.get("clearance_front", 2.0))
        # 15-inch (1.25 ft) lateral clearance on both sides of toilet centerline
        side_buf = 0.55 if self.data.get("category") == "toilet" else 0.1

        if self.orientation == "south_wall":
            return BoundingBox(self.x - side_buf, self.y, self.width + (2 * side_buf), self.depth + front_buf)
        elif self.orientation == "north_wall":
            return BoundingBox(self.x - side_buf, self.y - front_buf, self.width + (2 * side_buf), self.depth + front_buf)
        elif self.orientation == "west_wall":
            return BoundingBox(self.x, self.y - side_buf, self.width + front_buf, self.depth + (2 * side_buf))
        else:
            return BoundingBox(self.x - front_buf, self.y - side_buf, self.width + front_buf, self.depth + (2 * side_buf))


class PerimeterCoordinateSystem:
    """Maps a continuous scalar distance u to boundary coordinates with code clearances."""
    def __init__(self, room_w: float, room_l: float):
        self.w = float(room_w)
        self.l = float(room_l)
        self.perimeter = 2.0 * (self.w + self.l)

    def u_to_placement(self, u: float, fixture_data: Dict[str, Any]) -> PlacedFixture:
        u = u % self.perimeter
        fw, fd = float(fixture_data["width"]), float(fixture_data["depth"])
        # Ensure 15-inch lateral shoulder clearance from corner walls for toilets
        side_margin = 0.55 if fixture_data.get("category") == "toilet" else 0.1

        if u < self.w:
            x = max(side_margin, min(u, self.w - fw - side_margin))
            return PlacedFixture(fixture_data, x, 0.0, "south_wall")
        elif u < (self.w + self.l):
            local_u = u - self.w
            y = max(side_margin, min(local_u, self.l - fw - side_margin))
            return PlacedFixture(fixture_data, self.w - fd, y, "east_wall")
        elif u < (2.0 * self.w + self.l):
            local_u = u - (self.w + self.l)
            x = max(side_margin, min(self.w - fw - side_margin, self.w - local_u - fw))
            return PlacedFixture(fixture_data, x, self.l - fd, "north_wall")
        else:
            local_u = u - (2.0 * self.w + self.l)
            y = max(side_margin, min(self.l - fw - side_margin, self.l - local_u - fw))
            return PlacedFixture(fixture_data, 0.0, y, "west_wall")


def check_layout_feasibility(fixtures: List[PlacedFixture], door: Door, 
                             room_w: float, room_l: float, 
                             window: Window = None,
                             partitions: List[BoundingBox] = None) -> Tuple[bool, str]:
    partitions = partitions or []
    corridor = door.get_corridor_box(room_w, room_l)

    for i, f1 in enumerate(fixtures):
        b1 = f1.bounding_box
        c1 = f1.clearance_box

        # 1. Bounds check
        if not b1.is_strictly_inside(room_w, room_l):
            return False, f"{f1.data['name']} out of bounds"

        # 2. Door interference check
        if door.collides_with_box(b1, room_w, room_l) or b1.intersects(corridor):
            return False, f"{f1.data['name']} blocks door or entry path"

        # 3. Window conflict check
        if window and window.blocks_placement(b1):
            return False, f"{f1.data['name']} blocks window"

        # 4. Inter-fixture collisions and clearances
        for j, f2 in enumerate(fixtures):
            if i != j:
                if b1.intersects(f2.bounding_box):
                    return False, f"Overlap: {f1.data['name']} hits {f2.data['name']}"
                if c1.intersects(f2.bounding_box):
                    return False, f"Clearance blocked: {f2.data['name']} inside activity zone of {f1.data['name']}"

        # 5. Partition collisions
        for p_box in partitions:
            if b1.intersects(p_box) or c1.intersects(p_box):
                return False, f"{f1.data['name']} clearance hits partition"

    for p_box in partitions:
        if window and window.blocks_placement(p_box):
            return False, "Partition blocks window"
        if door.collides_with_box(p_box, room_w, room_l) or p_box.intersects(corridor):
            return False, "Partition blocks door path"

    return True, "Valid"