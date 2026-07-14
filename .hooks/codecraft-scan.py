#!/usr/bin/env python3
"""CodeCraft pre-commit hook — scan Python files before commit."""
import subprocess
import sys

def main():
    result = subprocess.run(
        ["codecraft", "scan", "dir", "."],
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()