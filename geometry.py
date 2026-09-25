"""
geometry.py - Continuous Coordinate Physics & Geometric Vector Reasoning Engine.
Provides parametric perimeter mapping, circular door-arc collision detection,
activity clearance calculation, and raycasting vector math.
All spatial dimensions are standardized in feet.
"""

import math
from typing import Tuple, Dict, Any, List


class BoundingBox:
    """Represents an Axis-Aligned Bounding Box (AABB) in 2D space."""
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

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.depth / 2.0)

    @property
    def area(self) -> float:
        return self.width * self.depth

    def intersects(self, other: "BoundingBox") -> bool:
        """Determines if two bounding boxes collide (strict interior overlap)."""
        return not (
            self.x_max <= other.x_min or
            self.x_min >= other.x_max or
            self.y_max <= other.y_min or
            self.y_min >= other.y_max
        )

    def intersection_area(self, other: "BoundingBox") -> float:
        """Calculates exact square footage of overlap between two boxes."""
        dx = max(0.0, min(self.x_max, other.x_max) - max(self.x_min, other.x_min))
        dy = max(0.0, min(self.y_max, other.y_max) - max(self.y_min, other.y_min))
        return dx * dy

    def is_inside(self, room_width: float, room_length: float, tolerance: float = 0.05) -> bool:
        """Verifies if the box sits completely inside room boundaries."""
        return (
            self.x_min >= -tolerance and
            self.y_min >= -tolerance and
            self.x_max <= room_width + tolerance and
            self.y_max <= room_length + tolerance
        )


