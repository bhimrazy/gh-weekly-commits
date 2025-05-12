# gh-weekly-commits

📊 Visualize your weekly GitHub contributions across multiple repositories.

## Features
- Fetch weekly commit data for a GitHub user across multiple repositories.
- Visualize the data as a stacked bar chart.
- CLI support for easy usage.

## Installation

Install directly from the repository:

```bash
pip install git+https://github.com/your-username/gh-weekly-commits.git
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

## Development

### Run Tests

```bash
pytest tests/
```

## License

MIT
