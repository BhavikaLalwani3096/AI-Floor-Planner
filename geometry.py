"""
geometry.py - Continuous Coordinate Physics & Geometric Vector Reasoning Engine.
Prevents boundary bleeding and provides strict collision detection for walls, doors, and partitions.
"""

import math
from typing import Tuple, Dict, Any, List


class BoundingBox:
    """Axis-Aligned Bounding Box (AABB) in 2D space."""
    def __init__(self, x: float, y: float, width: float, depth: float):
        self.x = round(x, 3)
        self.y = round(y, 3)
        self.width = round(width, 3)
        self.depth = round(depth, 3)

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

    def intersects(self, other: "BoundingBox", margin: float = 0.05) -> bool:
        """Determines if two boxes intersect with an allowable surface contact margin."""
        return not (
            self.x_max <= other.x_min + margin or
            self.x_min >= other.x_max - margin or
            self.y_max <= other.y_min + margin or
            self.y_min >= other.y_max - margin
        )

    def intersection_area(self, other: "BoundingBox") -> float:
        dx = max(0.0, min(self.x_max, other.x_max) - max(self.x_min, other.x_min))
        dy = max(0.0, min(self.y_max, other.y_max) - max(self.y_min, other.y_min))
        return dx * dy

    def is_strictly_inside(self, room_w: float, room_l: float) -> bool:
        """Guarantees the box is strictly contained within room walls."""
        return (
            self.x_min >= -0.01 and
            self.y_min >= -0.01 and
            self.x_max <= room_w + 0.01 and
            self.y_max <= room_l + 0.01
        )


class Door:
    """Represents an architectural door with radial swing and sliding track geometry."""
    def __init__(self, wall: str, offset: float, width: float = 2.5, door_type: str = "swing_inward"):
        self.wall = wall.lower()
        self.offset = offset
        self.width = width
        self.door_type = door_type

    def collides_with_box(self, box: BoundingBox, room_w: float, room_l: float) -> bool:
        frame_thick = 0.15
        if self.wall == "south":
            door_frame = BoundingBox(self.offset, 0.0, self.width, frame_thick)
            hx, hy = self.offset, 0.0
        elif self.wall == "north":
            door_frame = BoundingBox(self.offset, room_l - frame_thick, self.width, frame_thick)
            hx, hy = self.offset, room_l
        elif self.wall == "west":
            door_frame = BoundingBox(0.0, self.offset, frame_thick, self.width)
            hx, hy = 0.0, self.offset
        else:  # east
            door_frame = BoundingBox(room_w - frame_thick, self.offset, frame_thick, self.width)
            hx, hy = room_w, self.offset

        if box.intersects(door_frame):
            return True

        if self.door_type in ("swing_outward", "sliding"):
            return False

        # Inward radial swing arc
        corners = [
            (box.x_min, box.y_min), (box.x_max, box.y_min),
            (box.x_min, box.y_max), (box.x_max, box.y_max)
        ]
        for cx, cy in corners:
            if math.hypot(cx - hx, cy - hy) < (self.width - 0.05):
                return True

        return False


class PlacedFixture:
    """Rotation-aware fixture placed along perimeter walls."""
    def __init__(self, fixture_data: Dict[str, Any], x: float, y: float, orientation: str):
        self.data = fixture_data
        self.orientation = orientation

        if orientation in ("south_wall", "north_wall"):
            self.width = fixture_data["width"]
            self.depth = fixture_data["depth"]
        else:
            self.width = fixture_data["depth"]
            self.depth = fixture_data["width"]

        self.x = round(x, 3)
        self.y = round(y, 3)

    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self.x, self.y, self.width, self.depth)

    @property
    def activity_box(self) -> BoundingBox:
        front_buf = self.data.get("clearance_front", 2.0)
        if self.orientation == "south_wall":
            return BoundingBox(self.x, self.y, self.width, self.depth + front_buf)
        elif self.orientation == "north_wall":
            return BoundingBox(self.x, self.y - front_buf, self.width, self.depth + front_buf)
        elif self.orientation == "west_wall":
            return BoundingBox(self.x, self.y, self.width + front_buf, self.depth)
        elif self.orientation == "east_wall":
            return BoundingBox(self.x - front_buf, self.y, self.width + front_buf, self.depth)
        return self.bounding_box


