import json
from pathlib import Path

STOP_TIMES_FILE = Path("stop_times.jsonl")
OUTPUT_FILE = Path("stop_times_filtered.jsonl")

TRIP_ID_PREFIX = "8927"

def filter_stop_times():
    if not STOP_TIMES_FILE.exists():
        print(f"File not found: {STOP_TIMES_FILE}")
        return
    with STOP_TIMES_FILE.open() as infile, OUTPUT_FILE.open("w") as outfile:
        for line in infile:
            try:
                entry = json.loads(line)
                trip_id = str(entry.get("trip_id", ""))
                if trip_id.startswith(TRIP_ID_PREFIX):
                    outfile.write(json.dumps(entry) + "\n")
            except Exception:
                continue
    print(f"Filtered stop times written to {OUTPUT_FILE}")

if __name__ == "__main__":
    filter_stop_times()
