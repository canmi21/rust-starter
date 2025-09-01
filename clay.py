#!/usr/bin/env python3
import subprocess
import sys
import threading
import queue
import time
from prompt_toolkit import PromptSession

steps = [
    ("Lint check", ["cargo", "fmt", "--all", "--", "--check"]),
    ("Clippy check", ["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings"]),
    ("Git add", ["git", "add", "."]),
    ("Git commit", None),
    ("Git push", ["git", "push"]),
]

status_queue = queue.Queue()
stop_flag = threading.Event()
commit_message = ""
input_active = threading.Event()
last_status = {}

def worker():
    global commit_message
    total = len(steps)
    for i, (name, cmd) in enumerate(steps, start=1):
        status_queue.put((name, i, total, "running"))
        if name == "Git commit":
            input_active.set()
            status_queue.put((name, i, total, "input"))
            while not commit_message:
                time.sleep(0.05)
            input_active.clear()
            cmd = ["git", "commit", "-m", commit_message]
        try:
            if cmd:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    status_queue.put((name, i, total, "fail"))
                    stop_flag.set()
                    return
        except FileNotFoundError:
            status_queue.put((name, i, total, "fail"))
            stop_flag.set()
            return
        status_queue.put((name, i, total, "done"))
    stop_flag.set()

def print_loop():
    progress_width = 20
    while not stop_flag.is_set() or not status_queue.empty():
        if input_active.is_set():
            time.sleep(0.05)
            continue
        try:
            name, index, total, state = status_queue.get(timeout=0.1)
        except queue.Empty:
            continue
        key = (name, index)
        if last_status.get(key) == state:
            continue
        last_status[key] = state
        step_line = f"Run {name} ({index}/{total})"
        bar_done = int(progress_width * index / total)
        bar = f"[{'=' * bar_done}{'>' if bar_done < progress_width else '='}{' ' * (progress_width - bar_done - 1)}]"
        sys.stdout.write("\033[F\033[K" * 2)
        sys.stdout.write(f"{step_line}\n{bar}\n")
        sys.stdout.flush()
        if state == "fail":
            print(f"{name} failed.")
            stop_flag.set()
            break

def commit_input():
    global commit_message
    session = PromptSession("> ")
    commit_message = session.prompt()

threading.Thread(target=worker, daemon=True).start()
time.sleep(0.1)
sys.stdout.write("\n\n")
threading.Thread(target=commit_input, daemon=True).start()
print_loop()
print("All tasks done!")
