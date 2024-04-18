"""
    Updates rating for a given sport using the accurating library
    Usage: python rating.py --sport <sport_code>
"""

import accurating
import argparse
import json
import os

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="""
    Updates rating for a given sport in accordance to the NCAA defiend sport codes.
    See https://ncaaorg.s3.amazonaws.com/championships/resources/common/NCAA_SportCodes.pdf for the list of sport codes
    """
)
parser.add_argument("--sport", type=str, help="Sport code to scrape")
args = parser.parse_args()

# Sport to scrape
# See https://ncaaorg.s3.amazonaws.com/championships/resources/common/NCAA_SportCodes.pdf for the list of sport codes
sport_code = args.sport

matches = []

file_path = f"{sport_code}_2023.txt"
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip().split(":")
            matches.append(((line[0], int(line[1])), (line[2], int(line[3]))))
else:
    print(
        f"File '{file_path}' does not exist. Run scrape.py first to generate the file. Or check if the sport code is correct."
    )


match_dict = []
for match in matches:
    event = dict()
    event["season"] = 0
    event["p1"] = match[0][0]
    event["p2"] = match[1][0]
    s1 = match[0][1]
    s2 = match[1][1]
    if s1 > s2:
        event["winner"] = match[0][0]
    else:
        event["winner"] = match[1][0]
    match_dict.append(event)

matches = []

file_path = f"{sport_code}_2024.txt"
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip().split(":")
            matches.append(((line[0], int(line[1])), (line[2], int(line[3]))))
else:
    print(
        f"File '{file_path}' does not exist. Run scrape.py first to generate the file. Or check if the sport code is correct."
    )


for match in matches:
    event = dict()
    event["season"] = 1
    event["p1"] = match[0][0]
    event["p2"] = match[1][0]
    s1 = match[0][1]
    s2 = match[1][1]
    if s1 > s2:
        event["winner"] = match[0][0]
    else:
        event["winner"] = match[1][0]
    match_dict.append(event)

resultArray = accurating.data_from_dicts(match_dict)
config = accurating.Config(
    season_rating_stability=100,
    smoothing=0.1,
    # max_steps=100000,
    # do_log=True,
)
model = accurating.fit(resultArray, config)

# Dumps the rating dictionary to a json file
collapsed_dict = {}
for key, inner_dict in model.rating.items():
    # collapsed_dict[key] = inner_dict[1]
    for inner_key, value in inner_dict.items():
        collapsed_dict[key] = value

sorted_dict = dict(sorted(collapsed_dict.items(), key=lambda x: x[1], reverse=True))

with open(f"accurating_{sport_code}.json", "w") as f:
    json.dump(sorted_dict, f, indent=4)
