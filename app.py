"""
app.py - Customer-Facing AI Spatial Bathroom Planner for Kohler.
Integrates 2D Blueprints, Interactive 3D WebGL, 9-Design Matrix, and Product Showcase.
"""

import streamlit as st
import matplotlib.pyplot as plt
from geometry import Door
from generator import build_design_matrix
from visualizer_3d import render_3d_bathroom
from visualizer_2d import render_2d_blueprint

st.set_page_config(page_title="Kohler Spatial AI Studio", layout="wide", page_icon="🛁")

# Styling: Clean Modern Kohler Aesthetic
st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E5E7EB; }
    .product-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 600;
        border-radius: 4px;
        background-color: #E0F2FE;
        color: #0369A1;
        margin-right: 4px;
    }
    .badge-eco {
        background-color: #DCFCE7;
        color: #15803D;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.title("🛁 Spatial Parameters")
st.sidebar.markdown("Define room envelope and architectural openings.")

with st.sidebar.expander("1. Room Geometry", expanded=True):
    room_w = st.slider("Room Width (ft)", min_value=6.0, max_value=14.0, value=8.0, step=0.5)
    room_l = st.slider("Room Length (ft)", min_value=6.0, max_value=14.0, value=9.0, step=0.5)

with st.sidebar.expander("2. Architectural Openings", expanded=True):
    door_wall = st.selectbox("Door Wall", ["south", "north", "west", "east"], index=0)
    door_type = st.selectbox("Door Mechanism", ["swing_inward", "sliding", "swing_outward"], index=0)
    max_offset = (room_w if door_wall in ("south", "north") else room_l) - 3.0
    door_offset = st.slider("Door Hinge Position (ft from corner)", min_value=0.0, max_value=max(0.0, max_offset), value=0.5, step=0.5)
    window_wall = st.selectbox("Window Wall (Daylight)", ["north", "east", "west", "south"], index=0)

with st.sidebar.expander("3. Customer Intent & Priorities", expanded=True):
    macro_mode = st.radio("Spatial Flow", ["Free-Flow (Open Concept)", "Privacy-Focused (Partitioned)"], index=1)
    mode_key = "privacy_focused" if "Privacy" in macro_mode else "free_flow"
    budget_limit = st.number_input("Budget Limit (INR)", min_value=100000, max_value=1000000, value=450000, step=25000)

door = Door(wall=door_wall, offset=door_offset, width=2.5, door_type=door_type)

# ----------------- EXECUTE ENGINE -----------------
designs = build_design_matrix(
    room_w=room_w,
    room_l=room_l,
    door=door,
    style="Modern Minimalist",
    mode=mode_key,
    budget_limit=budget_limit
)

# ----------------- HEADER & CONTROLS -----------------
st.title("Kohler AI Spatial Design Studio")
st.markdown("Explore **9 generated designs** balancing clearance physics, line-of-sight privacy, and WaterSense eco-metrics.")

# Top Selection Bar: 3 Spatial Layouts
col_layout, col_tier = st.columns([1, 1])

with col_layout:
    layout_choice = st.radio(
        "📐 Select Spatial Layout (Physical Placement):",
        options=[1, 2, 3],
        format_func=lambda x: f"Layout {x}: " + ("Perimeter Open Flow" if x==1 else ("Wet/Dry Cluster" if x==2 else "Corner Focal Anchor")),
        horizontal=True
    )

with col_tier:
    tier_choice = st.radio(
        "💎 Select Product Curation (Intra-Style Bundle):",
        options=["Essential", "Sculptural", "High-Tech"],
        horizontal=True
    )

# Filter the matching design from our 9-solution matrix
active_design = next((d for d in designs if d["layout_index"] == layout_choice and d["tier"] == tier_choice), designs[0])

st.divider()

# ----------------- METRICS DASHBOARD -----------------
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("Total Investment", f"₹ {active_design['total_price_inr']:,}", 
              delta="Within Budget" if active_design['within_budget'] else "Exceeds Budget",
              delta_color="normal" if active_design['within_budget'] else "inverse")
with m2:
    st.metric("Spatial Fitness", f"{int(active_design['fitness_score'] * 100)} / 100")
with m3:
    st.metric("Circulation Flow", f"{int(active_design['sub_scores']['circulation'] * 100)}%")
with m4:
    st.metric("Privacy Shielding", f"{int(active_design['sub_scores']['sightline'] * 100)}%")
with m5:
    st.metric("Plumbing Clustering", f"{int(active_design['sub_scores']['plumbing'] * 100)}%")

# ----------------- DUAL VIEWPORT: 2D & 3D -----------------
st.subheader(f"Design Solution: {active_design['design_id']}")

tab_3d, tab_2d = st.tabs(["🌐 Interactive 3D Spatial Model", "📐 Contractor 2D Floor Plan"])

with tab_3d:
    st.markdown("*Click and drag to rotate, scroll to zoom, hover over fixtures for specifications.*")
    fig_3d = render_3d_bathroom(active_design, room_w, room_l, door)
    st.plotly_chart(fig_3d, use_container_width=True)

with tab_2d:
    st.markdown("*Architectural blueprint indicating door swing arc and activity clearance buffers.*")
    fig_2d = render_2d_blueprint(active_design, room_w, room_l, door)
    st.pyplot(fig_2d, use_container_width=False)
    plt.close(fig_2d)

st.divider()

# ----------------- SHOWROOM PRODUCT SPECIFICATION CARDS -----------------
st.subheader("Curated Kohler Hardware Specification")
st.markdown("All products match the **Modern Minimalist** aesthetic across coordinates.")

prod_cols = st.columns(len(active_design["placed_fixtures"]))

for idx, p in enumerate(active_design["placed_fixtures"]):
    item = p["item"]
    with prod_cols[idx]:
        st.markdown(f"""
        <div class="product-card">
            <span class="badge">{item['category'].upper()}</span>
            {"<span class='badge badge-eco'>WaterSense®</span>" if item.get('watersense') else ""}
            <h5 style="margin-top:8px; margin-bottom:4px;">{item['name']}</h5>
            <p style="color:#6B7280; font-size:12px; margin-bottom:8px;">SKU: {item['sku']}</p>
            <p style="font-size:13px; margin-bottom:4px;"><b>Finish:</b> {item.get('finish', 'Standard')}</p>
            <p style="font-size:13px; margin-bottom:4px;"><b>Size:</b> {item['width']}'W x {item['depth']}'D x {item['height']}'H</p>
            <p style="font-size:13px; margin-bottom:4px;"><b>Mount:</b> {item.get('mount', 'Surface').replace('_', ' ').title()}</p>
            <h4 style="color:#111827; margin-top:12px;">₹ {item['price_inr']:,}</h4>
        </div>
        """, unsafe_allow_html=True)