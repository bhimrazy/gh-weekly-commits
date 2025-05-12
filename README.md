# gh-weekly-commits

📊 Visualize your weekly GitHub contributions across multiple repositories.

## Features
- Fetch weekly commit data for a GitHub user across multiple repositories.
- Visualize the data as a stacked bar chart.
- CLI support for easy usage.

## Installation

You can install the package directly from the GitHub repository:

```bash
pip install git+https://github.com/bhimrazy/gh-weekly-commits
```

```bash
pip install -r requirements.txt
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

![Weekly Commits](./weekly_commits.png)

## Development

### Run Tests

```bash
pytest tests/
```

## License

MIT
