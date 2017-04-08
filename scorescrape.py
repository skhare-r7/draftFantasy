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
    conversion["Delhi Daredevils"] = "DD"
    conversion["Gujarat Lions"] = "GL"
    conversion["Kings XI Punjab"] = "KXIP"
    conversion["Kolkata Knight Riders"] = "KKR"
    conversion["Mumbai Indians"] = "MI"
    conversion["Rising Pune Supergiant"] = "RPS"
    conversion["Royal Challengers Bangalore"] = "RCB"
    conversion["Sunrisers Hyderabad"] = "SRH"
    return conversion[longName]

def getVal(player,xpathStr):
  try:
    return player.xpath(xpathStr)[0]
  except:
    return 0


#finalized scorecard scraping
#gamePage = "http://www.espncricinfo.com/indian-premier-league-2016/engine/match/980921.html"
gamePage = sys.argv[1]

tree = lxml.html.parse(gamePage)
matchPoints = {}
gre = Re()

batting = tree.xpath("//table[@class='batting-table innings']/tr[not(@*)]")
teamNameXpath = "../tr/th[@class='th-innings-heading']/text()"
min_batted_exists = int(tree.xpath("count(//th[@title='minutes batted'])"))>0
bowling = tree.xpath("//table[@class='bowling-table']/tr[not(@*)]")
dnb = tree.xpath("//div[@class='to-bat']/p/span/a")
dnbTeam = "../../../../preceding-sibling::table[@class='batting-table innings'][1]/tr/th[@class='th-innings-heading']/text()"
more_stats_second = tree.xpath("//div[@class='more-match-stats'][2]")
match_info = tree.xpath("//div[@class='match-information-strip']/text()")[0]
match_no_regex = ".*?(\d+).*"
match_teams_regex = ".*?:(.*?) v (.*?) at .*"
match_winner = tree.xpath("//div[@class='innings-requirement']/text()")[0]
match_winner_regex = "(.*?) won by .*"
mom = tree.xpath("//div[@class='match-information']/div[2]/span/text()")[0]
mom_regex = "(.*?)\(.*"


if gre.search(match_no_regex,match_info.strip()):
  matchId = gre.last_match.group(1)
matchPoints["matchId"] = matchId
if gre.search(match_teams_regex,match_info.strip()):
  team1 = convTeam(gre.last_match.group(1).strip())
  team2 = convTeam(gre.last_match.group(2).strip())
matchPoints["team1"] = team1
matchPoints["team2"] = team2
matchPoints["game"] = team1 + ' vs ' + team2
if gre.search(match_winner_regex,match_winner.strip()):
  winner = gre.last_match.group(1).strip()
  matchPoints["winner"] =  convTeam(winner)
if gre.search(mom_regex,mom.strip()):
  mom = gre.last_match.group(1).strip()
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
    name = getVal(player,"./td[@class='batsman-name']/a/text()")
    dismissal = getVal(player,"./td[3]/text()")
    if 'not out' in dismissal: out = False #err retired hurt?
    else: out = True
    runs = getVal(player,"./td[4]/text()")
    ballsIndex = 5
    if min_batted_exists: ballsIndex +=1
    balls = getVal(player,"./td["+str(ballsIndex)+"]/text()")
    fours = getVal(player,"./td["+str(ballsIndex+1)+"]/text()")
    sixes = getVal(player,"./td["+str(ballsIndex+2)+"]/text()")
    sr = getVal(player,"./td["+str(ballsIndex+3)+"]/text()")
      
    batting = {}
    batting["runs"] = runs
    batting["balls"] = balls
    batting["fours"] = fours
    batting["sixes"] = sixes
    batting["sr"] = sr
    batting["out"] = out
    players[name] = {}
    players[name]["team"] = convTeam(getVal(player,teamNameXpath).strip().split(' innings')[0])
    dismissals[players[name]["team"]].append(dismissal)
    players[name]["bat"] = batting


for player in dnb:
    name = getVal(player,"./text()")
    players[name] = {}
    inningsTitle = getVal(player,dnbTeam).strip()
    if 'innings' in inningsTitle:
      team = inningsTitle.split(' innings')[0]
    else:
      team = inningsTitle.split(' team')[0]
    players[name]['team'] = convTeam(team)

for player in bowling:
    name = getVal(player,"./td[@class='bowler-name']/a/text()")
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
