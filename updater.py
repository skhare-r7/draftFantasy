import json
from itertools import chain
import sys
from database import dbInterface
import os
import re

class updater:
    def __init__(self,db):
        self.db = db

    def updatePoints(self,matchId, teamId, points):
        dropCurrentQ = "delete from draftPoints where matchid=? and teamId=?"
        self.db.send(dropCurrentQ,[matchId,teamId])
        insertEntry = "insert into draftPoints (matchid, teamId, points) values (?,?,?)"
        self.db.send(insertEntry,[matchId,teamId,points])
        #self.db.commit()

    def getPoints(self,matchId, id):
        res = self.db.send("select points from iplpoints where playerId=? and matchid=?",[id,matchId])
        if len(res) < 1: return 0
        else: return res[0][0]


    def run(self):
        for fileName in os.listdir('lockedTeams'):
            #iterate all games
            if re.match('.*?team\d+\.json', filename):
                points = 0
                teamId = -1
                matchId = -1
                with open('lockedTeams/'+fileName) as lockFile:    
                    lockInfo = json.load(lockFile)
                    teamId = lockInfo['teamId']
                    matchId = lockInfo['info']
                    playerList = lockInfo['players']
                    if len(list(chain.from_iterable(playerList.values()))) < 7 or \
                       lockInfo['bank'] < 0 or \
                       len(lockInfo['players']['Wicketkeeper']) < 1 or \
                       len(lockInfo['players']['Batsman']) < 2 or \
                       len(lockInfo['players']['Allrounder']) < 1 or \
                       len(lockInfo['players']['Bowler']) < 1:
                        points = 0 #no point in processing data
                        print "Team:"+ teamId.__str__() + " failed check for match:" + matchId.__str__()
                    else: #team is ok
                        for player in chain.from_iterable(playerList.values()):
                            points += self.getPoints(matchId, player)
                    try:
                        self.updatePoints(matchId, teamId, points)
                    except: #db is busy, try again
                        print "Failed to update.., DB busy?"
                lockFile.close()
            else:
                continue

    def finishGame(self,game):
        print "finishing game " + game.__str__()
        for fileName in os.listdir('lockedTeams'):
            res = re.search("match(\d+)_team\d+.*",fileName)
            if res is not None and res.group(1) == game: #game is done, move file
                print "moving "  + fileName
                os.rename('lockedTeams/'+fileName,'lockedTeams/finished/'+fileName)

    def close(self):
        self.db.close()



if __name__=='__main__':
    db = dbInterface()
    u = updater(db)
    u.run()
