#written in python 3.x
from time import sleep
import re

# pip install telethon
from telethon.utils import get_display_name
from telethon import TelegramClient

from threading import Timer

# pip install python-telegram-bot
from TDD import telegram_tdd

#pip install git+https://github.com/ericsomdahl/python-bittrex.git
from API import bittrex_api

import Config

## source code begin --
# MODE enumeration : TRACKING(0), TRADING(1)
E_MODE = 0
PURCHARSED_COIN_NAME = ""

# pip install python-telegram-bot
# please refer to https://my.telegram.org
client = TelegramClient(Config.PHONE_NUMBER, Config.TELEGRAM_BOT_API_ID, Config.TELEGRAM_BOT_API_HASH)
client.session.report_errors = False
client.connect()

if not client.is_user_authorized():
    client.send_code_request(Config.PHONE_NUMBER)
    client.sign_in(Config.PHONE_NUMBER, input('Enter the code: '))


def ReadPublicChannelChatHistory(messages):
    texts= []
    for msg in reversed(messages):
        Forwarded = None
        if msg.fwd_from is None:
            Forwarded = "(direct)"
        else: # vip leading room : 1363396782, VIP intel room : 1394171509
            Forwarded = "(forwarded_from: " + str(msg.fwd_from.channel_id) + ") "

        if getattr(messages, 'media', None):
            content = '<{}> {}'.format(messages.media.__class__.__name__, getattr(messages.media, 'caption', ''))
        elif hasattr(msg, 'message'):
            content = msg.message
        elif hasattr(msg, 'action'):
            content = str(msg.action)
        else:
            content = msg.__class__.__name__

        text = '[{}:{}] (ID={}) {}:{}'.format(msg.date.hour, msg.date.minute, msg.id, Forwarded, content)
        
        # ignore forwared messages
        if Forwarded != None and "(direct)" in Forwarded:
            texts.append(text)
    return texts

def TrackingTargetChannel(URL, count):
    target_channel  = client.get_entity(URL)
    total_count, messages, senders = client.get_message_history(target_channel, count)
    texts= ReadPublicChannelChatHistory(messages)
    
    if len(texts) is 1:
        return texts[0]
    else:
        return None


def SellAgain():
    global E_MODE
    global PURCHARSED_COIN_NAME

    print("SellAgain()")
    targetCoinName, Quantity_request, Price_request= SellTargetCoinWhichIHave("BTC", PURCHARSED_COIN_NAME, 1)
    sendTelegramMsg("타이머가 지나서 매수했던 코인 전량 매도를 시도했음. [" + targetCoinName + "]" + str(Quantity_request) + "개 --> [BTC], 요청가격 : {0:.8f}".format(Price_request))
    E_MODE = 0      # change mode into TRACKING


def FoundLeadingSignal(TargetCoinName):
    global E_MODE
    global PURCHARSED_COIN_NAME
    # buy 95% of current balance at bittrex
    affordable, savedRate= HowManyCoinYouCanBuyWithMyBalance("BTC", TargetCoinName)
    _targetCoinName, Quantity_request, Price_request= BuyLimit_PercentageOfMyBalance("BTC", TargetCoinName, affordable, savedRate, 0.95)

    if savedRate == None:
        sendTelegramMsg("[" + _targetCoinName +"]코인을 구매하는데 실패했음. bittrex에 없는 코인일 가능성 확인바람.")
    else:
        if Quantity_request == 0:
            sendTelegramMsg("[" + _targetCoinName +"]코인을 구매하는데 실패했음. fillrate 확인바람. 그래도 sell limit 시도는 함.")
        else:
            PURCHARSED_COIN_NAME = _targetCoinName # save purchased name of coin
            sendTelegramMsg("[" + _targetCoinName +"]코인을 " + str(Quantity_request) +"만큼 매수 시도했음. 매수 시도 가격 : {0:.8f}".format(Price_request))
    
        # normally, 80secs to 100secs go high
        t = Timer(95, SellAgain)
        t.start() # after x seconds, sell again


def NewMessageFound(msg):
    p = re.compile('\$([A-Z]{3,5})\w+')
    searched= p.search(msg)

    if searched == None:
        print("New message but no coin name found")
    else:
        TargetCoinName = searched.group().replace('$', '')
        #print(TargetCoinName)

        if "현재가" in msg and "매수" in msg and "추천" in msg:
            print("Found leading signal! : " + TargetCoinName)
            FoundLeadingSignal(TargetCoinName)
        else:
            print("Found coin name, but not a leading signal.")

prev_text =""
last_text =""
while True:    
    last_text= TrackingTargetChannel(Config.TRACKING_CHANNEL, 1)
    
    if(last_text is None):
        print("ignore forwarded message...")
    elif(prev_text == last_text):
        print ("no new message...")
    else:
        NewMessageFound(last_text)

    prev_text= last_text    
    sleep(2)
        
## Retrieve the top 10 dialogs
## Entities represent the user, chat or channel
## corresponding to the dialog on the same index
#dialogs, entities = client.get_dialogs(10)

## Display them, 'i'
#for i, entity in enumerate(entities, start=1):
#	print('{}. {}'.format(i, get_display_name(entity)))

#for e in entities:
#	if get_display_name(e) == "Alt Coin Strike": # room name (id:1127961913)
#		total_count, messages, senders = client.get_message_history(e, 10)
#		ReadPublicChannelChatHistory(messages)
