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
