import json
import accurating

matches = list()
with open('games.txt', 'r') as f:
    for line in f:
        line = line.strip().split(':')
        matches.append(((line[0], int(line[1])), (line[2], int(line[3]))))

match_dict = list()
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

resultArray = accurating.data_from_dicts(match_dict)
config = accurating.Config(
        season_rating_stability=0.0,
        smoothing=0.2,
    )
model = accurating.fit(resultArray, config)

collapsed_dict = {}
for key, inner_dict in model.rating.items():
    for inner_key, value in inner_dict.items():
        collapsed_dict[key] = value

sorted_dict = dict(sorted(collapsed_dict.items(), key=lambda x: x[1], reverse=True))
accurating.win_prob(collapsed_dict['Salisbury'],collapsed_dict['Muhlenberg'])
# sorted_dict
with open('accurating.json', 'w') as f:
    json.dump(sorted_dict, f, indent=4)

def prob(eloA, eloB):
    exp = (eloB-eloA)/480.0
    return 1/((10.0**(exp))+1)

print(prob(collapsed_dict['Muhlenberg'],collapsed_dict['Tufts']))
print(prob(collapsed_dict['Muhlenberg'],collapsed_dict['McDaniel']))