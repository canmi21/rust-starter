#!/usr/bin/env python3
import subprocess
import sys
import time

steps = [
    ("Lint check", ["cargo", "fmt", "--all", "--", "--check"]),
    ("Clippy check", ["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"]),
    ("Git add", ["git", "add", "."]),
    ("Git commit", None),
    ("Git push", ["git", "push"]),
]

def print_progress_bar(completed, total, width=20):
    done = int(width * completed / total)
    bar = f"[{'=' * done}{'>' if done < width else '='}{' ' * (width - done - 1)}]"
    sys.stdout.write(f"\033[F\033[K{bar}\n")
    sys.stdout.flush()

def run_step(name, cmd, index, total):
    sys.stdout.write(f"\rRun {name} ({index}/{total})\033[K\n")
    sys.stdout.flush()
    sys.stdout.write("[>                    ]\n")
    sys.stdout.flush()

    if name == "Git commit":
        sys.stdout.write("Enter commit message: ")
        sys.stdout.flush()
        msg = sys.stdin.readline().strip()
        if not msg:
            sys.stdout.write("Commit message cannot be empty\n")
            sys.exit(1)
        cmd = ["git", "commit", "-m", msg]

    if name == "Git push":
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            time.sleep(0.05)
            print_progress_bar(index, total)
        process.wait()
        if process.returncode != 0:
            sys.stdout.write(f"\n{name} failed:\n")
            sys.exit(process.returncode)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            sys.stdout.write(f"\n{name} failed:\n")
            if result.stdout.strip():
                sys.stdout.write(result.stdout)
            if result.stderr.strip():
                sys.stderr.write(result.stderr)
            sys.exit(result.returncode)
        print_progress_bar(index, total)

def main():
    total = len(steps)
    for i, (name, cmd) in enumerate(steps, start=1):
        run_step(name, cmd, i, total)
    sys.stdout.write("All tasks done!\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
