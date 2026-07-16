# CodeCraft

```
   ______          __        ___________      _________
  / ____/___  ____/ /__     / ____/ ___/     / ____/   |  ____  ____
 / /   / __ \/ __  / _ \   / /    \__ \____ / /_  / /| | / __ \/ __ \
/ /___/ /_/ / /_/ /  __/  / /___ ___/ /___/ __/ / ___ |/ /_/ / /_/ /
\____/\____/\__,_/\___/   \____//____/     /_/   /_/ |_/ .___/ .___/
                                                        /_/   /_/
```

▶️ [**Watch Full Demo on YouTube**](https://youtu.be/qODFxYy5AGc) — Complete walkthrough of all 45+ features, 6 languages, 4 locales, and more.

> Your personal Python skill forge — **scans your code**, **finds learning gaps**, **generates transfer exercises**, and **schedules spaced repetition reviews** — all from patterns in your own code.

```bash
pip install codecraft-cli
```

---

## Quick Start

```bash
# Scan your codebase
codecraft scan ~/my-project

# See what you need to learn
codecraft remix gaps

# Start practicing
codecraft practice path beginner

# Review with spaced repetition
codecraft schedule queue
```

```
codecraft scan ~/Desktop/Python
codecraft remix generate --new-domain cricket
codecraft practice path beginner
codecraft schedule queue
```

---

## Setup Guide

### Prerequisites

- **Python 3.10+** — check with `python --version`
- **pip** — comes with Python
- **Git** — to clone and contribute

### Step 1: Clone

```bash
git clone https://github.com/rudrakhairnar16-bit/codecraft.git
cd codecraft
```

### Step 2: Install

```bash
# Basic install
pip install -e .

# With dev dependencies (tests, linting)
pip install -e ".[dev]"
```

### Step 3: Verify

```bash
codecraft --help
```

You should see available commands: `scan`, `debt`, `remix`, `schedule`, `dashboard`, `practice`, `progress`, `suggest`, `learn`, `stats`, `export`, `init`, `start`, `vacuum`, `precommit`, `sync`, `profile`, `status`.

### Step 4: Scan your first code

```bash
codecraft scan path/to/your/python/project
```

### Step 5: Explore

```bash
# Show your learning debt
codecraft debt report

# Find concept gaps
codecraft remix gaps

# Start beginner path
codecraft practice path beginner
```

---

## Features

### Code Scanner
- AST-based analysis reads your `.py` files without executing them
- Detects **130+ concepts** across 4 tiers (basics → advanced)
- Identifies **17 anti-patterns** (bare except, magic numbers, mutable defaults, etc.)
- Computes cyclomatic complexity and import dependency graphs

### Debt Tracker
- Aggregates debt items by pattern across your codebase
- Scores resolution rate (0–100%)
- Generates refactor challenges from your own code

### Remix Engine
- Finds concept gaps (< 3 exposures in your scanned code)
- Picks an unused domain from 20 available
- Generates transfer exercises with real-world context and starter code

### Spaced Repetition Scheduler
- SM-2 adaptation with exponential decay
- Per-concept strength from last-use timestamps
- Builds urgency-sorted review queue

### Practice Mode
- Inline terminal coding — type code, type `submit` to finish
- Live timer with `extend` for +2 minutes
- Full solution analysis: parse check, concept detection, complexity, score (0–100), strengths/issues, suggestion

### Beginner Path
Step-by-step curriculum:
1. `print_function` → `input_function` → `variable_assignment` → `basic_types`
2. `string_methods` → `f_strings` → `arithmetic`
3. `comparisons` → `if_else`
4. `for_loop` → `while_loop` → `list_ops` → `dict_ops`
5. `function_def` → `return_value`

---

## CLI Reference

### `scan` — Analyze code

```bash
codecraft scan <path>              # Scan a directory or file
```

### `debt` — Learning debt management

```bash
codecraft debt report              # Show summary of all debt
codecraft debt list                # List individual debt items
codecraft debt challenge           # Generate refactor challenge
```

### `remix` — Transfer exercises

```bash
codecraft remix gaps               # Find concept gaps
codecraft remix generate           # Generate an exercise for gap concepts
codecraft remix domains            # List all domains with coverage
codecraft remix review <domain>    # Show exercises for a domain
```

### `practice` — Inline coding practice

```bash
codecraft practice start <concept>          # Start practice with timer
codecraft practice list                     # List all available concepts
codecraft practice path                     # Show available learning paths
codecraft practice path beginner            # Show beginner path steps
codecraft practice path beginner --step 3   # Start from step 3
```

### `schedule` — Spaced repetition

```bash
codecraft schedule queue           # Show pending review items
codecraft schedule due             # Show items due now
codecraft schedule review          # Do a review session
codecraft schedule decay <days>    # Set decay constant (default: 7)
```

### `dashboard` — Visualize progress

```bash
codecraft dashboard summary        # Overall stats
codecraft dashboard heatmap        # Concept mastery heatmap
codecraft dashboard trends         # Learning trends over time
```

---

## Domains (20 total)

| Domain | Context |
|--------|---------|
| `finance` | Stocks, transactions, ledgers |
| `bioinfo` | DNA sequences, gene analysis |
| `sysadmin` | Logs, configs, system monitoring |
| `gaming` | Player stats, game mechanics |
| `iot` | Sensor data, device monitoring |
| `web_scraping` | HTML parsing, data extraction |
| `nlp` | Text processing, sentiment analysis |
| `cli_tools` | CLI argument parsing, file utils |
| `data_viz` | Charts, plots, data visualization |
| `simulation` | Monte Carlo, physics sims |
| `audio` | Sound processing, waveforms |
| `image` | Pixel manipulation, filters |
| `compilers` | AST, parsing, code gen |
| `networking` | Sockets, HTTP, protocols |
| `crypto` | Hashing, encryption, signing |
| `science` | Experiments, lab data, formulas |
| `sports_cricket` | 🏏 Scoring, stats, matches |
| `travel` | Trip planning, distances, budget |
| `education` | Grades, quizzes, student records |
| `health` | Fitness, BMI, diet tracking |

---

## Project Structure

```
codecraft/
├── src/codecraft/
│   ├── cli/              # Typer CLI commands
│   ├── db/               # DuckDB connection & migrations
│   ├── domains/          # 20 domain contexts with recipes
│   ├── engines/          # Debt, Remix, Scheduler, Templates
│   ├── models/           # Pydantic data models
│   ├── scanner/          # AST parser, concept extractor, debt detector
│   └── utils/            # Colors, helpers
├── tests/                # Pytest test suite (553+ tests)
├── pyproject.toml        # Project config & dependencies
└── README.md
```

---

## Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=codecraft --cov-report=term

# Run specific test file
pytest tests/test_scanner/test_concept_extractor.py -v
```

---

## License

All Rights Reserved. See [LICENSE](LICENSE) for details.

For usage permissions, contact [Rudra Khaire](https://github.com/rudrakhairnar16-bit).
