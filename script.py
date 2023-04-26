import json
import os
from winner_to_loser_algo import L1,L2,L3,L4,L5

# GETTERS & SETTERS


def get_json_dict (file:str)->dict:
    """Takes a json file and returns a dictionary containg all its data"""
    with open (file , encoding="utf-8") as f :
        bracket = json.load(f)
        f.close()
    return bracket


def save_bracket (file:str,bracket:dict):
    """Saves the new generated json structure"""
    with open(file, mode="w",encoding="utf-8") as f :
        json.dump(bracket,f,indent="\t")
        f.close()


def get_round_names(bracket:dict)->list:
    """Returns a list with all the round names of the given bracket"""
    rounds = []
    for r in bracket["Rounds"] :
        rounds.append(get_simplified_round_name(r["Name"]))
    return rounds


def get_round_details (bracket:dict,round_name:str)->dict:
    """Takes a bracket and a round name (ex: roundof16 or grandfinals) and returns it's details"""
    for r in bracket["Rounds"]:
        if get_simplified_round_name(r["Name"]) == round_name :
            return r


def get_amount_matches (round_name:str,first_round=False,first_loser_week=False,separate_loser_round=False)->int:
    """Returns the amount of matches that will be played during the specified rounds"""
    amount_matches_winner = {"roundof128":64,"roundof64":32,"roundof32":16,"roundof16":8,"quarterfinals":4,"semifinals":2,"finals":1,"grandfinals":2}
    winner_bracket = amount_matches_winner[round_name]
    if first_round : # first round    
        loser_bracket_round1 = 0
        loser_bracket_round2 = 0
    elif first_loser_week : # first loser bracket week
        loser_bracket_round1 = 0
        loser_bracket_round2 = winner_bracket 
    elif round_name == "grandfinals":
        loser_bracket_round1 = 1 # losers grand finals
        loser_bracket_round2 = 0
    else : # any other round
        loser_bracket_round1 = winner_bracket * 2
        loser_bracket_round2 = winner_bracket
    if separate_loser_round :
        return {"Winner":winner_bracket,"LoserR1":loser_bracket_round1, "LoserR2":loser_bracket_round2}
    else :
        return {"Winner":winner_bracket,"Loser":loser_bracket_round1 + loser_bracket_round2}


def get_round_lengths (rounds:list):
    """Takes a list of round_names:
    Returns a dictionary with the amount of matches that have to be played for each part of each round
        ex: {'round_name':{'Winner':n,'LoserR1':n,'LoserR2':n}, etc...}"""
    round_lengths = {}
    round_lengths[rounds[0]] = get_amount_matches(rounds[0],first_round=True,separate_loser_round=True)
    round_lengths[rounds[1]] = get_amount_matches(rounds[1],first_loser_week=True,separate_loser_round=True)
    for k in range(2,len(rounds)) :
        round_name = rounds[k]
        round_lengths[round_name] = get_amount_matches(round_name,separate_loser_round=True)
    return round_lengths

def get_simplified_round_name (round_name:str)->str:
    return round_name.lower().replace(" ","").replace("-","")

def get_next_round(round_name:str)->str:
    rounds = ["roundof128","roundof64","roundof32","roundof16","quarterfinals","semifinals","finals","grandfinals"]
    round_progression = {}
    for k in range(len(rounds)-1):
        round_progression[rounds[k]] = rounds[k+1]
    return round_progression[round_name]

def set_round_matches (bracket:dict,round_name:str,match_ids:list):
    for r in range(len( bracket["Rounds"])) :
        round_ = bracket["Rounds"][r]
        if get_simplified_round_name(round_["Name"]) == round_name :
            round_["Matches"] = match_ids
    return bracket


def sort_rounds (rounds:list)->list:
    """In the rounds are not ordered properly."""
    rounds_sorted = ['roundof128',"roundof64","roundof32","roundof16","quarterfinals","semifinals","finals","grandfinals"]
    rounds_sorted.reverse()
    first_round_index = len(rounds)
    rounds = rounds_sorted[:first_round_index]
    rounds.reverse()
    return rounds             
    

