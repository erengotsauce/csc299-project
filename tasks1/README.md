# Task CLI App

A simple command-line application for storing, listing, and searching tasks in a JSON file.

## Requirements

- Python 3.x

## Usage

Open your terminal and navigate to the `tasks1` directory.

### Add a new task

```
python task_cli.py add "Task Title" "Task Description"
```

### List all tasks

```
python task_cli.py list
```

### Search for tasks

```
python task_cli.py search keyword
```

## Notes

- All tasks are stored in `tasks.json` in the same directory.
- Status for new tasks is set to `pending` by default.
