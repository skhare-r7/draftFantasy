from database import dbInterface
from random import shuffle
from interface import interface
from datetime import datetime as dt
from threading import Thread 
from futureWorker import futureWorker
from time import sleep
from datetime import timedelta

class draftGame:
    def __init__(self):
        self.db = dbInterface()
        #game initialization
        self.tg = None
        self.rounds = []
#        self.rounds.append(['ban', 'ban', 'ban'])
        self.rounds.append(['ban'])
        self.rounds.append(['pick'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['pick_r'])



        
        self.currentPhase = 'waiting' #we start at drafting

        self.currentRound = 0
        self.currentStage = 0 
        self.currentPlayer = 0

        self.currentActivity = self.rounds[self.currentRound][self.currentStage]
        self.numberOfPlayers = self.db.send("select count(*) from humanPlayers",[])[0][0]
        #print self.numberOfPlayers
        self.order = [i for i in range(0,self.numberOfPlayers)]
        shuffle(self.order)
        

    def setTg(self,tg):
        self.tg = tg #used to broadcast messages

    def nextStage(self):
        totalRounds = len(self.rounds)
        if self.currentStage < len(self.rounds[self.currentRound])-1: #more stages in this round
            self.currentStage += 1
        elif self.currentStage == len(self.rounds[self.currentRound])-1 and self.currentRound < totalRounds -1: #next round
            self.currentStage = 0
            self.currentRound += 1
        elif self.currentStage == len(self.rounds[totalRounds-1])-1 and self.currentRound == totalRounds-1: #next phase
            #drafting is done
            self.currentPhase = 'game_on'
            self.moveAllPlayersToOpenMarket()
        if self.rounds[self.currentRound][self.currentStage][-2:] == '_r': self.order.reverse()


    def getCurrentStage(self):
        stage= self.rounds[self.currentRound][self.currentStage]
        if 'ban' in stage: return 'ban'
        elif 'pick' in stage: return 'pick'
        else: return 'none'

    def gameStage(self):
        toRet = "Current Phase:" + self.currentPhase + "\n"
        if self.currentPhase == 'draft':
            toRet += "Current Round:" + self.currentRound.__str__() + "\n"
            toRet += "Current Stage:" + self.rounds[self.currentRound][self.currentStage] + "\n"
            toRet += "Current Player:" + self.getUserById(self.order[self.currentPlayer])
        return toRet

    def nextPlayer(self):
        self.currentPlayer += 1
        if self.currentPlayer > len(self.order)-1: 
            self.nextStage()
            self.currentPlayer = 0
        

    def startGame(self,user):
        if user == 'Shreyas':
            self.currentPhase = 'draft'
            tg.broadcast("Game is on! Good luck")
            tg.broadcast(game.gameStage())
            return "Done"

    def getCurdrentStage(self):
        if 'ban' in self.rounds[self.currentRound][self.currentStage]: return 'ban'
        elif 'pick' in self.rounds[self.currentRound][self.currentStage]: return 'pick'
        else: return None

    def isValidId(self,id):
        query = "select count(*) from playerStatus where playerId=?"
        return self.db.send(query,[id])[0][0] == 1

    def isNotBanned(self, id): #player is not banned or picked
        query = "select status from playerStatus where playerId=?"
        return self.db.send(query,[id])[0][0] == 'Draft'
    
    def banId(self,user, id):
        price = self.getPrice(id)
        query = "update playerStatus set status='Open',lastModified=?,forSale=? where playerId=?"
        self.db.send(query,[dt.now(),price,id])
        teamId = self.getTeamIdFromUser(user)
        transactionQuery = "insert into transactions values (?,?,?,?,?,?)"
        self.db.send(transactionQuery,["Ban",id,0,teamId,1,dt.now()])
        self.db.commit()

    def moveAllPlayersToOpenMarket(self):
        pass
        
    def pickId(self,user, id):
        teamId = self.getTeamIdFromUser(user)
        playersQuery = "select count(*) from playerStatus where status=?"
        value = self.getPrice(id)
        bank = self.getBankValue(teamId)
        newBank = bank - value
        numPlayers = self.db.send(playersQuery,[teamId])[0][0]
        teamPos = numPlayers + 1 #this guy's position 
        playerUpdate = "update playerStatus set status=?,teamPos=?,lastModified=? where playerId=?"
        self.db.send(playerUpdate,[teamId,teamPos,dt.now(),id])
        #ok to get negative bank
        bankUpdate = "update humanPlayers set bank=? where teamId=?"
        self.db.send(bankUpdate,[newBank,teamId])
        transactionQuery = "insert into transactions values (?,?,?,?,?,?)"
        self.db.send(transactionQuery,["Pick",id,0,teamId,1,dt.now()])        
        self.db.commit()

    def getTeamIdFromUser(self,user):
        query = "select teamId from humanPlayers where name=?"
        return self.db.send(query,[user])[0][0]

    def getUserById(self,id):
        query = "select name from humanPlayers where teamId=?"
        return self.db.send(query,[id])[0][0]

    def handleCommand(self, user, command, args):
        if command == 'help':
            return self.getHelpText()
        elif command == 'stage':
            return self.gameStage()
        elif command == 'list':
            return self.getListQuery(args)
        elif command == 'find':
            return self.findPlayer(args)
        elif command == 'player':
            return self.findPlayerById(args)
        elif command == 'ban':
            return self.processBan(user,args)
        elif command == 'pick':
            return self.processPick(user,args)
        elif command == 'auction':
            return self.processAuction(user,args)
        elif command == 'forcesell':
            return self.processForcedSale(user,args)
        elif command == 'bid':
            return self.processBid(user,args)
        elif command == 'viewteam':
            return self.viewTeamQuery(user)
        elif command == 'swap':
            return self.processSwap(user,args)
        elif command == 'viewmarket':
            pass
        elif command == 'deadline':
            pass
        #hidden commands
        elif command == 'start':
            return self.startGame(user)
        else: pass
 
    def playerAvailableForBid(self,playerId):
        pass
    def existingAuction(self,playerId):
        pass
        
    def processBid(self,user,args):
        playerId = args.split(' ')[0]
        bid = None
        if self.isValidId(playerId) and self.playerAvailableForBid(playerId):
            try:
                bid = float(args.split(' ')[1])
                #some moron will try to do this
                if bid < 0 : bid = None
            except:
                return "Invalid bid"
            if bid is None: 
                return "Invalid bid. Check bidding syntax"
            elif self.existingAuction(playerId):
                #place bid
                pass
            else:
                self.prepareNewAuction(auctionCloseTime,playerName,startingPrice,playerId)

    def verifyOwnership(self,user,id):
        teamId = self.getTeamIdFromUser(user)
        verifyQuery = "select count(*) from playerStatus where playerId=? and status=?"
        return self.db.send(verifyQuery,[id,teamId])[0][0] == 1

    def getLastPos(self,user):
        teamId = self.getTeamIdFromUser(user)
        return self.db.send("select teamPos from playerStatus where status=? order by teamPos desc limit 1",[teamId])[0][0]

    def getPrice(self,id):
        valueQuery = "select price from playerInfo where playerId =?"
        return self.db.send(valueQuery,[id])[0][0]

    def getName(self,id):
        valueQuery = "select playerName from playerInfo where playerId =?"
        return self.db.send(valueQuery,[id])[0][0]

    def processAuction(self,user,args):
        playerId = args.split(' ')[0]
        startingPrice = None
        if self.isValidId(playerId) and self.verifyOwnership(user,playerId):
            try:
                startingPrice = float(args.split(' ')[1])
                #some moron will try to do this
                if startingPrice < 0 : startingPrice = 0
            except:
                startingPrice = self.getPrice(playerId)
            playerName = self.getName(id)
            teamId = self.getTeamIdFromUser(user)
            broadcastMessage = "User:" + user + " has put player:" + playerName + " for auction."
            self.tg.broadcast(broadcastMessage)            
            auctionQuery = "update playerStatus set forSale=?,lastModified=? where playerId=?"
            self.db.send(auctionQuery,[startingPrice,dt.now(),playerId])
            transactionQuery = "insert into transactions values (?,?,?,?,?,?)"
            self.db.send(transactionQuery,['Auction',id,startingPrice,teamId,0,dt.now()])
            self.prepareNewAuction(auctionCloseTime,playerName,startingPrice,playerId)
            self.db.commit()
        else: return "Invalid player id? Check auction syntax"

    def prepareNewAuction(self,auctionCloseTime,playerName,startingPrice,playerId):
        broadcastMessage= "Auction for:" + playerName + " has started\n"
        broadcastMessage+= "Starting bid: " + startingPrice.__str__() + "\n"
        auctionCloseTime = dt.now() + timedelta(days=2)
        broadcastMessage+= "Auction closes" + auctionCloseTime.__str__() + " EST"
        self.tg.broadcast(broadcastMessage)
        futuresQuery = "insert into futures (type,timestamp,info) values ('Auction',?,?)"
        self.db.send(futuresQuery,[auctionCloseTime,playerId])
 
        
    def processForcedSale(self,user,args):
        #verify ownership
        if self.isValidId(args) and self.verifyOwnership(user,args):
            id = args
            playerStatusQuery = "select status, forSale, teamPos from playerStatus where playerId=?"
            playerDetails = self.db.send(playerStatusQuery,[id])[0]
            status = playerDetails[0]
            forSale = playerDetails[1]
            teamPos = playerDetails[2]
            teamLastPos = self.getLastPos(user) 
            if forSale == -1:
                #close auction immediately
                pass
            #hack to ensure the force sale is last position
            self.processSwap(user, teamPos.__str__() + " " + teamLastPos.__str__())
            #move player to open market
            sellQuery = "update playerStatus set status='Open', lastModified=?,teamPos=-1 where playerId=?"
            self.db.send(sellQuery,[dt.now(),id])
            #transfer 70% to bank
            valueQuery = "select price,playerName from playerInfo where playerId=?"
            ret = self.db.send(valueQuery,[id])[0]
            value = ret[1]
            playerName = ret[0]
            newValue = 0.7 * value #todo: move to config file
            playerValueUpdateQuery = "update playerInfo set price=? where playerId=?"
            self.db.send(playerValueUpdateQuery,[newValue,id])
            teamId = self.getTeamIdFromUser(user)
            oldBank = self.getBankValue(teamId)
            newBank = oldBank + newValue
            bankUpdateQuery = "update humanPlayers set bank=? where teamId=?"
            self.db.send(bankUpdateQuery,[newBank,teamId])
            self.tg.broadcast("User: " + user + " just sold player: " + playerName + " to the market for: " + newValue.__str__())

            transactionQuery = "insert into transactions values (?,?,?,?,?,?)"
            self.db.send(transactionQuery,['ForceSell',id,newValue,teamId,1,dt.now()])
            self.db.commit()
            return "Done"
            

        
    def processSwap(self,user,args):
        try:
            pos1 = args.split(" ")[0]
            pos2 = args.split(" ")[1]
            posCheck = "select playerId from status=? and teamPos=?"
            pos1Exists = self.db.send(posCheck,[teamId,pos1])
            pos2Exists = self.db.send(posCheck,[teamId,pos2])
            if len(pos1Exists) and len(pos2Exists):
                pos1Id = pos1Exists[0][0]
                pos2Id = pos2Exists[0][0]
                swapQuery = "update playerStatus set teamPos=? where playerId=?"
                self.db.send(swapQuery,[pos2,pos1Id])
                self.db.send(swapQuery,[pos1,pos2Id])
                self.db.commit()
                return "Swapped position: " + pos1.__str__() + " with position:" + pos2.__str__()
            else:
                return "You do not have players in these positions. Check your team with /viewteam"
        except:
            return "Invalid positions, cannot swap"

    
    def processBan(self,user,args):
        currentUser = self.getUserById(self.order[self.currentPlayer])
        #validate user & stage
        if self.getCurrentStage() == 'ban' and user == currentUser:
            #is playerId valid?
            if self.isValidId(args):
                #cannot ban players not in auction
                if self.isNotBanned(args):
                    self.banId(user,args)
                    self.nextPlayer()
                    self.tg.broadcast("User:" + user + " banned " + self.getPlayerNameById(args))                
                    self.tg.broadcast(self.gameStage())
                    return "Done"
                else:
                    return args + " is already banned. Please retry"
            else:
                return "Invalid playerId"
        else:
            return "You cannot ban anyone at the moment. Check game stage"
    
    def processPick(self,user,args):
        currentUser = self.getUserById(self.order[self.currentPlayer])
        #validate user and stage
        if self.getCurrentStage() == 'pick' and user == currentUser:
            #is valid playerId?
            if self.isValidId(args):
                #can only pick directly from auction
                if self.isNotBanned(args):
                    self.pickId(user,args)
                    self.tg.broadcast("User:" + user + " picked " + self.getPlayerNameById(args))
                    self.nextPlayer()
                    self.tg.broadcast(self.gameStage())
                    return "Done"
                else: return args + " is banned or owned. Pick someone else."
            else: return "Invalid playerId"
        else: return "You cannot pick anyone at the moment. Check game stage"


    def getHelpText(self):
        helpText = "You can use the following commands:\n"
        helpText += "/help : display this page\n"
        helpText += "/stage : show current game stage\n"
        helpText += "/list [team] [category]: list all players from this team/category\n" #need to show status
        helpText += "/find <name>: get player ids by name\n" #need to show status
        helpText += "/player <id>: get player info\n"
        helpText += "/ban <id>: ban player from draft (draft stage only)\n"
        helpText += "/pick <id>: pick player from draft (draft stage only)\n"
        helpText += "/auction <id> [minimum bid]: place player for sale. minimum bid defaults to purchase price\n"
        helpText += "/bid <id> <amount> : place bid on player. bidding is blind auction and ends in 2 days."
        helpText += "/forcesell <id>: immediate sale for 70% price\n"
        helpText += "/viewteam: see your team. your top 11 will play\n"
        helpText += "/swap <pos1> <pos2>: swap players on bench with active 11\n"
        #helpText += "/viewmarket: see team owned players for sale\n"
        #helpText += "/deadline: view auction deadline and bids"
        return helpText

    def viewTeamQuery(self,user):
        teamId = self.getTeamIdFromUser(user)
        query = "select playerStatus.teamPos,playerStatus.playerId,playerInfo.playerName, playerInfo.team, playerInfo.price, playerInfo.skill1, playerInfo.overseas from playerStatus inner join playerInfo on playerStatus.playerId=playerInfo.playerId where status = ? order by playerStatus.teamPos"
        teamStr = "Team name: " + self.getTeamName(teamId) + "\n"
        teamStr += self.db.sendPretty(query,[teamId])
        teamStr += "\nBank Value:" + self.getBankValue(teamId).__str__()
        return teamStr

    def getBankValue(self,teamId):
        bankQuery = "select bank from humanPlayers where teamId=?"
        return self.db.send(bankQuery,[teamId])[0][0]

    def getTeamName(self,teamId):
        nameQuery = "select teamName from humanPlayers where teamId=?"
        return self.db.send(nameQuery,[teamId])[0][0]


    def getListQuery(self,args):
        argsList = args.split(" ")
        if len(argsList) > 2: return "Only 2 args allowed. Enter team name and/or skill"
        skill = ''
        team = ''
        for arg in argsList:
            if self.db.getSkill(arg) is not None:
                skill = arg 
            else:
                team = arg #may be a team?
            
        query = "select * from playerInfo where team like ? and (skill1 like ?)"
        return self.db.sendPretty(query,["%"+team+"%","%"+skill+"%"])

    def findPlayer(self,args):
        query = "select * from playerInfo where playerName like ?"
        return self.db.sendPretty(query,["%"+args.strip()+"%"])

    def getPlayerNameById(self,id):
        query = "select playerName from playerInfo where playerId=?"
        return self.db.send(query,[id])[0][0]

    def findPlayerById(self,args):
        query = "select playerInfo.playerId,playerInfo.team,playerInfo.playerName,playerInfo.price,playerInfo.skill1,playerInfo.overseas,playerStatus.status from playerInfo inner join playerStatus on playerInfo.playerId = playerStatus.playerId where playerInfo.playerId = ?"
        return self.db.sendPretty(query,[args.strip()])


def finalizeAuction(future):
    pass
def lockTeams(future):
    pass

def futureWorker(tg):
    db = dbInterface()
    while True:
        print 'monitoring future queue'
        checkFutureQuery = "select * from futures where timestamp <= datetime('now','localtime')"
        futures = db.send(checkFutureQuery,[])
        for future in futures:
            if future[0] == 'auction':
                message = finalizeAuction(future)
                tg.broadcast(message)
            elif future[1] == 'lock':
                message = lockTeams(future)
                tg.broadcast(message)
            else:
                pass
        sleep(120) #sleep 60 seconds?



if __name__=="__main__":
    game = draftGame()
    tg = interface(game)
    game.setTg(tg)

    t = Thread(target=futureWorker, args=(tg,))
#    t.start() #future workers, uncomment once deletion of future starts
    tg.start() #telegram worker
    
    tg.join()
    t.join()
