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
push_flag = threading.Event()
commit_message = ""

def worker():
    global commit_message
    total = len(steps)
    for i, (name, cmd) in enumerate(steps, start=1):
        status_queue.put((name, i, total, "running"))
        if name == "Git commit":
            status_queue.put((name, i, total, "input"))
            while not commit_message:
                time.sleep(0.05)
            cmd = ["git", "commit", "-m", commit_message]
        try:
            if name == "Git push":
                push_flag.set()
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                while process.poll() is None:
                    time.sleep(0.05)
                if process.returncode != 0:
                    status_queue.put((name, i, total, "fail"))
                    stop_flag.set()
                    return
                push_flag.clear()
            else:
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
        try:
            name, index, total, state = status_queue.get(timeout=0.1)
        except queue.Empty:
            continue
        step_line = f"Run {name} ({index}/{total})"
        bar_done = int(progress_width * index / total)
        bar = f"[{'=' * bar_done}{'>' if bar_done < progress_width else '='}{' ' * (progress_width - bar_done - 1)}]"
        sys.stdout.write("\033[F\033[K" * 2)
        if state == "input":
            sys.stdout.write(f"{step_line}\n> {commit_message}")
        elif push_flag.is_set():
            sys.stdout.write(f"{step_line}\n[ Pushing... ]")
        else:
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
