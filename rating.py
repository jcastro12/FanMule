import accurating

# Sport to scrape
# See https://ncaaorg.s3.amazonaws.com/championships/resources/common/NCAA_SportCodes.pdf for the list of sport codes
sport_code = 'MBA'
matches = []
with open(f'{sport_code}_2023.txt', 'r') as f:
    for line in f:
        line = line.strip().split(':')
        matches.append(((line[0], int(line[1])), (line[2], int(line[3]))))

match_dict = []
for match in matches:
    event = dict()
    event['season'] = 0
    event['p1'] = match[0][0]
    event['p2'] = match[1][0]
    s1 = match[0][1]
    s2 = match[1][1]
    if s1 > s2:
        event['winner'] = match[0][0]
    else:
        event['winner'] = match[1][0]
    match_dict.append(event)

matches = []
with open(f'{sport_code}_2024.txt', 'r') as f:
    for line in f:
        line = line.strip().split(':')
        matches.append(((line[0], int(line[1])), (line[2], int(line[3]))))

for match in matches:
    event = dict()
    event['season'] = 1
    event['p1'] = match[0][0]
    event['p2'] = match[1][0]
    s1 = match[0][1]
    s2 = match[1][1]
    if s1 > s2:
        event['winner'] = match[0][0]
    else:
        event['winner'] = match[1][0]
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
import json
collapsed_dict = {}
for key, inner_dict in model.rating.items():
    # collapsed_dict[key] = inner_dict[1]
    for inner_key, value in inner_dict.items():
        collapsed_dict[key] = value

sorted_dict = dict(sorted(collapsed_dict.items(), key=lambda x: x[1], reverse=True))

with open(f'accurating_{sport_code}.json', 'w') as f:
    json.dump(sorted_dict, f, indent=4)