import json
from configparser import ConfigParser
from pathlib import Path
from time import sleep

def build_df(season_id: int) -> dict:
    with open(f"season{season_id}.txt", "r") as f:
        df = {}
        data = f.read().split("\n")
        for track_data in data:
            track_data = track_data.split(" ")
            track_name = track_data[0]
            track_name = track_name[0:-1] # removes the colon
            track_scores = track_data[1:]
            if len(track_name) > 0 and len(track_scores) > 0:
                df[track_name] = [int(score) for score in track_scores]
        return df


if __name__ == "__main__":
    if Path("track_data.json").exists():
        print("track_data.json already exists. Aborting to avoid accidental data overwrite.")
        sleep(5)

    config = ConfigParser()
    config.read("settings.ini")
    cur = int(config["GENERAL"]["currentseason"])
    first = int(config["GENERAL"]["firstseason"])
    master_dict = {}

    for s in range(first, cur+1):
        season_data = build_df(s)
        master_dict[f"season_{s}"] = season_data
    
    with open("track_data.json", "w") as output_file:
        json.dump(master_dict, output_file, indent=4)