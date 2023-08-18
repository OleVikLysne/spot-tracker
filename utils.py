import math
import json
from configparser import ConfigParser

def variance(data, ddof=0):
    n = len(data)
    mean = sum(data) / n
    return sum((x - mean) ** 2 for x in data) / (n - ddof)

def stdev(data):
    var = variance(data)
    return math.sqrt(var)

def average(lst: list) -> float:
    return sum(lst) / len(lst)

def load_json(filename: str) -> dict:
    with open(filename, "r") as f:
        return json.load(f)
    
def dump_json(filename: str, data) -> None:
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
def get_current_season_id() -> int:
    config = ConfigParser()
    config.read("settings.ini")
    return int(config["GENERAL"]["currentseason"])

def get_first_season_id() -> int:
    config = ConfigParser()
    config.read("settings.ini")
    return int(config["GENERAL"]["firstseason"])

def update_config(parameter: str, value: str):
    config = ConfigParser()
    config.read("settings.ini")
    config.set("GENERAL", parameter, value)

    with open("settings.ini", "w") as configfile:
        config.write(configfile)