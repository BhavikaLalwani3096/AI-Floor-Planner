"""
geometry.py - Spatial Collision, Clearance Physics & Architectural Openings.
Enforces zero-tolerance collisions for fixtures, windows, doors, and access paths.
"""

import math
from typing import Tuple, Dict, Any, List


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

    def intersects(self, other: "BoundingBox", margin: float = 0.04) -> bool:
        """Determines if two boxes intersect with an allowable surface contact margin."""
        return not (
            self.x_max <= other.x_min + margin or
            self.x_min >= other.x_max - margin or
            self.y_max <= other.y_min + margin or
            self.y_min >= other.y_max - margin
        )

    def is_strictly_inside(self, room_w: float, room_l: float) -> bool:
        return (
            self.x_min >= -0.02 and
            self.y_min >= -0.02 and
            self.x_max <= room_w + 0.02 and
            self.y_max <= room_l + 0.02
        )


class Door:
    def __init__(self, wall: str, offset: float, width: float = 2.5, door_type: str = "swing_inward"):
        self.wall = wall.lower()
        self.offset = float(offset)
        self.width = float(width)
        self.door_type = door_type

    def get_entry_corridor_box(self, room_w: float, room_l: float) -> BoundingBox:
        """
        Calculates a required 2.5 ft walking entry vestibule in front of the door.
        No fixture or screen can block this path.
        """
        walk_depth = 2.8
        if self.wall == "south":
            return BoundingBox(self.offset - 0.2, 0.0, self.width + 0.4, walk_depth)
        elif self.wall == "north":
            return BoundingBox(self.offset - 0.2, room_l - walk_depth, self.width + 0.4, walk_depth)
        elif self.wall == "west":
            return BoundingBox(0.0, self.offset - 0.2, walk_depth, self.width + 0.4)
        else:  # east
            return BoundingBox(room_w - walk_depth, self.offset - 0.2, walk_depth, self.width + 0.4)

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

        # Inward radial swing arc check
        corners = [
            (box.x_min, box.y_min), (box.x_max, box.y_min),
            (box.x_min, box.y_max), (box.x_max, box.y_max)
        ]
        for cx, cy in corners:
            if math.hypot(cx - hx, cy - hy) < (self.width - 0.02):
                return True

        return False


class Window:
    """Represents a daylight window opening along a specific perimeter wall."""
    def __init__(self, wall: str, room_w: float, room_l: float, width: float = 3.5):
        self.wall = wall.lower()
        self.width = width
        thick = 0.15
        if self.wall == "north":
            self.box = BoundingBox((room_w - width) / 2.0, room_l - thick, width, thick)
        elif self.wall == "south":
            self.box = BoundingBox((room_w - width) / 2.0, 0.0, width, thick)
        elif self.wall == "west":
            self.box = BoundingBox(0.0, (room_l - width) / 2.0, thick, width)
        else:  # east
            self.box = BoundingBox(room_w - thick, (room_l - width) / 2.0, thick, width)

    def blocks_fixture(self, fixture: "PlacedFixture") -> bool:
        """
        A window blocks any fixture requiring full-height wall mounting (mirrors, tall cabinets).
        Low fixtures like tubs or floor toilets can sit below a high-sill window,
        but vanities (with tall mirrors) and storage towers are strictly prohibited.
        """
        cat = fixture.data.get("category", "")
        if cat in ("vanity", "storage"):
            return fixture.bounding_box.intersects(self.box, margin=0.0)
        return False


