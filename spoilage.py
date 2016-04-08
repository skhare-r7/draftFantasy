from database import dbInterface
from datetime import datetime as dt
from time import sleep



def checkSpoilage():
    db = dbInterface()
    spoilQuery = "select * from playerStatus where lastModified <= datetime('now','localtime', '-2 days')"

    for row in db.send(spoilQuery,[]):
        id = row[0]
        ValQuery = "select price from playerInfo where playerId=?"
        print "reducing price for playerId:" + id.__str__()
        price = db.sendQuery(valQuery,[id])
        price -= 0.1
        dropQuery = "udpate playerInfo set price=? where playerId=?"
        db.sendQuery(dropQuery,[price,id])
        touchQuery = "update playerStatus set lastModified=? where playerId=?"
        db.sendQuery(touchQuery,[dt.now(),id])
        db.commit()
    db.close()
    
while True:
    print "checking spoilage: " + dt.now().__str__()
    checkSpoilage()
    print "sleeping 30 mins"
    sleep(30*60) #check every 30 mins
    
    #dt.strptime(ts,"%Y-%m-%d %H:%M:%S.%f")
