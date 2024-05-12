import math
from bs4 import BeautifulSoup
import re
import json
import time
import random
from statistics import mean
import datetime as dt
import requests
import accurating
import subprocess

betDict = {"school": [], "MLA": [], "WLA": [], "MBA": [], "WSB": []}
uc = {"MLA": [], "WLA": [], "MBA": [], "WSB": []}

def convertOdds(percent):
  if percent > 0.95:
    return "-10000"
  elif percent == .5:
    return "-110"
  elif percent == 0.48:
    return "+100"
  elif percent > .48:
    return "-"+str(math.ceil((math.ceil((-100*percent+0.03) / (percent-0.97)))/5)*5)
  else:
    return "+"+str(math.ceil((math.floor((-100*(percent-0.99)) / (percent+0.01)))/5)*5)

def extract_links_between_keywords(url):
  # Send a GET request to the URL
  response = requests.get(url)
  # Check if the request was successful (status code 200)
  if response.status_code == 200:
    # Get the HTML content
    html_content = response.text
    # Find the start and end indices of the text content between the keywords
    start_index = re.search(r'\bROSTER\b', html_content).end()
    end_index = re.search(r'\bLATEST RESULTS\b', html_content).start()

    # Extract the text content between the keywords
    text_content = html_content[start_index:end_index]

    # Parse the extracted text content as HTML
    soup = BeautifulSoup(text_content, 'html.parser')

    # Find all links within the extracted HTML
    links = soup.find_all('a', href=True)
    ret = []
    # Print the links
    for link in links:
      html_line = str(link)
      # Parse the HTML line
      soup = BeautifulSoup(html_line, 'html.parser')
      # Extract player name
      player_name = soup.string
      ret.append(("https://www.tfrrs.org"+link['href'],player_name))
    return ret
  else:
      print("Failed to retrieve page.")

def scrape_date_time_table(d, tup):
  # Send a GET request to the URL
  response = requests.get(tup[0])
  athleteTimes = {}
  dataDict = d

  # Check if the request was successful (status code 200)
  if response.status_code == 200:
    html_content = response.text
    pattern = r'<h3 class="ml-5 outdoors">2024(.*?)<h3 class="ml-5 indoors">2024'
    matches = re.findall(pattern,html_content,re.DOTALL)
    if not matches:
      pattern = r'<h3 class="ml-5 outdoors">2024(.*?)<h3 class="ml-5 outdoors">2023'
      matches = re.findall(pattern,html_content,re.DOTALL)
      if not matches:
        pattern = r'<h3 class="ml-5 outdoors">2024(.*?)<div class="tab-pane tab-pane-custom " id="progression" role="tabpanel">'
        matches = re.findall(pattern,html_content,re.DOTALL)
    eventNames = []
    for match in matches:
      pattern2 = r'<span style="color:black">\s*(.*)\s*<\/span>'
      eventNames = re.findall(pattern2, match)
      timePatt = r'<div style="float:left">\s*<a data-turbo-frame="_top" data-turbo="false" href=.*?>(.*?)</a>|<span style="color:black">\s*(.*)\s*<\/span>'
      times = re.findall(timePatt,match)
    if not eventNames:
      return d
    else:
      for event in eventNames:
        athleteTimes[event] = []
      adding = times[0][1]
      for time in times:
        if time[0] == "":
          adding = time[1]
        else:
          t = time[0]
          if "FOUL" in t or "NM" in t or "NH" in t or "DNF" in t or "DNS" in t or "FS" in t:
            continue
          elif ":" in t:
            minutes, seconds_milliseconds = t.split(':')
            seconds, milliseconds = seconds_milliseconds.split('.')
  
            # Convert to integers
            minutes = int(minutes)
            seconds = int(seconds)
            milliseconds = int(milliseconds)
  
            # Calculate total seconds including milliseconds
            ti = minutes * 60 + seconds + milliseconds / 100.0
          elif "m" in t:
            ti = float(t.replace("m",""))
          else: 
            ti = float(t)
          athleteTimes[adding].append(ti)
      dataDict["school"][tup[1]] = {"history": athleteTimes, "bets": {}}
    return dataDict
  else:
    print("Failed to retrieve page.")


