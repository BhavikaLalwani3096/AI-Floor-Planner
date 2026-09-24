"""
app.py - Clean, Zero-Clutter Studio Interface.
Locked-down layout: Clean top controls, sidebar radio matrix, and centered viewport.
"""

import streamlit as st
import matplotlib.pyplot as plt
from geometry import Door
from generator import build_design_matrix
from visualizer_3d import render_3d_bathroom
from visualizer_2d import render_2d_blueprint

st.set_page_config(page_title="Spatial Studio", layout="wide", page_icon="🏛️")

# Clean, distraction-free styling
st.markdown("""
    <style>
    .block-container { 
        padding-top: 1.2rem; 
        padding-bottom: 1rem; 
        padding-left: 2rem;
        padding-right: 2rem;
    }
    header[data-testid="stHeader"] { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR: CONTROLS & SELECTION MATRIX -----------------
with st.sidebar:
    st.title("🏛️ Studio Controls")
    
    # 1. Layout & Design Pickers (6 Radio Buttons)
    st.subheader("📐 Spatial Layout")
    layout_selected = st.radio(
        "Select Room Placement",
        options=[1, 2, 3],
        format_func=lambda x: {
            1: "Layout 1: Perimeter Flow",
            2: "Layout 2: Wet / Dry Cluster",
            3: "Layout 3: Corner Anchor"
        }[x],
        label_visibility="collapsed"
    )

    st.subheader("🎨 Design Curation")
    design_selected = st.radio(
        "Select Hardware Bundle",
        options=[1, 2, 3],
        format_func=lambda x: {
            1: "Design 1: Essential Harmony",
            2: "Design 2: Sculptural Balance",
            3: "Design 3: Premium Precision"
        }[x],
        label_visibility="collapsed"
    )

    st.divider()

    # 2. Architectural Parameters
    with st.expander("📐 Room Geometry", expanded=True):
        room_w = st.slider("Width (ft)", 6.0, 14.0, 8.0, 0.5)
        room_l = st.slider("Length (ft)", 6.0, 14.0, 9.0, 0.5)

    with st.expander("🚪 Openings (Door & Window)", expanded=False):
        door_wall = st.selectbox("Door Wall", ["south", "west", "north", "east"], index=0)
        door_type = st.selectbox("Door Mechanism", ["swing_inward", "sliding", "swing_outward"], index=0)
        max_d_offset = (room_w if door_wall in ("south", "north") else room_l) - 2.8
        door_offset = st.slider("Door Position", 0.0, max(0.0, float(max_d_offset)), 0.5, 0.5)
        window_wall = st.selectbox("Daylight Window Wall", ["north", "east", "west", "south"], index=0)

    with st.expander("🎯 Intent & Budget", expanded=False):
        macro_mode = st.radio("Macro Mode", ["Free-Flow (Open Concept)", "Privacy-Focused (Partitioned)"], index=1)
        mode_key = "privacy_focused" if "Privacy" in macro_mode else "free_flow"
        budget_limit = st.number_input("Budget Ceiling (INR)", 100000, 1000000, 350000, 25000)

door = Door(wall=door_wall, offset=door_offset, width=2.5, door_type=door_type)

# Execute Generator Matrix
designs = build_design_matrix(
    room_w=room_w, room_l=room_l, door=door, 
    mode=mode_key, window_wall=window_wall, budget_limit=budget_limit
)

# Map the two sidebar radio buttons directly to one of the 9 solutions
target_id = f"L{layout_selected}_B{design_selected}"
active_design = next((d for d in designs if d["design_id"] == target_id), designs[0])


# ----------------- MODAL DIALOG: BUDGET & PRODUCT DETAILS -----------------
@st.dialog("📦 Curated Hardware & Investment Audit")
def show_budget_modal(design):
    st.markdown(f"### Design: `{design['design_id']}` ({design['tier']})")
    st.write(f"**Total Investment:** ₹ {design['total_price_inr']:,} "
             f"({'✅ Within Budget' if design['within_budget'] else '⚠️ Hard Limit Enforced (Within ₹30k)'})")
    st.divider()

    cols = st.columns(2)
    for idx, p in enumerate(design["placed_fixtures"]):
        item = p["item"]
        with cols[idx % 2]:
            with st.container(border=True):
                st.caption(f"{item['category'].upper()} • {'🌿 WaterSense' if item.get('watersense') else 'Standard'}")
                st.markdown(f"**{item['name']}**")
                st.caption(f"SKU: `{item['sku']}`")
                st.write(f"🎨 **Finish:** {item.get('finish')}")
                st.write(f"📏 **Dimensions:** {item['width']}'W × {item['depth']}'D × {item['height']}'H")
                st.markdown(f"#### ₹ {item['price_inr']:,}")


# ----------------- MAIN VIEWPORT (CENTERPIECE) -----------------
top_col1, top_col2 = st.columns([3, 1])

with top_col1:
    canvas_view = st.radio(
        "Viewport View",
        ["🌐 3D Spatial Interactive Model", "📐 2D Technical Floor Plan"],
        horizontal=True,
        label_visibility="collapsed"
    )

with top_col2:
    if st.button("📊 View Budget & Spec Sheet", use_container_width=True):
        show_budget_modal(active_design)

# Render Viewport Directly Underneath
if "3D" in canvas_view:
    fig_3d = render_3d_bathroom(active_design, room_w, room_l, door, window_wall=window_wall)
    st.plotly_chart(fig_3d, use_container_width=True, height=680)
else:
    fig_2d = render_2d_blueprint(active_design, room_w, room_l, door)
    c_left, c_mid, c_right = st.columns([1, 4, 1])
    with c_mid:
        st.pyplot(fig_2d, use_container_width=True)
    plt.close(fig_2d)