import typer
import json
from pathlib import Path

app = typer.Typer()

@app.command("greet")
def greet():
    """Greet the user."""
    print("Hello from cta-pkms-tool!")

data_dir = Path("data")
data_files = {
    "stations": data_dir / "cta_stations.json",
    "lines": data_dir / "cta_lines.json",
    "tasks": data_dir / "tasks.json",
    "commutes": data_dir / "commutes.json",
}

def load_data(file_name):
    file_path = data_files[file_name]
    if file_path.exists():
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_data(file_name, data):
    file_path = data_files[file_name]
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    app()
