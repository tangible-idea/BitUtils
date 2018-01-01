# written in python 3.*
#-*- coding: utf-8 -*-
import telegram
import Config

TELE_BOT = telegram.Bot(token=Config.TELEGRAM_CLIENT_TOKEN)

TELE_CHAT_ID = TELE_BOT.getUpdates()[-1].message.chat.id

def sendTelegramMsg(msg):
    TELE_BOT.sendMessage(chat_id=TELE_CHAT_ID, text= msg)