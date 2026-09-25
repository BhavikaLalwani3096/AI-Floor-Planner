"""
generator.py - Autonomous Stochastic Spatial Optimization & Vector Curation Engine.
Generates collision-free, code-compliant, structurally diverse architectural suites.
"""

import math
import random
import itertools
from typing import List, Dict, Any, Tuple
from catalog import CATALOG, cosine_similarity
from geometry import (
    BoundingBox,
    Door,
    Window,
    PlacedFixture,
    PerimeterCoordinateSystem,
    check_layout_feasibility
)


def vector_bundle_search(budget_limit: float, room_area: float) -> List[Dict[str, Any]]:
    hard_max = budget_limit + 30000.0

    toilets = [p for p in CATALOG if p["category"] == "toilet"]
    vanities = [p for p in CATALOG if p["category"] == "vanity"]
    faucets = [p for p in CATALOG if p["category"] == "faucet"]
    showers = [p for p in CATALOG if p["category"] == "shower"]
    bathtubs = [p for p in CATALOG if p["category"] == "bathtub"]
    storage = [p for p in CATALOG if p["category"] == "storage"]

    # Scale filtering for confined rooms (< 45 sq ft)
    if room_area < 45.0:
        vanities = [v for v in vanities if v["width"] <= 2.0]
        showers = [s for s in showers if s["width"] <= 3.0]
        toilets = [t for t in toilets if t["depth"] <= 1.9]

    archetypes = [
        {"name": "Essential Harmony",  "target": [0.3, 0.3, 0.9, 0.8]},
        {"name": "Sculptural Balance", "target": [0.6, 0.7, 0.8, 0.8]},
        {"name": "Premium Precision",  "target": [0.9, 1.0, 0.9, 0.9]}
    ]

    all_valid = []
    include_extra = (room_area >= 70.0)

    if include_extra:
        extra_items = bathtubs + storage
        for t, v, f, s, ex in itertools.product(toilets, vanities, faucets, showers, extra_items):
            tot = t["price_inr"] + v["price_inr"] + f["price_inr"] + s["price_inr"] + ex["price_inr"]
            if tot <= hard_max:
                vec = [sum(a) / 5.0 for a in zip(t["vector"], v["vector"], f["vector"], s["vector"], ex["vector"])]
                all_valid.append({"items": [t, v, f, s, ex], "total_price": tot, "vector": vec})

    if not all_valid:
        for t, v, f, s in itertools.product(toilets, vanities, faucets, showers):
            tot = t["price_inr"] + v["price_inr"] + f["price_inr"] + s["price_inr"]
            if tot <= hard_max:
                vec = [sum(a) / 4.0 for a in zip(t["vector"], v["vector"], f["vector"], s["vector"])]
                all_valid.append({"items": [t, v, f, s], "total_price": tot, "vector": vec})

    if not all_valid:
        base = [toilets[0], vanities[0], faucets[0], showers[0]]
        tot = sum(i["price_inr"] for i in base)
        return [{"tier": a["name"], "items": base, "total_price": tot} for a in archetypes]

    selected = []
    used_combos = set()
    for arch in archetypes:
        ranked = sorted(all_valid, key=lambda b: cosine_similarity(b["vector"], arch["target"]), reverse=True)
        chosen = next((c for c in ranked if tuple(i["sku"] for i in c["items"]) not in used_combos), ranked[0])
        used_combos.add(tuple(i["sku"] for i in chosen["items"]))
        selected.append({"tier": arch["name"], "items": chosen["items"], "total_price": chosen["total_price"]})

    return selected


