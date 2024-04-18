"""
    Updates match result for a given sport using beautifulsoup. Assumes end date is today or 2024-06-15. 
    Usage: python scrapper.py --sport <sport_code>
"""

import datetime as dt
import requests
from bs4 import BeautifulSoup
import argparse
import time
import random

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="""
    Updates match result for a given sport in 2024 using beautifulsoup. Assumes end date is today or 2024-06-15. 
    See https://ncaaorg.s3.amazonaws.com/championships/resources/common/NCAA_SportCodes.pdf for the list of sport codes
    """
)
parser.add_argument("--sport", type=str, help="Sport code to scrape")
args = parser.parse_args()

sport_code = args.sport

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",  # Do Not Track Request Header
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"  # Tells the server to redirect to HTTPS if the initial request is HTTP
}

# See https://stats.ncaa.org/contests/livestream_scoreboards for appropriate date range

# Start date
date = dt.datetime(2023, 2, 2)

# End date
end_date = min(dt.datetime.today(), dt.datetime(2023, 6, 7))

# List to store the results
results = []
while date < end_date:  
    # Add random time delay
    time.sleep(random.random())
    session = requests.Session()
    session.headers.update(headers)
    date += dt.timedelta(days=1)
    print(date.month, date.day, sep="/")

    link = "https://stats.ncaa.org/contests/livestream_scoreboards?utf8=%E2%9C%93&sport_code={}&academic_year={}&division=3&game_date={:0>2}%2F{:0>2}%2F{}&commit=Submit".format(
        sport_code, date.year, date.month, date.day, date.year
    )

    response = session.get(link)

    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        soup = soup.find("table", {"class": "livestream_table"})

        if soup == None:
            continue

        # Extract the table data
        list = soup.find_all("tr")[1:]
        for index, row in enumerate(list):
            if index % 5 == 0:
                teamA = row.find("a")
                teamB = list[index + 3].find("a")
                if teamA == None or teamB == None:
                    continue

                teamA = teamA.get_text(strip=True)
                if teamA[0] == "#":
                    teamA = " ".join(teamA.split(" ")[1:-1])
                else:
                    teamA = " ".join(teamA.split(" ")[:-1])

                teamB = teamB.get_text(strip=True)
                if teamB[0] == "#":
                    teamB = " ".join(teamB.split(" ")[1:-1])
                else:
                    teamB = " ".join(teamB.split(" ")[:-1])

                aScore = row.find("td", {"class": "totalcol"})
                bScore = list[index + 3].find("td", {"class": "totalcol"})
                if aScore == None or bScore == None:
                    continue
                aScore = int(aScore.get_text(strip=True))
                bScore = int(bScore.get_text(strip=True))
                results.append((teamA, aScore, teamB, bScore))
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Writes the results to a file
with open(f"{sport_code}_{date.year}.txt", "w") as f:
    f.write(
        "\n".join(
            [f"{result[0]}:{result[1]}:{result[2]}:{result[3]}" for result in results]
        )
    )
