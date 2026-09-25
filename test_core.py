# test_core.py
from catalog import CATALOG
from geometry import Door, PerimeterCoordinateSystem, check_layout_feasibility, calculate_sightline_vector_score

# 1. Fetch sample items
toilet = next(p for p in CATALOG if p["category"] == "toilet")
vanity = next(p for p in CATALOG if p["category"] == "vanity")
shower = next(p for p in CATALOG if p["category"] == "shower")

# 2. Setup a 10ft x 8ft room
room_w, room_l = 10.0, 8.0
pcs = PerimeterCoordinateSystem(room_w, room_l)
door = Door(wall="south", offset=1.0, width=2.5, door_type="swing_inward")

# 3. Test continuous perimeter placements (u values in feet)
# Perimeter = 2 * (10 + 8) = 36 ft total
p_toilet = pcs.u_to_placement(12.0, toilet) # u=12 is on East Wall (10 + 2)
p_vanity = pcs.u_to_placement(22.0, vanity) # u=22 is on North Wall (10 + 8 + 4)
p_shower = pcs.u_to_placement(30.0, shower) # u=30 is on West Wall (10 + 8 + 10 + 2)

fixtures = [p_toilet, p_vanity, p_shower]

# 4. Run Physics Check
valid, msg = check_layout_feasibility(fixtures, door, room_w, room_l)
sight_score = calculate_sightline_vector_score(door, p_toilet, p_vanity, room_w, room_l)

print(f"Physics Collision Check: {valid} -> {msg}")
print(f"Calculated Sightline Vector Score: {sight_score:.3f}")
for f in fixtures:
    print(f"  {f.data['name']} -> Position: ({f.x:.1f}, {f.y:.1f}) on {f.orientation}")