def calcTimes(gender):
  file = "{}TRACK.json".format(gender)
  with open(file, 'r') as j:
     dataDict = json.loads(j.read())
  for key in dataDict["school"]:
    for event in dataDict["school"][key]["history"]:
      if len(dataDict["school"][key]["history"][event]) >= 3:
        # estimate 
        div = 0
        num = 0
        for i in range(len(dataDict["school"][key]["history"][event])):
          mult = (len(dataDict["school"][key]["history"][event]) - i)
          div += (mult)
          num += (dataDict["school"][key]["history"][event][i])*(mult)
        val = num/div
        if "Relay" in event or "Meters" in event or "Mile" in event or "Steeplechase" in event or "Hurdles" in event: 
          val = round(val*0.98,2)
          if val > 60:
            minutes = math.floor(val/60)
            seconds = round(val - (minutes*60),2)
            if seconds < 10:
              seconds = "0"+str(seconds)
            ouPrint = str(minutes) + ":" + str(seconds) + "s"
          else:
            ouPrint = str(val) + "s"
        else:
          val = round(val*1.02,2)
          ouPrint = str(val) + "m"
        betDict["school"].append({"away": key, "home": event, "awayML": 0, "homeML": 0, "awaySP": 0, "homeSP": 0, "aspreadOdds": 0, "hspreadOdds": 0, "ouOdds": "-110", "ouLine":round(val,2), "ouPrint": ouPrint, "disclaimer": "Bets void if "+key+", does not compete in this event."})

def upcoming(school, sport_code):
  # Start date
  date = dt.datetime.today()
  # End date
  end_date = dt.datetime.today() + dt.timedelta(days=3)
  # List to store the results
  games = []
  if sport_code == "MLA":
    codeNum = 18242
  elif sport_code == "WLA":
    codeNum = 18263
  elif sport_code == "WSB":
    codeNum = 18265
  elif sport_code == "MBA":
    codeNum = 18302
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",  # Do Not Track Request Header
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"  # Tells the server to redirect to HTTPS if the initial request is HTTP
}
  while date < end_date:  
      time.sleep(random.random())
      session = requests.Session()
      session.headers.update(headers)
      date += dt.timedelta(days=1)
      link = "https://stats.ncaa.org/season_divisions/{}/livestream_scoreboards?utf8=%E2%9C%93&season_division_id=&game_date={:0>2}%2F{:0>2}%2F{}&conference_id=0&tournament_id=&commit=Submit".format(
         codeNum, date.month, date.day, date.year
      )

      response = requests.get(link, headers=headers)

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
                  if school in teamA or school in teamB:
                    games.append((teamA, teamB, date.month, date.day, date.year, sport_code))
                  if "Purdue" not in teamA and "Purdue" not in teamB:
                    uc[sport_code].append((teamA, teamB, date.month, date.day, date.year))

      else:
          print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
  generateOdds(school, sport_code, games)


def calcSpreadProbs(sport_code):
  winBy = {}
  file = "accurating_{}.json".format(sport_code)
  with open(file) as f:
      data = json.load(f)
  f.close()
  file_path = f"{sport_code}_2024.txt"
  with open(file_path, "r") as f:
    for line in f:
      game = line.strip().split(":")
      dif = int(game[3]) - int(game[1])
      if dif > 0:
        win = game[2]
        loss = game[0]
      else:
        win = game[0]
        loss = game[2]
        dif *= -1
      probW = accurating.win_prob(data[win],data[loss])
      if dif not in winBy:
        winBy[dif] = [probW]
      else:
        winBy[dif].append(probW)
  f.close()
  file_path = f"{sport_code}_2023.txt"
  with open(file_path, "r") as f:
    for line in f:
      game = line.strip().split(":")
      dif = int(game[3]) - int(game[1])
      if dif > 0:
        win = game[2]
        loss = game[0]
      else:
        win = game[0]
        loss = game[2]
        dif *= -1
      probW = accurating.win_prob(data[win],data[loss])
      if dif not in winBy:
        winBy[dif] = [probW]
      else:
        winBy[dif].append(probW)
  f.close()
  for key in winBy:
    if len(winBy[key]) < 50:
      winBy[key] = 0
    else:
      winBy[key] = sum(winBy[key]) / len(winBy[key])
      if sport_code == "MBA":
        winBy[key] *= 1.05
  return winBy