# MANAGE ROUNDS

def fix_bracket_missing_rounds (bracket:dict,rounds:list):
    """Since 'sort_rounds' is able to add new rounds that are not present in the initial json file
    this function will add them to prevent the program from crashing going forward"""
    current_bracket_rounds = []
    for round_ in bracket["Rounds"] :
        current_bracket_rounds.append(get_simplified_round_name(round_["Name"]))
    for round_name in rounds :
        if round_name not in current_bracket_rounds :
            bracket["Rounds"].append({"Name":round_name,"Description": "","BestOf":0,"Beatmaps": [],"StartDate": "2727-07-27T00:00:00+00:00","Matches":[]})
    return bracket 


# CREATE MATCHES


def create_bracket_matches (bracket:dict,rounds:str)->dict:
    bracket["Matches"] = []
    bracket = create_round_matches(bracket , rounds[0] , first_round=True) # First round
    bracket = create_round_matches(bracket , rounds[1] , matches_already_created=len(bracket["Matches"]) , first_loser_week=True) # Second round & first losers round
    for k in range(2,len(rounds)) :
        bracket = create_round_matches(bracket , rounds[k] , matches_already_created=len(bracket["Matches"]))
    return bracket 


def create_round_matches (bracket:dict,round_name:str,matches_already_created=0,first_round=False,first_loser_week=False)->list :
    """"""
    amount_matches = get_amount_matches(round_name,first_round=first_round,first_loser_week=first_loser_week)
    start_id = matches_already_created
    print(round_name)
    round_info = get_round_details(bracket, round_name)
    matches = []
    for k in range(start_id , start_id + amount_matches["Winner"]): # Winner matches 
        matches.append({"ID":k,"Team1Score":None,"Team2Score":None,"Completed":False,"Losers":False,"PicksBans":[],"Current": False,"Date": round_info["StartDate"],"ConditionalMatches": [],"Acronyms": [],"PointsToWin": round_info["BestOf"]})
        print("[Create]", "[Match]", round_name, "Winner", k)
    for k in range(start_id + amount_matches["Winner"] , start_id + amount_matches["Winner"] + amount_matches["Loser"]): # Loser matches
        print("[Create]", "[Match]", round_name, "loser", k)  
        matches.append({"ID":k,"Team1Score":None,"Team2Score":None,"Completed":False,"Losers":True,"PicksBans":[],"Current": False,"Date": round_info["StartDate"],"ConditionalMatches": [],"Acronyms": [],"PointsToWin": round_info["BestOf"]})
    bracket["Matches"] += matches
    bracket = set_round_matches (bracket,round_name,list(range(start_id , start_id + amount_matches["Winner"] + amount_matches["Loser"])))
    return bracket


# PLACE MATCHES 


def place_matches (bracket:dict,rounds:list)->list:
    matches = bracket["Matches"]
    round_lengths = get_round_lengths(rounds)
    print(round_lengths)
    matches = place_matches_winner(matches,rounds,round_lengths) # Winner matches
    matches = place_matches_loser(matches,rounds,round_lengths)# Loser
    bracket["Matches"] = matches
    return bracket


def place_matches_winner (matches:list,rounds:list,round_lengths:dict):
    """Set the position of every Winner bracket matches"""
    x = 100
    y = 100
    y_start = 100
    y_step = 100
    matches_placed = 0
    for round_name in rounds :
        print("[Position]", "[Round]", round_name, "Winner ", "[Done]", matches_placed, "[ToDo]", round_lengths[round_name]["LoserR1"])
        for match_id in range(matches_placed , matches_placed + round_lengths[round_name]["Winner"]):
            print("[Position]", "[Match]", round_name, "Winner ", "[Match_id]", match_id, "y:", y, "x:", x)
            if round_name == "grandfinals": # grand finals & reset bracket
                matches[match_id]["Position"] = {"X":x,"Y":y-int(y_step/4)}
                matches_placed += 1
                x += 400
            else :
                matches[match_id]["Position"] = {"X":x,"Y":y}
                matches_placed += 1
                y += y_step
        matches_placed += round_lengths[round_name]["LoserR1"] + round_lengths[round_name]["LoserR2"]
        x += 400
        y_step *= 2
        y_start += int(y_step/4)
        y = y_start
    return matches


