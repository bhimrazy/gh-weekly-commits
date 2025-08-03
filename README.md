# gh-weekly-commits

[![CI](https://github.com/bhimrazy/gh-weekly-commits/actions/workflows/ci.yml/badge.svg)](https://github.com/bhimrazy/gh-weekly-commits/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/bhimrazy/gh-weekly-commits/graph/badge.svg)](https://codecov.io/gh/bhimrazy/gh-weekly-commits)
[![license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/bhimrazy/gh-weekly-commits/blob/main/LICENSE)

📊 Visualize your weekly GitHub contributions across multiple repositories.

## Features
- Fetch weekly commit data for a GitHub user across multiple repositories.
- Visualize the data as a stacked bar chart.
- CLI support for easy usage.

## Installation

This project uses [uv](https://astral.sh/uv) for fast Python dependency management.

1. Install uv (if not already installed):

    ```bash
    curl -Ls https://astral.sh/uv/install.sh | sh
    ```

2. Install all dependencies:

    ```bash
    uv sync
    ```

## Usage

### CLI

```bash
ghweekly --username <your-username> \
         --repos org/repo1 org/repo2 \
         --start 2025-01-01 \
         --plot
```

### Script

Edit `scripts/plot_commits.py` to set your GitHub username and repository list, then run:

```bash
python scripts/plot_commits.py
```

## Weekly Commits Visualization

The latest weekly commits visualization is updated daily and can be found below:

![Weekly Commits](https://raw.githubusercontent.com/bhimrazy/gh-weekly-commits/refs/heads/main/weekly_commits.png)

## Development

### Run Tests

```bash
uv pip install pytest
pytest tests/
```

## License

MIT
