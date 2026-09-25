"""
visualizer_2d.py - Universal 2D Blueprint with 3-cell architectural privacy partitions.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, Any
from geometry import Door


def render_2d_blueprint(design_solution: Dict[str, Any], 
                        room_w: float, 
                        room_l: float, 
                        door: Door) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)

    # 1. Floor & Boundary Walls
    ax.plot([0, room_w, room_w, 0, 0], [0, 0, room_l, room_l, 0], color="#0F172A", linewidth=3)
    ax.fill([0, room_w, room_w, 0], [0, 0, room_l, room_l], color="#F8FAFC")

    # 2. Universal Door Openings across all 4 walls
    dw = door.width
    do = door.offset
    wall = door.wall

    if wall == "south":
        p_door = (do, 0.0)
        ax.plot([do, do + dw], [0, 0], color="#F8FAFC", linewidth=4)
        if door.door_type == "swing_inward":
            ax.plot([do, do], [0, dw], color="#2563EB", linewidth=2)
            ax.add_patch(patches.Arc(p_door, dw * 2, dw * 2, angle=0, theta1=0, theta2=90, color="#3B82F6", linestyle="--"))
        elif door.door_type == "sliding":
            ax.plot([do, do + dw], [-0.15, -0.15], color="#10B981", linewidth=3)
    elif wall == "north":
        p_door = (do, room_l)
        ax.plot([do, do + dw], [room_l, room_l], color="#F8FAFC", linewidth=4)
        if door.door_type == "swing_inward":
            ax.plot([do, do], [room_l, room_l - dw], color="#2563EB", linewidth=2)
            ax.add_patch(patches.Arc(p_door, dw * 2, dw * 2, angle=0, theta1=270, theta2=360, color="#3B82F6", linestyle="--"))
        elif door.door_type == "sliding":
            ax.plot([do, do + dw], [room_l + 0.15, room_l + 0.15], color="#10B981", linewidth=3)
    elif wall == "west":
        p_door = (0.0, do)
        ax.plot([0, 0], [do, do + dw], color="#F8FAFC", linewidth=4)
        if door.door_type == "swing_inward":
            ax.plot([0, dw], [do, do], color="#2563EB", linewidth=2)
            ax.add_patch(patches.Arc(p_door, dw * 2, dw * 2, angle=0, theta1=0, theta2=90, color="#3B82F6", linestyle="--"))
        elif door.door_type == "sliding":
            ax.plot([-0.15, -0.15], [do, do + dw], color="#10B981", linewidth=3)
    elif wall == "east":
        p_door = (room_w, do)
        ax.plot([room_w, room_w], [do, do + dw], color="#F8FAFC", linewidth=4)
        if door.door_type == "swing_inward":
            ax.plot([room_w - dw, room_w], [do, do], color="#2563EB", linewidth=2)
            ax.add_patch(patches.Arc(p_door, dw * 2, dw * 2, angle=0, theta1=90, theta2=180, color="#3B82F6", linestyle="--"))
        elif door.door_type == "sliding":
            ax.plot([room_w + 0.15, room_w + 0.15], [do, do + dw], color="#10B981", linewidth=3)

    # 3. Privacy Compartments (WC Cell & Wet Cell)
    partitions = design_solution.get("partitions", [])
    for part in partitions:
        ax.add_patch(patches.Rectangle(
            (part["x"], part["y"]), part["dx"], part["dy"],
            linewidth=2, edgecolor="#0284C7", facecolor="#BAE6FD", alpha=0.6
        ))
        ax.text(part["x"] + part["dx"]/2.0, part["y"] + part["dy"]/2.0, "SCREEN", 
                color="#0369A1", fontsize=6, weight="bold", ha="center", va="center")

    # 4. Placed Fixtures
    color_map = {"toilet": "#3B82F6", "vanity": "#D97706", "shower": "#06B6D4"}
    for p in design_solution["placed_fixtures"]:
        item = p["item"]
        cat = item["category"]
        if cat == "faucet":
            continue

        x, y, wall_str = p["x"], p["y"], p["wall"]
        w = item["depth"] if "west" in wall_str or "east" in wall_str else item["width"]
        d = item["width"] if "west" in wall_str or "east" in wall_str else item["depth"]

        rect = patches.Rectangle((x, y), w, d, linewidth=1.5, edgecolor="#1E293B", facecolor=color_map.get(cat, "#64748B"), alpha=0.9)
        ax.add_patch(rect)
        ax.text(x + w/2.0, y + d/2.0, f"{item['name'][:12]}\n{w:.1f}x{d:.1f}'", color="white", fontsize=7, ha="center", va="center", weight="bold")

    ax.set_xlim(-1.0, room_w + 1.0)
    ax.set_ylim(-1.0, room_l + 1.0)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    return fig