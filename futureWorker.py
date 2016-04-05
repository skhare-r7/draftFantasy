from interface import interface
from database import dbInterface
from time import sleep
from threading import Thread

class futureWorker(Thread):
    def __init__(self,tg):
        Thread.__init__(self)
        self.db = dbInterface()
        self.tg = tg
        
    def run(self):
        while True:
            sleep(60*1000) #sleep 60 seconds?
            checkFutureQuery = "select * from futures where timestamp <= datetime('now','localtime')"
            futures = db.send(checkFutureQuery,[])
            for future in futures:
                print future
            tg.sendMessage('Shreyas',future+' works!')

        
    
