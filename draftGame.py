from database import dbInterface

class draftGame:
    def __init__(self):
        self.db = dbInterface()
    

    def handleCommand(self, user, command, args):
        if command == 'help':
            return self.getHelpText()
        elif command == 'list':
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
