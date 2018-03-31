import sqlite3
from datetime import datetime
import lxml.html
from dateutil import parser
from dateutil import tz

HERE = tz.tzlocal()
_CURRENT_TZ_YEAR = '+0530 2018'

conn = sqlite3.connect('draftGame.db') 
c = conn.cursor()

series_url = 'http://www.espncricinfo.com/ci/content/series/1131611.html?template=fixtures'

gameFullSchedule = []

tree = lxml.html.parse(series_url)
dates = tree.xpath("//li[@class='large-20 medium-20 columns']/div[1]/span/text()")

gamesPlayedSofar = tree.xpath("//li[@class='large-20 medium-20 columns']/div[2]/span/a/text()")
gameFullSchedule = gameFullSchedule+gamesPlayedSofar

gamesNotPlayedYet = tree.xpath("//li[@class='large-20 medium-20 columns']/div[2]/span[1]/text()")
gameFullSchedule = gameFullSchedule+list(filter(None,[x.rstrip() for x in gamesNotPlayedYet]))


countGame = 0

for i in range(0,len(dates)):
	if (i%2==0):
		date_string = dates[i].strip()+' '+dates[i+1].split(u'\xa0')[0] + _CURRENT_TZ_YEAR
                try:
		  dt = parser.parse(date_string)
		  c.execute("insert into futures (type,game,deadline,info) values (?,?,?,?)",['Lock',gameFullSchedule[countGame].split('-')[1],dt.astimezone(HERE),(i/2)+1])
		  countGame = countGame + 1
                except:
                  break
conn.commit()
conn.close()
