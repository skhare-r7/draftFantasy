import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging
#from draftGame import draftGame

class interface:
    def __init__(self,game):
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        myBotToken='309142165:AAFE5_m9RqUvxQ2FESo9BxD8vQFbFvgCnOU'
        self.telegramIds = {}
        self.telegramIds['draftFantasyGroup'] = -197047422
        self.telegramIds['Shreyas'] = 21851479
        self.telegramIds['Akshay'] = 74058426
        self.telegramIds['Yenan'] =89001170
        self.telegramIds['Sri'] = 58583921
        self.telegramIds['Ripu'] = 76484915
        self.telegramIds['Shrikar'] = 183002377
        self.telegramIds['Ali'] = 120943853
        self.telegramIds['Kanav'] = 213318720
        self.telegramIds['Aniket'] = 212593489
        self.telegramIds['Farhan'] = 370194752

        self.updater = Updater(token=myBotToken)
        self.bot = telegram.Bot(token=myBotToken)
        dispatcher = self.updater.dispatcher
        dispatcher.addHandler(CommandHandler('help', self.help))
        dispatcher.addHandler(CommandHandler('rules', self.rules))
        dispatcher.addHandler(CommandHandler('stage', self.stage))
        dispatcher.addHandler(CommandHandler('list', self.list))
        dispatcher.addHandler(CommandHandler('find', self.find))
        dispatcher.addHandler(CommandHandler('player', self.player))
        dispatcher.addHandler(CommandHandler('ban', self.ban))
        dispatcher.addHandler(CommandHandler('pick', self.pick))
        dispatcher.addHandler(CommandHandler('viewteam', self.viewteam))
        dispatcher.addHandler(CommandHandler('swap', self.swap))
        dispatcher.addHandler(CommandHandler('start', self.startGame))
        dispatcher.addHandler(CommandHandler('auction', self.auction))
        dispatcher.addHandler(CommandHandler('bid', self.bid))
        dispatcher.addHandler(CommandHandler('forcesell', self.forcesell))
        dispatcher.addHandler(CommandHandler('viewmarket', self.viewmarket))
        dispatcher.addHandler(CommandHandler('viewbans', self.viewbans))
        dispatcher.addHandler(CommandHandler('viewbids', self.viewbids))
        dispatcher.addHandler(CommandHandler('cancelbid', self.cancelbid))
        dispatcher.addHandler(CommandHandler('unpicked', self.unpicked))
        dispatcher.addHandler(CommandHandler('league', self.league))
        dispatcher.addHandler(CommandHandler('viewpoints', self.viewpoints))

        self.game = game


    def broadcast(self, message):
        self.bot.sendMessage(chat_id = self.telegramIds['draftFantasyGroup'], text=message)

    def sendMessage(self, to, message):
        self.bot.sendMessage(chat_id = self.telegramIds[to], text=message)

    def help(self,bot,update):
        self.processCommand('help',update)

    def rules(self,bot,update):
        self.processCommand('rules',update)
    
    def stage(self,bot,update):
        self.processCommand('stage',update)

    def list(self,bot,update):
        self.processCommand('list',update)

    def find(self,bot,update):
        self.processCommand('find',update)

    def player(self,bot,update):
        self.processCommand('player',update)

    def ban(self,bot,update):
        self.processCommand('ban',update)

    def pick(self,bot,update):
        self.processCommand('pick',update)

    def auction(self,bot,update):
        self.processCommand('auction',update)

    def bid(self,bot,update):
        self.processCommand('bid',update)

    def forcesell(self,bot,update):
        self.processCommand('forcesell',update)

    def viewteam(self,bot,update):
        self.processCommand('viewteam',update)

    def swap(self,bot,update):
        self.processCommand('swap',update)

    def viewmarket(self,bot,update):
        self.processCommand('viewmarket',update)

    def unpicked(self,bot,update):
        self.processCommand('unpicked',update)

    def league(self,bot,update):
        self.processCommand('league',update)

    def viewpoints(self,bot,update):
        self.processCommand('viewpoints',update)

    def viewbans(self,bot,update):
        self.processCommand('viewbans',update)

    def viewbids(self,bot,update):
        self.processCommand('viewbids',update)

    def cancelbid(self,bot,update):
        self.processCommand('cancelbid',update)

    def startGame(self,bot,update):
        self.processCommand('start',update)


    def processCommand(self,command, update):
        if update.message.chat.type == 'group':
            self.bot.sendMessage(chat_id=update.message.chat_id, text="Please ask privately!")
        else:
            args = None
            try:
                args = update.message.text.split(' ',1)[1]
            except:
                pass
            user = self.get_user_from_id(update.message.chat_id)
            if user is None: user = update.message.chat_id
            self.bot.sendMessage(chat_id=update.message.chat_id, text=self.game.handleCommand(user, command, args))
        
    def get_user_from_id(self,id):
        for key,value in self.telegramIds.items():
            if value == id: return key
        print "ERROR: couldn't find user!"
        return None

                                 
                                 
    def start(self):
        self.updater.start_polling()
