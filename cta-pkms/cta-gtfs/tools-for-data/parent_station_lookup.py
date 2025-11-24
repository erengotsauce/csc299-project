import json

# Load stops.jsonl into a dict: stop_id -> (parent_station, stop_name)
stops = {}
with open("stops.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        stop = json.loads(line)
        stops[stop["stop_id"]] = (stop.get("parent_station"), stop.get("stop_name"))

# For each entity in route-stations.jsonl, find parent_station and stop_name
output = []
with open("route-stations.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        entity = json.loads(line)
        stop_id = entity["stop_id"]
        parent_station, stop_name = stops.get(stop_id, (None, None))
        parent_station_name = stops.get(parent_station, (None, None))[1] if parent_station else None
        output.append({"stop_id": stop_id, "parent_station": parent_station, "parent_station_name": parent_station_name, "stop_name": stop_name})

with open("parent_stations.jsonl", "w") as f:
    for item in output:
        f.write(json.dumps(item) + "\n")