import os
import requests
import typer
import json
from pathlib import Path
import sys
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Button
from openai import OpenAI

CTA_TRAIN_TRACKER_API_KEY = os.getenv("CTA_TRAIN_TRACKER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def fetch_cta_alerts():
    """
    Fetch CTA service alerts (Customer Alerts API).
    Returns a list of alerts (dicts).
    """
    url = f"http://lapi.transitchicago.com/api/1.0/alerts.aspx?outputType=JSON"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("CTAAlerts", {}).get("Alert", [])
    except Exception as e:
        print(f"Error fetching alerts: {e}")
        return []

def call_openai_route_planner(departure, arrival, arrivals, alerts, api_key=OPENAI_API_KEY):
    """
    Call OpenAI Chat Completions API to plan best route and estimate time.
    Returns dict with route and ETA.
    """

    client = OpenAI()
    import requests
    prompt = [
        {"role": "user", "content":
        f"You are a CTA commute planner. Given the following commute:\n"
        f"Departure: {departure['stop_name']} ({departure['stop_id']})\n"
        f"Arrival: {arrival['stop_name']} ({arrival['stop_id']})\n"
        f"Live arrivals: {json.dumps(arrivals)}\n"
        f"Service alerts: {json.dumps(alerts)}\n"
        "Find the quickest CTA 'L' route from departure to arrival, considering live arrivals and alerts. "
        "Feel free to use a different route if it is faster, even if it means terminating at a different station. Just make sure the it's not over 1 mile away from the original arrival station. "
        "Only return the recommended route and estimated time in minutes."
        "Format your response in this manner: [Briefly mention whether service alerts will affect commute, and how, if so] You will travel from [departure station] to [arrival station] via [line]. Estimated total commute time: [time] minutes. Your train will arrive at [departure time]. [mention transfers if applicable]"
        "Do not include brackets in your response."
        }
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=prompt
    )
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return "Could not get route recommendation."
    
    return completion.choices[0].message.content

def select_commute():
    """
    CLI to select a saved commute.
    Returns (departure, arrival) station dicts.
    """
    commutes = load_json(COMMUTES_FILE)
    if not commutes:
        typer.echo("No commutes found.")
        return None, None
    typer.echo("Select a commute:")
    for i, commute in enumerate(commutes, 1):
        typer.echo(f"{i}. {commute['name']} | Departure: {commute.get('departure_station', '')} | Arrival: {commute.get('arrival_station', '')}")
    idx = typer.prompt("Enter commute number", type=int)
    if 1 <= idx <= len(commutes):
        commute = commutes[idx - 1]
        departure = {"stop_name": commute["departure_station"], "stop_id": commute["departure_stop_id"]}
        arrival = {"stop_name": commute["arrival_station"], "stop_id": commute["arrival_stop_id"]}
        return departure, arrival
    else:
        typer.echo("Invalid selection.")
        return None, None



def run_single_station_selector():
    """
    TUI to select a single station (by stop_name/stop_id).
    Returns the selected station dict.
    """

    STATIONS_FILE = Path("cta-gtfs/route-stations.jsonl")

    def get_lines(stops):
            lines = {}
            for stop in stops:
                line = stop.get('route_id') or stop.get('line') or stop.get('line_id')
                if line:
                    if line not in lines:
                        lines[line] = []
                    lines[line].append(stop)
            return lines

    def load_stations():
        stations = []
        if STATIONS_FILE.exists():
            with STATIONS_FILE.open() as f:
                for line in f:
                    try:
                        station = json.loads(line)
                        stations.append(station)
                    except Exception:
                        continue
        return stations

    class StationSelector(App):
        CSS_PATH = None

        def __init__(self):
            super().__init__()
            self.stations = load_stations()
            self.lines = get_lines(self.stations)
            self.departure_line = None
            self.departure = None
            self.step = 'departure_line'

        def compose(self) -> ComposeResult:
            yield Header()
            if self.step == 'departure_line':
                yield Label("Select Departure Line:")
                yield ListView(*[
                    ListItem(Label(str(line))) for line in self.lines.keys()
                ], id="departure_line_list")
            elif self.step == 'departure_station':
                yield Label(f"Select Departure Station (Line: {self.departure_line}):")
                yield ListView(*[
                    ListItem(Label(f"{station['stop_name']}")) for station in self.lines[self.departure_line]
                ], id="departure_station_list")
            elif self.step == 'confirm':
                yield Label(f"Departure: {self.departure['stop_name']}")
                yield Button("Confirm Selection", id="confirm_btn")
            yield Footer()

        def on_mount(self):
                self.refresh_focus()
            
        def refresh_focus(self):
            if self.step == 'departure_line':
                self.query_one("#departure_line_list").focus()
            elif self.step == 'departure_station':
                self.query_one("#departure_station_list").focus()
            elif self.step == 'confirm':
                self.query_one("#confirm_btn").focus()

        def on_list_view_selected(self, event):
            list_id = event.list_view.id
            idx = event.index
            if self.step == 'departure_line' and list_id == "departure_line_list":
                self.departure_line = list(self.lines.keys())[idx]
                self.step = 'departure_station'
                self.refresh_screen()
            elif self.step == 'departure_station' and list_id == "departure_station_list":
                self.departure = self.lines[self.departure_line][idx]
                self.step = 'confirm'
                self.refresh_screen()
            

        def on_button_pressed(self, event):
            if event.button.id == "confirm_btn":
                if self.departure:
                    self.exit(self.departure)
                else:
                    self.step = 'departure_line'
                    self.refresh_screen()

        def refresh_screen(self):
            for widget in self.compose():
                self.mount(widget)
            self.refresh_focus()
    return StationSelector().run()

def fetch_next_arrivals(stop_id, api_key=CTA_TRAIN_TRACKER_API_KEY):
    """
    Fetch next 5 arrivals for a given stop_id from CTA Train Tracker API.
    Returns a list of arrivals (dicts).
    """
    # Placeholder endpoint and params (see CTA docs for details)
    url = f"http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key={api_key}&mapid={stop_id}&max=5&outputType=JSON"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Parse arrivals from API response (structure may vary)
        arrivals = []
        for eta in data.get("ctatt", {}).get("eta", []):
            arrivals.append({
                "route": eta.get("rt"),
                "destination": eta.get("destNm"),
                "arrival_time": eta.get("arrT"),
                "is_scheduled": eta.get("isSch"),
                "is_delayed": eta.get("isDly"),
                "train_id": eta.get("trainId"),
            })
        return arrivals
    except Exception as e:
        print(f"Error fetching arrivals: {e}")
        return []

def run_station_selector():

    STATIONS_FILE = Path("cta-gtfs/route-stations.jsonl")

    def get_lines(stops):
            lines = {}
            for stop in stops:
                line = stop.get('route_id') or stop.get('line') or stop.get('line_id')
                if line:
                    if line not in lines:
                        lines[line] = []
                    lines[line].append(stop)
            return lines

    def load_stations():
        stations = []
        if STATIONS_FILE.exists():
            with STATIONS_FILE.open() as f:
                for line in f:
                    try:
                        station = json.loads(line)
                        stations.append(station)
                    except Exception:
                        continue
        return stations

    class StationSelector(App):
        CSS_PATH = None

        def __init__(self):
            super().__init__()
            self.stations = load_stations()
            self.lines = get_lines(self.stations)
            self.departure_line = None
            self.arrival_line = None
            self.departure = None
            self.arrival = None
            self.step = 'departure_line'

        def compose(self) -> ComposeResult:
            yield Header()
            if self.step == 'departure_line':
                yield Label("Select Departure Line:")
                yield ListView(*[
                    ListItem(Label(str(line))) for line in self.lines.keys()
                ], id="departure_line_list")
            elif self.step == 'departure_station':
                yield Label(f"Select Departure Station (Line: {self.departure_line}):")
                yield ListView(*[
                    ListItem(Label(f"{station['stop_name']}")) for station in self.lines[self.departure_line]
                ], id="departure_station_list")
            elif self.step == 'arrival_line':
                yield Label("Select Arrival Line:")
                yield ListView(*[
                    ListItem(Label(str(line))) for line in self.lines.keys()
                ], id="arrival_line_list")
            elif self.step == 'arrival_station':
                yield Label(f"Select Arrival Station (Line: {self.arrival_line}):")
                yield ListView(*[
                    ListItem(Label(f"{station['stop_name']}")) for station in self.lines[self.arrival_line]
                ], id="arrival_station_list")
            elif self.step == 'confirm':
                yield Label(f"Departure: {self.departure['stop_name']}")
                yield Label(f"Arrival: {self.arrival['stop_name']}")
                yield Button("Confirm Selection", id="confirm_btn")
            yield Footer()

        def on_mount(self):
            self.refresh_focus()

        def refresh_focus(self):
            if self.step == 'departure_line':
                self.query_one("#departure_line_list").focus()
            elif self.step == 'departure_station':
                self.query_one("#departure_station_list").focus()
            elif self.step == 'arrival_line':
                self.query_one("#arrival_line_list").focus()
            elif self.step == 'arrival_station':
                self.query_one("#arrival_station_list").focus()
            elif self.step == 'confirm':
                self.query_one("#confirm_btn").focus()

        def on_list_view_selected(self, event):
            list_id = event.list_view.id
            idx = event.index
            if self.step == 'departure_line' and list_id == "departure_line_list":
                self.departure_line = list(self.lines.keys())[idx]
                self.step = 'departure_station'
                self.refresh_screen()
            elif self.step == 'departure_station' and list_id == "departure_station_list":
                self.departure = self.lines[self.departure_line][idx]
                self.step = 'arrival_line'
                self.refresh_screen()
            elif self.step == 'arrival_line' and list_id == "arrival_line_list":
                self.arrival_line = list(self.lines.keys())[idx]
                self.step = 'arrival_station'
                self.refresh_screen()
            elif self.step == 'arrival_station' and list_id == "arrival_station_list":
                self.arrival = self.lines[self.arrival_line][idx]
                self.step = 'confirm'
                self.refresh_screen()

        def on_button_pressed(self, event):
            if event.button.id == "confirm_btn":
                if self.departure and self.arrival:
                    self.exit((self.departure, self.arrival))
                else:
                    self.step = 'departure_line'
                    self.refresh_screen()

        def refresh_screen(self):
            for widget in self.compose():
                self.mount(widget)
            self.refresh_focus()
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

@app.command()
def next_arrivals():
    """
    Select a station via TUI and display next 3 train arrivals using CTA API.
    """
    typer.echo("Launching station selector...")
    station = run_single_station_selector()
    if not station or "stop_id" not in station:
        typer.echo("No station selected or missing stop_id.")
        return
    stop_id = station["stop_id"]
    typer.echo(f"Fetching next arrivals for {station['stop_name']} (stop_id: {stop_id})...")
    arrivals = fetch_next_arrivals(stop_id)
    if not arrivals:
        typer.echo("No arrivals found or API error.")
        return
    typer.echo(f"Next 3 arrivals at {station['stop_name']}:")
    for i, arr in enumerate(arrivals, 1):
        typer.echo(f"{i}. Route: {arr['route']} | Destination: {arr['destination']} | Arrival Time: {arr['arrival_time']}" +
                   (" | Delayed" if arr.get('is_delayed') == '1' else ""))
        
@app.command()
def plan_commute():
    """
    Plan a commute using saved commutes, CTA APIs, and OpenAI.
    """
    departure, arrival = select_commute()
    if not departure or not arrival:
        return
    typer.echo(f"Planning commute from {departure['stop_name']} to {arrival['stop_name']}...")
    arrivals = fetch_next_arrivals(departure["stop_id"])
    alerts = fetch_cta_alerts()
    typer.echo("Calling AI for best route and ETA...")
    result = call_openai_route_planner(departure, arrival, arrivals, alerts)
    typer.echo("--- Commute Plan ---")
    typer.echo(result)

def main():
    app()
