import sqlite3
from datetime import datetime
import lxml.html
from dateutil import parser
from dateutil import tz

HERE = tz.tzlocal()

conn = sqlite3.connect('draftGame.db') 
c = conn.cursor()

series_url = 'http://www.espncricinfo.com/indian-premier-league-2016/content/series/968923.html?template=fixtures'

tree = lxml.html.parse(series_url)
dates = tree.xpath("//li[@class='large-20 medium-20 columns']/div[1]/span/text()")

for i in range(0,len(dates),2):
    date_string = dates[i].strip()+' '+dates[i+1].split(u'\xa0')[0] + '+0530 2017'
    dt = parser.parse(date_string)
    c.execute("insert into futures (type,deadline,info) values (?,?,?)",['Lock',dt.astimezone(HERE),i+1])

conn.commit()
conn.close()

