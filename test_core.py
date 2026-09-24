# test_core.py
from catalog import get_products_by_filter
from geometry import Door, PlacedFixture, check_layout_feasibility

toilets = get_products_by_filter(category="toilet", style="Modern Minimalist")
vanities = get_products_by_filter(category="vanity", style="Modern Minimalist")

toilet_data = toilets[0]
vanity_data = vanities[0]

# South wall has a door at offset 0.5 (spans x=0.5 to x=3.0)
door_inward = Door(wall="south", offset=0.5, width=2.5, door_type="swing_inward")
door_sliding = Door(wall="south", offset=0.5, width=2.5, door_type="sliding")

# SCENARIO A: Toilet placed at x=1.0, y=1.0 (inside the inward swing arc, but away from the wall door frame)
# Note: Inward swing box is x in [0.5, 3.0], y in [0.0, 2.5]
t_in_swing = PlacedFixture(toilet_data, x=1.0, y=1.0, orientation="north_wall")

valid_inward, msg_inward = check_layout_feasibility([t_in_swing], door_inward, 8.0, 8.0)
valid_sliding, msg_sliding = check_layout_feasibility([t_in_swing], door_sliding, 8.0, 8.0)

print(f"Test Inside Swing Arc:")
print(f"  Inward Door:  {valid_inward} -> {msg_inward}")
print(f"  Sliding Door: {valid_sliding} -> {msg_sliding}")

# SCENARIO B: Proper layout along East wall (x=6.0, y=0.0) away from door
t_clear = PlacedFixture(toilet_data, x=4.0, y=0.0, orientation="south_wall")
v_clear = PlacedFixture(vanity_data, x=6.0, y=0.0, orientation="south_wall")

valid_both, msg_both = check_layout_feasibility([t_clear, v_clear], door_inward, 8.0, 8.0)
print(f"\nTest Clear Placement (x=4.0, 6.0):")
print(f"  Inward Door:  {valid_both} -> {msg_both}")