"""
generator.py - Flexible Multi-Objective Spatial Optimizer & Bundle Combinator.
Generates 3 structurally distinct spatial layouts and pairs them with 3 intra-style 
Kohler product bundles, yielding a 3x3 matrix of 9 fully realized designs.
"""

import math
from typing import List, Dict, Any, Tuple
from catalog import get_products_by_filter, KOHLER_CATALOG
from geometry import BoundingBox, Door, PlacedFixture, check_layout_feasibility


class SpatialCandidate:
    """Represents a generated layout candidate with its fitness breakdown."""
    def __init__(self, fixtures: List[PlacedFixture], fitness: float, scores: Dict[str, float]):
        self.fixtures = fixtures
        self.fitness = fitness
        self.scores = scores


def _safe_get_product(category: str, style: str, tier: str) -> Dict[str, Any]:
    """Helper to safely fetch a product, falling back gracefully if an exact tier match is missing."""
    items = get_products_by_filter(category=category, style=style, tier=tier)
    if items:
        return items[0]
    fallback = get_products_by_filter(category=category, style=style)
    if fallback:
        return fallback[0]
    all_cat = get_products_by_filter(category=category)
    if all_cat:
        return all_cat[0]
    raise ValueError(f"No catalog products available for category: '{category}'")


class LayoutOptimizer:
    """
    Evaluates perimeter wall candidate positions and uses multi-objective 
    scoring to find top structurally diverse layouts.
    """
    def __init__(self, room_w: float, room_l: float, door: Door, 
                 mode: str = "free_flow", 
                 window_wall: str = "north",
                 renovation_stack: Tuple[float, float] = None):
        self.room_w = room_w
        self.room_l = room_l
        self.door = door
        self.mode = mode.lower()  # 'free_flow' or 'privacy_focused'
        self.window_wall = window_wall.lower()
        self.renovation_stack = renovation_stack  # Optional (x, y) coordinates of fixed soil stack

        # Dynamic weights based on selected Macro Mode
        if self.mode == "privacy_focused":
            self.weights = {"circulation": 0.25, "sightline": 0.45, "daylight": 0.15, "plumbing": 0.15}
        else: # free_flow
            self.weights = {"circulation": 0.40, "sightline": 0.15, "daylight": 0.20, "plumbing": 0.25}

    def compute_fitness(self, fixtures: List[PlacedFixture]) -> Tuple[float, Dict[str, float]]:
        """Calculates multi-objective fitness scores in the range [0.0, 1.0]."""
        door_center_x = self.door.offset + (self.door.width / 2.0)
        door_center_y = 0.0 if self.door.wall == "south" else self.room_l

        # 1. Circulation Score (Activity Envelope overlap penalty)
        activity_clashes = 0
        for i, f1 in enumerate(fixtures):
            for j, f2 in enumerate(fixtures):
                if i != j and f1.activity_box.intersects(f2.bounding_box):
                    activity_clashes += 1
        s_circulation = max(0.0, 1.0 - (activity_clashes * 0.25))

        # 2. Sightline & Privacy Score
        s_sightline = 0.5
        toilet_fixture = next((f for f in fixtures if f.data["category"] == "toilet"), None)
        vanity_fixture = next((f for f in fixtures if f.data["category"] == "vanity"), None)

        if vanity_fixture:
            dist_v_door = math.hypot(vanity_fixture.x - door_center_x, vanity_fixture.y - door_center_y)
            s_sightline += 0.25 if dist_v_door > 2.0 else 0.1

        if toilet_fixture:
            dist_t_door = math.hypot(toilet_fixture.x - door_center_x, toilet_fixture.y - door_center_y)
            if self.mode == "privacy_focused":
                if dist_t_door < 3.5:
                    s_sightline -= 0.4
                else:
                    s_sightline += 0.25
            else:
                if dist_t_door < 2.5:
                    s_sightline -= 0.15

        s_sightline = min(1.0, max(0.0, s_sightline))

        # 3. Daylight & Fenestration Score
        s_daylight = 0.5
        shower_fixture = next((f for f in fixtures if f.data["category"] == "shower"), None)
        if shower_fixture and shower_fixture.orientation.startswith(self.window_wall):
            s_daylight += 0.4  # Bonus for natural ventilation in wet zone
        s_daylight = min(1.0, max(0.0, s_daylight))

        # 4. Plumbing Economy Score
        s_plumbing = 0.5
        if self.renovation_stack and toilet_fixture:
            dist_stack = math.hypot(toilet_fixture.x - self.renovation_stack[0], 
                                    toilet_fixture.y - self.renovation_stack[1])
            s_plumbing = max(0.0, 1.0 - (dist_stack / max(self.room_w, self.room_l)))
        elif toilet_fixture and shower_fixture:
            wet_dist = math.hypot(toilet_fixture.x - shower_fixture.x, toilet_fixture.y - shower_fixture.y)
            s_plumbing = max(0.0, 1.0 - (wet_dist / (self.room_w + self.room_l)))

        scores = {
            "circulation": s_circulation,
            "sightline": s_sightline,
            "daylight": s_daylight,
            "plumbing": s_plumbing
        }

        total_fitness = sum(scores[k] * self.weights[k] for k in self.weights)
        return total_fitness, scores

    def generate_top_layouts(self, template_items: List[Dict[str, Any]], count: int = 3) -> List[SpatialCandidate]:
        """
        Samples candidate configurations along wall perimeter slots,
        rejects collisions, and selects distinct high-scoring candidates.
        """
        candidates: List[SpatialCandidate] = []

        anchor_slots = [
            # South Wall (avoiding default door at 0.5-3.0)
            (4.5, 0.0, "south_wall"),
            (6.5, 0.0, "south_wall"),
            # North Wall
            (0.5, self.room_l - 2.5, "north_wall"),
            (3.0, self.room_l - 2.5, "north_wall"),
            (5.5, self.room_l - 2.5, "north_wall"),
            # West Wall
            (0.0, 3.0, "west_wall"),
            (0.0, 5.5, "west_wall"),
            # East Wall
            (self.room_w - 2.5, 2.5, "east_wall"),
            (self.room_w - 2.5, 5.0, "east_wall"),
        ]

        # Generate combinatorial fixture permutations
        for s1 in anchor_slots:
            for s2 in anchor_slots:
                if s1 == s2:
                    continue
                for s3 in anchor_slots:
                    if s3 in (s1, s2):
                        continue

                    # Instantiate placements for: [Toilet, Vanity, Shower]
                    f_toilet = PlacedFixture(template_items[0], s1[0], s1[1], s1[2])
                    f_vanity = PlacedFixture(template_items[1], s2[0], s2[1], s2[2])
                    f_shower = PlacedFixture(template_items[2], s3[0], s3[1], s3[2])

                    fixtures = [f_toilet, f_vanity, f_shower]

                    # 1. Hard Constraints Filter
                    is_valid, _ = check_layout_feasibility(fixtures, self.door, self.room_w, self.room_l)
                    if not is_valid:
                        continue

                    # 2. Score candidate
                    fitness, scores = self.compute_fitness(fixtures)
                    candidates.append(SpatialCandidate(fixtures, fitness, scores))

        # Sort candidates descending by fitness
        candidates.sort(key=lambda c: c.fitness, reverse=True)

        # Enforce spatial diversity so layouts are structurally distinct
        selected: List[SpatialCandidate] = []
        for cand in candidates:
            if not selected:
                selected.append(cand)
            else:
                is_distinct = True
                for s in selected:
                    same_walls = sum(
                        1 for i in range(len(cand.fixtures))
                        if cand.fixtures[i].orientation == s.fixtures[i].orientation
                    )
                    if same_walls >= 2:
                        is_distinct = False
                        break
                if is_distinct:
                    selected.append(cand)

            if len(selected) >= count:
                break

        return selected


