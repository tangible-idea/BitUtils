# written in python 3.*
#-*- coding: utf-8 -*-
import telegram

bot = telegram.Bot(token='000000000:AAGjKiBi8bZzB4wL8wIWvQSDG5wmwlxmOnc')

chat_id = bot.getUpdates()[-1].message.chat.id

#bot.sendMessage(chat_id=chat_id, text='안녕! 난 주주봇이야')
