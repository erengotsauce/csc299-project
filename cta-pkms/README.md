# CTA PKMS Commute Planner

A Python CLI/TUI tool for planning commutes on the Chicago 'L' using GTFS data, real-time CTA APIs, and OpenAI for intelligent route recommendations.

## Features
- **Task Management**: Add, list, amend, and delete personal tasks.
- **Commute Management**: Add, list, and delete commutes with station selection via TUI.
- **Real-Time Arrivals**: View next train arrivals for any station using CTA Train Tracker API.
- **Service Alerts**: Fetch current CTA service alerts.
- **AI-Powered Commute Planning**: Get optimal route and ETA using OpenAI Chat Completions API, considering live arrivals and service alerts.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/erengotsauce/csc299-project.git
   cd csc299-project
   ```
2. Create and activate a Python virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   Or, if using [uv](https://github.com/astral-sh/uv):
   ```sh
   uv pip install -r requirements.txt
   ```

## Environment Variables
Set the following environment variables for API access:
- `CTA_TRAIN_TRACKER_API_KEY`: Your CTA Train Tracker API key
- `OPENAI_API_KEY`: Your OpenAI API key

Example:
```sh
export CTA_TRAIN_TRACKER_API_KEY=your_cta_key
export OPENAI_API_KEY=your_openai_key
```

## Usage
Run the CLI:
```sh
python -m src.cta_pkms
```
Or, if installed as a package:
```sh
cta-pkms [COMMAND]
```

### Commands
- `add-task`         : Add a new task
- `amend-task`       : Amend an existing task
- `list-tasks`       : List all tasks
- `delete-task`      : Delete a task
- `add-commute`      : Add a new commute (TUI station selector)
- `list-commutes`    : List all commutes
- `delete-commute`   : Delete a commute
- `next-arrivals`    : Select a station and view next train arrivals
- `plan-commute`     : Select a saved commute and get AI-powered route/ETA

### Example
```sh
cta-pkms add-task "Buy groceries" "Pick up milk and eggs" --location "Near Clark/Lake"
cta-pkms add-commute "Home to Work"
cta-pkms plan-commute
```

## Testing
Run unit tests with pytest:
```sh
pytest
```

## Data Files
- GTFS-derived files should be placed in `cta-gtfs/` (e.g., `route-stations.jsonl`).
- Tasks and commutes are stored in `tasks.json` and `commutes.json` in the project root.
