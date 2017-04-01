import pickle
import sqlite3
import datetime
from prettytable import PrettyTable
import json

#Create a table that has details of human players
# game initializes with everyone having equal bank value of 100M?

# example:
# ______________________________________
#| teamId | teamName | name     | bank |
#|    1   |  n_emoo  | Shreyas  | 100M |

#TODO
def create_humanplayers(c):
    c.execute('''CREATE TABLE humanPlayers
              (teamId integer, teamName text, name text, bank real)''')
    humanPlayers = {}
    humanPlayers[0] = ['Unique Losers', 'Shreyas']
    humanPlayers[1] = ['Champion', 'Sri']
    humanPlayers[2] = ['Bangla2019', 'Shrikar']
    humanPlayers[3] = ['Ma Niggas', 'Yenan']



    for teamId, info in humanPlayers.items():
        c.execute("INSERT INTO humanPlayers VALUES (?,?,?,'100.0')",[teamId,info[0],info[1]])


#Create a player Status table
# status: [Draft|Open|TeamId]
#   Draft : Player is available for pick / ban in draft stage. 
#             All players will be moved from Auction after initial setup
#   Open    : Player is available for bidding in the open market
#             Stale players lose value in the open market
#   TeamId  : Player belongs to Team TeamId
# startBid: Indicates opening auction price. -1 means not on auction
#           For players on open market, this should be the price
# lastModified: Keep track of time spent in open market
# teamPos: Indicates playing position in roster (players 1-11 are active)

# example:
#_______________________________________________________
#| playerId | status | startBid | lastModified | teamPos|
#|   12     | Open   |    3.2   | 2016-03-28   |  -1    |  <- player is in open market
#|   156    |  2     |    -1    | 2016-03-25   |   3    |  <- player is in team 2, position 3
#|   25     |  1     |    5.0   | 2016-03-26   |   5    |  <- player is in team 1, position 5, and up for sale 
#

def create_playerStatus(c):
    c.execute('''CREATE TABLE playerStatus
              (playerId integer, status text, startBid real, lastModified ts, teamPos int)''')

    c.execute("select playerId from playerInfo")
    for entry in c.fetchall():
        id = entry[0]
        c.execute("INSERT INTO playerStatus VALUES (?,'Draft',-1,?, -1)",[id,datetime.datetime.now()])
    


def getSkillFromCategory(value):
    if value == 1: return "Batsman"
    elif value == 2: return "Bowler"
    elif value == 3: return "Allrounder"
    elif value == 4: return "Wicketkeeper"
    else: return None

def getFullTeamNameFromSideId(value):
    if value == "DEL": return "Delhi Daredevils"
    elif value == "GUJ": return "Gujarat Lions"
    elif value == "PNJ": return "Kings XI Punjab"
    elif value == "KOL": return "Kolkata Knight Riders"
    elif value == "MUM": return "Mumbai Indians"
    elif value == "PUN": return "Rising Pune Supergiants"
    elif value == "BNG": return "Royal Challengers Bangalore"
    elif value == "HYD": return "Sunrisers Hyderabad"
    else: return None

def getTeamNameFromSideId(value):
    if value == "DEL": return "DD"
    elif value == "GUJ": return "GL"
    elif value == "PNJ": return "KXIP"
    elif value == "KOL": return "KKR"
    elif value == "MUM": return "MI"
    elif value == "PUN": return "RPS"
    elif value == "BNG": return "RCB"
    elif value == "HYD": return "SRH"
    else: return None


    
#Create player info table
# This is extracted from  http://fantasy.icc-cricket.com/fantasydata/playerlist/game_playerlist_tour_350.json
# Price is intialized from ICC, but is allowed to fluctuate once game commences

# example:
#____________________________________________________________________
#|playerId | team     | playerName       | price | skill1 | overseas|
#| 220     | Zimbabwe | Tawanda Mupariwa |  6.0  | Bowler |  1      |



def create_playerinfo(c):
#    f = open("playerListJson.dump","rb") #downloaded offline from ICC
#    playerList = pickle.load(f)
#    f.close() 
    json_data = open('ipl2017PlayerList.json')
    data = json.load(json_data)

    c.execute('''CREATE TABLE playerInfo
              (playerId integer, team text, playerName text, price real, skill1 text, overseas integer)''')
    for player in data:
        playerId = None
        teamName = None
        name = None
        value = None
        skill1 = None
        overseas = 0
        for key,value in  player.items():
            if key == 'PlayerId': playerId = value
            elif key == 'PlayerName' : name = value
            elif key == 'RealTeamName' : teamName = getTeamNameFromSideId(value)
            elif key == 'Price' : price = value
            elif key == 'PlayerTypeId' : skill1 = getSkillFromCategory(value)
            elif key == 'info4' : overseas = 1
            else: pass

        if (playerId and name and teamName and price):
            insertQuery = "INSERT INTO playerInfo VALUES (?,?,?,?,?,?)"
            c.execute(insertQuery,[playerId,teamName,name,price,skill1,overseas])

