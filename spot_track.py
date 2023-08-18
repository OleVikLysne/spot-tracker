from rich.table import Table
from rich.console import Console
from utils import average, stdev, load_json, dump_json, get_current_season_id, get_first_season_id, update_config, get_track_data_path, get_track_path
from enum import Enum
import re
from pathlib import Path
from time import sleep

QUERY_TYPE = Enum("QUERY_TYPES", ["ADD", "REVERT", "AVERAGE", "FIRST_X", "LAST_X", "SEASON_X", "NEW_SEASON", "TRACK_DATA", "DIST", "HELP"])
TRACK_DATA_PATH = get_track_data_path()
TRACKS: dict = load_json(get_track_path())


def initialise() -> bool:
    if get_first_season_id() != get_current_season_id():
        return False
    new_entry = f"season_{get_first_season_id()}"
    json = {new_entry : {}}
    dump_json(TRACK_DATA_PATH, json)
    return True
    

def get_query_type(query: str) -> QUERY_TYPE:
    if query == "avg" or query == "average":
        return QUERY_TYPE.AVERAGE
    if query == "new season":
        return QUERY_TYPE.NEW_SEASON
    if query == "dist" or query == "distribution":
        return QUERY_TYPE.DIST
    if query == "help":
        return QUERY_TYPE.HELP
    
    args = query.split()
    if len(args) == 2 and args[0] in TRACKS.keys() and args[1].isnumeric():
        return QUERY_TYPE.ADD
    if len(args) == 2 and args[0] in TRACKS.keys() and args[1] == "revert":
        return QUERY_TYPE.REVERT
    if len(args) == 2 and args[0] in TRACKS.keys() and args[1] == "data":
        return QUERY_TYPE.TRACK_DATA
    if len(args) == 2 and args[0] == "last" and args[1].isnumeric():
        return QUERY_TYPE.LAST_X
    if len(args) == 2 and args[0] == "first" and args[1].isnumeric():
        return QUERY_TYPE.FIRST_X
    if (
        len(args) == 1 and (args[0] == "cur" or args[0] == "current") or
        bool(re.match(r"^s ?[1-9][0-9]*( [1-9][0-9]*)* ?$", query)) or
        bool(re.match(r"^season ?[1-9][0-9]*( [1-9][0-9]*)* ?$", query))
    ):
        return QUERY_TYPE.SEASON_X
    return None


def get_seasons(*season_ids: tuple[int]) -> dict:
    TRACK_DATA: dict = load_json(TRACK_DATA_PATH)
    master_dict = {}
    for id in season_ids:
        season = f"season_{id}"
        if season not in TRACK_DATA:
            continue
        season_data = TRACK_DATA[season]

        for track, scores in season_data.items():
            if track not in TRACKS.keys():
                raise ValueError("Invalid track name.")
            if track in master_dict:
                master_dict[track] += scores
            else:
                master_dict[track] = scores
    return master_dict


def trim_to_subset(df: dict, amount: int, side="back") -> None:
    for track, race_scores in df.items():
        if len(race_scores) <= amount:
            continue
        if side == "back":
            df[track] = race_scores[-amount:]
        elif side == "front":
            df[track] = race_scores[:amount]
        else:
            raise ValueError("Invalid side selection")


def get_macro_info(df: dict) -> tuple:
    races_played = sum(len(x) for x in df.values())
    total_pts_scored = sum(sum(df.values(), []))
    overall_avg = round(total_pts_scored*12/races_played, 1)
    return overall_avg, races_played


def display_table(
        data_array: list[tuple], 
        *columns: tuple[str], 
        title: str = None, 
        styles: list[str] = None,
        justify: list[str] = None
        ):
    styles = ["cyan", "green", "white", "red"] if styles is None else styles
    justify = ["center" for _ in range(len(columns))] if justify is None else justify
    table = Table(title=title)
    for i, column in enumerate(columns):
        table.add_column(column, style=styles[i%len(styles)], justify=justify[i])
    for track_data in data_array:
        table.add_row(*(str(x) for x in track_data))
    Console().print(table)


def add_race(track: str, pts: int, season_id: int = None) -> None:
    season_id = get_current_season_id() if season_id is None else season_id
    track_data = load_json(TRACK_DATA_PATH)
    season = f"season_{season_id}"
    if season not in track_data:
        raise ValueError("Attempted to add race to a non-existant season")
    
    season_data = track_data[season]
    if track in season_data:
        season_track_data = season_data[track]
        season_track_data.append(pts)
    else:
        season_data[track] = [pts]
    
    dump_json(TRACK_DATA_PATH, track_data)


def revert_race(track: str, season_id: int = None):
    season_id = get_current_season_id() if season_id is None else season_id
    track_data = load_json(TRACK_DATA_PATH)
    season = f"season_{season_id}"
    if season not in track_data:
        raise ValueError("Attempted to revert race from a non-existant season")
    
    season_data = track_data[season]
    if track in season_data:
        season_track_data = season_data[track]
        if len(season_track_data) > 0:
            season_track_data.pop()
        if len(season_track_data) == 0:
            season_data.pop(track)

    dump_json(TRACK_DATA_PATH, track_data)


def new_season(new_id: int) -> None:
    json = load_json(TRACK_DATA_PATH)
    new_entry = f"season_{new_id}"
    json[new_entry] = {}
    dump_json(TRACK_DATA_PATH, json)
    update_config("currentseason", str(new_id))


