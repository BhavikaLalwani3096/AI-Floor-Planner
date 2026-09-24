"""
visualizer_3d.py - Interactive 3D scene with physical privacy screens and architectural cutouts.
"""

import plotly.graph_objects as go
from typing import Dict, Any, List
from geometry import Door


def _create_3d_box(x: float, y: float, z: float, 
                   dx: float, dy: float, dz: float, 
                   name: str, color: str, opacity: float = 1.0) -> List[go.Mesh3d]:
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
        lighting=dict(ambient=0.7, diffuse=0.8, specular=0.3, roughness=0.3),
        hoverinfo="name"
    )
    return [mesh]


def render_3d_bathroom(design_solution: Dict[str, Any], 
                       room_w: float, 
                       room_l: float, 
                       door: Door,
                       window_wall: str = "north") -> go.Figure:
    fig = go.Figure()
    wall_color = "#94A3B8"
    thick = 0.2
    wall_h = 3.5

    # 1. Floor
    fig.add_trace(go.Mesh3d(
        x=[0, room_w, room_w, 0], y=[0, 0, room_l, room_l], z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3], color="#F1F5F9", name="Porcelain Floor", opacity=1.0
    ))

    # 2. Universal Parametric Walls
    # South
    if door.wall == "south":
        fig.add_traces(_create_3d_box(0, 0, 0, door.offset, thick, wall_h, "South Wall (L)", wall_color, 0.4))
        fig.add_traces(_create_3d_box(door.offset + door.width, 0, 0, room_w - (door.offset + door.width), thick, wall_h, "South Wall (R)", wall_color, 0.4))
    else:
        fig.add_traces(_create_3d_box(0, 0, 0, room_w, thick, wall_h, "South Wall", wall_color, 0.4))

    # North
    if door.wall == "north":
        fig.add_traces(_create_3d_box(0, room_l - thick, 0, door.offset, thick, wall_h, "North Wall (L)", wall_color, 0.4))
        fig.add_traces(_create_3d_box(door.offset + door.width, room_l - thick, 0, room_w - (door.offset + door.width), thick, wall_h, "North Wall (R)", wall_color, 0.4))
    else:
        fig.add_traces(_create_3d_box(0, room_l - thick, 0, room_w, thick, wall_h, "North Wall", wall_color, 0.4))

    # West
    if door.wall == "west":
        fig.add_traces(_create_3d_box(0, 0, 0, thick, door.offset, wall_h, "West Wall (B)", wall_color, 0.4))
        fig.add_traces(_create_3d_box(0, door.offset + door.width, 0, thick, room_l - (door.offset + door.width), wall_h, "West Wall (T)", wall_color, 0.4))
    else:
        fig.add_traces(_create_3d_box(0, 0, 0, thick, room_l, wall_h, "West Wall", wall_color, 0.4))

    # East
    if door.wall == "east":
        fig.add_traces(_create_3d_box(room_w - thick, 0, 0, thick, door.offset, wall_h, "East Wall (B)", wall_color, 0.4))
        fig.add_traces(_create_3d_box(room_w - thick, door.offset + door.width, 0, thick, room_l - (door.offset + door.width), wall_h, "East Wall (T)", wall_color, 0.4))
    else:
        fig.add_traces(_create_3d_box(room_w - thick, 0, 0, thick, room_l, wall_h, "East Wall", wall_color, 0.4))

    # 3. Privacy Partition Wall
    part = design_solution.get("partition")
    if part:
        fig.add_traces(_create_3d_box(part["x"], part["y"], 0.0, part["dx"], part["dy"], part["dz"], 
                                      "Frosted Glass Privacy Screen", "#38BDF8", 0.55))

    # 4. Placed Fixtures
    for p in design_solution["placed_fixtures"]:
        item = p["item"]
        cat = item["category"]
        x, y, wall_str = p["x"], p["y"], p["wall"]
        dx = item["depth"] if "west" in wall_str or "east" in wall_str else item["width"]
        dy = item["width"] if "west" in wall_str or "east" in wall_str else item["depth"]
        dz = item["height"]
        z = 0.3 if (cat == "toilet" and item.get("mount") == "wall_hung") else (0.6 if cat == "vanity" and item.get("mount") == "wall_hung" else 0.0)

        if cat == "toilet":
            col = "#09090B" if "Black" in item.get("finish", "") else "#FFFFFF"
            fig.add_traces(_create_3d_box(x, y, z, dx, dy, dz, item["name"], col, 0.98))
        elif cat == "vanity":
            col = "#78350F" if "Walnut" in item.get("finish", "") else "#1E293B"
            fig.add_traces(_create_3d_box(x, y, z, dx, dy, dz, item["name"], col, 0.95))
            fig.add_traces(_create_3d_box(x, y, z + dz + 0.2, dx, 0.05, 2.0, "Backlit Mirror", "#E0F2FE", 0.75))
        elif cat == "faucet":
            fig.add_traces(_create_3d_box(x + dx*0.3, y + dy*0.3, 2.8, 0.3, 0.3, 0.7, item["name"], "#0F172A", 1.0))
        elif cat == "shower":
            fig.add_traces(_create_3d_box(x, y, 0.0, dx, dy, dz, item["name"], "#BAE6FD", 0.35))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (ft)", range=[-0.5, room_w + 0.5]),
            yaxis=dict(title="Y (ft)", range=[-0.5, room_l + 0.5]),
            zaxis=dict(title="Z (ft)", range=[0, 8.5]),
            aspectmode="data",
            camera=dict(eye=dict(x=1.6, y=-1.6, z=1.4), center=dict(x=0, y=0, z=-0.2))
        ),
        margin=dict(l=0, r=0, b=0, t=10),
        showlegend=False
    )
    return fig