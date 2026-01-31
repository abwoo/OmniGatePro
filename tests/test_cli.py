from typer.testing import CliRunner
from cli import app
import json

runner = CliRunner()

def test_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Artfish System Diagnosis" in result.stdout

def test_status_json():
    result = runner.invoke(app, ["status", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "system" in data
    assert "version" in data

def test_run_dry_run():
    result = runner.invoke(app, ["run", "Test goal", "--style", "minimal"])
    assert result.exit_code == 0
    assert "DRY-RUN MODE" in result.stdout
    assert "Test goal" in result.stdout

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Artfish Runtime Engine CLI" in result.stdout
