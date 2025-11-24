import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

import src.cta_pkms.__init__ as cta

def test_ensure_file(tmp_path):
    file_path = tmp_path / "test.json"
    cta.ensure_file(file_path)
    assert file_path.exists()
    assert file_path.read_text() == "[]"

def test_load_and_save_json(tmp_path):
    file_path = tmp_path / "data.json"
    data = [{"foo": "bar"}]
    cta.save_json(file_path, data)
    loaded = cta.load_json(file_path)
    assert loaded == data

@patch("requests.get")
def test_fetch_next_arrivals_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "ctatt": {"eta": [{"rt": "Red", "destNm": "Howard", "arrT": "12:00", "isSch": "1", "isDly": "0", "trainId": "123"}]}
    }
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp
    arrivals = cta.fetch_next_arrivals("40320")
    assert arrivals[0]["route"] == "Red"
    assert arrivals[0]["destination"] == "Howard"

@patch("requests.get")
def test_fetch_cta_alerts_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"CTAAlerts": {"Alert": [{"alert": "Test"}]}}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp
    alerts = cta.fetch_cta_alerts()
    assert alerts[0]["alert"] == "Test"

@patch("src.cta_pkms.__init__.OpenAI")
def test_call_openai_route_planner_success(mock_openai):
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "Test route recommendation"
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client
    result = cta.call_openai_route_planner(
        {"stop_name": "A", "stop_id": "1"},
        {"stop_name": "B", "stop_id": "2"},
        [], [], "fake-key"
    )
    assert "Test route recommendation" in result

def test_select_commute(monkeypatch, tmp_path):
    commutes = [
        {"name": "Test", "departure_station": "A", "departure_stop_id": "1", "arrival_station": "B", "arrival_stop_id": "2"}
    ]
    file_path = tmp_path / "commutes.json"
    file_path.write_text(json.dumps(commutes))
    monkeypatch.setattr(cta, "COMMUTES_FILE", file_path)
    monkeypatch.setattr("typer.prompt", lambda *args, **kwargs: 1)
    departure, arrival = cta.select_commute()
    assert departure["stop_name"] == "A"
    assert arrival["stop_name"] == "B"
