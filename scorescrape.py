from lxml import etree
import lxml.html
import re
from datetime import datetime as dt
from datetime import timedelta
from database import dbInterface

db = dbInterface()

iplFixturesPage = "http://www.espncricinfo.com/indian-premier-league-2016/content/series/968923.html?template=fixtures"
tree = lxml.html.parse(iplFixturesPage)

listings = tree.xpath("//li[@class='large-20 medium-20 columns']")
#print len(listings)

conversion = {}
conversion["Delhi Daredevils"] = "DD"
conversion["Gujarat Lions"] = "GL"
conversion["Kings XI Punjab"] = "KXIP"
conversion["Kolkata Knight Riders"] = "KKR"
conversion["Mumbai Indians"] = "MI"
conversion["Rising Pune Supergiants"] = "RPS"
conversion["Royal Challengers Bangalore"] = "RCP"
conversion["Sunrisers Hyderabad"] = "SRH"

sqlQueries = []

for match in listings:
    try:
        dateText = match.xpath(".//span[@class='fixture_date']/text()")
        fullDate = dateText[0].encode('utf-8').strip()+ " "  + dateText[1].encode('utf-8').strip()
        
        date = dt.strptime(fullDate, "%a %b %d %H:%M\xc2\xa0local")
        
        #fix local time to EST
        dateEst = date.replace(year=2016) - timedelta(seconds=9*60*60+30*60)
        gameText = match.xpath(".//span[@class='play_team']/text()")[0]
        if gameText.strip() == '':
            #continue
            gameText = match.xpath(".//span[@class='play_team']/a/text()")[0]
            print "Game is over or live, skipping:" + gameText
            continue

#        print gameText
        gameTextRegex = re.compile("(?P<matchid>\d+).*?- (?P<team1>.*?) v (?P<team2>.*)")
        result = re.match(gameTextRegex,gameText.strip())
        futuresQuery = "insert into futures (type,deadline,info) values ('Lock',?," + result.group('matchid') + ")"
        db.send(futuresQuery,[dateEst])
    except:        
        print "error when parsing entry"
        print lxml.html.tostring(match)

    
db.commit()
db.close()
