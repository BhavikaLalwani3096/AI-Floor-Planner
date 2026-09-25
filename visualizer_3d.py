"""
visualizer_3d.py - Interactive 3D scene with 3-cell architectural compartments and flush mirrors.
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

    # 1. Neutral Porcelain Floor
    fig.add_trace(go.Mesh3d(
        x=[0, room_w, room_w, 0], y=[0, 0, room_l, room_l], z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3], color="#F8FAFC", name="Porcelain Floor", opacity=1.0
    ))

    # 2. Universal Parametric Outer Walls with Door Openings
    for wall_name in ["south", "north", "west", "east"]:
        is_door = (door.wall == wall_name)
        if wall_name == "south":
            if is_door:
                d_s, d_e = door.offset, door.offset + door.width
                if d_s > 0.05:
                    fig.add_traces(_create_3d_box(0, 0, 0, d_s, thick, wall_h, "South Wall (L)", wall_color, 0.4))
                if d_e < room_w - 0.05:
                    fig.add_traces(_create_3d_box(d_e, 0, 0, room_w - d_e, thick, wall_h, "South Wall (R)", wall_color, 0.4))
            else:
                fig.add_traces(_create_3d_box(0, 0, 0, room_w, thick, wall_h, "South Wall", wall_color, 0.4))

        elif wall_name == "north":
            if is_door:
                d_s, d_e = door.offset, door.offset + door.width
                if d_s > 0.05:
                    fig.add_traces(_create_3d_box(0, room_l - thick, 0, d_s, thick, wall_h, "North Wall (L)", wall_color, 0.4))
                if d_e < room_w - 0.05:
                    fig.add_traces(_create_3d_box(d_e, room_l - thick, 0, room_w - d_e, thick, wall_h, "North Wall (R)", wall_color, 0.4))
            else:
                fig.add_traces(_create_3d_box(0, room_l - thick, 0, room_w, thick, wall_h, "North Wall", wall_color, 0.4))

        elif wall_name == "west":
            if is_door:
                d_s, d_e = door.offset, door.offset + door.width
                if d_s > 0.05:
                    fig.add_traces(_create_3d_box(0, 0, 0, thick, d_s, wall_h, "West Wall (B)", wall_color, 0.4))
                if d_e < room_l - 0.05:
                    fig.add_traces(_create_3d_box(0, d_e, 0, thick, room_l - d_e, wall_h, "West Wall (T)", wall_color, 0.4))
            else:
                fig.add_traces(_create_3d_box(0, 0, 0, thick, room_l, wall_h, "West Wall", wall_color, 0.4))

        elif wall_name == "east":
            if is_door:
                d_s, d_e = door.offset, door.offset + door.width
                if d_s > 0.05:
                    fig.add_traces(_create_3d_box(room_w - thick, 0, 0, thick, d_s, wall_h, "East Wall (B)", wall_color, 0.4))
                if d_e < room_l - 0.05:
                    fig.add_traces(_create_3d_box(room_w - thick, d_e, 0, thick, room_l - d_e, wall_h, "East Wall (T)", wall_color, 0.4))
            else:
                fig.add_traces(_create_3d_box(room_w - thick, 0, 0, thick, room_l, wall_h, "East Wall", wall_color, 0.4))

    # 3. Privacy Compartment Screens (WC Cell and Wet Cell Screens)
    partitions = design_solution.get("partitions", [])
    for part in partitions:
        fig.add_traces(_create_3d_box(
            part["x"], part["y"], 0.0, part["dx"], part["dy"], part.get("dz", 5.5),
            part.get("name", "Privacy Cell Partition"), "#38BDF8", 0.45
        ))

    # 4. Placed Fixtures & Flush Mounting
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

            # Flush Architectural Mirror mounted on the supporting wall
            m_h = 2.4
            m_thick = 0.04
            if wall_str == "south_wall":
                fig.add_traces(_create_3d_box(x, 0.02, z + dz + 0.2, dx, m_thick, m_h, "Backlit Mirror", "#E0F2FE", 0.8))
            elif wall_str == "north_wall":
                fig.add_traces(_create_3d_box(x, room_l - m_thick - 0.02, z + dz + 0.2, dx, m_thick, m_h, "Backlit Mirror", "#E0F2FE", 0.8))
            elif wall_str == "west_wall":
                fig.add_traces(_create_3d_box(0.02, y, z + dz + 0.2, m_thick, dy, m_h, "Backlit Mirror", "#E0F2FE", 0.8))
            elif wall_str == "east_wall":
                fig.add_traces(_create_3d_box(room_w - m_thick - 0.02, y, z + dz + 0.2, m_thick, dy, m_h, "Backlit Mirror", "#E0F2FE", 0.8))

        elif cat == "faucet":
            fig.add_traces(_create_3d_box(x + dx * 0.35, y + dy * 0.35, z + 2.8, 0.3, 0.3, 0.7, item["name"], "#0F172A", 1.0))

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