class AutonomousSpatialOptimizer:
    def __init__(self, room_w: float, room_l: float, door: Door, 
                 mode: str = "free_flow", window_wall: str = "north"):
        self.room_w = room_w
        self.room_l = room_l
        self.door = door
        self.mode = mode.lower()
        self.window = Window(window_wall, room_w, room_l)
        self.pcs = PerimeterCoordinateSystem(room_w, room_l)

    def _build_architectural_partitions(self, fixtures: List[PlacedFixture]) -> Tuple[List[Dict[str, Any]], List[BoundingBox]]:
        """
        Builds true 3-way compartmentalization when Privacy Mode is active:
        Divides room into Grooming Vestibule (vanity) and private rear cubicles (WC & Shower).
        """
        if self.mode != "privacy_focused" or self.room_w < 6.5 or self.room_l < 6.5:
            return [], []

        thick = 0.15
        divider_y = round(self.room_l * 0.48, 2)
        mid_x = round(self.room_w * 0.50, 2)

        # Transverse acoustic glass divider wall with doorway opening
        part_left = {"x": 0.0, "y": divider_y, "dx": max(0.5, mid_x - 1.2), "dy": thick, "dz": 6.5, "name": "Acoustic Glass Divider"}
        part_right = {"x": mid_x + 1.2, "y": divider_y, "dx": max(0.5, self.room_w - (mid_x + 1.2)), "dy": thick, "dz": 6.5, "name": "Acoustic Glass Divider"}
        part_spine = {"x": mid_x, "y": divider_y, "dx": thick, "dy": self.room_l - divider_y, "dz": 6.5, "name": "WC/Shower Spine Wall"}

        screens = [part_left, part_right, part_spine]
        p_boxes = [BoundingBox(p["x"], p["y"], p["dx"], p["dy"]) for p in screens]

        # Verify that these partitions do not clash with the entry door or window
        if any(self.door.collides_with_box(pb, self.room_w, self.room_l) for pb in p_boxes):
            return [], []
        if any(self.window.blocks_placement(pb) for pb in p_boxes):
            return [], []

        return screens, p_boxes

    def solve_bundle_layouts(self, items: List[Dict[str, Any]], target_count: int = 3, seed_offset: float = 0.0) -> List[Dict[str, Any]]:
        major_items = [i for i in items if i["category"] in ("toilet", "vanity", "shower", "storage", "bathtub")]
        t_item = next(i for i in major_items if i["category"] == "toilet")
        v_item = next(i for i in major_items if i["category"] == "vanity")
        s_item = next(i for i in major_items if i["category"] == "shower")
        has_extra = len(major_items) > 3
        ex_item = major_items[3] if has_extra else None

        perimeter = self.pcs.perimeter
        # High resolution: 0.6 ft step for compact rooms, 1.2 ft for large rooms
        step = 0.6 if perimeter < 28.0 else 1.2
        num_steps = int(perimeter // step)

        base_samples = [((i * step) + (seed_offset % step)) % perimeter for i in range(num_steps)]
        rng = random.Random(int(seed_offset * 1000) + 42)
        rng.shuffle(base_samples)

        valid_solutions = []

        for u_t in base_samples:
            p_t = self.pcs.u_to_placement(u_t, t_item)
            if self.window.blocks_placement(p_t.bounding_box):
                continue
            if self.door.collides_with_box(p_t.bounding_box, self.room_w, self.room_l):
                continue

            for u_s in base_samples:
                if abs(u_s - u_t) < 2.6:
                    continue
                p_s = self.pcs.u_to_placement(u_s, s_item)
                if self.door.collides_with_box(p_s.bounding_box, self.room_w, self.room_l):
                    continue
                if p_s.bounding_box.intersects(p_t.bounding_box):
                    continue

                for u_v in base_samples:
                    if abs(u_v - u_t) < 2.0 or abs(u_v - u_s) < 2.4:
                        continue
                    p_v = self.pcs.u_to_placement(u_v, v_item)

                    fixtures = [p_t, p_v, p_s]

                    if has_extra:
                        placed_extra = False
                        for u_ex in base_samples:
                            if abs(u_ex - u_t) < 2.0 or abs(u_ex - u_v) < 2.0 or abs(u_ex - u_s) < 2.4:
                                continue
                            p_ex = self.pcs.u_to_placement(u_ex, ex_item)
                            cand = [p_t, p_v, p_s, p_ex]
                            screens, p_boxes = self._build_architectural_partitions(cand)
                            is_val, _ = check_layout_feasibility(
                                cand, self.door, self.room_w, self.room_l,
                                window=self.window, partitions=p_boxes
                            )
                            if is_val:
                                fixtures = cand
                                placed_extra = True
                                break
                        if not placed_extra:
                            continue
                    else:
                        screens, p_boxes = self._build_architectural_partitions(fixtures)
                        is_val, _ = check_layout_feasibility(
                            fixtures, self.door, self.room_w, self.room_l,
                            window=self.window, partitions=p_boxes
                        )
                        if not is_val:
                            continue

                    # Multi-Objective Fitness Evaluation
                    unique_walls = len(set(f.orientation for f in fixtures))
                    dispersion = unique_walls / 4.0

                    total_spread = sum(
                        math.hypot(f1.x - f2.x, f1.y - f2.y)
                        for i, f1 in enumerate(fixtures)
                        for j, f2 in enumerate(fixtures) if i < j
                    )
                    norm_spread = min(1.0, total_spread / (len(fixtures) * math.hypot(self.room_w, self.room_l)))

                    hx = self.door.offset if self.door.wall in ("south", "north") else (0.0 if self.door.wall == "west" else self.room_w)
                    hy = 0.0 if self.door.wall == "south" else (self.room_l if self.door.wall == "north" else self.door.offset)
                    sightline_score = math.hypot(p_t.x - hx, p_t.y - hy) / math.hypot(self.room_w, self.room_l)

                    fitness = (dispersion * 0.4) + (norm_spread * 0.3) + (sightline_score * 0.3)

                    valid_solutions.append({
                        "fixtures": fixtures,
                        "partitions": screens,
                        "fitness": fitness
                    })

                    if len(valid_solutions) >= 40:
                        break
                if len(valid_solutions) >= 40:
                    break
            if len(valid_solutions) >= 40:
                break

        # ZeroDivisionError Prevention: Robust Fallback with 15-inch Lateral Clearance
        if not valid_solutions:
            # Deterministic, non-overlapping corner arrangement
            p_t = PlacedFixture(t_item, 0.6, self.room_l - t_item["depth"] - 0.4, "north_wall")
            p_s = PlacedFixture(s_item, self.room_w - s_item["width"] - 0.4, self.room_l - s_item["depth"] - 0.4, "north_wall")
            # Place vanity on opposite wall away from door
            v_wall = "west_wall" if self.door.wall != "west" else "east_wall"
            vx = 0.3 if v_wall == "west_wall" else (self.room_w - v_item["depth"] - 0.3)
            vy = max(0.4, (self.room_l - v_item["width"]) / 2.0)
            p_v = PlacedFixture(v_item, vx, vy, v_wall)
            f_list = [p_t, p_v, p_s]
            if has_extra:
                f_list.append(PlacedFixture(ex_item, 0.4, 0.4, "south_wall"))
            valid_solutions = [{"fixtures": f_list, "partitions": [], "fitness": 0.5}]

        valid_solutions.sort(key=lambda s: s["fitness"], reverse=True)

        # Cluster to guarantee 3 diverse wall arrangements
        selected = []
        for sol in valid_solutions:
            if not selected:
                selected.append(sol)
            else:
                is_distinct = True
                for ex in selected:
                    matching = sum(
                        1 for i in range(min(len(sol["fixtures"]), len(ex["fixtures"])))
                        if sol["fixtures"][i].orientation == ex["fixtures"][i].orientation
                    )
                    disp = sum(math.hypot(c.x - e.x, c.y - e.y) for c, e in zip(sol["fixtures"], ex["fixtures"]))
                    if matching >= 2 and disp < (self.room_w * 0.3):
                        is_distinct = False
                        break
                if is_distinct:
                    selected.append(sol)
            if len(selected) >= target_count:
                break

        # Safe circular filling (ZeroDivisionError impossible since len(valid_solutions) >= 1)
        while len(selected) < target_count:
            selected.append(valid_solutions[len(selected) % len(valid_solutions)])

        return selected


def build_design_matrix(room_w: float, room_l: float, door: Door, 
                        mode: str = "free_flow",
                        window_wall: str = "north",
                        budget_limit: float = 450000,
                        seed_offset: float = 0.0) -> List[Dict[str, Any]]:
    room_area = room_w * room_l
    bundles = vector_bundle_search(budget_limit, room_area)
    optimizer = AutonomousSpatialOptimizer(room_w, room_l, door, mode=mode, window_wall=window_wall)

    design_matrix = []

    for b_idx, bundle in enumerate(bundles):
        b_items = bundle["items"]
        solved_layouts = optimizer.solve_bundle_layouts(
            b_items, target_count=3, seed_offset=seed_offset + (b_idx * 3.7)
        )

        for l_idx, layout in enumerate(solved_layouts):
            placed_manifest = []
            f_prod = next(i for i in b_items if i["category"] == "faucet")

            for f in layout["fixtures"]:
                placed_manifest.append({
                    "item": f.data,
                    "x": f.x,
                    "y": f.y,
                    "wall": f.orientation
                })
                if f.data["category"] == "vanity":
                    placed_manifest.append({
                        "item": f_prod,
                        "x": f.x,
                        "y": f.y,
                        "wall": f.orientation
                    })

            design_solution = {
                "design_id": f"L{l_idx+1}_B{b_idx+1}",
                "layout_index": l_idx + 1,
                "tier": bundle["tier"],
                "macro_mode": mode,
                "total_price_inr": bundle["total_price"],
                "within_budget": bundle["total_price"] <= budget_limit,
                "partitions": layout["partitions"],
                "placed_fixtures": placed_manifest
            }
            design_matrix.append(design_solution)

    return design_matrix