class PlacedFixture:
    def __init__(self, fixture_data: Dict[str, Any], x: float, y: float, orientation: str):
        self.data = fixture_data
        self.orientation = orientation

        if orientation in ("south_wall", "north_wall"):
            self.width = float(fixture_data["width"])
            self.depth = float(fixture_data["depth"])
        else:
            self.width = float(fixture_data["depth"])
            self.depth = float(fixture_data["width"])

        self.x = round(float(x), 3)
        self.y = round(float(y), 3)

    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self.x, self.y, self.width, self.depth)

    @property
    def clearance_box(self) -> BoundingBox:
        """Required frontal activity buffer."""
        front_buf = float(self.data.get("clearance_front", 2.2))
        if self.orientation == "south_wall":
            return BoundingBox(self.x, self.y + self.depth, self.width, front_buf)
        elif self.orientation == "north_wall":
            return BoundingBox(self.x, self.y - front_buf, self.width, front_buf)
        elif self.orientation == "west_wall":
            return BoundingBox(self.x + self.width, self.y, front_buf, self.depth)
        elif self.orientation == "east_wall":
            return BoundingBox(self.x - front_buf, self.y, front_buf, self.depth)
        return self.bounding_box


class PerimeterCoordinateSystem:
    def __init__(self, room_w: float, room_l: float):
        self.w = float(room_w)
        self.l = float(room_l)
        self.perimeter = 2.0 * (self.w + self.l)

    def u_to_placement(self, u: float, fixture_data: Dict[str, Any]) -> PlacedFixture:
        u = u % self.perimeter
        fw = float(fixture_data["width"])
        fd = float(fixture_data["depth"])

        if u < self.w:
            x = max(0.0, min(u, self.w - fw))
            return PlacedFixture(fixture_data, x, 0.0, "south_wall")
        elif u < (self.w + self.l):
            local_u = u - self.w
            y = max(0.0, min(local_u, self.l - fw))
            return PlacedFixture(fixture_data, self.w - fd, y, "east_wall")
        elif u < (2.0 * self.w + self.l):
            local_u = u - (self.w + self.l)
            x = max(0.0, min(self.w - fw, self.w - local_u - fw))
            return PlacedFixture(fixture_data, x, self.l - fd, "north_wall")
        else:
            local_u = u - (2.0 * self.w + self.l)
            y = max(0.0, min(self.l - fw, self.l - local_u - fw))
            return PlacedFixture(fixture_data, 0.0, y, "west_wall")


def check_layout_feasibility(fixtures: List[PlacedFixture], door: Door, 
                             room_w: float, room_l: float, 
                             window: Window = None,
                             partitions: List[BoundingBox] = None) -> Tuple[bool, str]:
    partitions = partitions or []
    entry_corridor = door.get_entry_corridor_box(room_w, room_l)

    for i, f1 in enumerate(fixtures):
        b1 = f1.bounding_box
        c1 = f1.clearance_box

        # 1. Room boundary check
        if not b1.is_strictly_inside(room_w, room_l):
            return False, f"{f1.data['name']} out of bounds"

        # 2. Door collision & entry corridor check
        if door.collides_with_box(b1, room_w, room_l):
            return False, f"{f1.data['name']} blocks door leaf"
        if b1.intersects(entry_corridor):
            return False, f"{f1.data['name']} blocks entry corridor"

        # 3. Window conflict check (vanity/storage cannot cover windows)
        if window and window.blocks_fixture(f1):
            return False, f"{f1.data['name']} blocks window wall"

        # 4. Inter-fixture clearance and overlap checks
        for j, f2 in enumerate(fixtures):
            if i != j:
                # Direct physical collision
                if b1.intersects(f2.bounding_box):
                    return False, f"Overlap: {f1.data['name']} hits {f2.data['name']}"

                # Front activity clearance collision (toilet facing vanity/storage head-on)
                if c1.intersects(f2.bounding_box):
                    return False, f"Clearance clash: {f2.data['name']} in front of {f1.data['name']}"

        # 5. Partition collision checks
        for part_box in partitions:
            if b1.intersects(part_box):
                return False, f"{f1.data['name']} collides with partition"

    # Partitions must not block the door or entry vestibule
    for part_box in partitions:
        if door.collides_with_box(part_box, room_w, room_l) or part_box.intersects(entry_corridor):
            return False, "Partition blocks entry path"

    return True, "Valid"