import lxml.html
import re
import difflib
import json
import sys

#matchPoints dict will look as follows
#{ "matchId": 11,
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


def convTeam(longName):
    conversion = {}
    conversion["Delhi Daredevils"] = "DD"
    conversion["Gujarat Lions"] = "GL"
    conversion["Kings XI Punjab"] = "KXIP"
    conversion["Kolkata Knight Riders"] = "KKR"
    conversion["Mumbai Indians"] = "MI"
    conversion["Rising Pune Supergiants"] = "RPS"
    conversion["Royal Challengers Bangalore"] = "RCB"
    conversion["Sunrisers Hyderabad"] = "SRH"
    return conversion[longName]


#finalized scorecard scraping
#gamePage = "http://www.espncricinfo.com/indian-premier-league-2016/engine/match/980921.html"
gamePage = sys.argv[1]

tree = lxml.html.parse(gamePage)
matchPoints = {}

batting = tree.xpath("//table[@class='batting-table innings']/tr[not(@*)]")
bowling = tree.xpath("//table[@class='bowling-table']/tr[not(@*)]")
dnb = tree.xpath("//div[@class='to-bat']/p/span/a/text()")

more_stats_second = tree.xpath("//div[@class='more-match-stats'][2]")
match_info = tree.xpath("//div[@class='match-information-strip']/text()")[0]
match_no_regex = ".*?(\d+).*"
match_teams_regex = ".*?:(.*?) v (.*?) at .*"
match_winner = tree.xpath("//div[@class='innings-requirement']/text()")[0]
match_winner_regex = "(.*?) won by .*"
mom = tree.xpath("//div[@class='match-information']/div[2]/span/text()")[0]
mom_regex = "(.*?)\(.*"

m = re.search(match_no_regex,match_info.strip())
matchId = m.group(1)
matchPoints["matchId"] = matchId
m = re.search(match_teams_regex,match_info.strip())
team1 = m.group(1).strip()
team2 = m.group(2).strip()
matchPoints["game"] = convTeam(team1) + ' vs ' + convTeam(team2)
m = re.search(match_winner_regex,match_winner.strip())
winner = m.group(1).strip()
matchPoints["winner"] =  convTeam(winner)
m = re.search(mom_regex,mom.strip())
mom = m.group(1).strip()
matchPoints["mom"] = mom
players = {}
matchPoints["players"] = players
dismissals = []
caught_regex = "c (.*?) b .*"
runout_regex = "run out \((.*)"
stumped_regex = "st (.*?) b .*"

for player in batting:
    name = player.xpath("./td[@class='batsman-name']/a/text()")[0]
    dismissal = player.xpath("./td[3]/text()")[0]
    dismissals.append(dismissal)
    runs = player.xpath("./td[4]/text()")[0]
    balls = player.xpath("./td[5]/text()")[0]
    fours = player.xpath("./td[6]/text()")[0]
    sixes = player.xpath("./td[7]/text()")[0]
    sr = player.xpath("./td[8]/text()")[0]
    batting = {}
    batting["runs"] = runs
    batting["balls"] = balls
    batting["fours"] = fours
    batting["sixes"] = sixes
    batting["sr"] = sr
    players[name] = {}
    players[name]["bat"] = batting

for player in dnb:
    name = player
    players[name] = {}

for player in bowling:
    name = player.xpath("./td[@class='bowler-name']/a/text()")[0]
    overs = player.xpath("./td[3]/text()")[0]
    maidens = player.xpath("./td[4]/text()")[0]
    runs = player.xpath("./td[5]/text()")[0]
    wickets = player.xpath("./td[6]/text()")[0]
    econ = player.xpath("./td[7]/text()")[0]
    dots = player.xpath("./td[8]/text()")[0]
    fours = player.xpath("./td[9]/text()")[0]
    sixes = player.xpath("./td[10]/text()")[0]
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

def closest(player):
    return difflib.get_close_matches(player,players.keys(),1)[0]

for name,info in players.items():
   info['field'] = {}
   info['field']['runouts'] = 0
   info['field']['catches'] = 0
   info['field']['stumpings'] = 0

gre = Re()
for dismissal in dismissals:
    if gre.match(runout_regex,dismissal):
        player = gre.last_match.group(1)
        players[closest(player)]["field"]["runouts"] += 1
    elif gre.match(caught_regex,dismissal):
        player = gre.last_match.group(1)
        players[closest(player)]["field"]["catches"] += 1
    elif gre.match(stumped_regex,dismissal):
        player = gre.last_match.group(1)
        players[closest(player)]["field"]["stumpings"] += 1
    else:
        pass


#print matchPoints

with open("scorecards/match"+ matchId.__str__()+ ".json","w") as outfile:
  json.dump(matchPoints, outfile)
