import pickle
import sqlite3
import datetime
from prettytable import PrettyTable

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
    humanPlayers[0] = ['n_emoo', 'Shreyas']
    humanPlayers[1] = ['team1', 'Akshay']
    humanPlayers[2] = ['Dozer', 'Sri']
    humanPlayers[3] = ['team2', 'Ripu']
    humanPlayers[4] = ['team3', 'Yenan']
    humanPlayers[5] = ['team4', 'Ali']
    for teamId, info in humanPlayers.items():
        c.execute("INSERT INTO humanPlayers VALUES (?,?,?,'100.0')",[teamId,info[0],info[1]])


#Create a player Status table
# status: [Auction|Open|TeamId]
#   Auction : Player is available for pick / ban in auction stage. 
#             All players will be moved from Auction after initial setup
#   Open    : Player is available for bidding in the open market
#             Stale players lose value in the open market
#   TeamId  : Player belongs to Team TeamId
# forSale[0|1]: Indicates if player is privately up for auction  
# lastModified: Keep track of time spent in open market
# teamPos: Indicates playing position in roster (players 1-11 are active)

# example:
#_______________________________________________________
#| playerId | status | forSale | lastModified | teamPos|
#|   12     | Open   |    0    | 2016-03-28   |  -1    |  <- player is in open market
#|   156    |  2     |    0    | 2016-03-25   |   3    |  <- player is in team 2, position 3
#|   25     |  1     |    1    | 2016-03-26   |   5    |  <- player is in team 1, position 5, and up for sale 
#

def create_playerStatus(c):
    c.execute('''CREATE TABLE playerStatus
              (playerId integer, status text, teamId integer, forSale int, lastModified ts, teamPos int)''')

    c.execute("select playerId from playerInfo")
    for entry in c.fetchall():
        id = entry[0]
        c.execute("INSERT INTO playerStatus VALUES (?,'Auction', NULL, '0',?, NULL)",[id,datetime.datetime.now()])
    

    
#Create player info table
# This is extracted from  http://fantasy.icc-cricket.com/fantasydata/playerlist/game_playerlist_tour_350.json
# Price is intialized from ICC, but is allowed to fluctuate once game commences

# example:
#___________________________________________________________________
#|playerId | team     | playerName       | price | skill1 | skill2 |
#| 220     | Zimbabwe | Tawanda Mupariwa |  6.0  | Bowler |        |



def create_playerinfo(c):
    f = open("playerListJson.dump","rb") #downloaded offline from ICC
    playerList = pickle.load(f)
    f.close() 

    c.execute('''CREATE TABLE playerInfo
              (playerId integer, team text, playerName text, price real, skill1 text, skill2 text)''')
    for player in playerList:
        playerId = None
        teamName = None
        name = None
        value = None
        skill1 = None
        skill2 = None
        for key,value in  player.items():
            if key == 'No': playerId = value
            elif key == 'Name' : name = value
            elif key == 'TeamName' : teamName = value
            elif key == 'Value' : price = value
            elif key == 'SkillDesc' : skill1 = value
            elif key == 'SecondarySkillDesc' : skill2 = value
            else: pass

        if (playerId and name and teamName and price):
            insertQuery = "INSERT INTO playerInfo VALUES (?,?,?,?,?,?)"
            c.execute(insertQuery,[playerId,teamName,name,price,skill1,skill2])

#Create transaction table
# type:
#   Ban: Ban playerId from auction
#   Pick: Pick playerId from auction
#   Auction: Put up player from team for auction, [value] is min. price
#   Bid: Bid [value] on player
#   ForceSell: Instantly sell player to open market. [value] is 75%(?) of purchase price
# value: Only applicable for Auction, Bid and forceSell
# complete [0|1]: mark all (bid / auction) transactions as complete after auction finishes

#example:
#__________________________________________________
#|type     | playerId | value | humanId | complete |
#|Ban      | 12       |  0    |    1    |    1     | 
#|Pick     | 16       |  0    |    2    |    1     |
#|Auction  | 76       |  7.5  |    5    |    0     |  <- playerId 76 is up for bidding, starting bid is 7.5
#|ForceSell| 100      |  5    |    6    |    1     |  
#|Bid      | 65       |  5    |    2    |    1     |  <- 5M bid was made on playerid 65, auction is now closed

def create_transaction(c):
    c.execute('''CREATE TABLE transactions
              (type text, playerId integer, value real, humanId integer, complete integer)''')


def init_database():
    conn = sqlite3.connect('draftGame.db')
    c = conn.cursor()
    create_playerinfo(c)
    create_humanplayers(c)
    create_playerStatus(c)
    create_transaction(c)
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
        return c.fetchall()

    def sendPretty(self,query,args):
        self.c.execute(query,args)
        header = [description[0] for description in self.c.description]
        
        table = PrettyTable(header)
        for row in self.c:
            table.add_row(row)
        result =  table.get_string()
        #print result
        return result

    def close(self):
        self.conn.commit()
        self.conn.close()


