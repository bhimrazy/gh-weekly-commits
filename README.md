# gh-weekly-commits

[![CI](https://github.com/bhimrazy/gh-weekly-commits/actions/workflows/ci.yml/badge.svg)](https://github.com/bhimrazy/gh-weekly-commits/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/bhimrazy/gh-weekly-commits/graph/badge.svg)](https://codecov.io/gh/bhimrazy/gh-weekly-commits)
[![license](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/bhimrazy/gh-weekly-commits/blob/main/LICENSE)

## 📊 Visualize Your GitHub Activity

**gh-weekly-commits** is a fast, modern CLI tool to visualize your weekly GitHub contributions across multiple repositories.  
See your commit history, and (soon) issues, PRs, and discussions—all in one beautiful chart.

---

## Features

- 🔥 Fetch weekly commit data for any GitHub user across multiple repositories
- 📊 Visualize as a stacked bar chart (PNG)
- ⚡ Fast, reproducible setup with [uv](https://astral.sh/uv)
- 🛠️ CLI for easy usage
- 🧪 Tested and CI/CD ready
- 🚀 Upcoming: issues, PRs, discussions, more!

---

## Example Visualization

![Weekly Commits](https://raw.githubusercontent.com/bhimrazy/gh-weekly-commits/refs/heads/main/weekly_commits.png)

---

## Installation

This project uses [uv](https://astral.sh/uv) for fast Python dependency management.

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
uv sync --dev
```

---

## Quickstart

Fetch and plot your weekly commits:

```bash
ghweekly --username <your-username> \
         --repos org/repo1 org/repo2 \
         --plot
```

- `--start` and `--end` can be set to filter by date (default: start of year to today).
- `--token` (optional) for higher GitHub API rate limits.

---

## Advanced Usage

- **Scriptable:** Edit `scripts/plot_commits.py` for custom visualizations.
- **Export:** (Planned) Export data as CSV, JSON, or HTML.
- **Filter:** (Planned) Filter by repo, type, or date.
- **Config:** (Planned) Use a config file for persistent settings.

---

## Development

Clone the repo and install dev dependencies:

```bash
git clone https://github.com/bhimrazy/gh-weekly-commits.git
cd gh-weekly-commits
uv venv --python 3.12
source .venv/bin/activate
uv sync --dev
```

Run tests:

```bash
uv run pytest tests/
```

Lint code:

```bash
uv run ruff check src/ tests/
```

---

## Contributing

We welcome issues, feature requests, and PRs!  

---

## FAQ & Troubleshooting

- **API rate limits?** Use `--token` with a GitHub personal access token.
- **No output or empty chart?** Check your username, repo names, and date range.
- **Want more features?** open an issue!

---

## Roadmap

- [x] Fast, uv-native setup
- [x] Weekly commit visualization
- [ ] Issues, PRs, discussions, more
- [ ] Export and filter options
- [ ] Interactive CLI and config support

---

## Links

- [Documentation](https://github.com/bhimrazy/gh-weekly-commits#readme)
- [Issues](https://github.com/bhimrazy/gh-weekly-commits/issues)
- [PyPI](https://pypi.org/project/ghweekly/)

---

## License

MIT

---

## Author

Bhimraj Yadav
