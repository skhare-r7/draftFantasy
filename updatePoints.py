import json
from itertools import chain
import sys
from database import dbInterface
import os



def updatePoints(matchId, teamId, points, db):
    entryExists = "select count(*) from draftPoints where matchid=? and teamId=?"
    if db.send(entryExists,[matchId,teamId])[0][0]:
        insertEntry = "insert into draftPoints (matchid, teamId, points) values (?,?,?)"
        db.send(insertEntry,[matchId,teamId,points])
    else:
        updateEntry = "update draftPoints set points=? where matchId=? and teamId=?"
        db.send(updateEntry,[points,matchId,teamId])
    db.commit()

def getPoints(matchId, id,db):
    res = db.send("select points from iplpoints where playerId=? and matchid=?",[id,matchId])
    if len(res) < 1: return 0
    else: return res[0][0]


db= dbInterface()

for fileName in os.listdir('lockedTeams'):
    if fileName.endswith(".json"): 
        print fileName
        points = 0
        teamId = -1
        matchId = -1
        with open('lockedTeams/'+fileName) as lockFile:    
            lockInfo = json.load(lockFile)
            print lockInfo
            teamId = lockInfo['teamId']
            matchId = lockInfo['info']
            #first check point criteria
            if lockInfo['overseas'] > 5 or \
               lockInfo['bank'] < 0 or \
               len(lockInfo['players']['Wicketkeeper']) < 1 or \
               len(lockInfo['players']['Batsman']) < 4 or \
               len(lockInfo['players']['Allrounder']) < 1 or \
               len(lockInfo['players']['Bowler']) < 2:
               points = 0 #no point in processing data
            else:
                playerList = lockInfo['players']
                for player in chain.from_iterable(playerList.values()):
                    points += getPoints(matchId, player,db)
        updatePoints(matchId, teamId, points,db)
    else:
        continue

db.close()