def help():
    data_array = [
        ('add race', 'add a new race to the stats. Input track name + points (eg. "lc 7")'),
        ('revert', 'reverts the last race you added to a given track. Input as track name + revert (eg. "mc3 revert")'),
        ('average', 'shows various information about your performance on each track (average score, standard deviation)'),
        ('last x', '"x" is replaced by a number, which shows your stats across the last x amount of races'),
        ('first x', '"x" is replaced by a number, which shows your stats across the first x amount of races'),
        ('current', 'shows your stats for the current season'),
        ('new season', 'changes to a new season'),
        ('season x', '"x" is replaced by a number, which shows your stats from a given season'),
        ('track data', 'shows all data for a given track in chronological order (eg. "dks data")'),
        ('dist', 'shows hows often each track is picked per mogi')
    ]
    display_table(data_array, "Command", "Description", styles=["magenta", "white"], justify=["center", "left"])


def print_dist_table(df: dict, title: str = None) -> None:
    _, total_races = get_macro_info(df)
    data_array = [
        (
            track, # Track name
            "{:.0%}".format(len(scores)*12/total_races), # percentage
            round(average(scores), 1), # Average score
        )
        for track, scores in df.items()
    ]
    data_array.sort(key = lambda x: float(x[1].strip("%")) / 100.0, reverse=True)
    total_mogis = int(round(total_races/12, 0))
    title = f"Track distribution across {total_mogis} mogis" if title is None else title
    display_table(data_array, "track", "%", "avg", title=title)


def print_avg_table(df: dict, title: str = None, title_header: str = None) -> None:
    if len(df) == 0: return
    data_array = [
        (
            track, # Track name
            round(average(scores), 1), # Average score
            len(scores), # Number of races played
            round(stdev(scores), 1) # standard deviation
        )
        for track, scores in df.items()
    ]
    data_array.sort(key = lambda x : x[1], reverse=True)

    if title is None:
        overall_avg, total_races = get_macro_info(df)
        total_mogis = int(round(total_races/12, 0))
        title = f"{total_mogis} mogis with a {overall_avg} average"
    if title_header is not None:
        title = title_header + "\n" + title
    
    display_table(data_array, "track", "avg", "races", "STDev", title=title)



if __name__ == "__main__":
    FIRST_SEASON = get_first_season_id()
    CURRENT_SEASON = get_current_season_id()

    if not Path(TRACK_DATA_PATH).exists():
        if not initialise():
            print("Initialization failed. Check your settings.ini and make sure current and first is the same value.")
            sleep(10)
            exit()

    while True:
        query = input("\nQuery: ").lower()
        print()
        query_type = get_query_type(query)
        args = query.split()

        if query_type is None:
            print('Invalid query; check your formatting. Consider using "help".')
            continue

        elif query_type == QUERY_TYPE.ADD:
            track, pts = args[0], int(args[1])
            if pts < 0 or pts > 15:
                print("Invalid number of points.")
                continue
            else:
                add_race(track, pts)
                print(f'Added {pts} pts to {track}. If this was a mistake, type "{track} revert"')
        

        elif query_type == QUERY_TYPE.REVERT:
            track = args[0]
            revert_race(track)
            print(f"{track} has been reverted.")


        elif query_type == QUERY_TYPE.AVERAGE:
            df = get_seasons(*(s_id for s_id in range(FIRST_SEASON, CURRENT_SEASON+1)))
            print_avg_table(df, title_header="STATS FOR ALL SEASONS:")


        elif query_type == QUERY_TYPE.DIST:
            df = get_seasons(*(s_id for s_id in range(FIRST_SEASON, CURRENT_SEASON+1)))
            print_dist_table(df)


        elif query_type == QUERY_TYPE.LAST_X:
            df = get_seasons(*(s_id for s_id in range(FIRST_SEASON, CURRENT_SEASON+1)))
            amount = int(args[1])
            trim_to_subset(df, amount, side="back")
            print_avg_table(df, title=f"Average across last {amount} races for each track")


        elif query_type == QUERY_TYPE.FIRST_X:
            df = get_seasons(*(s_id for s_id in range(FIRST_SEASON, CURRENT_SEASON+1)))
            amount = int(args[1])
            trim_to_subset(df, amount, side="front")
            print_avg_table(df, title=f"Average across first {amount} for each track")
        

        elif query_type == QUERY_TYPE.SEASON_X:
            if query == "cur" or query == "current":
                season_ids = (CURRENT_SEASON,)
            else:
                season_ids = list(map(int, re.findall(r"\d+", query)))
                if max(season_ids) > CURRENT_SEASON or min(season_ids) < FIRST_SEASON:
                    print("One of the queried season IDs are invalid.")
                    continue
            df = get_seasons(*season_ids)
            print_avg_table(df, title_header=f"STATS FOR SEASON{'S' if len(season_ids)>1 else ''} {', '.join(map(str, season_ids))}:")


        elif query_type == QUERY_TYPE.NEW_SEASON:
            print(f"Are you sure you want to change from season {CURRENT_SEASON} to season {CURRENT_SEASON+1}?")
            confirmation = input('Type "yes" to confirm: ')
            if confirmation == "yes":
                new_season(CURRENT_SEASON+1)
                print("New season has started!")
                CURRENT_SEASON+=1
            else:
                print("Did not change to new season.")
                continue


        elif query_type == QUERY_TYPE.TRACK_DATA:
            track = args[0]
            df = get_seasons(*(s_id for s_id in range(FIRST_SEASON, CURRENT_SEASON+1)))
            print(df[track])

        
        elif query_type == QUERY_TYPE.HELP:
            help()