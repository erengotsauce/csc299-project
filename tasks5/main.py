import json
import argparse
from pathlib import Path

# Define the path to the JSON file
tasks_file = Path("tasks.json")

# Ensure the JSON file exists
def initialize_tasks_file():
    if not tasks_file.exists():
        with open(tasks_file, "w") as file:
            json.dump([], file)

# Load tasks from the JSON file
def load_tasks():
    with open(tasks_file, "r") as file:
        return json.load(file)

# Save tasks to the JSON file
def save_tasks(tasks):
    with open(tasks_file, "w") as file:
        json.dump(tasks, file, indent=4)

# Add a new task
def add_task(name, description, status):
    tasks = load_tasks()
    tasks.append({"name": name, "description": description, "status": status})
    save_tasks(tasks)
    print(f"Task '{name}' added successfully.")

# List all tasks
def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks available.")
    else:
        for i, task in enumerate(tasks, start=1):
            print(f"{i}. {task['name']} - {task['description']} [{task['status']}]")

# Update an existing task
def amend_task(index, name=None, description=None, status=None):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        if name:
            tasks[index]["name"] = name
        if description:
            tasks[index]["description"] = description
        if status:
            tasks[index]["status"] = status
        save_tasks(tasks)
        print(f"Task {index + 1} updated successfully.")
    else:
        print("Invalid task index.")

# Delete a task
def delete_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        removed_task = tasks.pop(index)
        save_tasks(tasks)
        print(f"Task '{removed_task['name']}' deleted successfully.")
    else:
        print("Invalid task index.")

# Main function to handle CLI arguments
def main():
    parser = argparse.ArgumentParser(description="Task Manager CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Add task command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("name", help="Name of the task")
    add_parser.add_argument("description", help="Description of the task")
    add_parser.add_argument("status", choices=["completed", "pending"], help="Status of the task")

    # List tasks command
    subparsers.add_parser("list", help="List all tasks")

    # Amend task command
    amend_parser = subparsers.add_parser("amend", help="Amend an existing task")
    amend_parser.add_argument("index", type=int, help="Index of the task to amend (1-based)")
    amend_parser.add_argument("--name", help="New name of the task")
    amend_parser.add_argument("--description", help="New description of the task")
    amend_parser.add_argument("--status", choices=["completed", "pending"], help="New status of the task")

    # Delete task command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("index", type=int, help="Index of the task to delete (1-based)")

    args = parser.parse_args()

    initialize_tasks_file()

    if args.command == "add":
        add_task(args.name, args.description, args.status)
    elif args.command == "list":
        list_tasks()
    elif args.command == "amend":
        amend_task(args.index - 1, args.name, args.description, args.status)
    elif args.command == "delete":
        delete_task(args.index - 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