def calcAvgGoals(sport_code,team,opp):
  file_path = f"{sport_code}_2024.txt"
  totG = 0
  g = 0
  with open(file_path, "r") as f:
    for line in f:
      game = line.strip().split(":")
      if (game[2] == team and game[0] == opp):
        g += 20
        totG += int(game[3])*20
      elif (game[0] == team and game[2] == opp):
        g += 20
        totG += int(game[1])*20
      elif game[0] == team:
        g += 1
        totG += int(game[1])
      elif game[2] == team:
        g += 1
        totG += int(game[3])
      elif game[0] == opp:
        g += 1
        totG += int(game[3])
      elif game[2] == opp:
        g += 1
        totG += int(game[1])
  f.close()
  file_path = f"{sport_code}_2023.txt"
  with open(file_path, "r") as f:
    for line in f:
      game = line.strip().split(":")
      if (game[2] == team and game[0] == opp):
        g += 20
        totG += int(game[3])*20
      elif (game[0] == team and game[2] == opp):
        g += 20
        totG += int(game[1])*20
      elif game[0] == team:
        g += 1
        totG += int(game[1])
      elif game[2] == team:
        g += 1
        totG += int(game[3])
      elif game[0] == opp:
        g += 1
        totG += int(game[3])
      elif game[2] == opp:
        g += 1
        totG += int(game[1])
  f.close()
  
  if "B" in sport_code:
    totG *= 0.87
  if "WS" in sport_code:
    totG *= 0.95
  elif "LA" in sport_code:
    totG *= 1.02
  return totG / g
  
def calcSpread(code, map, prob):
  min = 1
  spr = 0
  for key in map:
    if abs(map[key] - prob) < min:
      min = abs(map[key] - prob)
      spr = key
  if spr > 15:
    spr = 15 + round((prob-.6)*10,0)
  if "WSB" in code and spr > 1:
    spr -= 1
    if spr > 5:
      spr -= 1
  return spr-0.5

