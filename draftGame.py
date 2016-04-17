from database import dbInterface
from random import shuffle
from interface import interface
from datetime import datetime as dt
from threading import Thread
from time import sleep
from datetime import timedelta
import json

class draftGame:
    def __init__(self):
        self.AUCTION_TIME_SECONDS = 8 * 60 * 60 #12 hours
        self.FORCED_SALE_RATIO = 0.7
    

        self.db = dbInterface()
        #game initialization
        self.tg = None
        self.rounds = []
        self.rounds.append(['ban'])
        self.rounds.append(['ban'])
        self.rounds.append(['ban'])
        self.rounds.append(['pick'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['pick_r'])
        self.currentPhase = 'Live' #we start at drafting

        self.currentRound = 0
        self.currentStage = 0 
        self.currentPlayer = 0

        self.currentActivity = self.rounds[self.currentRound][self.currentStage]
        self.numberOfPlayers = self.db.send("select count(*) from humanPlayers",[])[0][0]
        
        #TODO: DONT DO THIS -> causes things to break if players 1,2,3,4,5 are not available!!
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
            self.currentPhase = 'Live'
            self.moveAllPlayersToOpenMarket()
        if self.rounds[self.currentRound][self.currentStage][-2:] == '_r': self.order.reverse()


    def getCurrentStage(self):
        stage= self.rounds[self.currentRound][self.currentStage]
        if 'ban' in stage: return 'ban'
        elif 'pick' in stage: return 'pick'
        else: return 'none'

    def gameStage(self):
        toRet = "Current Phase:" + self.currentPhase + "\n"
        if self.currentPhase == 'Draft':
            toRet += "Current Round:" + self.currentRound.__str__() + " of " + len(self.rounds).__str__()+  "\n"
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
            self.currentPhase = 'Draft'
            tg.broadcast("Game is on! Good luck")
            tg.broadcast(game.gameStage())
            return "Done"

    def getCurdrentStage(self):
        if 'ban' in self.rounds[self.currentRound][self.currentStage]: return 'ban'
        elif 'pick' in self.rounds[self.currentRound][self.currentStage]: return 'pick'
        else: return None

    def isValidId(self,id):
        try:
            query = "select count(*) from playerStatus where playerId=?"
            return self.db.send(query,[id])[0][0] == 1
        except: return False

    def isNotBanned(self, id): #player is not banned or picked
        query = "select status from playerStatus where playerId=?"
        return self.db.send(query,[id])[0][0] == 'Draft'
    
    def banId(self,user, id):
        price = self.getPrice(id)
        query = "update playerStatus set status='Open',lastModified=?,startBid=? where playerId=?"
        self.db.send(query,[dt.now(),price,id])
        teamId = self.getTeamIdFromUser(user)
        transactionQuery = "insert into transactions values (?,?,?,?,?,?)"
        self.db.send(transactionQuery,["Ban",id,0,teamId,1,dt.now()])
        self.db.commit()

    def moveAllPlayersToOpenMarket(self):
        #sqlite join and update doesnt work!
        draftPlayerQuery = "select playerId from playerStatus where status='Draft'"
        response = self.db.send(draftPlayerQuery,[])
        for player in response:
            id = player[0]
            price = self.getPrice(id)
            updateQuery = "update playerStatus set status='Open',lastModified=?,teamPos=-1,startBid=? where playerId=?"
            self.db.send(updateQuery,[dt.now(),price,id])
        self.db.commit()
        
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
        query = "select teamId from humanPlayers where name like ?"
        try:
            return self.db.send(query,["%"+user+"%"])[0][0]
        except: return None

    def getUserById(self,id):
        query = "select name from humanPlayers where teamId=?"
        return self.db.send(query,[id])[0][0]

    def handleCommand(self, user, command, args):
        if command == 'help':
            return self.getHelpText()
        elif command == 'rules':
            return self.getRulesText()
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
            return self.viewTeamQuery(user,args)
        elif command == 'swap':
            return self.processSwap(user,args)
        elif command == 'viewmarket':
            return self.processViewMarket()
        elif command == 'viewbans':
            return self.processViewBans()
        elif command == 'viewbids':
            return self.processViewBids(user)
        elif command == 'cancelbid':
            return self.processCancelBid(user,args)
        elif command == 'unpicked':
            return self.processUnpicked(args)
        elif command == 'league':
            return self.processLeague()
        elif command == 'viewpoints':
            return self.processViewPoints(user,args)

        #hidden commands
        elif command == 'start':
            return self.startGame(user)
        else: pass
 
    def processCancelBid(self,user,args):
        if self.isValidId(args):
            deleteQuery = "delete from transactions where type = 'Bid' and humanId=? and complete=0 and playerId=?"
            self.db.send(deleteQuery,[self.getTeamIdFromUser(user),args])
            self.db.commit()
            return "Done"
        else:
            return "Invalid id"

    def processLeague(self):
        leagueQuery = "select name, totals.points from humanPlayers inner join (select teamId, sum(points) as points from draftPoints group by teamId) as totals on humanPlayers.teamId = totals.teamId order by points desc"
        return self.db.sendPretty(leagueQuery,[])

    def processViewPoints(self,user,args):
        teamId = None
        if args is None:
            teamId = self.getTeamIdFromUser(user)
        else:
            teamId = self.getTeamIdFromUser(args)
        if teamId is None: return 'Invalid query'
        ownerQuery = "select teamName, name from humanPlayers where teamId=?"
        ownerInfo = self.db.send(ownerQuery,[teamId])[0]
        toRet = "Team Name: " + ownerInfo[0] + "(" + ownerInfo[1]+")\n"
        toRet += self.db.sendPretty("select draftPoints.points, (select game from iplPoints where draftPoints.matchid = iplPoints.matchid) as game from draftPoints where teamId=?",[teamId])
        return toRet

    def processUnpicked(self,args):
        underVal = None
        if args is None:
            underVal = 9999 #todo: fix later
        else:
            try:
                underVal = float(args)
            except:
                pass
        if underVal is None: return 'Invalid query'
        unpickedQuery = "select playerInfo.playerName, playerInfo.team, playerInfo.skill1, playerInfo.price, (select sum(points) from iplpoints where iplpoints.playerId=playerInfo.playerId) as points from playerInfo inner join playerStatus on playerInfo.playerId = playerStatus.playerId where playerInfo.price <= ? and playerStatus.status = 'Open' order by points desc"
        return self.db.sendPretty(unpickedQuery,[underVal])
    
    def processViewBans(self):
        if self.currentPhase == 'Draft':
            toRet = "The following players have been banned:\n"
            banQuery = "select playerInfo.playerId, playerInfo.playerName from playerStatus inner join playerInfo on playerInfo.playerId = playerStatus.playerId where status='Open'"
            toRet += self.db.sendPretty(banQuery,[])
            return toRet
        else: return "Game is live, no players are banned"

    def processViewMarket(self):
        viewMarketQuery = "select info, playerInfo.playerName, playerStatus.startBid, deadline from futures inner join playerInfo on futures.info = playerInfo.playerId inner join playerStatus on playerStatus.playerId = futures.info where type='Auction' order by deadline"
        return self.db.sendPretty(viewMarketQuery,[])


    def playerAvailableForBid(self,playerId):
        bidQuery = "select startBid from playerStatus where playerId=?"
        return self.db.send(bidQuery,[playerId])[0][0] != -1

    def existingAuction(self,playerId):
        existingQuery = "select count(*) from futures where type='Auction' and info=?"
        return self.db.send(existingQuery,[playerId])[0][0]==1

    def userCanBid(self,teamId):
        numPlayersQuery = "select count(*) from playerStatus where status=?"
        numPlayers = self.db.send(numPlayersQuery,[teamId])[0][0]
        activeBidsQuery = "select count(distinct playerId) from transactions where type='Bid' and humanId=? and complete=0"
        activeBids = self.db.send(activeBidsQuery,[teamId])[0][0]
        return numPlayers + activeBids <= 15 #check if # of players + active bids <= 15

    def processBid(self,user,args):
        playerId = args.split(' ')[0]
        teamId = self.getTeamIdFromUser(user)
        bid = None
        if self.isValidId(playerId) and self.playerAvailableForBid(playerId) and self.userCanBid(teamId):
            try:
                bid = float(args.split(' ')[1])
                #some moron will try to do this
                if bid < 0 : bid = None
            except:
                return "Invalid bid"
            if bid is None: 
                return "Invalid bid. Check bidding syntax"
            if not self.existingAuction(playerId):
                playerName = self.getName(playerId)
                startingPrice = self.getPrice(playerId)
                self.prepareNewAuction(playerName,startingPrice,playerId)
            #place bid
            bidQuery = "insert into transactions values ('Bid',?,?,?,?,?)"
            self.db.send(bidQuery,[playerId,bid,teamId,0,dt.now()])
            self.db.commit()
            self.tg.broadcast("User:"+user+" placed bid on player:"+self.getName(playerId))
            return "Done"
        else: return "Unable to bid" 


    def verifyOwnership(self,user,id):
        teamId = self.getTeamIdFromUser(user)
        verifyQuery = "select count(*) from playerStatus where playerId=? and status=?"
        return self.db.send(verifyQuery,[id,teamId])[0][0] == 1

    def getLastPos(self,teamId):
        try:
            self.db.send("select teamPos from playerStatus where status=? order by teamPos desc limit 1",[teamId])[0][0]
        except:
            return 0

    def getTeamPos(self,playerId):
        return self.db.send("select teamPos from playerStatus where playerId=?",[playerId])[0][0]

    def getPrice(self,id):
        valueQuery = "select price from playerInfo where playerId =?"
        return self.db.send(valueQuery,[id])[0][0]

    def getName(self,id):
        valueQuery = "select playerName from playerInfo where playerId =?"
        return self.db.send(valueQuery,[id])[0][0]

    def isNotAuctioned(self,id):
        aucQuery = "select count(*) from transactions where complete=0 and type='Auction' and playerId=?"
        return self.db.send(aucQuery,[id])[0][0] == 0

    def processAuction(self,user,args):
        playerId = args.split(' ')[0]
        startingPrice = None
        if self.isValidId(playerId) and self.verifyOwnership(user,playerId) and self.isNotAuctioned(playerId):
            try:
                startingPrice = float(args.split(' ')[1])
                #some moron will try to do this
                if startingPrice < 0 : startingPrice = 0
            except:
                startingPrice = self.getPrice(playerId)
            playerName = self.getName(playerId)
            teamId = self.getTeamIdFromUser(user)
            broadcastMessage = "User:" + user + " has put player:" + playerName + " for auction."
            self.tg.broadcast(broadcastMessage)            
            auctionQuery = "update playerStatus set startBid=?,lastModified=? where playerId=?"
            self.db.send(auctionQuery,[startingPrice,dt.now(),playerId])
            transactionQuery = "insert into transactions values (?,?,?,?,?,?)"
            self.db.send(transactionQuery,['Auction',playerId,startingPrice,teamId,0,dt.now()])
            self.prepareNewAuction(playerName,startingPrice,playerId)
            self.db.commit()
            return "Done"
        else: return "Invalid player id? Check auction syntax"

    def prepareNewAuction(self,playerName,startingPrice,playerId):
        broadcastMessage= "Auction for: " + playerName + " has started\n"
        broadcastMessage+= "Starting bid: " + startingPrice.__str__() + "\n"
        auctionCloseTime = dt.now() + timedelta(seconds=self.AUCTION_TIME_SECONDS) 
        broadcastMessage+= "Auction closes: " + auctionCloseTime.__str__() + " EST"
        self.tg.broadcast(broadcastMessage)
        futuresQuery = "insert into futures (type,deadline,info) values ('Auction',?,?)"
        self.db.send(futuresQuery,[auctionCloseTime,playerId])
        self.db.commit()
        return "Done"
 
        
    def closeAuction(self,id):
        closeQuery = "delete from futures where info=?"
        self.db.send(closeQuery,[id])
        transactionsQuery = "update transactions set complete=1 where playerId=? and (type='Auction' or type='Bid')"
        self.db.send(transactionsQuery,[id])
        self.db.commit()

    def processForcedSale(self,user,args):
        #verify ownership
        if self.isValidId(args) and self.verifyOwnership(user,args):
            id = args
            playerStatusQuery = "select status, startBid, teamPos from playerStatus where playerId=?"
            playerDetails = self.db.send(playerStatusQuery,[id])[0]
            status = playerDetails[0]
            startBid = playerDetails[1]
            teamPos = playerDetails[2]
            teamId = self.getTeamIdFromUser(user)
            teamLastPos = self.getLastPos(teamId) 
            #hack to ensure the force sale is last position
            self.processSwap(user, teamPos.__str__() + " " + teamLastPos.__str__())
            #transfer 70% to bank
            valueQuery = "select price,playerName from playerInfo where playerId=?"
            ret = self.db.send(valueQuery,[id])[0]
            value = ret[0]
            playerName = ret[1]
            if startBid != -1:
                tg.broadcast("Auction on player:"+playerName+ " is closed due to forced sale")
                #close auction immediately (delete from futures)
                self.closeAuction(id)
            newValue = self.FORCED_SALE_RATIO * value #todo: move to config file
            #move player to open market
            sellQuery = "update playerStatus set status='Open', startBid=?,lastModified=?,teamPos=-1 where playerId=?"
            self.db.send(sellQuery,[newValue,dt.now(),id])

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
            teamId = self.getTeamIdFromUser(user)
            posCheck = "select playerId from playerStatus where status=? and teamPos=?"
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


    def getRulesText(self):
        rulesText = "Game consists of 2 stages: Draft and Live\n"
        rulesText += "In the draft stage, there will be 3 rounds of bans follwed by 6 rounds of picks.\n"
        rulesText += "Manager order for draft is decided randomly\n"
        rulesText += "During picks, order is reversed every round, so last pick for one round gets first pick in the next\n"
        rulesText += "You cannot pick a player who is banned / pick by someone else\n"
        rulesText += "Each manager stars with 100.0 in the bank. Each pick counts towards that limit\n"
        rulesText += "Once 9 rounds are complete, game becomes Live\n"
        rulesText += "In a live game, you can bid on any player in the open market.\n"
        rulesText += "These include all players unpicked during draft PLUS banned players from the draft\n"
        rulesText += "The minimum bid for these players is their default value\n"
        rulesText += "Auctions bids are blind, but bid actions be broadcasted in the group\n"
        rulesText += "Auctions close in 12(?) hours. Highest bid will be awarded player\n"
        rulesText += "At any point, managers may choose to auction a player from their team or force sell him for 70% value\n"
        rulesText += "Managers decide the starting bid for the player auction\n"
        rulesText += "==========================\n"
        rulesText += "Scoring will be done using the rules from IPL fantasy\n"
        rulesText += "Teams are frozen at every match deadline, and top 11 players will score points\n"
        rulesText += "Managers will receive NO points for a match unless two conditions are met at every match deadline\n"
        rulesText += "1. Bank value cannot be negative\n"
        rulesText += "2. Must have atleast 11 players, including 4 bat, 1 wk, 2 bowl, 1 AR (max 5 intl)\n"
        rulesText += "Good luck and have fun!"
        return rulesText

    def getHelpText(self):
        helpText = "You can use the following commands:\n"
        helpText += "/help : display this page\n"
        helpText += "/rules : show game rules\n"
        helpText += "/stage : show current game stage\n"
        helpText += "/list [team] [category]: list all players from this team/category\n" #need to show status
        helpText += "/find <name>: get player ids by name\n" #need to show status
        helpText += "/player <id>: get player info\n"
        helpText += "/ban <id>: ban player from Draft (Draft stage only)\n"
        helpText += "/pick <id>: pick player from Draft (Draft stage only)\n"
        helpText += "/viewteam [user]: see your team. your top 11 will play\n"
        helpText += "/swap <pos1> <pos2>: swap players on bench with active 11\n"
        helpText += "/auction <id> [minimum bid]: place player for sale. minimum bid defaults to purchase price\n"
        helpText += "/bid <id> <amount> : place bid on player. bidding is blind auction and ends in 2 days.\n"
        helpText += "/forcesell <id>: immediate sale for 70% price\n"
        helpText += "/viewmarket: view auction players and deadlines\n"
        helpText += "/viewbans: view banned players (Draft stage only)\n"
        helpText += "/viewbids: see your active bids\n"
        helpText += "/cancelbid <id> : cancel all bids on player\n"
        helpText += "/unpicked [max price] : view top unpicked players. optional max price\n"
        helpText += "/league : view current draft league\n"
        helpText += "/viewpoints [user]: view points\n"
        helpText += "Anything I missed? Suggest more commands!"
        return helpText

    def viewTeamQuery(self,user,args):
        teamId = None
        if args is None:
            teamId = self.getTeamIdFromUser(user)
        else:
            teamId = self.getTeamIdFromUser(args)
        if teamId is None: return 'Invalid query'
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


    def processViewBids(self,user):
        viewQuery = "select transactions.playerId,transactions.value,playerInfo.playerName from transactions inner join playerInfo on playerInfo.playerId = transactions.playerId where humanId=? and complete=0"
        return self.db.sendPretty(viewQuery,[self.getTeamIdFromUser(user)])

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
            
        query = "select *,(select sum(points) from iplpoints where iplPoints.playerId=playerInfo.playerId) as points from playerInfo where team like ? and (skill1 like ?) order by points desc"
        return self.db.sendPretty(query,["%"+team+"%","%"+skill+"%"])

    def findPlayer(self,args):
        query = "select * from playerInfo where playerName like ?"
        return self.db.sendPretty(query,["%"+args.strip()+"%"])

    def getPlayerNameById(self,id):
        query = "select playerName from playerInfo where playerId=?"
        return self.db.send(query,[id])[0][0]

    def findPlayerById(self,args):
        if self.isValidId(args):
            query = "select * from playerInfo where playerInfo.playerId = ?"
            toRet = self.db.sendPretty(query,[args.strip()])
            ownerId = self.getOwnerId(args)
            if ownerId == 'Open':
                toRet += "\nCurrently available"
            elif ownerId == 'Draft':
                toRet += "\nIn draft"
            else: #owned by some team
                ownerQuery = "select teamName, name from humanPlayers where teamId=?"
                ownerInfo = self.db.send(ownerQuery,[ownerId])[0]
                toRet += "\nCurrently owned by " + ownerInfo[0] + "(" + ownerInfo[1]+")"
            return toRet
        else: return "Invalid player Id"


    def getOwnerId(self,id):
        if self.isValidId(id):
            ownerQuery = "select status from playerStatus where playerId=?"
            ret = self.db.send(ownerQuery,[id])[0][0]
            if ret != 'Open': return ret #this is what happens when we overload status
        return None

    def getNameFromTeamId(self,teamId):
        nameQuery = "select name from humanPlayers where teamId=?"
        return self.db.send(nameQuery,[teamId])[0][0]

    def isValidOwner(self,id):
        if id is None: return False
        query = "select count(*) from humanPlayers where teamId=?"
        try:
            return self.db.send(query,[id])[0][0] == 1
        except:
            return False


def finalizeAuction(future,game):
    futureId = future[0]
    id = future[3]
    bidsQuery = "select value, humanId from transactions where playerId=? and complete=0 and type='Bid' order by value desc limit 1"
    try:
        highestBid = game.db.send(bidsQuery,[id])[0]
    except: highestBid = [-1, '0'] #todo fix this!
    value = highestBid[0]
    newOwner = highestBid[1]
    startingBidQuery = "select startBid from playerStatus where playerId=?"
    startingBid = game.db.send(startingBidQuery,[id])[0][0]
    message = ""
    completeQuery = "update transactions set complete=1 where playerId=?"
    game.db.send(completeQuery,[id])
    #todo: remove above 2 lines since close auction should deal with this
    if value >= startingBid:
        message= "Congratulations. User:"+game.getUserById(newOwner)+" has won the bid on player:" + game.getPlayerNameById(id) +"\n"
        message+= "Winning bid:"+value.__str__()
        #transfer ownership
        #transfer money
        oldOwner = game.getOwnerId(id)
        if game.isValidOwner(oldOwner):
            oldOwnerBank = game.getBankValue(oldOwner) + value
            BankUpdate = "update humanPlayers set bank=? where teamId=?"
            game.db.send(BankUpdate,[oldOwnerBank,oldOwner])
            #getting rid of player, put him in last position!
            oldLastPos = game.getLastPos(oldOwner)
            oldTeamPos = game.getTeamPos(id)
            game.processSwap(game.getNameFromTeamId(oldOwner),oldLastPos.__str__() + " " + oldTeamPos.__str__())

        newOwnerBank = game.getBankValue(newOwner) - value
        newOwnerBankUpdate = "update humanPlayers set bank=? where teamId=?"
        game.db.send(newOwnerBankUpdate,[newOwnerBank,newOwner])
        lastPos = game.getLastPos(newOwner) + 1
        playerTransferQuery = "update playerStatus set status=?,startBid=-1,teamPos=? where playerId=?"
        game.db.send(playerTransferQuery,[newOwner,lastPos,id])
        updatePrice = "update playerInfo set price=? where playerId=?"
	game.db.send(updatePrice,[value,id])
    else:
        message = "Closing auction on player:" + game.getPlayerNameById(id) + "\n"
        message += "No bids received were higher than starting bid"
    game.closeAuction(id) #is this method broken?!
    deleteFutureQuery = "delete from futures where id=?"
    game.db.send(deleteFutureQuery,[futureId])
    game.db.commit()
    return message


def lockTeams(future,game):
    futureId = future[0]
    futureInfo = future[3]
    teamIdQuery = "select teamId from humanPlayers"
    teamIds = game.db.send(teamIdQuery,[])
    for teamTuple in teamIds:
        teamId = teamTuple[0]
        playerInfo = {}
        overseasPlayers = 0
        lockInfo = {}
        lockInfo['bank'] = game.getBankValue(teamId) #bank value
        lockInfo['teamId'] = teamId #teamId
        lockInfo['players'] = playerInfo #this is a playerInfo dictionary
        #key is skill, value is playerid
        lockInfo['info'] = futureInfo
        playerInfo['Wicketkeeper'] = []
        playerInfo['Batsman'] = []
        playerInfo['Allrounder'] = []
        playerInfo['Bowler'] = []
        
        #save json file for each player
        getTeams = "select playerStatus.playerId, playerInfo.skill1, playerInfo.overseas from playerStatus inner join playerInfo on playerStatus.playerId = playerInfo.playerId where playerStatus.status=? order by playerStatus.teamPos limit 11"
        players = game.db.send(getTeams,[teamId])
        for player in players:
            id = player[0]
            skill = player[1]
            overseas = player[2]
            if overseas: overseasPlayers += 1
            playerInfo[skill].append(id)
        lockInfo['overseasTotal'] = overseasPlayers
        with open("lockedTeams/match"+futureInfo.__str__() + "_team" + teamId.__str__() + ".json","w") as outfile:
            json.dump(lockInfo, outfile)
    deleteFutureQuery = "delete from futures where id=?"
    game.db.send(deleteFutureQuery,[futureId])
    game.db.commit()
    return "Teams are locked for match. ID:" + futureInfo.__str__() #todo: get actual match name



def futureWorker(tg,game):
    db = dbInterface()
    while True:
        print 'monitoring future queue'
        checkFutureQuery = "select * from futures where deadline <= datetime('now','localtime')"
        futures = db.send(checkFutureQuery,[])
        for future in futures:
            if future[1] == 'Auction':
                message = finalizeAuction(future,game)
                tg.broadcast(message)
            elif future[1] == 'Lock':
                message = lockTeams(future,game)
                tg.broadcast(message)
            else:
                pass
        sleep(60) #sleep 60 seconds?



if __name__=="__main__":
    game = draftGame()
    tg = interface(game)
    game.setTg(tg)

    t = Thread(target=futureWorker, args=(tg,game,))
    t.start() #future workers, uncomment once deletion of future starts
    tg.start() #telegram worker

    t.join()

#todos: 
#1. viewmarket
#2. fix viewteam
#3. view ownership when viewing player
