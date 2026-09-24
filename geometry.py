"""
geometry.py - Spatial 2D geometric reasoning, collision checks, and door clearances.
Coordinates are (x, y) with (0,0) at bottom-left corner of the bounding room.
"""

import math
from typing import Tuple, Dict, Any, List


class BoundingBox:
    """Axis-Aligned Bounding Box (AABB) in 2D space."""
    def __init__(self, x: float, y: float, width: float, depth: float):
        self.x = x
        self.y = y
        self.width = width
        self.depth = depth

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

    def intersects(self, other: "BoundingBox") -> bool:
        """Standard AABB intersection test."""
        return not (
            self.x_max <= other.x_min or
            self.x_min >= other.x_max or
            self.y_max <= other.y_min or
            self.y_min >= other.y_max
        )

    def is_inside(self, room_width: float, room_length: float) -> bool:
        """Verifies if the box is fully contained within the room boundary."""
        return (
            self.x_min >= 0.0 and
            self.y_min >= 0.0 and
            self.x_max <= room_width and
            self.y_max <= room_length
        )


class Door:
    """Represents a door with dynamic clearance rules."""
    def __init__(self, wall: str, offset: float, width: float = 2.5, door_type: str = "swing_inward"):
        self.wall = wall.lower()           # 'south', 'north', 'west', 'east'
        self.offset = offset               # distance from wall origin to hinge
        self.width = width                 # door leaf width in feet
        self.door_type = door_type         # 'swing_inward', 'swing_outward', 'sliding'

    def get_clearance_box(self, room_width: float, room_length: float) -> BoundingBox:
        """
        Calculates the internal bounding box occupied by the door clearance.
        Sliding and outward doors produce a zero-depth bounding envelope inside the room.
        """
        if self.door_type in ("swing_outward", "sliding"):
            # Only occupies wall thickness; zero interior floor clearance required
            if self.wall == "south":
                return BoundingBox(self.offset, 0.0, self.width, 0.1)
            elif self.wall == "north":
                return BoundingBox(self.offset, room_length - 0.1, self.width, 0.1)
            elif self.wall == "west":
                return BoundingBox(0.0, self.offset, 0.1, self.width)
            elif self.wall == "east":
                return BoundingBox(room_width - 0.1, self.offset, 0.1, self.width)

        # Inward swinging door: requires a square clearance envelope equal to door width
        if self.wall == "south":
            return BoundingBox(self.offset, 0.0, self.width, self.width)
        elif self.wall == "north":
            return BoundingBox(self.offset, room_length - self.width, self.width, self.width)
        elif self.wall == "west":
            return BoundingBox(0.0, self.offset, self.width, self.width)
        elif self.wall == "east":
            return BoundingBox(room_width - self.width, self.offset, self.width, self.width)

        raise ValueError(f"Unknown wall orientation: {self.wall}")


class PlacedFixture:
    """A specific fixture placed at coordinates (x, y) with rotation and clearance."""
    def __init__(self, fixture_data: Dict[str, Any], x: float, y: float, orientation: str = "south_wall"):
        self.data = fixture_data
        self.x = x
        self.y = y
        self.orientation = orientation  # which wall it's backed against: 'south_wall', 'north_wall', etc.
        
        # Dimensions change based on orientation
        if orientation in ("south_wall", "north_wall"):
            self.width = fixture_data["width"]
            self.depth = fixture_data["depth"]
        else: # east_wall, west_wall (swaps axes)
            self.width = fixture_data["depth"]
            self.depth = fixture_data["width"]

    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self.x, self.y, self.width, self.depth)

    @property
    def activity_box(self) -> BoundingBox:
        """Expands footprint to include required front standing/clearance buffer."""
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


def check_layout_feasibility(fixtures: List[PlacedFixture], door: Door, room_w: float, room_l: float) -> Tuple[bool, str]:
    """
    Evaluates hard physical feasibility:
    1. Fixture outside room walls.
    2. Fixture colliding with another fixture.
    3. Fixture encroaching on the door swing/clearance.
    """
    door_box = door.get_clearance_box(room_w, room_l)

    for i, f1 in enumerate(fixtures):
        # 1. Room bounds check
        if not f1.bounding_box.is_inside(room_w, room_l):
            return False, f"Fixture {f1.data['name']} exceeds room boundary."

        # 2. Door clearance check
        if f1.bounding_box.intersects(door_box):
            return False, f"Fixture {f1.data['name']} collides with {door.door_type} door clearance."

        # 3. Inter-fixture collisions
        for j, f2 in enumerate(fixtures):
            if i != j and f1.bounding_box.intersects(f2.bounding_box):
                return False, f"Collision detected between {f1.data['name']} and {f2.data['name']}."

    return True, "Valid spatial layout."