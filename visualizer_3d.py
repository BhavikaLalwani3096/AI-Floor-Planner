"""
visualizer_3d.py - Interactive 3D WebGL Bathroom Visualizer using Plotly.
Renders architectural cutaways, fenestration, door gaps, true 3D fixtures, and mirrors.
"""

import plotly.graph_objects as go
from typing import Dict, Any, List
from geometry import Door


def _create_3d_box(x: float, y: float, z: float, 
                   dx: float, dy: float, dz: float, 
                   name: str, color: str, opacity: float = 1.0) -> List[go.Mesh3d]:
    """Generates a 3D rectangular mesh representing a fixture or architectural element."""
    vx = [x, x + dx, x + dx, x, x, x + dx, x + dx, x]
    vy = [y, y, y + dy, y + dy, y, y, y + dy, y + dy]
    vz = [z, z, z, z, z + dz, z + dz, z + dz, z + dz]

    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    mesh = go.Mesh3d(
        x=vx, y=vy, z=vz,
        i=i, j=j, k=k,
        name=name,
        color=color,
        opacity=opacity,
        flatshading=True,
        lighting=dict(ambient=0.65, diffuse=0.85, specular=0.4, roughness=0.2),
        hoverinfo="name"
    )
    return [mesh]


def render_3d_bathroom(design_solution: Dict[str, Any], 
                       room_w: float, 
                       room_l: float, 
                       door: Door = None,
                       room_h: float = 8.5) -> go.Figure:
    """
    Renders an interactive 3D scene with architectural openings, true fixture elevations,
    and showroom material aesthetics.
    """
    fig = go.Figure()

    # 1. Neutral Porcelain Floor Slab
    fig.add_trace(go.Mesh3d(
        x=[0, room_w, room_w, 0],
        y=[0, 0, room_l, room_l],
        z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color="#F3F4F6",
        name="Porcelain Floor Tile",
        opacity=1.0
    ))

    # 2. Architectural Walls with Door Opening Gap
    wall_color = "#9CA3AF"
    wall_thick = 0.2
    wall_h = 3.5  # Architect cutaway height for clear internal visibility

    # South Wall (Carve out the door passage if present)
    if door and door.wall == "south":
        door_start = door.offset
        door_end = door.offset + door.width

        # Segment left of door
        if door_start > 0.05:
            fig.add_traces(_create_3d_box(0, 0, 0, door_start, wall_thick, wall_h, "South Wall (Left)", wall_color, 0.4))
        # Segment right of door
        if door_end < (room_w - 0.05):
            fig.add_traces(_create_3d_box(door_end, 0, 0, room_w - door_end, wall_thick, wall_h, "South Wall (Right)", wall_color, 0.4))
        # Door Threshold Line (warm wood / dark bronze indicator)
        fig.add_traces(_create_3d_box(door_start, 0, 0.02, door.width, wall_thick, 0.05, f"Entry Door ({door.door_type})", "#4B5563", 0.9))
    else:
        fig.add_traces(_create_3d_box(0, 0, 0, room_w, wall_thick, wall_h, "South Wall", wall_color, 0.4))

    # North Wall (Carve daylight window slot)
    win_w = 3.0
    win_start = (room_w - win_w) / 2.0
    fig.add_traces(_create_3d_box(0, room_l - wall_thick, 0, win_start, wall_thick, wall_h, "North Wall (Left)", wall_color, 0.4))
    fig.add_traces(_create_3d_box(win_start + win_w, room_l - wall_thick, 0, room_w - (win_start + win_w), wall_thick, wall_h, "North Wall (Right)", wall_color, 0.4))
    # Window glass pane
    fig.add_traces(_create_3d_box(win_start, room_l - wall_thick, 1.8, win_w, wall_thick, 1.5, "Exterior Daylight Window", "#93C5FD", 0.5))

    # East & West Walls
    fig.add_traces(_create_3d_box(0, 0, 0, wall_thick, room_l, wall_h, "West Wall", wall_color, 0.4))
    fig.add_traces(_create_3d_box(room_w - wall_thick, 0, 0, wall_thick, room_l, wall_h, "East Wall", wall_color, 0.4))

    # 3. Fixtures & Material Meshes
    for p in design_solution["placed_fixtures"]:
        item = p["item"]
        cat = item["category"]
        x = p["x"]
        y = p["y"]
        wall = p["wall"]
        
        if wall in ("south_wall", "north_wall"):
            dx = item["width"]
            dy = item["depth"]
        else:
            dx = item["depth"]
            dy = item["width"]

        dz = item["height"]
        z = 0.0

        if cat == "toilet":
            z = 0.3 if item.get("mount") == "wall_hung" else 0.0
            color = "#111827" if "Black" in item.get("finish", "") else "#FFFFFF"
            fig.add_traces(_create_3d_box(x, y, z, dx, dy, dz, f"{item['name']}", color, 0.98))

        elif cat == "vanity":
            z = 0.6 if item.get("mount") == "wall_hung" else 0.0
            color = "#78350F" if "Walnut" in item.get("finish", "") else "#1F2937"
            fig.add_traces(_create_3d_box(x, y, z, dx, dy, dz, f"{item['name']}", color, 0.95))

            # Floating Architectural Mirror above vanity
            mirror_h = 2.4
            mirror_thick = 0.05
            if wall == "south_wall":
                fig.add_traces(_create_3d_box(x, y + 0.1, z + dz + 0.3, dx, mirror_thick, mirror_h, "Backlit LED Mirror", "#E0F2FE", 0.8))
            elif wall == "north_wall":
                fig.add_traces(_create_3d_box(x, y + dy - 0.15, z + dz + 0.3, dx, mirror_thick, mirror_h, "Backlit LED Mirror", "#E0F2FE", 0.8))
            elif wall == "west_wall":
                fig.add_traces(_create_3d_box(x + 0.1, y, z + dz + 0.3, mirror_thick, dy, mirror_h, "Backlit LED Mirror", "#E0F2FE", 0.8))
            elif wall == "east_wall":
                fig.add_traces(_create_3d_box(x + dx - 0.15, y, z + dz + 0.3, mirror_thick, dy, mirror_h, "Backlit LED Mirror", "#E0F2FE", 0.8))

        elif cat == "faucet":
            # Countertop elevation
            z = 2.8
            color = "#000000" if "Black" in item.get("finish", "") else "#F59E0B"
            fig.add_traces(_create_3d_box(x + 0.2, y + 0.2, z, 0.3, 0.3, 0.8, f"{item['name']}", color, 1.0))

        elif cat == "shower":
            # Glass enclosure with subtle blue tint
            color = "#BAE6FD"
            opacity = 0.35
            fig.add_traces(_create_3d_box(x, y, z, dx, dy, dz, f"{item['name']}", color, opacity))

    fig.update_layout(
        title=f"Kohler 3D Spatial Visualizer - {design_solution['design_id']} ({design_solution['tier']} Tier)",
        scene=dict(
            xaxis=dict(title="Width (ft)", range=[-0.5, room_w + 0.5], showgrid=True),
            yaxis=dict(title="Length (ft)", range=[-0.5, room_l + 0.5], showgrid=True),
            zaxis=dict(title="Height (ft)", range=[0, room_h], showgrid=True),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.5, y=-1.5, z=1.4),
                center=dict(x=0, y=0, z=-0.2)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        showlegend=False
    )

    return fig