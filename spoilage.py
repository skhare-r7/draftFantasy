from database import dbInterface
from datetime import datetime as dt
from time import sleep



def checkSpoilage():
    db = dbInterface()
    spoilQuery = "select * from playerStatus where lastModified <= datetime('now','localtime', '-2 days')"

    for row in db.send(spoilQuery,[]):
        id = row[0]
        valQuery = "select price from playerInfo where playerId=?"
        print "reducing price for playerId:" + id.__str__()
        price = db.send(valQuery,[id])[0][0]
        if price >= 2.04: price -= (0.02 * price) #2 percent spoilage
        dropQuery = "update playerInfo set price=? where playerId=?"
        db.send(dropQuery,[price,id])
        touchQuery = "update playerStatus set lastModified=? where playerId=?"
        db.send(touchQuery,[dt.now(),id])
        db.commit()
    db.close()
    
while True:
    print "checking spoilage: " + dt.now().__str__()
    checkSpoilage()
    print "sleeping 30 mins"
    sleep(30*60) #check every 30 mins
    
    #dt.strptime(ts,"%Y-%m-%d %H:%M:%S.%f")
