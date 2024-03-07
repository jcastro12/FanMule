
"""
This script is used to scrape NCAA D3 lacrosse stats for a specific team. 
It takes a team name as a command-line argument and retrieves game-by-game statistics 
from the NCAA website for that team. The script then parses the HTML content, extracts 
the table data, and saves it to a CSV file. The CSV file is named based on the team 
name and the year of the statistics.

Usage:
    python scrapper.py [team]

Saves the game-by-game statistics in CSV for the specified team to 3 folders (2021/, 2022/, 2023/)    
"""

import requests
from bs4 import BeautifulSoup
import csv
import os
import argparse

parser = argparse.ArgumentParser(description='Scrape NCAA D3 lacrosse stats')
parser.add_argument('team', type=str, help='The team to scrape (Muhlenberg, McDaniel, etc.)')
# parser.add_argument('year', type=int, help='The year to scrape (2021-2023)')
args = parser.parse_args()

# Read team codes json
import json
with open('team_codes.json', 'r') as f:
    team_codes = json.load(f)
code = team_codes[args.team]
# year = args.year

# The URL of the webpage you want to parse
url = [f'http://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=15560&org_id={code}&stats_player_seq=-100',
        f'http://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=15921&org_id={code}&stats_player_seq=-100',
        f'http://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=16320&org_id={code}&stats_player_seq=-100']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ApplseWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

for i in range(0, len(url)):
    response = requests.get(url[i], headers=headers)

    # Fetch the webpage

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        soup = soup.find('div', {'id': 'game_breakdown_div'})
        # soup = soup.table
        
        # Extract the table data
        table_text = []
        for row in soup.find_all('tr'):
            if row.get('class') == ['heading']:
                # print(row.get_text(strip=True))
                continue
            else:
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text(strip=True))
                table_text.append(row_data)
        table_text = table_text[1:]
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    
    # Write the table to a CSV file
    filename = f'./{2021+i}/{args.team}.csv'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile)
        for row in table_text:
            writer.writerow(row)


