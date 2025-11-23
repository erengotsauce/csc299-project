import typer
import json
from pathlib import Path
import sys

def run_station_selector():
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Footer, ListView, ListItem, Label, Button
    from pathlib import Path
    import json

    STOPS_FILE = Path("cta-gtfs/stops.jsonl")

    def load_stops():
        stops = []
        if STOPS_FILE.exists():
            with STOPS_FILE.open() as f:
                for line in f:
                    try:
                        stop = json.loads(line)
                        stop_id = str(stop.get("stop_id", ""))
                        if stop_id.startswith("4"):
                            stops.append(stop)
                    except Exception:
                        continue
        return stops

    class StationSelector(App):
        CSS_PATH = None

        def __init__(self):
            super().__init__()
            self.stops = load_stops()
            self.departure = None
            self.arrival = None

        def compose(self) -> ComposeResult:
            yield Header()
            yield Label("Select Departure Station:")
            yield ListView(*[
                ListItem(Label(f"{stop['stop_name']} ({stop['stop_id']})")) for stop in self.stops
            ], id="departure_list")
            yield Label("Select Arrival Station:")
            yield ListView(*[
                ListItem(Label(f"{stop['stop_name']} ({stop['stop_id']})")) for stop in self.stops
            ], id="arrival_list")
            yield Button("Confirm Selection", id="confirm_btn")
            yield Footer()

        def on_mount(self):
            self.query_one("#departure_list").focus()

        def on_list_view_selected(self, event):
            list_id = event.list_view.id
            idx = event.index
            stop = self.stops[idx]
            if list_id == "departure_list":
                self.departure = stop
            elif list_id == "arrival_list":
                self.arrival = stop

        def on_button_pressed(self, event):
            if event.button.id == "confirm_btn":
                if self.departure and self.arrival:
                    self.exit((self.departure, self.arrival))
                else:
                    self.query_one("#departure_list").focus()

    return StationSelector().run()

app = typer.Typer()

TASKS_FILE = Path("tasks.json")
COMMUTES_FILE = Path("commutes.json")

def ensure_file(file_path):
    if not file_path.exists():
        file_path.write_text("[]")

def load_json(file_path):
    ensure_file(file_path)
    with file_path.open() as f:
        return json.load(f)

def save_json(file_path, data):
    with file_path.open("w") as f:
        json.dump(data, f, indent=2)

@app.command()
def add_task(
    name: str = typer.Argument(..., help="Task name"),
    description: str = typer.Argument(..., help="Task description"),
    location: str = typer.Option(None, help="Task location (optional)")
):
    """
    Add a new task with name, description, and optional location.
    """
    tasks = load_json(TASKS_FILE)
    task = {
        "name": name,
        "description": description,
        "status": "pending"
    }
    if location:
        task["location"] = location
    tasks.append(task)
    save_json(TASKS_FILE, tasks)
    typer.echo(f"Task added: {name}\nDescription: {description}" + (f"\nLocation: {location}" if location else "") + "\nStatus: pending")

@app.command()
def amend_task(
    index: int = typer.Argument(..., help="Task number to amend"),
    name: str = typer.Option(None, help="New task name"),
    description: str = typer.Option(None, help="New task description"),
    location: str = typer.Option(None, help="New task location"),
    status: str = typer.Option(None, help="New status: 'pending' or 'completed'")
):
    """
    Amend a task's name, description, location, or status.
    Status can only be 'pending' or 'completed'.
    """
    tasks = load_json(TASKS_FILE)
    if 1 <= index <= len(tasks):
        task = tasks[index - 1]
        changed = False
        if name is not None:
            task["name"] = name
            changed = True
        if description is not None:
            task["description"] = description
            changed = True
        if location is not None:
            if location == "":
                task.pop("location", None)
            else:
                task["location"] = location
            changed = True
        if status is not None:
            if status in ["pending", "completed"]:
                task["status"] = status
                changed = True
            else:
                typer.echo("Status must be 'pending' or 'completed'.")
                return
        if changed:
            save_json(TASKS_FILE, tasks)
            typer.echo(f"Task {index} amended.")
        else:
            typer.echo("No changes provided.")
    else:
        typer.echo("Invalid task number.")

@app.command()
def list_tasks():
    "List all tasks."
    tasks = load_json(TASKS_FILE)
    if not tasks:
        typer.echo("No tasks found.")
        return
    pending = [task for task in tasks if task.get('status', 'pending') == 'pending']
    completed = [task for task in tasks if task.get('status', 'pending') == 'completed']

    typer.echo("Pending Tasks:")
    if not pending:
        typer.echo("  None")
    else:
        for i, task in enumerate(pending, 1):
            typer.echo(f"{i}. {task['name']}\n   Description: {task.get('description', '')}")
            if 'location' in task:
                typer.echo(f"   Location: {task['location']}")
            typer.echo(f"   Status: {task.get('status', 'pending')}")

    typer.echo("")
    typer.echo("Completed Tasks:")
    if not completed:
        typer.echo("  None")
    else:
        for i, task in enumerate(completed, 1):
            typer.echo(f"{i}. {task['name']}\n   Description: {task.get('description', '')}")
            if 'location' in task:
                typer.echo(f"   Location: {task['location']}")
            typer.echo(f"   Status: {task.get('status', 'completed')}")

@app.command()
def delete_task(index: int):
    "Delete a task by its number."
    tasks = load_json(TASKS_FILE)
    if 1 <= index <= len(tasks):
        removed = tasks.pop(index - 1)
        save_json(TASKS_FILE, tasks)
        typer.echo(f"Deleted task: {removed['name']}")
    else:
        typer.echo("Invalid task number.")

@app.command()
def add_commute(
    name: str = typer.Argument(..., help="Commute name")
):
    """
    Add a new commute with name, and select departure/arrival stations via TUI.
    """
    typer.echo("Launching station selector...")
    result = run_station_selector()
    if result and isinstance(result, tuple) and len(result) == 2:
        departure, arrival = result
        commutes = load_json(COMMUTES_FILE)
        commute = {
            "name": name,
            "departure_station": departure["stop_name"],
            "departure_stop_id": departure["stop_id"],
            "arrival_station": arrival["stop_name"],
            "arrival_stop_id": arrival["stop_id"]
        }
        commutes.append(commute)
        save_json(COMMUTES_FILE, commutes)
        typer.echo(f"Commute added: {name}\nDeparture: {departure['stop_name']} ({departure['stop_id']})\nArrival: {arrival['stop_name']} ({arrival['stop_id']})")
    else:
        typer.echo("Commute creation cancelled or failed.")

@app.command()
def list_commutes():
    "List all commutes."
    commutes = load_json(COMMUTES_FILE)
    if not commutes:
        typer.echo("No commutes found.")
        return
    for i, commute in enumerate(commutes, 1):
        typer.echo(f"{i}. {commute['name']}\n   Departure: {commute.get('departure_station', '')}\n   Arrival: {commute.get('arrival_station', '')}")

@app.command()
def delete_commute(index: int):
    "Delete a commute by its number."
    commutes = load_json(COMMUTES_FILE)
    if 1 <= index <= len(commutes):
        removed = commutes.pop(index - 1)
        save_json(COMMUTES_FILE, commutes)
        typer.echo(f"Deleted commute: {removed['name']}")
    else:
        typer.echo("Invalid commute number.")

def main():
    app()
