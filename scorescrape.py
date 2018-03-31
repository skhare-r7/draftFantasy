import lxml.html
import re
import difflib
import json
import sys

#matchPoints dict will look as follows
#{ "matchId": 11,
#  "team1": RCB,
#  "team2": DD,
#  "game": "RCB vs DD",
#  "players": {
#    "CH Gayle":{
#       "Bat":{
#          "runs":,
#          "balls":,
#          "fours":,
#          "sixes":,
#          "sr":
#        },
#        "Bowl":{
#          "Overs":,
#          "Maidens":,
#          "Runs":,
#          "Wickets":,
#          "Econ":,
#          "Dots":,
#          "4s":,
#          "6s":
#        },
#        "Field":{
#          "Catches":,
#          "Runouts":,
#          "Stumpings"
#        }
#      },
#      ..other players
#   },
#  "MOM":,
#  "winner":
#  }  
#}


class Re(object):
  def __init__(self):
    self.last_match = None
  def match(self,pattern,text):
    self.last_match = re.match(pattern,text)
    return self.last_match
  def search(self,pattern,text):
    self.last_match = re.search(pattern,text)
    return self.last_match



def convTeam(longName):
    conversion = {}
    conversion["Chennai Super Kings"] = "CSK"
    conversion["Mumbai Indians"] = "MI"
    conversion["Mum Indians"] = "MI"
    conversion["Sunrisers Hyderabad"] = "SRH"
    conversion["Sunrisers"] = "SRH"
    conversion["Royal Challengers Bangalore"] = "RCB"
    conversion["Bangladesh"] = "BAN"
    conversion["India"] = "IND"
    conversion["South Africa"] = "SA"
    conversion["New Zealand"] = "NZ"
    conversion["Pakistan"] = "PAK"
    conversion["Srilanka"] = "SL"
    return conversion[longName]

def getVal(player,xpathStr):
  try:
    return player.xpath(xpathStr)[0]
  except:
    return 0

def fixName(name):
  return name.encode('ascii', errors='ignore').split('(')[0].strip(' ,')

#finalized scorecard scraping
#gamePage = "http://www.espncricinfo.com/indian-premier-league-2016/engine/match/980921.html"
gamePage = sys.argv[1]
matchId = sys.argv[2]

tree = lxml.html.parse(gamePage)
matchPoints = {}
gre = Re()

batting = tree.xpath("//div[@class='scorecard-section batsmen']//div[@class='wrap batsmen']")
teamNameXpath = "../../../preceding-sibling::div[@class='accordion-header']//h2/text()"
bowling = tree.xpath("//div[@class='scorecard-section bowling']//tbody/tr")
dnb = tree.xpath("//div[@class='wrap dnb']//a/span")
dnbTeam = "../../../../../../preceding-sibling::div[@class='accordion-header']//h2/text()"
teams = tree.xpath("//div[@class='layout-bc']//span[contains(@class,'cscore_name--abbrev')]/text()")

match_winner = tree.xpath("//div[@class='layout-bc']//span[@class='cscore_notes_game']/text()")[0]
match_winner_regex = "(.*?) won by .*"
mom = tree.xpath("//div[@class='layout-bc']//div[@class='gp__cricket__player-match__player__detail']/a/text()")[0]

matchPoints["matchId"] = matchId
team1 = teams[0]
team2 = teams[1]

matchPoints["team1"] = team1
matchPoints["team2"] = team2
matchPoints["game"] = team1 + ' vs ' + team2
if gre.search(match_winner_regex,match_winner.strip()):
  winner = gre.last_match.group(1).strip()
  matchPoints["winner"] =  convTeam(winner)
matchPoints["mom"] = mom
players = {}
matchPoints["players"] = players
dismissals = {}
dismissals[team1] = []
dismissals[team2] = []

caught_regex = "c ((?!&|sub).*?) b .*"
c_and_b_regex = "c & b (.*)"
runout_regex = "run out \((?!sub)(.*?)(/.*)?\).*"
stumped_regex = "st (.*?) b .*"

for player in batting:
    name = fixName(getVal(player,"./div[@class='cell batsmen']/a/text()").strip())
    dismissal = player.xpath("./div[@class='cell commentary']//text()")[0]
    if 'not out' in dismissal: out = False #err retired hurt?
    else: out = True
    runs = player.xpath("./div[@class='cell runs']/text()")[0]
    minutes = player.xpath("./div[@class='cell runs']/text()")[1]
    balls = player.xpath("./div[@class='cell runs']/text()")[2]
    fours = player.xpath("./div[@class='cell runs']/text()")[3]
    sixes = player.xpath("./div[@class='cell runs']/text()")[4]
    sr = player.xpath("./div[@class='cell runs']/text()")[5]
      
    batting = {}
    batting["runs"] = runs
    batting["balls"] = balls
    batting["fours"] = fours
    batting["sixes"] = sixes
    batting["sr"] = sr
    batting["out"] = out
    players[name] = {}
    players[name]["team"] = convTeam(getVal(player,teamNameXpath).strip().split(' Innings')[0])
    dismissals[players[name]["team"]].append(dismissal)
    players[name]["bat"] = batting


for player in dnb:
    name = fixName(getVal(player,"./text()"))
    players[name] = {}
    inningsTitle = getVal(player,dnbTeam).strip()
    if 'Innings' in inningsTitle:
      team = inningsTitle.split(' Innings')[0]
    else:
      team = inningsTitle.split(' team')[0]
    players[name]['team'] = convTeam(team)

for player in bowling:
    name = fixName(getVal(player,"./td[1]/a/text()"))
    overs = getVal(player,"./td[3]/text()")
    maidens = getVal(player,"./td[4]/text()")
    runs = getVal(player,"./td[5]/text()")
    wickets = getVal(player,"./td[6]/text()")
    econ = getVal(player,"./td[7]/text()")
    dots = getVal(player,"./td[8]/text()")
    fours = getVal(player,"./td[9]/text()")
    sixes = getVal(player,"./td[10]/text()")
    bowling = {}
    bowling["overs"] = overs
    bowling["runs"] = runs
    bowling["maidens"] = maidens
    bowling["wickets"] = wickets
    bowling["econ"] = econ
    bowling["dots"] = dots
    bowling["fours"] = fours
    bowling["sixes"] = sixes
    players[name]["bowl"] = bowling

def closest(player,team):
  oppPlayers = [i for i in players.keys() if players[i]["team"]!=team] #opposition team only!
  try:
    return difflib.get_close_matches(player,oppPlayers,1)[0]
  except:
    print player
    print difflib.get_close_matches(player,oppPlayers,3,0)

for name,info in players.items():
   info['field'] = {}
   info['field']['runouts'] = 0
   info['field']['catches'] = 0
   info['field']['stumpings'] = 0


for team,dismissalList in dismissals.items():
  for dismissal in dismissalList:
    if gre.match(runout_regex,dismissal):
        player = gre.last_match.group(1)
        players[closest(player,team)]["field"]["runouts"] += 1
    elif gre.match(caught_regex,dismissal) or gre.match(c_and_b_regex,dismissal):
        player = gre.last_match.group(1)
        players[closest(player,team)]["field"]["catches"] += 1
    elif gre.match(stumped_regex,dismissal):
        player = gre.last_match.group(1)
        players[closest(player,team)]["field"]["stumpings"] += 1
    else:
        pass


#print matchPoints

with open("scorecards/match"+ matchId.__str__()+ ".json","w") as outfile:
  json.dump(matchPoints, outfile)
