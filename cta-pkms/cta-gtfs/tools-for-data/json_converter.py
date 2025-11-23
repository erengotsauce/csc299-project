import pandas as pd

input_file = 'stops.txt'
output_file = 'stops.jsonl'
chunk_size = 100000  # Process 100k rows at a time

print(f"Converting {input_file} to {output_file}...")

# Open the output file in write mode
with open(output_file, 'w', encoding='utf-8') as f:
    # Read the file in chunks
    for i, chunk in enumerate(pd.read_csv(input_file, chunksize=chunk_size, dtype=str)):
        # Note: dtype=str keeps times like "25:30:00" or leading zero IDs intact
        
        # Write chunk to file as JSON Lines (no brackets, one object per line)
        chunk.to_json(f, orient='records', lines=True)
        
        print(f"Processed chunk {i+1} ({chunk_size * (i+1)} rows estimated)...")

print("Conversion complete.")