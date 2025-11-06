import pytest
from unittest.mock import patch
from tasks3.task_cli import list_tasks

def test_list_tasks_prints_tasks():
    mock_tasks = [
        {'id': 1, 'title': 'Test', 'description': 'Desc', 'status': 'pending'},
        {'id': 2, 'title': 'Another', 'description': 'More', 'status': 'complete'}
    ]
    with patch('tasks3.task_cli.load_tasks', return_value=mock_tasks), \
            patch('builtins.print') as mock_print:
            list_tasks()
            mock_print.assert_any_call("[1] Test - Desc (Status: pending)")
            mock_print.assert_any_call("[2] Another - More (Status: complete)")

def test_list_tasks_prints_no_tasks():
    with patch('tasks3.task_cli.load_tasks', return_value=[]), \
         patch('builtins.print') as mock_print:
        list_tasks()
        mock_print.assert_called_once_with("No tasks found.")