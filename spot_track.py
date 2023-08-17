from rich.table import Table
from rich.console import Console
from configparser import ConfigParser
import json
from utils import average, stdev, load_json



def get_current_season() -> int:
    config = ConfigParser()
    config.read("settings.ini")
    return int(config["GENERAL"]["currentseason"])

def get_first_season() -> int:
    config = ConfigParser()
    config.read("settings.ini")
    return int(config["GENERAL"]["firstseason"])




# def fetch_season_raw(id: int) -> str:
#     with open(f"season{id}.txt", "r") as f:
#         return f.read()


# def build_df(rawdata: str) -> dict:
#     df = {}
#     data = rawdata.split("\n")
#     for track_data in data:
#         track_data = track_data.split(" ")
#         track_name = track_data[0]
#         track_name = track_name[0:-1] # removes the colon
#         track_scores = track_data[1:]
#         if len(track_name) > 0 and len(track_scores) > 0:
#             df[track_name] = [int(score) for score in track_scores]

#     return df

# def fetch_season(id) -> dict:
#     rawdata = fetch_season_raw(id)
#     return build_df(rawdata)

# def fetch_seasons(*args) -> dict:
#     return merge_seasons(*(fetch_season(id) for id in args))

# def merge_seasons(*args):
#     df = args[0]
#     for season in args[1:]:
#         for track in df.keys():
#             if track in season:
#                 df[track] += season[track]

#     return df

def get_display_format(data):
    sorted_data_array = []
    for track, scores in data.items(): # Build an array containing data for console display
        avg = round(average(scores), 1)
        race_count = len(scores)
        std = round(stdev(scores), 1)
        sorted_data_array.append((avg, track, race_count, std))

    sorted_data_array.sort(reverse=True)
    return sorted_data_array

def get_general_info(data) -> tuple:
    sum = 0
    races = 0
    for scores in data.values():
        for score in scores:
            sum += score
            races += 1
    
    overall_avg = round(sum*12/races, 1)
    total_mogis = int(round(races/12, 0))
    return overall_avg, total_mogis



def print_table(data, title=""):
    table = Table(title=title)
    table.add_column("avg", style="cyan")
    table.add_column("track", style="magenta")
    table.add_column("races", style="green")
    table.add_column("STDev", style="red")

    for track_data in data:
        table.add_row(*(str(x) for x in track_data))
    
    console = Console()
    console.print(table)

def load_json(filename: str) -> dict:
    with open(filename, "r") as f:
        return json.load(f)

        
def main():
    # first_season = get_first_season()
    # current_season = get_current_season()
    # all_seasons = fetch_seasons(*(s for s in range(first_season, current_season+1)))
    # displayable = get_display_format(all_seasons)
    # overall_avg, total_mogis = get_general_info(all_seasons)
    # title = f"{overall_avg} average across {total_mogis} mogis"
    # print_table(displayable, title=title)

    track_data = load_json("track_data.json")
    print(track_data)




if __name__ == "__main__":
    main()
    from time import sleep
    #sleep(10)