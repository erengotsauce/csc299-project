import typer
import json
from pathlib import Path

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
def list_tasks():
    "List all tasks."
    tasks = load_json(TASKS_FILE)
    if not tasks:
        typer.echo("No tasks found.")
    for i, task in enumerate(tasks, 1):
        typer.echo(f"{i}. {task['name']}\n   Description: {task.get('description', '')}")
        if 'location' in task:
            typer.echo(f"   Location: {task['location']}")
        typer.echo(f"   Status: {task.get('status', 'pending')}")

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
def add_commute(name: str):
    "Add a new commute."
    commutes = load_json(COMMUTES_FILE)
    commutes.append({"name": name})
    save_json(COMMUTES_FILE, commutes)
    typer.echo(f"Commute added: {name}")

@app.command()
def list_commutes():
    "List all commutes."
    commutes = load_json(COMMUTES_FILE)
    if not commutes:
        typer.echo("No commutes found.")
    for i, commute in enumerate(commutes, 1):
        typer.echo(f"{i}. {commute['name']}")

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