#Create transaction table
# type:
#   Ban: Ban playerId from draft
#   Pick: Pick playerId from draft
#   Auction: Put up player from team for auction, [value] is min. price
#   Bid: Bid [value] on player
#   ForceSell: Instantly sell player to open market. [value] is 75%(?) of purchase price
# value: Only applicable for Auction, Bid and forceSell
# complete [0|1]: mark all (bid / auction) transactions as complete after auction finishes

#example:
#_______________________________________________________________
#|type     | playerId | value | humanId | complete | timestamp |
#|Ban      | 12       |  0    |    1    |    1     |           |
#|Pick     | 16       |  0    |    2    |    1     |           |
#|Auction  | 76       |  7.5  |    5    |    0     |           |  <- playerId 76 is up for bidding, starting bid is 7.5
#|ForceSell| 100      |  5    |    6    |    1     |           |
#|Bid      | 65       |  5    |    2    |    1     |           |  <- 5M bid was made on playerid 65, auction is now closed

def create_transaction(c):
    c.execute('''CREATE TABLE transactions
              (type text, playerId integer, value real, humanId integer, complete integer, timestamp ts)''')


#Create futures table
#type:
# auction : Execute and resolve auction 
# lock : Freeze teams before match time
#deadline: future timestamp when activity should occur
#info: playerId for type auction, gameId for gameLock
#
#example:
#__________________________________
#id | type      | deadline  | info |
# 1 | Auction   |           | 125  |
# 2 | Lock      |           | 4    |<-- game number (optional)
def create_futures(c):
    c.execute('''CREATE TABLE futures
              (id integer primary key, type text, deadline ts, info integer)''')


#Create IPL points table
#id: Unique id
#matchid : Identifier for the game (used for filename)
#game : some text (e.g. team names or something)
#playerId : column for player code: XXXX
#points : points earned by that player for that game
#example:
#_____________________________________________
#| matchid | game      | playerId | points |
#|  100    | SRH vs RCB| 2733     |     33 |
# 
def create_iplpoints(c):
    pquery = "CREATE TABLE iplpoints \
          (matchid integer, game text, playerId integer, points integer)"
    c.execute(pquery)


#Create draft points table
#id: Unique id
#matchid : Identifier for the game (used for filename)
#teamId : column for teamId code
#points : points from match
#example:
#_________________________________
#| matchid | teamId | points  |
#|  100    | 0      |  34     |
#
def create_draftpoints(c):
    tquery = "CREATE TABLE draftPoints \
          (matchid integer, teamId integer, points integer)"
    c.execute(tquery)



def init_database():
    conn = sqlite3.connect('draftGame.db')
    c = conn.cursor()
    create_playerinfo(c)
    create_humanplayers(c)
    create_playerStatus(c)
    create_transaction(c)
    create_futures(c)
    create_iplpoints(c)
    create_draftpoints(c)
    conn.commit()
    conn.close()

if __name__=='__main__':
    init_database()




class dbInterface:
    def __init__(self):
        self.conn = sqlite3.connect('draftGame.db',check_same_thread=False)
        self.c = self.conn.cursor()


    def simpleQuery(self,query):
        self.c.execute(query)
        print(self.c.fetchall())
    
    def send(self,query, args):
        self.c.execute(query, args)
        self.conn.commit() #should only commit for create, insert , update and delete?
        return self.c.fetchall()

    def sendPretty(self,query,args):
        print query
        self.c.execute(query,args)
        self.conn.commit()
        header = [description[0] for description in self.c.description]
        
        table = PrettyTable(header)
        rows = 0
        for row in self.c:
            if rows > 25: break
            rows += 1
            table.add_row(row)
        result =  table.get_string()
        print result
        return result

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def getSkill(self,val):
        skills = ["Allrounder","Batsman", "Wicketkeeper", "Bowler"]
        for skill in skills:
            try:
                if skill.lower().index(val.lower()) >= 0: return skill
            except:
                pass
        return None



