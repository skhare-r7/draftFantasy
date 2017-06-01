from database import dbInterface
from updater import updater
from series import series
from datetime import datetime as dt
from datetime import timedelta
from time import sleep
import sys
import os
from iplPoints import iplPoints
from threading import Thread


class livescorer(Thread):
    def __init__(self,db,matchId):
        self.db = db
        self.updater = updater(db)
        self.matchId = int(matchId)
        self.iplPoints = iplPoints(db)
        self.time = 0
        self.interval = 0
        self.scoreType = None
        Thread.__init__(self)
    
    def setScorerType(self,scoreType='aggressive', time=9*60*60 ,interval=2*60):
        self.time = time
        self.interval = interval
        self.scoreType = scoreType

    def runOnce(self):
        #get live url
        url = series.get_live_url(self.matchId)
        #run scorecard scraper
        os.system("python scorescrape.py " + url + " " + self.matchId.__str__())
        #update points
        try:
            self.iplPoints.run(self.matchId)
            self.updater.run()
        except:
            print "Failed to update points, db locked?"

    def run(self):
        if self.scoreType == 'once':
            self.runOnce()
        elif self.scoreType == 'aggressive':
            self.runAgressive()
        else:
            pass

    def runAgressive(self):
        end = dt.now() + timedelta(seconds=self.time)
        while dt.now() < end:
            self.runOnce()
            sleep(self.interval)
        self.updater.finishGame(self.matchId)


if __name__=='__main__':
    db = dbInterface()
    ls = livescorer(db,sys.argv[1])
    ls.setScorerType(scoreType='aggressive')
    ls.start()