def place_matches_loser (matches:list,rounds:list,round_lengths:dict):
    """Set the position of every Loser bracket matches"""
    rounds = list(rounds)
    x = -300
    y = (round_lengths[rounds[0]]["Winner"]+1)*100 + 200 - 25# on prend la plus grande colonne de match et on se met 200 en dessous
    y_start = y
    y_step = 50
    matches_placed = round_lengths[rounds.pop(0)]["Winner"]
    for round_name in rounds :
        matches_placed += round_lengths[round_name]["Winner"]
        # round 1
        print("[Position]", "[Round]", round_name, "LoserR1", "[Done]", matches_placed, "[ToDo]", round_lengths[round_name]["LoserR1"])
        for match_id in range(matches_placed , matches_placed + round_lengths[round_name]["LoserR1"]):
            print("[Position]", "[Match]", round_name, "LoserR1", "[Match_id]", match_id, "y:", y, "x:", x)
            matches[match_id]["Position"] = {"X":x,"Y":y}
            matches_placed += 1
            y += y_step
        # round2
        print("[Position]", "[Round]", round_name, "LoserR2", "[Done]", matches_placed, "[ToDo]", round_lengths[round_name]["LoserR2"])
        x += 400
        y_step *= 2
        y_start += int(y_step/4)
        y = y_start
        for match_id in range(matches_placed , matches_placed + round_lengths[round_name]["LoserR2"]):
            print("[Position]", "[Match]", round_name, "LoserR2", "[Match_id]", match_id, "y:", y, "x:", x)
            matches[match_id]["Position"] = {"X":x,"Y":y}
            matches_placed += 1
            y += y_step
        x += 400
        y = y_start
    return matches


# LINK MATCHES TOGOTHEEEREEE BFF!!!!!    (Progression uwu)


def link_matches(bracket:dict,rounds:list):
    """Link every match together for a better experience <3"""
    progression = []
    progression += link_winner_to_winner(rounds)
    progression += link_winner_to_loser(rounds)
    progression += link_loser_to_loser(rounds)
    bracket["Progressions"] = progression
    return bracket

def link_winner_to_winner(rounds:list)-> list:
    """Links every winner bracker match to the next winner bracket match"""
    progression = []
    round_lengths = get_round_lengths(rounds)
    matches_linked = 0
    for round_name in rounds:
        for k in range (0,round_lengths[round_name]["Winner"],2):
            source_id = k + matches_linked
            # grandfinals
            if round_name == "grandfinals" :
                source_id -= 1
                progression.append({"SourceID":source_id,"TargetID":source_id+1})
                progression.append({"SourceID":source_id,"TargetID":source_id+1,"Losers":True})
                progression.append({"SourceID":source_id+2,"TargetID":source_id})
                print(source_id,source_id+1,round_name)
                print(source_id+2,source_id,round_name)
            # any other round
            else :
                target_id = k//2 + matches_linked + round_lengths[round_name]["Winner"] + round_lengths[round_name]["LoserR1"] + round_lengths[round_name]["LoserR2"]
                # CREATES THE LINKS
                for i in range(2):
                    if not (round_name == "finals" and i == 1 ):
                        print("[Link]","Winner to winner","[Round]",round_name,source_id+i,"-->",target_id)
                        progression.append({"SourceID":source_id+i,"TargetID":target_id })
        matches_linked += k+2 + round_lengths[round_name]["LoserR1"] + round_lengths[round_name]["LoserR2"]
    return progression

