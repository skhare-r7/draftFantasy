from database import dbInterface
from updater import updater
from series import series
from datetime import datetime as dt
from datetime import timedelta
from time import sleep
import sys
import os
from iplPoints import iplPoints

class livescorer:
    def __init__(self,db,matchId):
        self.db = db
        self.updater = updater(db)
        self.matchId = int(matchId)
        self.iplPoints = iplPoints(db)

    def runOnce(self):
        #get live url
        url = series.get_live_url(self.matchId)
        #run scorecard scraper
        os.system("python scorescrape.py " + url) 
        #update points
        self.iplPoints.run(self.matchId)
        self.updater.run()

    
    def runAgressive(self,time,interval):
        end = dt.now() + timedelta(seconds=time)
        while dt.now() < end:
            self.runOnce()
            sleep(interval)
        self.updater.finishGame(self.matchId)


if __name__=='__main__':
    db = dbInterface()
    ls = livescorer(db,sys.argv[1])
    ls.runOnce()
