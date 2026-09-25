"""
visualizer_3d.py - High-Fidelity 3D Parametric Bathroom Visualizer.
Renders compound realistic fixture geometries: cisterns, bowls, vanities with inset basins,
cantilevered spouts, shower curbs with rainheads, and storage towers.
"""

import plotly.graph_objects as go
from typing import Dict, Any, List
from geometry import Door


def _box_mesh(x: float, y: float, z: float, 
              dx: float, dy: float, dz: float, 
              name: str, color: str, opacity: float = 1.0) -> List[go.Mesh3d]:
    """Generates an axis-aligned 3D rectangular prism."""
    vx = [x, x + dx, x + dx, x, x, x + dx, x + dx, x]
    vy = [y, y, y + dy, y + dy, y, y, y + dy, y + dy]
    vz = [z, z, z, z, z + dz, z + dz, z + dz, z + dz]

    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    return [go.Mesh3d(
        x=vx, y=vy, z=vz, i=i, j=j, k=k,
        name=name, color=color, opacity=opacity,
        flatshading=True,
        lighting=dict(ambient=0.7, diffuse=0.85, specular=0.4, roughness=0.2),
        hoverinfo="name"
    )]


def render_3d_bathroom(design_solution: Dict[str, Any], 
                       room_w: float, 
                       room_l: float, 
                       door: Door,
                       window_wall: str = "north") -> go.Figure:
    fig = go.Figure()
    wall_color = "#94A3B8"
    thick = 0.2
    wall_h = 3.5

    # 1. Tile Floor Slab
    fig.add_trace(go.Mesh3d(
        x=[0, room_w, room_w, 0], y=[0, 0, room_l, room_l], z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3], color="#F1F5F9", name="Porcelain Tile Floor", opacity=1.0
    ))

    # 2. Universal Parametric Outer Cutaway Walls
    for wall_name in ["south", "north", "west", "east"]:
        is_door = (door.wall == wall_name)
        if wall_name == "south":
            if is_door:
                d_s, d_e = door.offset, door.offset + door.width
                if d_s > 0.05:
                    fig.add_traces(_box_mesh(0, 0, 0, d_s, thick, wall_h, "South Wall", wall_color, 0.35))
                if d_e < room_w - 0.05:
                    fig.add_traces(_box_mesh(d_e, 0, 0, room_w - d_e, thick, wall_h, "South Wall", wall_color, 0.35))
            else:
                fig.add_traces(_box_mesh(0, 0, 0, room_w, thick, wall_h, "South Wall", wall_color, 0.35))

        elif wall_name == "north":
            if is_door:
                d_s, d_e = door.offset, door.offset + door.width
                if d_s > 0.05:
                    fig.add_traces(_box_mesh(0, room_l - thick, 0, d_s, thick, wall_h, "North Wall", wall_color, 0.35))
                if d_e < room_w - 0.05:
                    fig.add_traces(_box_mesh(d_e, room_l - thick, 0, room_w - d_e, thick, wall_h, "North Wall", wall_color, 0.35))
            else:
                fig.add_traces(_box_mesh(0, room_l - thick, 0, room_w, thick, wall_h, "North Wall", wall_color, 0.35))

        elif wall_name == "west":
            if is_door:
                d_s, d_e = door.offset, door.offset + door.width
                if d_s > 0.05:
                    fig.add_traces(_box_mesh(0, 0, 0, thick, d_s, wall_h, "West Wall", wall_color, 0.35))
                if d_e < room_l - 0.05:
                    fig.add_traces(_box_mesh(0, d_e, 0, thick, room_l - d_e, wall_h, "West Wall", wall_color, 0.35))
            else:
                fig.add_traces(_box_mesh(0, 0, 0, thick, room_l, wall_h, "West Wall", wall_color, 0.35))

        elif wall_name == "east":
            if is_door:
                d_s, d_e = door.offset, door.offset + door.width
                if d_s > 0.05:
                    fig.add_traces(_box_mesh(room_w - thick, 0, 0, thick, d_s, wall_h, "East Wall", wall_color, 0.35))
                if d_e < room_l - 0.05:
                    fig.add_traces(_box_mesh(room_w - thick, d_e, 0, thick, room_l - d_e, wall_h, "East Wall", wall_color, 0.35))
            else:
                fig.add_traces(_box_mesh(room_w - thick, 0, 0, thick, room_l, wall_h, "East Wall", wall_color, 0.35))

    # 3. Privacy Architectural Screen (Frosted Glass Divider)
    partitions = design_solution.get("partitions", [])
    for part in partitions:
        fig.add_traces(_box_mesh(
            part["x"], part["y"], 0.0, part["dx"], part["dy"], part.get("dz", 5.5),
            part.get("name", "WC Divider Screen"), "#38BDF8", 0.45
        ))

    # 4. Realistic Detailed Fixture Components
    for p in design_solution["placed_fixtures"]:
        item = p["item"]
        cat = item["category"]
        x, y, wall_str = p["x"], p["y"], p["wall"]
        w = item["depth"] if "west" in wall_str or "east" in wall_str else item["width"]
        d = item["width"] if "west" in wall_str or "east" in wall_str else item["depth"]
        h = item["height"]
        finish = item.get("finish", "")
        ceramic_col = "#0F172A" if "Black" in finish else "#FFFFFF"

        # --- A. TOILET: Dual-Element Model (Cistern Tank + Forward Bowl) ---
        if cat == "toilet":
            z_mount = 0.35 if item.get("mount") == "wall_hung" else 0.0
            bowl_h = 1.2
            tank_h = h - bowl_h if h > 1.3 else 1.2

            if wall_str == "south_wall":
                # Rear tank along south wall
                fig.add_traces(_box_mesh(x + 0.1, y, z_mount + 0.4, w - 0.2, 0.5, tank_h, f"{item['name']} (Tank)", ceramic_col, 0.98))
                # Extended bowl forward into +y
                fig.add_traces(_box_mesh(x + 0.15, y + 0.4, z_mount, w - 0.3, d - 0.4, bowl_h, f"{item['name']} (Bowl)", ceramic_col, 1.0))
            elif wall_str == "north_wall":
                fig.add_traces(_box_mesh(x + 0.1, y + d - 0.5, z_mount + 0.4, w - 0.2, 0.5, tank_h, f"{item['name']} (Tank)", ceramic_col, 0.98))
                fig.add_traces(_box_mesh(x + 0.15, y, z_mount, w - 0.3, d - 0.4, bowl_h, f"{item['name']} (Bowl)", ceramic_col, 1.0))
            elif wall_str == "west_wall":
                fig.add_traces(_box_mesh(x, y + 0.1, z_mount + 0.4, 0.5, d - 0.2, tank_h, f"{item['name']} (Tank)", ceramic_col, 0.98))
                fig.add_traces(_box_mesh(x + 0.4, y + 0.15, z_mount, w - 0.4, d - 0.3, bowl_h, f"{item['name']} (Bowl)", ceramic_col, 1.0))
            else:  # east_wall
                fig.add_traces(_box_mesh(x + w - 0.5, y + 0.1, z_mount + 0.4, 0.5, d - 0.2, tank_h, f"{item['name']} (Tank)", ceramic_col, 0.98))
                fig.add_traces(_box_mesh(x, y + 0.15, z_mount, w - 0.4, d - 0.3, bowl_h, f"{item['name']} (Bowl)", ceramic_col, 1.0))

        # --- B. VANITY: Countertop Slab + Base Cabinet + Basin + Flush Mirror ---
        elif cat == "vanity":
            z_elev = 0.5 if item.get("mount") == "wall_hung" else 0.0
            cab_col = "#78350F" if "Walnut" in finish else ("#18181B" if "Black" in finish else "#475569")
            top_col = "#F8FAFC" if "Quartz" in finish or "White" in finish else "#1E293B"

            # Cabinet body
            fig.add_traces(_box_mesh(x, y, z_elev, w, d, h - 0.15, f"{item['name']} (Cabinet)", cab_col, 0.96))
            # Countertop slab
            fig.add_traces(_box_mesh(x - 0.05, y - 0.05, z_elev + h - 0.15, w + 0.1, d + 0.1, 0.15, f"{item['name']} (Slab)", top_col, 1.0))
            # Inset white porcelain basin
            fig.add_traces(_box_mesh(x + w * 0.25, y + d * 0.25, z_elev + h - 0.05, w * 0.5, d * 0.5, 0.1, "Porcelain Basin", "#FFFFFF", 1.0))

            # Flush Backlit Mirror
            m_h = 2.4
            m_th = 0.04
            m_z = z_elev + h + 0.3
            if wall_str == "south_wall":
                fig.add_traces(_box_mesh(x + 0.1, 0.02, m_z, w - 0.2, m_th, m_h, "Backlit Mirror", "#E0F2FE", 0.85))
            elif wall_str == "north_wall":
                fig.add_traces(_box_mesh(x + 0.1, room_l - m_th - 0.02, m_z, w - 0.2, m_th, m_h, "Backlit Mirror", "#E0F2FE", 0.85))
            elif wall_str == "west_wall":
                fig.add_traces(_box_mesh(0.02, y + 0.1, m_z, m_th, d - 0.2, m_h, "Backlit Mirror", "#E0F2FE", 0.85))
            elif wall_str == "east_wall":
                fig.add_traces(_box_mesh(room_w - m_th - 0.02, y + 0.1, m_z, m_th, d - 0.2, m_h, "Backlit Mirror", "#E0F2FE", 0.85))

        # --- C. FAUCET: Gooseneck Riser & Forward Cantilever Spout ---
        elif cat == "faucet":
            f_col = "#000000" if "Black" in finish else "#D97706"
            # Vertical stalk
            fig.add_traces(_box_mesh(x + w * 0.45, y + d * 0.45, 2.8, 0.1, 0.1, 0.6, f"{item['name']} (Riser)", f_col, 1.0))
            # Cantilever spout arm
            fig.add_traces(_box_mesh(x + w * 0.45, y + d * 0.45, 3.4, 0.1, 0.35, 0.08, f"{item['name']} (Spout)", f_col, 1.0))

        # --- D. SHOWER: Base Curb + Glass Enclosure + Overhead Showerhead ---
        elif cat == "shower":
            # Acrylic base tray/curb
            fig.add_traces(_box_mesh(x, y, 0.0, w, d, 0.25, f"{item['name']} (Curb)", "#E2E8F0", 1.0))
            # Glass enclosure screen
            fig.add_traces(_box_mesh(x, y, 0.25, w, d, h - 0.25, f"{item['name']} (Glass Screen)", "#BAE6FD", 0.3))
            # Overhead rain showerhead armature
            fig.add_traces(_box_mesh(x + w * 0.35, y + d * 0.35, h - 0.3, 0.3, 0.3, 0.1, "Rain Showerhead", "#0F172A", 1.0))

        # --- E. BATHTUB: Soaking Tub with Rim and Hollow Center ---
        elif cat == "bathtub":
            tub_col = "#FFFFFF"
            # Outer ergonomic tub body
            fig.add_traces(_box_mesh(x, y, 0.0, w, d, h, f"{item['name']}", tub_col, 0.98))
            # Inner contrasting cavity (dark water reflection)
            fig.add_traces(_box_mesh(x + 0.3, y + 0.3, 0.2, max(0.5, w - 0.6), max(0.5, d - 0.6), h - 0.15, "Tub Basin", "#38BDF8", 0.4))

        # --- F. STORAGE TOWER: Vertical Linen Column with Shelving Lines ---
        elif cat == "storage":
            st_col = "#78350F" if "Walnut" in finish else "#18181B"
            fig.add_traces(_box_mesh(x, y, 0.4, w, d, h, f"{item['name']}", st_col, 0.95))
            # Shelving reveal line
            fig.add_traces(_box_mesh(x + 0.05, y + 0.05, 0.4 + h * 0.5, w - 0.1, d - 0.1, 0.05, "Storage Shelf", "#E2E8F0", 1.0))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (ft)", range=[-0.5, room_w + 0.5]),
            yaxis=dict(title="Y (ft)", range=[-0.5, room_l + 0.5]),
            zaxis=dict(title="Z (ft)", range=[0, 8.5]),
            aspectmode="data",
            camera=dict(eye=dict(x=1.6, y=-1.6, z=1.35), center=dict(x=0, y=0, z=-0.2))
        ),
        margin=dict(l=0, r=0, b=0, t=10),
        showlegend=False
    )
    return fig