class Door:
    """Represents a door with dynamic circular sweep geometry and threshold lines."""
    def __init__(self, wall: str, offset: float, width: float = 2.5, door_type: str = "swing_inward"):
        self.wall = wall.lower()
        self.offset = offset
        self.width = width
        self.door_type = door_type

    @property
    def hinge_and_vector(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Computes the door hinge coordinates (x, y) and an inward normal unit vector
        pointing straight into the room along the entry path.
        """
        if self.wall == "south":
            return (self.offset, 0.0), (0.0, 1.0)
        elif self.wall == "north":
            return (self.offset, 0.0), (0.0, -1.0)  # Y coordinate adjusted by room length when checked
        elif self.wall == "west":
            return (0.0, self.offset), (1.0, 0.0)
        elif self.wall == "east":
            return (0.0, self.offset), (-1.0, 0.0)
        return (0.0, 0.0), (0.0, 1.0)

    def collides_with_fixture(self, fixture_box: BoundingBox, room_w: float, room_l: float) -> bool:
        """
        True physical collision check against the door:
        - Outward & Sliding doors: only protects the entry frame gap along the wall.
        - Inward swing: checks both circular sweep radius from hinge and the 2D bounding sector.
        """
        # 1. Door opening frame footprint along the wall
        frame_thick = 0.2
        if self.wall == "south":
            door_frame = BoundingBox(self.offset, 0.0, self.width, frame_thick)
            hinge_x, hinge_y = self.offset, 0.0
        elif self.wall == "north":
            door_frame = BoundingBox(self.offset, room_l - frame_thick, self.width, frame_thick)
            hinge_x, hinge_y = self.offset, room_l
        elif self.wall == "west":
            door_frame = BoundingBox(0.0, self.offset, frame_thick, self.width)
            hinge_x, hinge_y = 0.0, self.offset
        elif self.wall == "east":
            door_frame = BoundingBox(room_w - frame_thick, self.offset, frame_thick, self.width)
            hinge_x, hinge_y = room_w, self.offset
        else:
            door_frame = BoundingBox(self.offset, 0.0, self.width, frame_thick)
            hinge_x, hinge_y = self.offset, 0.0

        # Fixtures cannot mount across the opening frame
        if fixture_box.intersects(door_frame):
            return True

        # If sliding or outward, interior room floor space is completely free
        if self.door_type in ("swing_outward", "sliding"):
            return False

        # Inward swing: Radial sector test
        # Check closest corner of the fixture to the hinge
        corners = [
            (fixture_box.x_min, fixture_box.y_min),
            (fixture_box.x_max, fixture_box.y_min),
            (fixture_box.x_min, fixture_box.y_max),
            (fixture_box.x_max, fixture_box.y_max)
        ]
        
        for cx, cy in corners:
            dist = math.hypot(cx - hinge_x, cy - hinge_y)
            if dist < self.width:
                # Inside radial distance; verify it sits on interior side
                if self.wall == "south" and cy >= 0.0:
                    return True
                elif self.wall == "north" and cy <= room_l:
                    return True
                elif self.wall == "west" and cx >= 0.0:
                    return True
                elif self.wall == "east" and cx <= room_w:
                    return True

        return False


class PlacedFixture:
    """A physical bathroom fixture mapped onto 2D room space."""
    def __init__(self, fixture_data: Dict[str, Any], x: float, y: float, orientation: str):
        self.data = fixture_data
        self.x = x
        self.y = y
        self.orientation = orientation  # 'south_wall', 'north_wall', 'west_wall', 'east_wall'

        # Swap width and depth when backed against East or West walls
        if orientation in ("south_wall", "north_wall"):
            self.width = fixture_data["width"]
            self.depth = fixture_data["depth"]
        else:
            self.width = fixture_data["depth"]
            self.depth = fixture_data["width"]

    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self.x, self.y, self.width, self.depth)

    @property
    def activity_box(self) -> BoundingBox:
        """Returns the standing buffer box required in front of the fixture."""
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
    """
    Continuous 1D mapping along room perimeter.
    Maps a single scalar u in [0, Perimeter) to continuous (x, y) coordinates
    and an outward wall orientation. No hardcoded walls.
    """
    def __init__(self, room_w: float, room_l: float):
        self.w = room_w
        self.l = room_l
        self.perimeter = 2.0 * (room_w + room_l)

    def u_to_placement(self, u: float, fixture_data: Dict[str, Any]) -> PlacedFixture:
        """Converts a perimeter distance u into exact (x, y) and orientation."""
        u = u % self.perimeter
        fw, fd = fixture_data["width"], fixture_data["depth"]

        if u < self.w:
            # South wall (y = 0.0, backed against south, projects +y)
            x = min(u, self.w - fw)
            return PlacedFixture(fixture_data, x, 0.0, "south_wall")

        elif u < (self.w + self.l):
            # East wall (x = w - depth, backed against east, projects -x)
            local_u = u - self.w
            y = min(local_u, self.l - fw)
            return PlacedFixture(fixture_data, self.w - fd, y, "east_wall")

        elif u < (2.0 * self.w + self.l):
            # North wall (y = l - depth, backed against north, projects -y)
            local_u = u - (self.w + self.l)
            x = min(self.w - fw, max(0.0, self.w - local_u - fw))
            return PlacedFixture(fixture_data, x, self.l - fd, "north_wall")

        else:
            # West wall (x = 0.0, backed against west, projects +x)
            local_u = u - (2.0 * self.w + self.l)
            y = min(self.l - fw, max(0.0, self.l - local_u - fw))
            return PlacedFixture(fixture_data, 0.0, y, "west_wall")


# ----------------- VECTOR RAYCASTING & GEOMETRIC METRICS -----------------

def calculate_sightline_vector_score(door: Door, toilet: PlacedFixture, vanity: PlacedFixture, 
                                     room_w: float, room_l: float) -> float:
    """
    Raycast dot product from door entry point:
    Rewards vanity in immediate line-of-sight (+1.0).
    Penalizes toilet in immediate line-of-sight (-1.0).
    """
    # Hinge location
    if door.wall == "south":
        hx, hy, nx, ny = door.offset, 0.0, 0.0, 1.0
    elif door.wall == "north":
        hx, hy, nx, ny = door.offset, room_l, 0.0, -1.0
    elif door.wall == "west":
        hx, hy, nx, ny = 0.0, door.offset, 1.0, 0.0
    else: # east
        hx, hy, nx, ny = room_w, door.offset, -1.0, 0.0

    # Ray to Vanity
    vx, vy = vanity.bounding_box.center
    v_vec = (vx - hx, vy - hy)
    v_dist = math.hypot(v_vec[0], v_vec[1]) or 1.0
    v_norm = (v_vec[0] / v_dist, v_vec[1] / v_dist)
    dot_vanity = (v_norm[0] * nx) + (v_norm[1] * ny)  # Cosine angle to entry path

    # Ray to Toilet
    tx, ty = toilet.bounding_box.center
    t_vec = (tx - hx, ty - hy)
    t_dist = math.hypot(t_vec[0], t_vec[1]) or 1.0
    t_norm = (t_vec[0] / t_dist, t_vec[1] / t_dist)
    dot_toilet = (t_norm[0] * nx) + (t_norm[1] * ny)

    # Score: Higher is better (vanity aligned, toilet angled away or further back)
    score = (0.5 * (dot_vanity + 1.0)) - (0.5 * (dot_toilet + 1.0))
    return max(0.0, min(1.0, (score + 1.0) / 2.0))


def calculate_plumbing_euclidean_score(fixtures: List[PlacedFixture], room_w: float, room_l: float) -> float:
    """
    Measures the Euclidean distance between water drain points.
    Shorter pipe distance = higher installation economy.
    """
    wet_fixtures = [f for f in fixtures if f.data["category"] in ("toilet", "shower")]
    if len(wet_fixtures) < 2:
        return 1.0

    f1, f2 = wet_fixtures[0], wet_fixtures[1]
    c1 = f1.bounding_box.center
    c2 = f2.bounding_box.center

    dist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
    max_diag = math.hypot(room_w, room_l)
    return max(0.0, 1.0 - (dist / max_diag))


def check_layout_feasibility(fixtures: List[PlacedFixture], door: Door, room_w: float, room_l: float) -> Tuple[bool, str]:
    """
    Absolute Hard Constraint Physics Evaluator:
    Returns False if boundary, door clearance, or inter-fixture collision occurs.
    """
    for i, f1 in enumerate(fixtures):
        b1 = f1.bounding_box

        # 1. Bounds check
        if not b1.is_inside(room_w, room_l):
            return False, f"{f1.data['name']} exceeds room boundary"

        # 2. Door clearance check
        if door.collides_with_fixture(b1, room_w, room_l):
            return False, f"{f1.data['name']} collides with {door.door_type} clearance"

        # 3. Inter-fixture collision check
        for j, f2 in enumerate(fixtures):
            if i != j and b1.intersects(f2.bounding_box):
                return False, f"Collision: {f1.data['name']} overlaps {f2.data['name']}"

    return True, "Valid Layout"