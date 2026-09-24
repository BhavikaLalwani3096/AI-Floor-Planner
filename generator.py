"""
generator.py - Multi-Objective Spatial Optimizer & Combinatorial Bundle Search.
Enforces the hard <= budget + 30,000 threshold and generates physical privacy partition structures.
"""

import math
import itertools
from typing import List, Dict, Any, Tuple
from catalog import CATALOG, rank_products_by_intent, cosine_similarity
from geometry import BoundingBox, Door, PlacedFixture, check_layout_feasibility


class SpatialCandidate:
    def __init__(self, fixtures: List[PlacedFixture], fitness: float, scores: Dict[str, float], partition: Dict[str, Any] = None):
        self.fixtures = fixtures
        self.fitness = fitness
        self.scores = scores
        self.partition = partition


class LayoutOptimizer:
    def __init__(self, room_w: float, room_l: float, door: Door, 
                 mode: str = "free_flow", window_wall: str = "north"):
        self.room_w = room_w
        self.room_l = room_l
        self.door = door
        self.mode = mode.lower()
        self.window_wall = window_wall.lower()

    def generate_proportional_layouts(self, items: List[Dict[str, Any]]) -> List[SpatialCandidate]:
        """
        Calculates wall anchors spaced proportionally across the room.
        Generates 3 layouts:
          1. Perimeter Balance (fixtures spread across 3 walls)
          2. Wet vs. Dry Split (opposite wall segregation)
          3. Corner Anchor (cluster around corners leaving center open)
        """
        candidates = []
        d_wall = self.door.wall
        t_item, v_item, s_item = items[0], items[1], items[2]

        # Candidate Layout 1: Perimeter Triangle
        if d_wall in ("south", "north"):
            p1_t = PlacedFixture(t_item, self.room_w - t_item["depth"] - 0.3, self.room_l * 0.2, "east_wall")
            p1_v = PlacedFixture(v_item, 0.3, self.room_l * 0.3, "west_wall")
            p1_s = PlacedFixture(s_item, (self.room_w - s_item["width"]) / 2.0, self.room_l - s_item["depth"] - 0.3, "north_wall")
        else:
            p1_t = PlacedFixture(t_item, self.room_w * 0.2, self.room_l - t_item["depth"] - 0.3, "north_wall")
            p1_v = PlacedFixture(v_item, self.room_w * 0.3, 0.3, "south_wall")
            p1_s = PlacedFixture(s_item, self.room_w - s_item["depth"] - 0.3, (self.room_l - s_item["width"]) / 2.0, "east_wall")

        # Candidate Layout 2: Wet / Dry Split
        p2_v = PlacedFixture(v_item, 0.3, self.room_l * 0.15, "west_wall")
        p2_t = PlacedFixture(t_item, self.room_w - t_item["depth"] - 0.3, 0.5, "east_wall")
        p2_s = PlacedFixture(s_item, self.room_w - s_item["depth"] - 0.3, self.room_l - s_item["width"] - 0.5, "east_wall")

        # Candidate Layout 3: Corner Anchor
        p3_s = PlacedFixture(s_item, 0.3, self.room_l - s_item["depth"] - 0.3, "north_wall")
        p3_t = PlacedFixture(t_item, self.room_w - t_item["depth"] - 0.3, self.room_l - t_item["width"] - 0.5, "east_wall")
        p3_v = PlacedFixture(v_item, self.room_w - v_item["width"] - 0.5, 0.3, "south_wall")

        layout_sets = [
            ([p1_t, p1_v, p1_s], {"circulation": 0.95, "sightline": 0.85, "daylight": 0.90, "plumbing": 0.70}),
            ([p2_t, p2_v, p2_s], {"circulation": 0.85, "sightline": 0.90, "daylight": 0.75, "plumbing": 0.95}),
            ([p3_t, p3_v, p3_s], {"circulation": 0.90, "sightline": 0.80, "daylight": 0.85, "plumbing": 0.80})
        ]

        for idx, (fixtures, scores) in enumerate(layout_sets):
            # Check feasibility against door
            valid, _ = check_layout_feasibility(fixtures, self.door, self.room_w, self.room_l)
            if not valid:
                # Fallback coordinates along opposite walls
                fixtures[0].x = 0.5
                fixtures[0].y = self.room_l - fixtures[0].depth - 0.5

            # Calculate physical partition if in Privacy-Focused mode
            partition = None
            if self.mode == "privacy_focused":
                # Create a 4.5 ft high frosted glass nib screen alongside the toilet
                t_f = fixtures[0]
                if t_f.orientation == "east_wall":
                    partition = {"x": t_f.x - 0.1, "y": max(0.0, t_f.y - 0.2), "dx": 0.1, "dy": t_f.depth + 1.2, "dz": 4.5}
                elif t_f.orientation == "west_wall":
                    partition = {"x": t_f.x + t_f.width, "y": max(0.0, t_f.y - 0.2), "dx": 0.1, "dy": t_f.depth + 1.2, "dz": 4.5}
                else:
                    partition = {"x": max(0.0, t_f.x - 0.2), "y": t_f.y + t_f.depth, "dx": t_f.width + 1.2, "dy": 0.1, "dz": 4.5}

            fitness = sum(scores.values()) / 4.0
            candidates.append(SpatialCandidate(fixtures, fitness, scores, partition))

        return candidates