def build_design_matrix(room_w: float, room_l: float, door: Door, 
                        style: str = "Modern Minimalist", 
                        mode: str = "free_flow",
                        budget_limit: float = 350000) -> List[Dict[str, Any]]:
    """
    Main pipeline: Generates 3 layouts x 3 bundles = 9 complete design solutions.
    """
    tiers = ["Essential", "Sculptural", "High-Tech"]
    
    # Representative template items to determine initial spatial footprints
    base_toilet = _safe_get_product("toilet", style, "Essential")
    base_vanity = _safe_get_product("vanity", style, "Essential")
    base_shower = _safe_get_product("shower", style, "Essential")

    optimizer = LayoutOptimizer(room_w, room_l, door, mode=mode)
    top_layouts = optimizer.generate_top_layouts([base_toilet, base_vanity, base_shower], count=3)

    design_matrix = []

    for l_idx, layout in enumerate(top_layouts):
        for tier in tiers:
            # Safe retrieval with fallback to guarantee zero IndexError
            t_prod = _safe_get_product("toilet", style, tier)
            v_prod = _safe_get_product("vanity", style, tier)
            f_prod = _safe_get_product("faucet", style, tier)
            s_prod = _safe_get_product("shower", style, tier)

            bundle_items = [t_prod, v_prod, f_prod, s_prod]
            total_price = sum(item["price_inr"] for item in bundle_items)

            # Map the bundle fixtures onto the spatial coordinates established by the layout
            placed_manifest = [
                {"item": t_prod, "x": layout.fixtures[0].x, "y": layout.fixtures[0].y, "wall": layout.fixtures[0].orientation},
                {"item": v_prod, "x": layout.fixtures[1].x, "y": layout.fixtures[1].y, "wall": layout.fixtures[1].orientation},
                {"item": s_prod, "x": layout.fixtures[2].x, "y": layout.fixtures[2].y, "wall": layout.fixtures[2].orientation},
                {"item": f_prod, "x": layout.fixtures[1].x, "y": layout.fixtures[1].y, "wall": layout.fixtures[1].orientation}
            ]

            design_solution = {
                "design_id": f"L{l_idx+1}_{tier.upper()}",
                "layout_index": l_idx + 1,
                "tier": tier,
                "style": style,
                "macro_mode": mode,
                "total_price_inr": total_price,
                "within_budget": total_price <= budget_limit,
                "fitness_score": round(layout.fitness, 3),
                "sub_scores": {k: round(v, 2) for k, v in layout.scores.items()},
                "placed_fixtures": placed_manifest
            }
            design_matrix.append(design_solution)

    return design_matrix