# CodeCraft

Your personal Python skill forge — **scans your code**, **finds gaps**, **generates challenges**, and **schedules reviews**.

```
codecraft scan ~/Desktop/Python
codecraft debt report
codecraft remix generate
codecraft schedule queue
```

## Features

- **Code Scanner** — AST-based analysis, detects 76+ concepts, 12 anti-pattern detectors
- **Debt Tracker** — identifies learning gaps from your own code
- **Remix Engine** — generates transfer exercises in 20 domains
- **Spaced Repetition** — SM-2 scheduler for long-term retention
- **Practice Mode** — inline terminal coding with analysis & scoring
- **Beginner Path** — step-by-step learning (print → if/else → loops → functions)

## Install

```bash
git clone https://github.com/rudra/codecraft.git
cd codecraft
pip install -e ".[dev]"
codecraft --help
```

## Quick Start

```bash
# Scan your code
codecraft scan ~/Desktop/Python

# See what you're missing
codecraft debt report
codecraft remix gaps

# Practice step-by-step
codecraft practice path beginner

# Generate transfer exercises
codecraft remix generate --new-domain sports_cricket
```

## Domains

finance, bioinfo, sysadmin, gaming, iot, web_scraping, nlp, cli_tools, data_viz, simulation, audio, image, compilers, networking, crypto, **science**, **sports_cricket**, **travel**, **education**, **health**

## License

MIT
