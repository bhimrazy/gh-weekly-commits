# gh-weekly-commits

gh-weekly-commits is a fast, modern Python CLI tool to visualize weekly GitHub commit activity across multiple repositories. It fetches commit data via GitHub API and generates stacked bar charts using matplotlib.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Bootstrap and Setup
- Install uv package manager: `pip install uv`
- Create virtual environment: `uv venv --python 3.12` -- takes 2 seconds. NEVER CANCEL.
- Activate environment: `source .venv/bin/activate`
- Install dependencies: `uv sync --dev` -- takes <1 second. NEVER CANCEL.
- Verify installation: `uv run ghweekly --help`

### Build and Test
- Run linting: `uv run ruff check src/ tests/` -- takes <1 second. NEVER CANCEL.
- Run tests: `uv run pytest tests/ -v` -- takes 5 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
- Run tests with coverage: `uv run pytest --cov=ghweekly src/ tests/ -v -s` -- takes 8 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
- Coverage reporting: `uv run coverage report && uv run coverage xml` -- takes <1 second. NEVER CANCEL.

### Run the Application
- Basic usage: `uv run ghweekly --username <username> --repos <org/repo1> <org/repo2>` -- takes <1 second. NEVER CANCEL.
- With plotting: `uv run ghweekly --username <username> --repos <org/repo1> <org/repo2> --plot` -- takes 1-2 seconds. NEVER CANCEL.
- Set non-interactive backend for headless environments: `export MPLBACKEND=Agg`
- For higher rate limits, use GitHub token: `--token <github_token>`
- Example script: `python scripts/plot_commits.py` -- takes 2 seconds. NEVER CANCEL.

## Validation

### Manual Testing Scenarios
- ALWAYS test CLI help after making changes: `uv run ghweekly --help`
- Test basic functionality: `uv run ghweekly --username test --repos test/test --start 2025-01-01 --end 2025-01-05`
- Test plotting functionality: `export MPLBACKEND=Agg && uv run ghweekly --username test --repos test/test --start 2025-01-01 --end 2025-01-05 --plot`
- Verify PNG generation: Check that `weekly_commits.png` is created
- Test example script: `export MPLBACKEND=Agg && python scripts/plot_commits.py`
- Test error handling: `uv run ghweekly` (should show usage error)
- ALWAYS run linting and tests before committing changes
- Expected behavior: Application handles API rate limits gracefully (HTTP 403 errors are normal without token)

### Complete End-to-End Validation
After making any changes, run this complete validation sequence:
```bash
# Clean environment
rm -rf .venv .coverage coverage.xml .pytest_cache .ruff_cache weekly_commits.png

# Setup
export PATH=$PATH:$HOME/.local/bin
uv venv --python 3.12
source .venv/bin/activate
uv sync --dev

# Verify installation
uv run ghweekly --help

# Test linting and formatting
uv run ruff check src/ tests/

# Run tests with coverage
uv run pytest --cov=ghweekly src/ tests/ -v -s

# Test basic functionality
export MPLBACKEND=Agg
uv run ghweekly --username test --repos test/test --start 2025-01-01 --end 2025-01-05 --plot

# Verify output
ls -la weekly_commits.png
```
Expected results: All commands succeed, tests pass, PNG file is created.

### CI Validation
- The CI pipeline (.github/workflows/ci.yml) tests Python 3.10, 3.11, and 3.12
- ALWAYS run `uv run ruff check src/ tests/` before committing (CI will fail otherwise)
- ALWAYS run `uv run pytest --cov=ghweekly src/ tests/ -v -s` before committing

## Important Details

### Timing Expectations
- Environment setup (uv venv): 2 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
- Dependency installation (uv sync --dev): <1 second. NEVER CANCEL. Set timeout to 60+ seconds.
- Linting (ruff check): <1 second. NEVER CANCEL. Set timeout to 10+ seconds.
- Tests (pytest): 5 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
- Tests with coverage: 8 seconds. NEVER CANCEL. Set timeout to 30+ seconds.
- CLI execution: 1-2 seconds. NEVER CANCEL. Set timeout to 30+ seconds.

### Key Dependencies
- Python 3.10+ required
- Core: requests, pandas, matplotlib
- Development: ruff, pytest, coverage, pytest-cov
- Uses uv for fast dependency management

### API Rate Limits
- GitHub API rate limits apply (60 requests/hour without token, 5000 with token)
- HTTP 403 errors are expected when rate limited
- Use `--token <github_token>` for higher limits
- Application handles rate limit errors gracefully

## Repository Structure

### Key Directories and Files
```
src/ghweekly/          # Main source code
├── __init__.py        # Package initialization (empty)
├── cli.py            # Command-line interface and argument parsing
└── main.py           # Core functionality for fetching and processing data

tests/                 # Test suite
├── test_cli.py       # CLI functionality tests
└── test_main.py      # Core functionality tests

scripts/              # Example scripts
└── plot_commits.py   # Example usage script

.github/workflows/    # CI/CD pipelines
└── ci.yml           # Main CI pipeline with matrix testing

Configuration files:
├── pyproject.toml    # Project metadata and dependencies
├── ruff.toml        # Linting configuration
├── setup.py         # Legacy setuptools configuration
└── uv.lock          # Dependency lock file
```

### Important Files to Check After Changes
- Always check `src/ghweekly/cli.py` when modifying command-line interface
- Always check `src/ghweekly/main.py` when modifying data fetching logic
- Always run tests in `tests/` after any changes
- Check `pyproject.toml` for dependency and metadata changes

## Common Tasks

### Adding New Dependencies
- Add to pyproject.toml dependencies array
- Run `uv sync --dev` to install
- Run tests to verify compatibility

### Modifying CLI Interface
- Edit `src/ghweekly/cli.py`
- Update argument parser in main() function
- Add corresponding tests in `tests/test_cli.py`
- Test with `uv run ghweekly --help`

### Changing Data Processing
- Edit `src/ghweekly/main.py`
- Modify fetch_weekly_commits() function
- Add tests in `tests/test_main.py`
- Test with real data scenarios

### Output Files
- `weekly_commits.png` - Generated chart file (not committed, created when using --plot)
- `.coverage` - Coverage data file (not committed, created by pytest --cov)
- `coverage.xml` - XML coverage report (not committed, created by coverage xml)
- `.pytest_cache/` - Pytest cache directory (not committed)
- `.ruff_cache/` - Ruff cache directory (not committed)
- All temporary files are in .gitignore

## Troubleshooting

### Common Issues
- Missing uv: Install with `pip install uv`
- Virtual environment not activated: Run `source .venv/bin/activate`
- matplotlib display errors in headless environments: Set `export MPLBACKEND=Agg`
- GitHub API rate limits: Use `--token <github_token>` parameter
- Test failures: Check that all dependencies are installed with `uv sync --dev`

### Environment Variables
- `MPLBACKEND=Agg` - Required for headless matplotlib plotting
- `GH_TOKEN` - Can be used by scripts for GitHub API authentication

### Known Limitations
- Requires internet access for GitHub API calls
- Subject to GitHub API rate limits
- matplotlib requires GUI backend or Agg backend for headless use