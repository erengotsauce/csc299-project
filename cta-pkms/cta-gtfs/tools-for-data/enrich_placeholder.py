import json

# Load trips.jsonl into a dict: trip_id -> route_id
trip_id_to_route = {}
with open("trips.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        trip = json.loads(line)
        trip_id_to_route[trip["trip_id"]] = trip["route_id"]

# Load stops.jsonl into a dict: stop_id -> parent_station, stop_name
stop_id_to_parent = {}
parent_station_to_name = {}
with open("stops.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        stop = json.loads(line)
        stop_id = stop["stop_id"]
        parent_station = stop.get("parent_station")
        stop_name = stop.get("stop_name")
        stop_id_to_parent[stop_id] = parent_station
        parent_station_to_name[parent_station] = stop_name

# Process placeholder.jsonl
output = []
with open("placeholder.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        entity = json.loads(line)
        trip_id = entity.get("trip_id")
        stop_id = entity.get("stop_id")
        if trip_id is None or stop_id is None:
            print(f"Warning: Missing trip_id or stop_id in line: {line}")
            continue
        route_id = trip_id_to_route.get(trip_id)
        parent_station = stop_id_to_parent.get(stop_id)
        stop_name = parent_station_to_name.get(parent_station)
        output.append({
            "route_id": route_id,
            "parent_station": parent_station,
            "stop_name": stop_name
        })

with open("placeholder_enriched.jsonl", "w") as f:
    for item in output:
        f.write(json.dumps(item) + "\n")
