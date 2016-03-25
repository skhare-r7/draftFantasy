from database import dbInterface
from random import shuffle


class draftGame:
    def __init__(self):
        self.db = dbInterface()
        #game initialization
        self.rounds = []
        self.rounds.append(['ban', 'ban', 'pick'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['ban_r', 'ban', 'pick'])
        self.rounds.append(['pick_r'])
        self.rounds.append(['ban_r', 'pick'])
        self.rounds.append(['pick_r'])
        
        self.currentPhase = 'draft' #we start at drafting

        self.currentRound = 0
        self.currentStage = 0 
        self.currentPlayer = 0

        self.currentActivity = self.rounds[self.currentRound][self.currentStage]
        numberOfPlayers = 5 #TODO
        self.order = [i for i in range(0,numberOfPlayers)]
        shuffle(self.order)
        


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


    def nextPlayer(self):
        print self.currentPhase + ":" + self.currentRound.__str__() + ":" + self.rounds[self.currentRound][self.currentStage] + ":" + self.order[self.currentPlayer].__str__()
        self.currentPlayer += 1
        if self.currentPlayer > len(self.order)-1: 
            self.nextStage()
            self.currentPlayer = 0


    def handleCommand(self, user, command, args):
        if command == 'help':
            return self.getHelpText()
        elif command == 'list':
            return self.getListQuery(args)
        elif command == 'ban':
            #validate user & stage
            #process request
            #move to next player
            pass
        elif command == 'pick':
            #validate user & stage
            #process request
            #move to next player
            pass
        elif command == 'auction':
            #validate stage
            #process request
            pass
        elif command == 'forcesell':
            #validate stage
            #process request
            pass
        elif command == 'setcap':
            #validate stage
            #process request
            pass
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
 
    def getHelpText(self):
        helpText = "You can use the following commands:\n"
        helpText += "/help : display this page\n"
        helpText += "/list [team] [category]: list all players from this team/category\n"
        #helpText += "/find <name>: get player ids by name\n"
        #helpText += "/playerInfo <id>: get player info\n"
        #helpText += "/ban <id>: ban player from draft (draft stage only)\n"
        #helpText += "/pick <id>: pick player from draft (draft stage only)\n"
        #helpText += "/auction <id> [minimum bid]: place player for sale. minimum bid defaults to purchase price\n"
        #helpText += "/forcesell <id>: immediate sale for 75% price\n"
        #helpText += "/viewteam: see your team. your top 11 will play\n"
        #helpText += "/setcap <id>: set your captain. default player at position 1 is captain\n"
        #helpText += "/swap <pos1> <pos2>: swap players on bench with active 11\n"
        #helpText += "/viewmarket: see team owned players for sale\n"
        #helpText += "/deadline: view auction deadline and bids"
 
        return helpText

    def getListQuery(self,args):
        arg = args.split(" ")[0]
        query = "SELECT * FROM playerInfo WHERE team like ?"
#        self.db.simpleQuery(query)
        return self.db.sendPretty(query,["%"+arg+"%"])


if __name__=="__main__":
    game = draftGame()
    while(game.currentPhase != 'game_on'):
        game.nextPlayer()
