"""
visualizer_2d.py - 2D Architectural Blueprint Floor Plan using Matplotlib.
Draws precise walls, dynamic door swing arcs, clearance zones, and fixture dimensions.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, Any
from geometry import Door


def render_2d_blueprint(design_solution: Dict[str, Any], 
                        room_w: float, 
                        room_l: float, 
                        door: Door) -> plt.Figure:
    """
    Renders an architectural blueprint plan with clearance buffer envelopes
    and door swing physics.
    """
    fig, ax = plt.subplots(figsize=(7, 7), dpi=100)

    # 1. Room Boundary Walls
    ax.plot([0, room_w, room_w, 0, 0], [0, 0, room_l, room_l, 0], color="#111827", linewidth=3)
    ax.fill([0, room_w, room_w, 0], [0, 0, room_l, room_l], color="#F9FAFB")

    # 2. Door Visualization
    if door.wall == "south":
        d_x = door.offset
        d_y = 0.0
        d_w = door.width

        # Clear the opening wall segment
        ax.plot([d_x, d_x + d_w], [0, 0], color="#F9FAFB", linewidth=4)

        if door.door_type == "swing_inward":
            # Door Leaf
            ax.plot([d_x, d_x], [0, d_w], color="#2563EB", linewidth=2.5)
            # Door Swing Arc
            arc = patches.Arc((d_x, 0), d_w * 2, d_w * 2, angle=0, theta1=0, theta2=90, 
                              color="#3B82F6", linestyle="--", linewidth=1.5)
            ax.add_patch(arc)
        elif door.door_type == "sliding":
            # Sliding track symbol
            ax.plot([d_x, d_x + d_w], [-0.15, -0.15], color="#10B981", linewidth=3, linestyle="-")
            ax.text(d_x + (d_w / 2.0), -0.4, "SLIDING TRACK", color="#059669", fontsize=8, ha="center")

    # 3. Fixtures with Clearance Boxes
    color_map = {
        "toilet": "#3B82F6",   # Blue
        "vanity": "#D97706",   # Amber / Wood
        "shower": "#06B6D4",   # Cyan
        "faucet": "#4B5563"    # Grey
    }

    for p in design_solution["placed_fixtures"]:
        item = p["item"]
        cat = item["category"]
        if cat == "faucet":
            continue  # Faucet sits on vanity; avoid cluttering 2D box

        x = p["x"]
        y = p["y"]
        wall = p["wall"]

        if wall in ("south_wall", "north_wall"):
            w = item["width"]
            d = item["depth"]
        else:
            w = item["depth"]
            d = item["width"]

        # Activity Clearance Envelope (dashed box)
        front_buf = item.get("clearance_front", 2.0)
        c_x, c_y, c_w, c_d = x, y, w, d
        if wall == "south_wall":
            c_d += front_buf
        elif wall == "north_wall":
            c_y -= front_buf
            c_d += front_buf
        elif wall == "west_wall":
            c_w += front_buf
        elif wall == "east_wall":
            c_x -= front_buf
            c_w += front_buf

        # Draw clearance box
        clearance_rect = patches.Rectangle(
            (c_x, c_y), c_w, c_d,
            linewidth=1, linestyle=":", edgecolor="#9CA3AF", facecolor="#E5E7EB", alpha=0.3
        )
        ax.add_patch(clearance_rect)

        # Draw Physical Fixture Footprint
        color = color_map.get(cat, "#6B7280")
        fixture_rect = patches.Rectangle(
            (x, y), w, d,
            linewidth=1.8, edgecolor="#1F2937", facecolor=color, alpha=0.85
        )
        ax.add_patch(fixture_rect)

        # Label inside fixture box
        ax.text(x + (w / 2.0), y + (d / 2.0), f"{item['name'][:12]}..\n({w:.1f}x{d:.1f}')",
                color="white", fontsize=7.5, weight="bold", ha="center", va="center")

    # Plot Settings
    ax.set_xlim(-1.0, room_w + 1.0)
    ax.set_ylim(-1.0, room_l + 1.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Plan View Blueprint - {design_solution['design_id']} ({design_solution['tier']} Tier)", 
                 fontsize=12, weight="bold", pad=15)

    plt.tight_layout()
    return fig