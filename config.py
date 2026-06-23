#Allows for savable difficulties via config.json, planned to add more but thats all for now

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
DEFAULT_DIFFICULTY = "medium"
VALID_DIFFICULTIES = ("easy", "medium", "hard")


def load_config():
    if not CONFIG_PATH.exists():
        save_config({"difficulty": DEFAULT_DIFFICULTY})
        return {"difficulty": DEFAULT_DIFFICULTY}

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    difficulty = data.get("difficulty", DEFAULT_DIFFICULTY)
    if difficulty not in VALID_DIFFICULTIES:
        difficulty = DEFAULT_DIFFICULTY

    return {"difficulty": difficulty}


def save_config(data):
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
