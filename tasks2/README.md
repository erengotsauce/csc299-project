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

### Update a task's status

```
python task_cli.py update TASK_ID NEW_STATUS
```

Replace `TASK_ID` with the numeric ID of the task and `NEW_STATUS` with the desired status (e.g., `completed`, `pending`, etc.).

### Delete a task

```
python task_cli.py delete TASK_ID
```

Replace `TASK_ID` with the numeric ID of the task you want to remove.

## Notes

- All tasks are stored in `tasks.json` in the same directory.
- Status for new tasks is set to `pending` by default.
