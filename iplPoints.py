import json
from database import dbInterface
import difflib
import os
import math
import re

class iplPoints:
    def __init__(self,db):
        self.db = db


    def getAct(self,perf,skill,act):
        try:
            return float(perf[skill][act])
        except:
            return 0

    def iplPointCalculator(self,name,match):
        points = 0
        perf = match["players"][name]
        #1 point per run
        points += (1* self.getAct(perf,"bat","runs"))
        #2 points per six
        points += (2* self.getAct(perf,"bat","sixes"))
        #50 run bonus
        points += (15* math.floor(self.getAct(perf,"bat","runs")/50))
        #-5 for duck
        if self.getAct(perf,"bat","runs")==0 and self.getAct(perf,"bat","out"): points -= 5
        #strike rate
        if self.getAct(perf,"bat","runs") >= 10:
            if self.getAct(perf,"bat","sr") < 60: points -= 5
            elif self.getAct(perf,"bat","sr") < 100: points += 0
            elif self.getAct(perf,"bat","sr") <= 140: points += 5
            else: points += 10
        #20 points per wicket
        points += (20 * self.getAct(perf,"bowl","wickets"))
        #10 point wicket bonus
        if self.getAct(perf,"bowl","wickets") > 2:
            points += (10 * (self.getAct(perf,"bowl","wickets")-1))
        #1 point per dot
        points += self.getAct(perf,"bowl","dots")
        #5 points per maiden
        points += (5 * self.getAct(perf,"bowl","maidens"))
        #economy
        if self.getAct(perf,"bowl","overs") >= 1: #remeber overs can be 1.3!
            if self.getAct(perf,"bowl","econ") <= 4: points += 10
            elif self.getAct(perf,"bowl","econ") <= 6: points += 5
            elif self.getAct(perf,"bowl","econ") <= 8: points += 0
            else: points -= 5
        #10 points per catch
        points += (10 * self.getAct(perf,"field","catches"))
        #15 points per stumping
        points += (15 * self.getAct(perf,"field","stumpings")) 
        #10 points per runout
        points += (10 * self.getAct(perf,"field","runouts"))
        #25 points for mom
        if 'mom' in match and match['mom'] == name:
            points += 25
        #winning team
        #print match
        #print perf
        if 'winner' in match and match['winner'] == perf['team']:
            points += 5
        return int(points)
    
    def run(self,match):
        delSql = "delete from iplpoints where matchid=?"
        pointSql = "insert into iplpoints (matchid,game,playerId,points) values (?,?,?,?)"
                    
        for fileName in os.listdir('scorecards'):
            res = re.search("match"+match.__str__()+".json",fileName)
            if res is not None:
                with open('scorecards/'+fileName) as scoreFile:
                    match = json.load(scoreFile)
                    playerPoints = {}
                    matchId = match['matchId']
                    gameInfo = match['game']
                    team1 = match['team1']
                    team2 = match['team2']
                    players = self.db.send("select playerName,playerId from playerInfo where team like ? or team like ?",[team1,team2])
                    players_dict = dict((item[0].split(' ')[0][:2] + ' ' +item[0].split(' ',1)[1],item[1]) for item in players)
                    playerName = None
                    if matchId != None and gameInfo != None:
                        self.db.send(delSql,[matchId])
                    for name, playerInfo in match["players"].items():
                        points = self.iplPointCalculator(name,match)
                        try:
                            playerName = difflib.get_close_matches(name,players_dict.keys(),1,0)[0]
                        except:
                            print name
                            print players_dict.keys()
                            print difflib.get_close_matches(name,players_dict.keys(),3,0)
                            raise
                        print playerName + "(" + name + ") : " + points.__str__()
                        playerId = players_dict[playerName]
                        tokenUpdate = applyMatchTokens(matchId, playerId, points)
                        if tokenUpdate != 0:
                            points += tokenUpdate
                            print "Token change: "+ playerName + "(" + name + ") : " + points.__str__()
                        try:
                            self.db.send(pointSql,[matchId,gameInfo,playerId,points])
                            #self.db.commit()
                        except:
                            print "cannot update ipl points.., db busy?"
                scoreFile.close()

    def applyMatchTokens(matchId, playerId, points):
        tokenUpdate = 0
        token_filename = 'lockedTeams/match'+matchId+'_tokens.json'
        # dont throw errors?
        if not os.path.isfile(token_filename): return tokenUpdate
        # maybe only load this once?
        with open(token_fileName) as tokenFile:
            tokenInfo = json.load(tokenFile)
            for token in tokenInfo:
                if token['playerId'] == playerId:
                    if token['type'] == 'boost':
                        tokenUpdate += points * 0.5
                    elif token['type'] == 'curse':
                        tokenUpdate += points * -0.5
        return int(round(tokenUpdate))

    def close(self):
        self.db.close()
