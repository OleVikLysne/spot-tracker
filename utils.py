import math
import json

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