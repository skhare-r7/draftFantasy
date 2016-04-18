import json
from database import dbInterface
import difflib
import os
import math

db = dbInterface()


def getAct(perf,skill,act):
    try:
        return float(perf[skill][act])
    except:
        return 0

def iplPointCalculator(name,match):
    points = 0
    perf = match["players"][name]
    #1 point per run
    points += (1* getAct(perf,"bat","runs"))
    #2 points per six
    points += (2* getAct(perf,"bat","sixes"))
    #25 run bonus
    points += (10* math.floor(getAct(perf,"bat","runs")/25))
    #-5 for duck
    if getAct(perf,"bat","runs")==0 and getAct(perf,"bat","out"): points -= 5
    #strike rate
    if getAct(perf,"bat","runs") >= 10:
        if getAct(perf,"bat","sr") < 75: points -= 15
        elif getAct(perf,"bat","sr") < 100: points -= 10
        elif getAct(perf,"bat","sr") < 150: points += 5
        elif getAct(perf,"bat","sr") < 200: points += 10
        else: points += 15
    #20 points per wicket
    points += (20 * getAct(perf,"bowl","wickets"))
    #10 point wicket bonus
    if getAct(perf,"bowl","wickets") > 1:
        points += (10 * (getAct(perf,"bowl","wickets")-1))
    #1 point per dot
    points += getAct(perf,"bowl","dots")
    #20 points per maiden
    points += (20 * getAct(perf,"bowl","maidens"))
    #economy
    if getAct(perf,"bowl","overs") >= 1: #remeber overs can be 1.3!
        if getAct(perf,"bowl","econ") <= 5: points += 15
        elif getAct(perf,"bowl","econ") <= 8: points += 10
        elif getAct(perf,"bowl","econ") <= 10: points += 5
        elif getAct(perf,"bowl","econ") <= 12: points -= 10
        else: points -= 15
    #10 points per catch
    points += (10 * getAct(perf,"field","catches"))
    #15 points per stumping
    points += (15 * getAct(perf,"field","stumpings")) 
    #10 points per runout
    points += (10 * getAct(perf,"field","runouts"))
    #25 points for mom
    if match['mom'] == name:
        points += 25
    #winning team
    #print match
    #print perf
    if match['winner'] == perf['team']:
        points += 5
    return int(points)

for fileName in os.listdir('scorecards'):
    if fileName.endswith(".json"):
        with open('scorecards/'+fileName) as scoreFile:
            match = json.load(scoreFile)
            playerPoints = {}
            matchId = match['matchId']
            gameInfo = match['game']
            team1 = match['team1']
            team2 = match['team2']
            players = db.send("select playerName,playerId from playerInfo where team like ? or team like ?",[team1,team2])
            players_dict = dict((item[0].split(' ')[0][:2] + ' ' +item[0].split(' ')[1],item[1]) for item in players)
            playerName = None
            for name, playerInfo in match["players"].items():
                points = iplPointCalculator(name,match)
                try:
                    playerName = difflib.get_close_matches(name,players_dict.keys(),1,0)[0]
                except:
                    print name
                    print players_dict.keys()
                    print difflib.get_close_matches(name,players_dict.keys(),3,0)
                    raise
                print playerName + "(" + name + ") : " + points.__str__()


#        delSql = "delete from iplpoints where matchid=?"
#        pointSql = "insert into iplpoints (matchid,game,playerId,points) values (?,?,?,?)"
#        if matchId != None and gameInfo != None:
#            db.send(delSql,[matchId])
#            for id,pts in dbDict.items():
#                db.send(pointSql,[matchId,gameInfo,id,pts])
#            db.commit()

#db.close()
