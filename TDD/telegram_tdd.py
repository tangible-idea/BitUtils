# written in python 3.*
#-*- coding: utf-8 -*-
import telegram
import Config
bot = telegram.Bot(token=Config.TELEGRAM_CLIENT_TOKEN)

chat_id = bot.getUpdates()[-1].message.chat.id

#bot.sendMessage(chat_id=chat_id, text='안녕! 난 주주봇이야')
