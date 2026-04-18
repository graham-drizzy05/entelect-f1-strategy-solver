import json

with open('1.txt', 'r') as f:
    data = json.load(f)

braking_distances = {
    1: 163.5,   # straight 1 (920m) before corner 2 (radius 53)
    4: 167.2,   # straight 4 (600m) before corner 5 (radius 50)
    7: 161.8,   # straight 7 (880m) before corner 8 (radius 60)
    9: 120.5,   # straight 9 (700m) before corner 10 (radius 95)
    12: 158.3,  # straight 12 (810m) before corner 13 (radius 78)
    14: 160.9   # straight 14 (660m) before corner 15 (radius 55)
}

segments = []
for seg in data['track']['segments']:
    if seg['type'] == 'straight':
        brake = braking_distances.get(seg['id'], 0)
        segments.append({
            "id": seg['id'],
            "type": "straight",
            "target_m/s": 90,
            "brake_start_m_before_next": brake
        })
    else:
        segments.append({
            "id": seg['id'],
            "type": "corner"
        })

laps = []
for lap_num in range(1, 51):
    laps.append({
        "lap": lap_num,
        "segments": segments,
        "pit": {"enter": False}
    })

output = {
    "initial_tyre_id": 1,
    "laps": laps
}

with open('output.txt', 'w') as f:
    json.dump(output, f, indent=2)

print("output.txt created successfully!")