# test_visualizer.py
import matplotlib.pyplot as plt
from geometry import Door
from generator import build_design_matrix
from visualizer_3d import render_3d_bathroom
from visualizer_2d import render_2d_blueprint

# 1. Setup room
door = Door(wall="south", offset=0.5, width=2.5, door_type="swing_inward")
designs = build_design_matrix(
    room_w=8.0, 
    room_l=9.0, 
    door=door, 
    style="Modern Minimalist", 
    mode="privacy_focused",
    budget_limit=400000
)

target_design = designs[0]
print(f"Rendering 2D & 3D for: {target_design['design_id']}")

# 2. Render 2D Blueprint (Saves image to disk for inspection)
fig_2d = render_2d_blueprint(target_design, room_w=8.0, room_l=9.0, door=door)
fig_2d.savefig("test_blueprint.png", bbox_inches="tight")
print("Saved 2D floor plan to: test_blueprint.png")

# 3. Launch interactive 3D WebGL in browser
fig_3d = render_3d_bathroom(target_design, room_w=8.0, room_l=9.0, door=door)
fig_3d.show()