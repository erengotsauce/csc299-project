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

def update_task_status(task_id, new_status):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            save_tasks(tasks)
            print(f"Task [{task_id}] status updated to '{new_status}'.")
            return
    print(f"No task found with ID {task_id}.")

def delete_task(task_id):
    tasks = load_tasks()
    new_tasks = [task for task in tasks if task['id'] != task_id]
    if len(new_tasks) == len(tasks):
        print(f"No task found with ID {task_id}.")
        return
    # Reassign IDs in chronological order
    for idx, task in enumerate(new_tasks, start=1):
        task['id'] = idx
    save_tasks(new_tasks)
    print(f"Task [{task_id}] deleted and IDs reordered.")

def main():
    parser = argparse.ArgumentParser(description='Task CLI App')
    subparsers = parser.add_subparsers(dest='command')

    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('description', help='Task description')

    list_parser = subparsers.add_parser('list', help='List all tasks')

    search_parser = subparsers.add_parser('search', help='Search tasks')
    search_parser.add_argument('query', help='Search query')

    update_parser = subparsers.add_parser('update', help='Update task status')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('status', help='New status')

    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task ID')

    args = parser.parse_args()

    if args.command == 'add':
        add_task(args.title, args.description)
    elif args.command == 'list':
        list_tasks()
    elif args.command == 'search':
        search_tasks(args.query)
    elif args.command == 'update':
        update_task_status(args.id, args.status)
    elif args.command == 'delete':
        delete_task(args.id)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