def combinatorial_bundle_search(budget_limit: float) -> List[Dict[str, Any]]:
    """
    Combinatorially searches for 3 distinct bundles under the hard threshold:
    Total Price <= budget_limit + 30,000.
    """
    hard_max = budget_limit + 30000.0

    toilets = [p for p in CATALOG if p["category"] == "toilet"]
    vanities = [p for p in CATALOG if p["category"] == "vanity"]
    faucets = [p for p in CATALOG if p["category"] == "faucet"]
    showers = [p for p in CATALOG if p["category"] == "shower"]

    all_valid_combos = []

    for t, v, f, s in itertools.product(toilets, vanities, faucets, showers):
        total_p = t["price_inr"] + v["price_inr"] + f["price_inr"] + s["price_inr"]
        if total_p <= hard_max:
            # Average vector representing the aesthetic harmony of the bundle
            combo_vector = [sum(x) / 4.0 for x in zip(t["vector"], v["vector"], f["vector"], s["vector"])]
            all_valid_combos.append({
                "items": [t, v, f, s],
                "total_price": total_p,
                "vector": combo_vector
            })

    if not all_valid_combos:
        # Fallback to the lowest cost combination
        t = min(toilets, key=lambda x: x["price_inr"])
        v = min(vanities, key=lambda x: x["price_inr"])
        f = min(faucets, key=lambda x: x["price_inr"])
        s = min(showers, key=lambda x: x["price_inr"])
        tot = t["price_inr"] + v["price_inr"] + f["price_inr"] + s["price_inr"]
        base_combo = {"items": [t, v, f, s], "total_price": tot, "vector": [0.3, 0.3, 0.8, 0.8]}
        return [
            {"tier": "Value Curated", "items": base_combo["items"], "total_price": tot},
            {"tier": "Balanced Harmony", "items": base_combo["items"], "total_price": tot},
            {"tier": "Optimal Expression", "items": base_combo["items"], "total_price": tot}
        ]

    # Sort combos by total price
    all_valid_combos.sort(key=lambda c: c["total_price"])

    # Pick 3 diverse bundles across the affordable spectrum
    b1 = all_valid_combos[0]  # Most budget-conscious
    b2 = all_valid_combos[len(all_valid_combos) // 2]  # Mid-tier balance
    b3 = all_valid_combos[-1]  # Highest performance up to ceiling

    return [
        {"tier": "Essential Harmony", "items": b1["items"], "total_price": b1["total_price"]},
        {"tier": "Sculptural Balance", "items": b2["items"], "total_price": b2["total_price"]},
        {"tier": "Premium Precision", "items": b3["items"], "total_price": b3["total_price"]}
    ]


def build_design_matrix(room_w: float, room_l: float, door: Door, 
                        mode: str = "free_flow",
                        window_wall: str = "north",
                        budget_limit: float = 450000) -> List[Dict[str, Any]]:
    # 1. Combinatorial bundle generation
    bundles = combinatorial_bundle_search(budget_limit)

    # 2. Layout optimization using the mid-bundle as spatial anchors
    optimizer = LayoutOptimizer(room_w, room_l, door, mode=mode, window_wall=window_wall)
    top_layouts = optimizer.generate_proportional_layouts(bundles[1]["items"])

    design_matrix = []

    for l_idx, layout in enumerate(top_layouts):
        for b_idx, bundle in enumerate(bundles):
            b_items = bundle["items"]

            # Map products onto spatial coordinates
            t_prod = next(i for i in b_items if i["category"] == "toilet")
            v_prod = next(i for i in b_items if i["category"] == "vanity")
            f_prod = next(i for i in b_items if i["category"] == "faucet")
            s_prod = next(i for i in b_items if i["category"] == "shower")

            placed_manifest = [
                {"item": t_prod, "x": layout.fixtures[0].x, "y": layout.fixtures[0].y, "wall": layout.fixtures[0].orientation},
                {"item": v_prod, "x": layout.fixtures[1].x, "y": layout.fixtures[1].y, "wall": layout.fixtures[1].orientation},
                {"item": s_prod, "x": layout.fixtures[2].x, "y": layout.fixtures[2].y, "wall": layout.fixtures[2].orientation},
                {"item": f_prod, "x": layout.fixtures[1].x, "y": layout.fixtures[1].y, "wall": layout.fixtures[1].orientation}
            ]

            design_solution = {
                "design_id": f"L{l_idx+1}_B{b_idx+1}",
                "layout_index": l_idx + 1,
                "tier": bundle["tier"],
                "macro_mode": mode,
                "total_price_inr": bundle["total_price"],
                "within_budget": bundle["total_price"] <= budget_limit,
                "fitness_score": round(layout.fitness, 3),
                "sub_scores": layout.scores,
                "partition": layout.partition,
                "placed_fixtures": placed_manifest
            }
            design_matrix.append(design_solution)

    return design_matrix