def link_winner_to_loser (rounds:list)->list:
    """Links every winner bracker match to the next loser bracket match"""
    progression = []
    round_lengths = get_round_lengths(rounds)
    first_round = True
    loser_week = 0
    matches_linked = 0
    for round_name in rounds :
        if round_name != "grandfinals":
            next_round_name = get_next_round(round_name)
            for match_count in range (round_lengths[round_name]["Winner"]):
                source_id = matches_linked + match_count
                if first_round :
                    target_id = ( source_id//2 ) + round_lengths[round_name]["Winner"] + round_lengths[next_round_name]["Winner"]
                else :
                    
                    target_id = matches_linked + round_lengths[round_name]["Winner"] + round_lengths[round_name]["LoserR1"] + round_lengths[round_name]["LoserR2"] + round_lengths[next_round_name]["Winner"] + get_winner_to_loser_link(match_count,round_lengths[round_name]["Winner"],loser_week)
                print("[Link]","Winner to loser","[Round]",round_name,source_id,"-->",target_id)
                progression.append({"SourceID":source_id,"TargetID":target_id,"Losers":True})
            matches_linked += match_count+1 + round_lengths[round_name]["LoserR1"] + round_lengths[round_name]["LoserR2"]
            loser_week += 1
            first_round = False
    return progression

def link_loser_to_loser (rounds:list)->list:
    """Links every loser bracker match to the next loser bracket match"""
    progression = []
    round_lengths = get_round_lengths(rounds)
    matches_linked = 0
    for round_name in rounds :
        matches_linked += round_lengths[round_name]["Winner"]
        if round_name != "grandfinals" :
            next_round_name = get_next_round(round_name)
            match_count = 0
            for match_count in range(0,max( round_lengths[round_name]["LoserR1"] , round_lengths[round_name]["LoserR2"] ),2):
                source_id = matches_linked + match_count
                target_id = match_count//2 + matches_linked + round_lengths[round_name]["LoserR1"]
                second_target_id = target_id + round_lengths[round_name]["LoserR2"] + round_lengths[next_round_name]["Winner"]
                if round_lengths[round_name]["LoserR1"] > round_lengths[round_name]["LoserR2"] : # if we are in the first losers round
                    print("[Link]","Loser to loser","[Round]",round_name,source_id,"-->",target_id)
                    print("[Link]","Loser to loser","[Round]",round_name,source_id+1,"-->",target_id)
                    progression.append({"SourceID":source_id,"TargetID":target_id})
                    progression.append({"SourceID":source_id+1,"TargetID":target_id})
                else :
                    gap = round_lengths[round_name]["LoserR2"]//2
                    print("[Link]","Loser to loser","[Round]",round_name,target_id+gap,"-->",second_target_id+gap)
                    progression.append({"SourceID":target_id+gap,"TargetID":second_target_id+gap})
                print("[Link]","Loser to loser","[Round]",round_name,target_id,"-->",second_target_id)
                progression.append({"SourceID":target_id,"TargetID":second_target_id})
        matches_linked += round_lengths[round_name]["LoserR1"] + round_lengths[round_name]["LoserR2"]
    return progression

def get_winner_to_loser_link (match_location_winner:int,round_length:int,loser_week:int):
    loser_placements = globals()["L"+str(loser_week)](int(in_power_of_two(round_length)))
    match_location_loser = loser_placements[match_location_winner]
    return match_location_loser

def in_power_of_two (x):
    n = 0
    while x > 1 :
        x//=2
        n += 1
    return n

# MAIN


def MAIN ():
    print("Welcome!\nFor this script to work you'll need a 'bracket.json' file containing every round you want (up to Ro128).\nThese has to be named with their complete name\n(ex: Quarterfianls, Grand Finals or Round of 16),spaces & capital letters don't matter.")
    bracket_file = input("Your bracket.json file directory: ").replace("/", "\\")
    if os.path.exists(bracket_file) and bracket_file[-5:] == ".json" :
        # set up & get up
        bracket = get_json_dict(bracket_file)
        rounds = get_round_names(bracket)
        print(rounds)
        rounds = sort_rounds(rounds)
        print(rounds)
        bracket = fix_bracket_missing_rounds (bracket,rounds)
        # manipulations
        bracket = create_bracket_matches(bracket,rounds)
        bracket = place_matches(bracket,rounds)
        bracket = link_matches(bracket,rounds)
        # save
        save_bracket(bracket_file,bracket)
        print("[Success]\n Thanks for using me!")
    else :
        print("error :)")
MAIN()