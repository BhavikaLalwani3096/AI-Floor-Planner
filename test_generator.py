# test_generator.py
from geometry import Door
from generator import build_design_matrix

# Configure an 8ft x 9ft bathroom with an inward swinging door
door = Door(wall="south", offset=0.5, width=2.5, door_type="swing_inward")

# Generate the 9 designs
designs = build_design_matrix(
    room_w=8.0, 
    room_l=9.0, 
    door=door, 
    style="Modern Minimalist", 
    mode="privacy_focused",
    budget_limit=400000
)

print(f"Total Unique Designs Generated: {len(designs)}\n")
for d in designs:
    print(f"[{d['design_id']}] Layout {d['layout_index']} | {d['tier']} Bundle")
    print(f"  Total Cost: Rs. {d['total_price_inr']:,} (Within Budget: {d['within_budget']})")
    print(f"  Fitness: {d['fitness_score']} -> Sub-scores: {d['sub_scores']}")
    print(f"  Fixtures Placed: {len(d['placed_fixtures'])}")
    print("-" * 60)