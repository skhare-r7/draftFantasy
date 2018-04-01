import pickle
import sqlite3
import datetime
from prettytable import PrettyTable
import json

_START_MONEY = 700

_CURSE_TOKENS = 1
_BOOST_TOKENS = 1
_BORROW_TOKENS = 2

#Create a table that has details of human players
# game initializes with everyone having equal bank value of 100M?

# example:
# ______________________________________
#| teamId | teamName | name     | bank |
#|    1   |  n_emoo  | Shreyas  | 100M |

#TODO
def create_humanplayers(c):
    c.execute('''CREATE TABLE humanPlayers
              (teamId integer, teamName text, name text, bank int)''')
    humanPlayers = {}
    humanPlayers[0] = ['Cursed XI', 'Shreyas']
    humanPlayers[1] = ['Champion x2', 'Sri']
    humanPlayers[2] = ['NoPakXI', 'Shrikar']
    humanPlayers[3] = ["Kia Kaha",'Ripu']
    humanPlayers[4] = ["Khan's Super Kings",'Farhan']
    humanPlayers[5] = ["Boyzrback",'Srikaran']
    humanPlayers[6] = ["Ball Busters",'Yenan']
    humanPlayers[7] = ["Random Name",'Anoop']
    

    
    for teamId, info in humanPlayers.items():
        c.execute("INSERT INTO humanPlayers VALUES (?,?,?,?)",[teamId,info[0],info[1],_START_MONEY])


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
              (playerId integer, status text, startBid int, lastModified ts, teamPos int)''')

    c.execute("select playerId from playerInfo")
    for entry in c.fetchall():
        id = entry[0]
        c.execute("INSERT INTO playerStatus VALUES (?,'Draft',-1,?, -1)",[id,datetime.datetime.now()])
    


def getSkillFromCategory(value):
    if value == 1: return "Batsman"
    elif value == 4: return "Wicketkeeper"
    elif value == 3: return "Allrounder"
    elif value == 2: return "Bowler"
    else: return None


def getTeamNameFromSideId(value):
    if value == 'CHN': return "CSK"
    elif value == 'HYD': return "SRH"
    elif value == 'PNJ': return "KXIP"
    elif value == 'KOL': return "KKR"
    elif value == 'DEL': return "DD"
    elif value == 'BNG': return "RCB"
    elif value == 'RJS': return "RR"
    elif value == 'MUM': return "MI"
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
    json_data = open('ipl2018PlayerList.json')
    data = json.load(json_data)
    players = data['d']['Result']['lstAvPlayers']
    c.execute('''CREATE TABLE playerInfo
              (playerId integer, team text, playerName text, price int, skill1 text, overseas integer)''')
    for player in players:
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
            elif key == 'Price' : price = value*10
            elif key == 'PlayerTypeId' : skill1 = getSkillFromCategory(value)
#            elif key == 'OPlayerId' and value: overseas = 1
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
#   Token: Play token on playerId. Value is a hack here, different values will map to different tokens
#                1 - boost
#                2 - curse
#                3 - borrow
# value: Only applicable for Auction, Bid and forceSell (special meaning for token, see above)
# complete [0|1]: mark all (bid / auction) transactions as complete after auction finishes


#example:
#_______________________________________________________________
#|type     | playerId | value | teamId | complete  | timestamp |
#|Ban      | 12       |  0    |    1    |    1     |           |
#|Pick     | 16       |  0    |    2    |    1     |           |
#|Auction  | 76       |  7.5  |    5    |    0     |           |  <- playerId 76 is up for bidding, starting bid is 7.5
#|ForceSell| 100      |  5    |    6    |    1     |           |
#|Bid      | 65       |  5    |    2    |    1     |           |  <- 5M bid was made on playerid 65, auction is now closed
#|Token    | 65       |  1    |    2    |    0     |           |  <- Player 2 has played token type 1 against playerId 65


def create_transaction(c):
    c.execute('''CREATE TABLE transactions
              (type text, playerId integer, value int, teamId integer, complete integer, timestamp ts)''')


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
              (id integer primary key, type text, game text, deadline ts, info integer)''')


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

#Create tokens table
#teamId: Team name
#token: Token type. Currently supported tokens are:
   # boost - double player's points for the day
   # curse - half player's points for the day
   # borrow - borrow another team's player for the day
#count: Number of available tokens
#
#example:
#_________________________________
#| teamId  | token  | count  |
#|  100    | curse  |  0     |
#|  100    | boost  |  1     |
#|  100    | borrow |  2     |
#|  102    | curse  |  0     |
#
def create_tokens(c):
    tquery = "CREATE TABLE tokens \
          (teamId integer, token text, count integer)"
    c.execute(tquery)
    c.execute("select teamId from humanPlayers")
    for entry in c.fetchall():
        teamId = entry[0]
        c.execute("INSERT INTO tokens VALUES (?,?,?)",[teamId,'boost', _BOOST_TOKENS])
        c.execute("INSERT INTO tokens VALUES (?,?,?)",[teamId,'curse', _CURSE_TOKENS])
        c.execute("INSERT INTO tokens VALUES (?,?,?)",[teamId,'borrow', _BORROW_TOKENS])

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
    create_tokens(c)
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



