import telegram
from telegram.ext import Updater
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


myBotToken='184819989:AAHAXw47XxOQlYMQbe6TtFuSqdSVhCLKM70'
draftFantasyGroupId = '-65624170'


updater = Updater(token=myBotToken)
bot = telegram.Bot(token=myBotToken)

dispatcher = updater.dispatcher


def help(bot, update):
    if update.message.chat.type == 'group':
        bot.sendMessage(chat_id=update.message.chat_id, text="Please ask privately!")
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="This is the help page")


dispatcher.addTelegramCommandHandler('help', help)


def say(bot, update):
    if update.message.chat.type == 'group':
        pass
    else:
        user = update.message.from_user.first_name
        text = update.message.text.split(' ',1)[1]
        bot.sendMessage(chat_id=draftFantasyGroupId, text= user + " said " + text)

dispatcher.addTelegramCommandHandler('say', say)

updater.start_polling()