class PerimeterCoordinateSystem:
    """Continuous coordinate parameterization with strict corner boundary clipping."""
    def __init__(self, room_w: float, room_l: float):
        self.w = room_w
        self.l = room_l
        self.perimeter = 2.0 * (room_w + room_l)

    def u_to_placement(self, u: float, fixture_data: Dict[str, Any]) -> PlacedFixture:
        u = u % self.perimeter
        fw, fd = fixture_data["width"], fixture_data["depth"]

        if u < self.w:
            # South wall: clamped strictly between 0 and room_w - fw
            x = max(0.0, min(u, self.w - fw))
            return PlacedFixture(fixture_data, x, 0.0, "south_wall")

        elif u < (self.w + self.l):
            # East wall: clamped strictly between 0 and room_l - fw
            local_u = u - self.w
            y = max(0.0, min(local_u, self.l - fw))
            return PlacedFixture(fixture_data, self.w - fd, y, "east_wall")

        elif u < (2.0 * self.w + self.l):
            # North wall: clamped strictly between 0 and room_w - fw
            local_u = u - (self.w + self.l)
            x = max(0.0, min(self.w - fw, self.w - local_u - fw))
            return PlacedFixture(fixture_data, x, self.l - fd, "north_wall")

        else:
            # West wall: clamped strictly between 0 and room_l - fw
            local_u = u - (2.0 * self.w + self.l)
            y = max(0.0, min(self.l - fw, self.l - local_u - fw))
            return PlacedFixture(fixture_data, 0.0, y, "west_wall")


def calculate_sightline_vector_score(door: Door, toilet: PlacedFixture, vanity: PlacedFixture, 
                                     room_w: float, room_l: float) -> float:
    if door.wall == "south":
        hx, hy, nx, ny = door.offset, 0.0, 0.0, 1.0
    elif door.wall == "north":
        hx, hy, nx, ny = door.offset, room_l, 0.0, -1.0
    elif door.wall == "west":
        hx, hy, nx, ny = 0.0, door.offset, 1.0, 0.0
    else:
        hx, hy, nx, ny = room_w, door.offset, -1.0, 0.0

    vx, vy = vanity.bounding_box.center
    v_dist = math.hypot(vx - hx, vy - hy) or 1.0
    dot_vanity = ((vx - hx) / v_dist) * nx + ((vy - hy) / v_dist) * ny

    tx, ty = toilet.bounding_box.center
    t_dist = math.hypot(tx - hx, ty - hy) or 1.0
    dot_toilet = ((tx - hx) / t_dist) * nx + ((ty - hy) / t_dist) * ny

    score = (0.5 * (dot_vanity + 1.0)) - (0.5 * (dot_toilet + 1.0))
    return max(0.0, min(1.0, (score + 1.0) / 2.0))


def calculate_plumbing_euclidean_score(fixtures: List[PlacedFixture], room_w: float, room_l: float) -> float:
    wet = [f for f in fixtures if f.data["category"] in ("toilet", "shower", "bathtub")]
    if len(wet) < 2:
        return 1.0
    c1, c2 = wet[0].bounding_box.center, wet[1].bounding_box.center
    dist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
    return max(0.0, 1.0 - (dist / math.hypot(room_w, room_l)))


def check_layout_feasibility(fixtures: List[PlacedFixture], door: Door, 
                             room_w: float, room_l: float, 
                             partitions: List[BoundingBox] = None) -> Tuple[bool, str]:
    partitions = partitions or []

    for i, f1 in enumerate(fixtures):
        b1 = f1.bounding_box

        # 1. Bounds: Must be strictly inside walls
        if not b1.is_strictly_inside(room_w, room_l):
            return False, f"{f1.data['name']} exceeds room boundary"

        # 2. Door interference
        if door.collides_with_box(b1, room_w, room_l):
            return False, f"{f1.data['name']} blocks {door.door_type} clearance"

        # 3. Inter-fixture collision
        for j, f2 in enumerate(fixtures):
            if i != j and b1.intersects(f2.bounding_box):
                return False, f"Collision: {f1.data['name']} overlaps {f2.data['name']}"

        # 4. Partition screen collision
        for part_box in partitions:
            if b1.intersects(part_box):
                return False, f"{f1.data['name']} collides with privacy partition wall"

    # Verify partition does not block the door
    for part_box in partitions:
        if door.collides_with_box(part_box, room_w, room_l):
            return False, "Partition screen blocks the door entryway"

    return True, "Valid Layout"