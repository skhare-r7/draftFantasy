import re
from database import dbInterface
import difflib 

db = dbInterface()
points = open('points.txt')
team = None
players = None
matchId = None
gameInfo = None
dbDict = {}

class Re(object):
  def __init__(self):
    self.last_match = None
  def match(self,pattern,text):
    self.last_match = re.match(pattern,text)
    return self.last_match

gre = Re()
for line in points:
    if gre.match('.*?\(([A-Z]{2,3})\).*',line):
        team= gre.last_match.group(1)
        players = db.send("select playerName,playerId from playerInfo where team like ?",[team])        
        players_dict = dict((item[0],item[1]) for item in players)
    elif gre.match('Match (\d+) - (.*)',line):
        matchId = gre.last_match.group(1)
        gameInfo = gre.last_match.group(2)
    elif gre.match('(.*?)(\-?\d+)',line):
        player = gre.last_match.group(1)
        score = gre.last_match.group(2)
        match = difflib.get_close_matches(player,players_dict.keys(),1)[0]
        dbDict[players_dict[match]]=score
    elif line.strip() == '':
        continue
    else:
        print "unable to parse line: "  + line

print matchId
print gameInfo
print dbDict

delSql = "delete from iplpoints where matchid=?"
pointSql = "insert into iplpoints (matchid,game,playerId,points) values (?,?,?,?)"
if matchId != None and gameInfo != None:
    db.send(delSql,[matchId])
    for id,pts in dbDict.items():
        db.send(pointSql,[matchId,gameInfo,id,pts])
    db.commit()

points.close()
db.close()


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
        
