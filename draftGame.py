from database import dbInterface
from random import shuffle
from interface import interface
from datetime import datetime as dt

class draftGame:
    def __init__(self):
        self.db = dbInterface()
        #game initialization
        self.tg = None
        self.rounds = []
        self.rounds.append(['ban', 'ban', 'pick'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['ban_r', 'ban', 'pick'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['ban_r', 'pick'])
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

        if self.rounds[self.currentRound][self.currentStage][-2:] == '_r': self.order.reverse()


    def gameStage(self):
        toRet = "Current Phase:" + self.currentPhase + "\n"
        if self.currentPhase == 'draft':
            toRet += "Current Round:" + self.currentRound.__str__() + "\n"
            toRet += "Current Stage:" + self.rounds[self.currentRound][self.currentStage] + "\n"
            toRet += "Current Player:" + self.getUserById(self.order[self.currentPlayer])
        return toRet

    def nextPlayer(self):
        #print self.currentPhase + ":" + self.currentRound.__str__() + ":" + self.rounds[self.currentRound][self.currentStage] + ":" + self.order[self.currentPlayer].__str__()
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


    def getCurrentStage(self):
        if 'ban' in self.rounds[self.currentRound][self.currentStage]: return 'ban'
        elif 'pick' in self.rounds[self.currentRound][self.currentStage]: return 'pick'
        else: return None

    def isValidId(self,id):
        query = "select count(*) from playerStatus where playerId=?"
        return self.db.send(query,[id])[0][0] == 1

    def isNotBanned(self, id): #player is not banned or picked
        query = "select status from playerStatus where playerId=?"
        return self.db.send(query,[id])[0][0] == 'Auction'
    
    def banId(self,user, id):
        query = "update playerStatus set status='Open',lastModified=? where playerId=?"
        self.db.send(query,[dt.now(),id])
        teamId = self.getTeamIdFromUser(user)
        transactionQuery = "insert into transactions values (?,?,?,?,?,?)"
        self.db.send(transactionQuery,["Ban",id,0,teamId,1,dt.now()])
        self.db.commit()
        
    def pickId(self,user, id):
        teamId = self.getTeamIdFromUser(user)
        playersQuery = "select count(*) from playerStatus where status=?"
        valueQuery = "select price from playerInfo where playerId =?"
        value = self.db.send(valueQuery,[id])[0][0]
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
            return self.processBan(user)
        elif command == 'pick':
            return self.processPick(user)
        elif command == 'auction':
            #validate stage
            #process request
            pass
        elif command == 'forcesell':
            #validate stage
            #process request
            pass
        elif command == 'viewteam':
            return self.viewTeamQuery(user)
        elif command == 'swap':
            #validate stage
            #process 
            pass
        elif command == 'viewmarket':
            #process
            pass
        elif command == 'deadline':
            #??
            pass
        elif command == 'start':
            return self.startGame(user)
 
    def processBan(self,user):
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
    
    def processPick(self,user):
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
                else:
                    return args + " is banned. Pick someone else."
            else:
                return "Invalid playerId"
            else:
                return "You cannot pick anyone at the moment. Check game stage"


    def getHelpText(self):
        helpText = "You can use the following commands:\n"
        helpText += "/help : display this page\n"
        helpText += "/stage : show current game stage\n"
        helpText += "/list [team] [category]: list all players from this team/category\n" #need to show status
        helpText += "/find <name>: get player ids by name\n" #need to show status
        helpText += "/player <id>: get player info\n"
        helpText += "/ban <id>: ban player from draft (draft stage only)\n"
        helpText += "/pick <id>: pick player from draft (draft stage only)\n"
        #helpText += "/auction <id> [minimum bid]: place player for sale. minimum bid defaults to purchase price\n"
        #helpText += "/forcesell <id>: immediate sale for 75% price\n"
        helpText += "/viewteam: see your team. your top 11 will play\n"
        #helpText += "/setcap <id>: set your captain. default player at position 1 is captain\n"
        #helpText += "/swap <pos1> <pos2>: swap players on bench with active 11\n"
        #helpText += "/viewmarket: see team owned players for sale\n"
        #helpText += "/deadline: view auction deadline and bids"
        #TODOs: rabbitMq for snapshot, auction resolution and spoilage
 
        return helpText

    def viewTeamQuery(self,user):
        teamId = self.getTeamIdFromUser(user)
        query = "select playerStatus.teamPos,playerStatus.playerId,playerInfo.playerName, playerInfo.team, playerInfo.price, playerInfo.skill1, playerInfo.skill2 from playerStatus inner join playerInfo on playerStatus.playerId=playerInfo.playerId where status = ? order by playerStatus.teamPos"
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
            
        query = "select * from playerInfo where team like ? and (skill1 like ? or skill2 like ?)"
        return self.db.sendPretty(query,["%"+team+"%","%"+skill+"%","%"+skill+"%"])

    def findPlayer(self,args):
        query = "select * from playerInfo where playerName like ?"
        return self.db.sendPretty(query,["%"+args.strip()+"%"])

    def getPlayerNameById(self,id):
        query = "select playerName from playerInfo where playerId=?"
        return self.db.send(query,[id])[0][0]

    def findPlayerById(self,args):
        query = "select playerInfo.playerId,playerInfo.team,playerInfo.playerName,playerInfo.price,playerInfo.skill1,playerInfo.skill2,playerStatus.status from playerInfo inner join playerStatus on playerInfo.playerId = playerStatus.playerId where playerInfo.playerId = ?"
        return self.db.sendPretty(query,[args.strip()])


if __name__=="__main__":
    game = draftGame()
    tg = interface(game)
    game.setTg(tg)

    while(game.currentPhase != 'game_on'):
        tg.start()
