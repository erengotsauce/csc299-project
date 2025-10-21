import json
import argparse
import os

DATA_FILE = 'tasks.json'

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def add_task(title, description):
    tasks = load_tasks()
    task_id = max([t['id'] for t in tasks], default=0) + 1
    task = {'id': task_id, 'title': title, 'description': description, 'status': 'pending'}
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task added: {task}")

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        print(f"[{task['id']}] {task['title']} - {task['description']} (Status: {task['status']})")

def search_tasks(query):
    tasks = load_tasks()
    found = [t for t in tasks if query.lower() in t['title'].lower() or query.lower() in t['description'].lower()]
    if not found:
        print("No matching tasks found.")
        return
    for task in found:
        print(f"[{task['id']}] {task['title']} - {task['description']} (Status: {task['status']})")

def main():
    parser = argparse.ArgumentParser(description='Task CLI App')
    subparsers = parser.add_subparsers(dest='command')

    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('description', help='Task description')

    list_parser = subparsers.add_parser('list', help='List all tasks')

    search_parser = subparsers.add_parser('search', help='Search tasks')
    search_parser.add_argument('query', help='Search query')

    args = parser.parse_args()

    if args.command == 'add':
        add_task(args.title, args.description)
    elif args.command == 'list':
        list_tasks()
    elif args.command == 'search':
        search_tasks(args.query)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
