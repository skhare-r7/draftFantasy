import telegram
from telegram.ext import Updater
import logging
from draftGame import draftGame

class interface:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        myBotToken='184819989:AAHAXw47XxOQlYMQbe6TtFuSqdSVhCLKM70'
        self.telegramIds = {}
        self.telegramIds['draftFantasyGroup'] = -65624170
        self.telegramIds['Shreyas'] = 21851479
        self.telegramIds['Akshay'] = -1
        self.telegramIds['Yenan'] =89001170
        self.telegramIds['Sri'] = -1
        self.telegramIds['Ripu'] = -1
        self.telegramIds['Ali'] = -1


        self.updater = Updater(token=myBotToken)
        self.bot = telegram.Bot(token=myBotToken)
        dispatcher = self.updater.dispatcher
        dispatcher.addTelegramCommandHandler('help', self.help)
        dispatcher.addTelegramCommandHandler('list', self.list)

        self.game = draftGame()



    def sendMessage(self, to, message):
        self.bot.sendMessage(chat_id = self.telegramIds[to], text=message)


    def help(self,bot, update):
        self.processCommand('help',update)

    def list(self,bot, update):
        self.processCommand('list',update)

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



if __name__=='__main__':
    draft = interface()
    draft.start()
