#!/usr/bin/env python3
import subprocess
import sys

steps = [
    ("Lint check", ["cargo", "fmt", "--all", "--", "--check"]),
    ("Clippy check", ["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"]),
    ("Git add", ["git", "add", "."]),
    ("Git commit", None),
]

def run_step(name, cmd, index, total):
    sys.stdout.write(f"\rRun {name} ({index}/{total})\033[K")
    sys.stdout.flush()

    if name == "Git commit":
        sys.stdout.write("\nEnter commit message: ")
        sys.stdout.flush()
        msg = sys.stdin.readline().strip()
        if not msg:
            sys.stdout.write("Commit message cannot be empty\n")
            sys.exit(1)
        cmd = ["git", "commit", "-m", msg]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stdout.write(f"\n{name} failed:\n")
        if result.stdout.strip():
            sys.stdout.write(result.stdout)
        if result.stderr.strip():
            sys.stderr.write(result.stderr)
        sys.exit(result.returncode)

def main():
    total = len(steps)
    for i, (name, cmd) in enumerate(steps, start=1):
        run_step(name, cmd, i, total)
    sys.stdout.write("\nAll checks passed!\n")

if __name__ == "__main__":
    main()
