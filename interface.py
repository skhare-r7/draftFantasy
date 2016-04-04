import telegram
from telegram.ext import Updater
import logging
#from draftGame import draftGame

class interface:
    def __init__(self,game):
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        myBotToken='184819989:AAHAXw47XxOQlYMQbe6TtFuSqdSVhCLKM70'
        self.telegramIds = {}
        self.telegramIds['draftFantasyGroup'] = -65624170
        self.telegramIds['Shreyas'] = 21851479
        self.telegramIds['Akshay'] = 74058426
        self.telegramIds['Yenan'] =89001170
        self.telegramIds['Sri'] = 58583921
        self.telegramIds['Ripu'] = -1
        self.telegramIds['Ali'] = 120943853


        self.updater = Updater(token=myBotToken)
        self.bot = telegram.Bot(token=myBotToken)
        dispatcher = self.updater.dispatcher
        dispatcher.addTelegramCommandHandler('help', self.help)
        dispatcher.addTelegramCommandHandler('stage', self.stage)
        dispatcher.addTelegramCommandHandler('list', self.list)
        dispatcher.addTelegramCommandHandler('find', self.find)
        dispatcher.addTelegramCommandHandler('player', self.player)
        dispatcher.addTelegramCommandHandler('ban', self.ban)
        dispatcher.addTelegramCommandHandler('pick', self.pick)
        dispatcher.addTelegramCommandHandler('viewteam', self.viewteam)
        
        dispatcher.addTelegramCommandHandler('setcap', self.setcap)
        dispatcher.addTelegramCommandHandler('swap', self.swap)
        dispatcher.addTelegramCommandHandler('start', self.startGame)

        dispatcher.addTelegramCommandHandler('auction', self.auction)
        dispatcher.addTelegramCommandHandler('forcesell', self.forcesell)
        dispatcher.addTelegramCommandHandler('viewmarket', self.viewmarket)
        dispatcher.addTelegramCommandHandler('deadline', self.deadline)


        self.game = game


    def broadcast(self, message):
        self.bot.sendMessage(chat_id = self.telegramIds['draftFantasyGroup'], text=message)

    def sendMessage(self, to, message):
        self.bot.sendMessage(chat_id = self.telegramIds[to], text=message)

    def help(self,bot,update):
        self.processCommand('help',update)
    
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

    def forcesell(self,bot,update):
        self.processCommand('forcesell',update)

    def viewteam(self,bot,update):
        self.processCommand('viewteam',update)

    def setcap(self,bot,update):
        self.processCommand('setcap',update)

    def swap(self,bot,update):
        self.processCommand('swap',update)

    def viewmarket(self,bot,update):
        self.processCommand('viewmarket',update)

    def deadline(self,bot,update):
        self.processCommand('deadline',update)

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
            self.bot.sendMessage(chat_id=update.message.chat_id, text=self.game.handleCommand(user, command, args))
        
    def get_user_from_id(self,id):
        for key,value in self.telegramIds.items():
            if value == id: return key
        print "ERROR: couldn't find user!"
        return None

                                 
                                 
    def start(self):
        self.updater.start_polling()



#if __name__=='__main__':
#    draft = interface()
#    draft.start()
