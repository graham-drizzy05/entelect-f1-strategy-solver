import json

with open('1.txt', 'r') as f:
    data = json.load(f)

braking_distances = {
    1: 162,   # straight 1 before corner 2 (radius 53)
    4: 150,   # straight 4 before corner 5 (radius 50)
    7: 160,   # straight 7 before corner 8 (radius 60)
    9: 140,   # straight 9 before corner 10 (radius 95)
    12: 158,  # straight 12 before corner 13 (radius 78)
    14: 155   # straight 14 before corner 15 (radius 55)
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