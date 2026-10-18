from pathlib import Path

def load_healthlink_prompt():
    return Path(__file__).with_name("healthlink.txt").read_text(encoding="utf-8")
