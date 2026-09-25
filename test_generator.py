# test_generator.py
from geometry import Door
from generator import build_design_matrix

door = Door(wall="south", offset=1.0, width=2.5, door_type="swing_inward")

# Test with a budget ceiling of Rs. 350,000
designs = build_design_matrix(
    room_w=9.0, 
    room_l=8.0, 
    door=door, 
    mode="privacy_focused",
    window_wall="north",
    budget_limit=350000
)

print(f"Total Unique Solutions Generated: {len(designs)}\n")
for d in designs[:3]:
    print(f"[{d['design_id']}] Layout {d['layout_index']} | {d['tier']}")
    print(f"  Total Cost: Rs. {d['total_price_inr']:,} (Within Budget: {d['within_budget']})")
    print(f"  Calculated Fitness: {d['fitness_score']} | Sub-scores: {d['sub_scores']}")
    print(f"  Partition Screen Created: {d['partition'] is not None}")
    for p in d['placed_fixtures']:
        print(f"    - {p['item']['name']} at ({p['x']:.1f}, {p['y']:.1f}) on {p['wall']}")
    print("-" * 65)