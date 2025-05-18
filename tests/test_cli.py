import subprocess
import sys
from pathlib import Path


def test_cli_help():
    result = subprocess.run([sys.executable, '-m', 'ghweekly.cli', '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'usage:' in result.stdout
    assert '--username' in result.stdout

def test_cli_runs(monkeypatch, tmp_path):
    # Patch environment to avoid real API calls
    monkeypatch.setenv('GH_TOKEN', 'dummy')
    script = Path(__file__).parent.parent / 'src' / 'ghweekly' / 'cli.py'
    # Use a dummy repo and username, expect DataFrame printout
    result = subprocess.run([
        sys.executable, str(script),
        '--username', 'testuser',
        '--repos', 'org/repo1',
        '--start', '2025-01-01',
        '--end', '2025-05-01'
    ], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'repo1' in result.stdout

# Optionally, add more CLI tests for --plot, error handling, etc.