def emergencyPolicy(sport_code, spread, favorite):
  file_path = f"{sport_code}_2024.txt"
  favoriteAllow = 0
  g = 0
  with open(file_path, "r") as f:
    for line in f:
      game = line.strip().split(":")
      if game[0] == favorite:
        g += 1
        favoriteAllow += int(game[3])
      elif game[2] == favorite:
        g += 1
        favoriteAllow += int(game[1])
  f.close()
  file_path = f"{sport_code}_2023.txt"
  with open(file_path, "r") as f:
    for line in f:
      game = line.strip().split(":")
      if game[0] == favorite:
        g += 1
        favoriteAllow += int(game[3])
      elif game[2] == favorite:
        g += 1
        favoriteAllow += int(game[1])
  f.close()
  favoriteAvg = (favoriteAllow // g) // 2
  return favoriteAvg + spread + favoriteAvg

def generateOdds(school, code, games):
  file = "accurating_{}.json".format(code)
  with open(file) as f:
      data = json.load(f)
  spreadMap = calcSpreadProbs(code)
  for game in games:
    if accurating.win_prob(data[game[0]],data[game[1]]) >= 0.5:
      favW = accurating.win_prob(data[game[0]],data[game[1]])
      home = False
    else:
      favW = accurating.win_prob(data[game[1]],data[game[0]])
      home = True
    spread = calcSpread(code, spreadMap, favW)
    opp = game[0]
    if game[0] == school:
      opp = game[1]
    ouG = calcAvgGoals(code,school,opp)
    add = calcAvgGoals(code,opp,school)
    ouG += add
    if home:
      h = "-"+str(spread)
      a = "+"+str(spread)
    else:
      h = "+"+str(spread)
      a = "-"+str(spread)
    hOdds = "-110"
    aOdds = "-110"
    if spread == 0.5:
      h += " (Pick / ML)"
      a += " (Pick / ML)"
      hOdds = convertOdds(accurating.win_prob(data[game[1]],data[game[0]]))
      aOdds = convertOdds(accurating.win_prob(data[game[0]],data[game[1]]))
    ouG = round(ouG) - 0.5
    if spread > ouG:
      if home:
        ouG = round(emergencyPolicy(code, spread, game[1])) + 0.5
      else:
        ouG = round(emergencyPolicy(code, spread, game[0])) + 0.5
    ouPrint = str(ouG)
    betDict["school"].append({"sport": game[5], "date": str(game[2])+"/"+str(game[3])+"/"+str(game[4]), "away": game[0], "home": game[1], "awayML": convertOdds(accurating.win_prob(data[game[0]],data[game[1]])), "homeML": convertOdds(accurating.win_prob(data[game[1]],data[game[0]])), "awaySP": a, "homeSP": h, "aspreadOdds": aOdds, "hspreadOdds": hOdds, "ouOdds": "-110", "ouLine": ouG, "ouPrint": ouPrint, "disclaimer": ""})

def track(school, rescrape):
  if rescrape:
    school = school.replace(" ","_")
    school = school.replace("&"," ")
    d = {"school": {}}
    print("scraping mtrack")
    url = "https://www.tfrrs.org/teams/tf/PA_college_m_{}.html".format(school)
    tup = extract_links_between_keywords(url)
    for link in tup:
      d = scrape_date_time_table(d, link)
    fname = "MTRACK.json"
    file = open(fname, "w") 
    json.dump(d, file) 
    file.close()
    d = {"school": {}}
    print("scraping wtrack")
    url = "https://www.tfrrs.org/teams/tf/PA_college_w_{}.html".format(school)
    tup = extract_links_between_keywords(url)
    for link in tup:
      d = scrape_date_time_table(d, link)
    fname = "WTRACK.json"
    file = open(fname, "w") 
    json.dump(d, file) 
    file.close()
    
  print("Calculating odds for track")
  calcTimes("M")
  calcTimes("W")

def lax(school, rescrape):
  if rescrape:
    print("scraping mlax")
    subprocess.check_output(['python3', 'scrapper.py', '--sport', 'MLA'])
    print("scraping wlax")
    subprocess.check_output(['python3', 'scrapper.py', '--sport', 'WLA'])
    print("generating new ratings mlax")
    subprocess.check_output(['python3', 'rating.py', '--sport', 'MLA'])
    print("generating new ratings wlax")
    subprocess.check_output(['python3', 'rating.py', '--sport', 'WLA'])
  print("Calculating odds for mlax")
  upcoming(school, "MLA")
  print("Calculating odds for wlax")
  upcoming(school, "WLA")

def bball(school, rescrape):
  if rescrape:
    print("scraping bball")
    subprocess.check_output(['python3', 'scrapper.py', '--sport', 'MBA'])
    print("generating new ratings bball")
    subprocess.check_output(['python3', 'rating.py', '--sport', 'MBA'])
  print("Calculating odds for baseball")
  upcoming(school, "MBA")

def sball(school, rescrape):
  if rescrape:
    print("scraping sball")
    subprocess.check_output(['python3', 'scrapper.py', '--sport', 'WSB'])
    print("generating new ratings sball")
    subprocess.check_output(['python3', 'rating.py', '--sport', 'WSB'])
  print("Calculating odds for softball")
  upcoming(school, "WSB")
  
def getWeek():
  getWeekOdds("MLA", uc["MLA"])
  getWeekOdds("WLA", uc["WLA"])
  getWeekOdds("MBA", uc["MBA"])
  getWeekOdds("WSB", uc["WSB"])

def getWeekOdds(code, games):
  file = "accurating_{}.json".format(code)
  with open(file) as f:
      data = json.load(f)
  spreadMap = calcSpreadProbs(code)
  for game in games:
    if accurating.win_prob(data[game[0]],data[game[1]]) >= 0.5:
      favW = accurating.win_prob(data[game[0]],data[game[1]])
      home = False
    else:
      favW = accurating.win_prob(data[game[1]],data[game[0]])
      home = True
    spread = calcSpread(code, spreadMap, favW)
    ouG = calcAvgGoals(code,game[0],game[1])
    add = calcAvgGoals(code,game[1],game[0])
    ouG += add
    if home:
      h = "-"+str(spread)
      a = "+"+str(spread)
    else:
      h = "+"+str(spread)
      a = "-"+str(spread)
    hOdds = "-110"
    aOdds = "-110"
    if spread == 0.5:
      h += " (Pick / ML)"
      a += " (Pick / ML)"
      hOdds = convertOdds(accurating.win_prob(data[game[1]],data[game[0]]))
      aOdds = convertOdds(accurating.win_prob(data[game[0]],data[game[1]]))
    ouG = round(ouG) - 0.5
    if spread > ouG:
      if home:
        ouG = round(emergencyPolicy(code, spread, game[1])) + 0.5
      else:
        ouG = round(emergencyPolicy(code, spread, game[0])) + 0.5
    ouPrint = str(ouG)
    betDict[code].append({"date": str(game[2])+"/"+str(game[3])+"/"+str(game[4]), "away": game[0], "home": game[1], "awayML": convertOdds(accurating.win_prob(data[game[0]],data[game[1]])), "homeML": convertOdds(accurating.win_prob(data[game[1]],data[game[0]])), "awaySP": a, "homeSP": h, "aspreadOdds": aOdds, "hspreadOdds": hOdds, "ouOdds": "-110", "ouLine": ouG, "ouPrint": ouPrint, "disclaimer": ""})


def run(school, rescrapeTrack, rescrapeOthers):
  getWeek()
  dName = "AllWith{}BetsPlayoffs.json".format(school)
  out = open(dName, "w") 
  json.dump(betDict, out, indent = 2) 
  

def main():
  print(convertOdds(.25))
  print(convertOdds(.40))
  print(convertOdds(.48))
  print(convertOdds(.52))
  print(convertOdds(.66))
  print(convertOdds(.80))
  exit()
  school = "Muhlenberg"
  run(school, False, False)
  print("done")
  
main()

"""
def getToday(sport_code):

  # List to store the results
  games = []
  if sport_code == "MLA":
    codeNum = 18242
  elif sport_code == "WLA":
    codeNum = 18263
  elif sport_code == "WSB":
    codeNum = 18265
  elif sport_code == "MBA":
    codeNum = 18302
  link = "https://stats.ncaa.org/season_divisions/{}/livestream_scoreboards?utf8=%E2%9C%93&season_division_id=&game_date=04%2F24%2F2024&conference_id=0&tournament_id=&commit=Submit".format(
         codeNum
      )
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ApplseWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
  response = requests.get(link, headers=headers)

  if response.status_code == 200:
      # Parse the HTML content
      soup = BeautifulSoup(response.text, "html.parser")
      soup = soup.find("table", {"class": "livestream_table"})
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
            if teamA == "Stevenson":
              games.append((teamA, bScore, teamB, aScore))
            else:
              games.append((teamA, aScore, teamB, bScore))
  else:
      print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
  return games

def todayOdds(code, game, spreadMap):
  file = "accurating_{}.json".format(code)
  with open(file) as f:
      data = json.load(f)
  homeT = game[2]
  awayT = game[0]
  if accurating.win_prob(data[homeT],data[awayT]) >= 0.5:
    favW = accurating.win_prob(data[homeT],data[awayT])
    favorite = homeT
    home = True
  else:
    favorite = awayT
    favW = accurating.win_prob(data[awayT],data[homeT])
    home = False
  spread = calcSpread(code, spreadMap, favW)
  ouG = calcAvgGoals(code,homeT,awayT)
  ouG += calcAvgGoals(code,awayT,homeT)
  ouG = round(ouG)
  if spread > ouG:
    if home:
      ouG = round(emergencyPolicy(code, spread, homeT)) + 0.5
    else:
      ouG = round(emergencyPolicy(code, spread, awayT)) + 0.5
  if game[1] > game[3]:
    winner = awayT
  else:
    winner = homeT
  tot = game[1]+game[3]
  score = awayT+": "+str(game[1])+", "+homeT+": " + str(game[3])
  s = spread + 0.5
  if favorite == homeT:
    hScore = round((ouG / 2) + (s/2))
    aScore = ouG - hScore
  else:
    aScore = round((ouG / 2) + (s/2))
    hScore = ouG - aScore
  predScore = awayT+": "+str(aScore)+", "+homeT+": " + str(hScore)
  betDict[code].append({"away": awayT, "home": homeT, "favorite": favorite, "winner": winner, "favSp": -1*spread, "score": score, "prediction": predScore, "ouLine": (ouG-0.5), "ouTot": tot})
"""
# overs hit 30/54
# favorites won 51/54