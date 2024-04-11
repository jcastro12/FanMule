import datetime as dt
import requests
from bs4 import BeautifulSoup

# Sport to scrape
# See https://ncaaorg.s3.amazonaws.com/championships/resources/common/NCAA_SportCodes.pdf for the list of sport codes
sport_code = 'WLA' 

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ApplseWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# See https://stats.ncaa.org/contests/livestream_scoreboards for appropriate date range

# Start date
date = dt.datetime(2024, 2, 2)

while date < dt.datetime(2024, 4, 11): # End date
    date += dt.timedelta(days=1)
    print(date.month, date.day, sep='/')
    
    link = 'https://stats.ncaa.org/contests/livestream_scoreboards?utf8=%E2%9C%93&sport_code={}&academic_year={}&division=3&game_date={:0>2}%2F{:0>2}%2F{}&commit=Submit'.format(sport_code, date.year, date.month, date.day, date.year)
    
    response = requests.get(link, headers=headers)

    if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            soup = soup.find('table', {'class': 'livestream_table'})
            
            if soup == None: continue
        
            # Extract the table data
            list = soup.find_all('tr')[1:]
            with open(f'{sport_code}_{date.year}.txt', 'a') as f:
                for index, row in enumerate(list):
                    if index % 5 == 0: 
                        teamA = row.find('a')
                        teamB = list[index+3].find('a')
                        if teamA == None or teamB == None:
                            continue

                        teamA = teamA.get_text(strip=True)
                        if(teamA[0] == '#'): teamA = ' '.join(teamA.split(' ')[1:-1])
                        else: teamA = ' '.join(teamA.split(' ')[:-1])
                        
                        teamB = teamB.get_text(strip=True)
                        if teamB[0] == '#': teamB = ' '.join(teamB.split(' ')[1:-1])
                        else: teamB = ' '.join(teamB.split(' ')[:-1])

                        aScore = row.find('td', {'class': 'totalcol'})
                        bScore = list[index + 3].find('td', {'class': 'totalcol'})
                        if aScore == None or bScore == None:
                            continue
                        aScore = int(aScore.get_text(strip=True))
                        bScore = int(bScore.get_text(strip=True))
                        f.write(f"{teamA}:{aScore}:{teamB}:{bScore}\n")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
