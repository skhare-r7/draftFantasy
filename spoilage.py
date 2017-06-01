from database import dbInterface
from datetime import datetime as dt
from time import sleep



def checkSpoilage():
    SPOILAGE_RATE = 0.04
    try:
        db = dbInterface()
        spoilQuery = "select * from playerStatus where status='Open' and lastModified <= datetime('now','localtime', '-1 days')"
        for row in db.send(spoilQuery,[]):
            id = row[0]
            valQuery = "select price from playerInfo where playerId=?"
            print "reducing price for playerId:" + id.__str__()
            price = db.send(valQuery,[id])[0][0]
            price -= int(SPOILAGE_RATE * price)
            dropQuery = "update playerInfo set price=? where playerId=?"
            db.send(dropQuery,[price,id])
            touchQuery = "update playerStatus set startBid=?,lastModified=? where playerId=?"
            db.send(touchQuery,[price,dt.now(),id])
            #db.commit()
        db.close()
    except Exception,e:
        print "..failed"
        print e
        pass # database locked? we'll try again later
    
while True:
    print "checking spoilage: " + dt.now().__str__()
    checkSpoilage()
    print "sleeping 15 mins"
    sleep(15*60) #check every 30 mins
    
    #dt.strptime(ts,"%Y-%m-%d %H:%M:%S.%f")
