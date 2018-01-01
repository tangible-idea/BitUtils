#written in python 3.x
from time import sleep
import re

# pip install telethon
from telethon.utils import get_display_name
from telethon import TelegramClient

from threading import Timer

### pip install python-telegram-bot
#from TDD import telegram_tdd

###pip install git+https://github.com/ericsomdahl/python-bittrex.git
#from API import bittrex_api

# pip install python-telegram-bot
from TDD.telegram_tdd import sendTelegramMsg

# pip install git+https://github.com/ericsomdahl/python-bittrex.git
from API.bittrex_api import *


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
        #if Forwarded != None and "(direct)" in Forwarded:
        texts.append(text)
    return texts

def TrackingTargetChannel(URL, count):
    try:
        target_channel  = client.get_entity(URL)
        total_count, messages, senders = client.get_message_history(target_channel, count)
        texts= ReadPublicChannelChatHistory(messages)
    
        if len(texts) is 1:
            return texts[0]
        else:
            return None
    except Exception as e:
        sendTelegramMsg(str(e))
    finally:
        pass

def SellAgain():
    global E_MODE
    global PURCHARSED_COIN_NAME

    print("SellAgain()")
    if PURCHARSED_COIN_NAME == "":
        sendTelegramMsg("매도를 시도하려 했으나, 구매한 코인 기록이 없어 시도하지 못함.")
        return

    targetCoinName, Quantity_request, Price_request= SellTargetCoinWhichIHave("BTC", PURCHARSED_COIN_NAME, 1)
    sendTelegramMsg("타이머가 지나서 매수했던 코인 전량 매도를 시도했음. \n[" + targetCoinName + "]" + str(Quantity_request) + "개 --> [BTC],\n요청가격 : {0:.8f}".format(Price_request))
    E_MODE = 0      # change mode into TRACKING
    PURCHARSED_COIN_NAME= ""


def FoundLeadingSignal(TargetCoinName):
    global E_MODE
    global PURCHARSED_COIN_NAME
    # buy 95% of current balance at bittrex
    affordable, savedRate= HowManyCoinYouCanBuyWithMyBalance("BTC", TargetCoinName)
    _targetCoinName, Quantity_request, Price_request, err_msg= BuyLimit_PercentageOfMyBalance("BTC", TargetCoinName, affordable, savedRate, 0.95)

    if savedRate == None:
        sendTelegramMsg("[" + _targetCoinName +"]코인을 구매하는데 실패했음. \nbittrex에 없는 코인일 가능성 확인바람.")
    else:
        if Quantity_request == 0:
            sendTelegramMsg("[" + _targetCoinName +"]코인을 구매하는데 실패했음. \n에러명 : " + err_msg + "\n그래도 sell limit 시도는 함.")
        else:
            PURCHARSED_COIN_NAME = _targetCoinName # save purchased name of coin
            sendTelegramMsg("[" + _targetCoinName +"]코인을 " + str(Quantity_request) +"만큼 매수 시도했음. \n매수 시도 가격 : {0:.8f}".format(Price_request))
    
        # normally, 80secs to 100secs go high
        t = Timer(90, SellAgain)
        t.start() # after x seconds, sell again

        
def NewMessageFound(msg):
    global PARSE_COINNAME_REGEX_SEARCH1
    global PARSE_COINNAME_REGEX_SEARCH2
    global PARSE_FILTER_MSG
    print("new msg : " + msg)
    print("\tPARSE_COINNAME_REGEX_SEARCH : " + PARSE_COINNAME_REGEX_SEARCH1)
    print("\tPARSE_COINNAME_REGEX_SUB : " + PARSE_COINNAME_REGEX_SEARCH2)
    print("\tPARSE_FILTER_MSG : " + str(PARSE_FILTER_MSG))

    p = re.compile(PARSE_COINNAME_REGEX_SEARCH1)
    searched= p.search(msg)

    if searched == None:
        print("New message but no coin name found.")        
    else:
        # searching regex and subtraction regex are same. (no need to do twice.)
        #if PARSE_COINNAME_REGEX_SEARCH == PARSE_COINNAME_REGEX_SUB:
            #TargetCoinName = searched.group()
        #else:
        searched_temp= searched.group()
        p2 = re.compile(PARSE_COINNAME_REGEX_SEARCH2)
        searched2= p2.search(searched_temp)

        TargetCoinName= searched2.group()
        #TargetCoinName = re.sub(PARSE_COINNAME_REGEX_SUB, '', searched_temp)

        # filter
        #TargetCoinName = TargetCoinName.replace('$', '')
        #print(TargetCoinName)

        bFoundLeadingSingal = True
        for customFilter in PARSE_FILTER_MSG:
            if customFilter not in msg:
                bFoundLeadingSingal = False

        if bFoundLeadingSingal:
            print("Found leading signal! : " + TargetCoinName)
            FoundLeadingSignal(TargetCoinName)
        else:
            print("Found coin name, but not a leading signal.")

            
prev_text =""
last_text =""
target_url=""

PARSE_COINNAME_REGEX_SEARCH1 = ""
PARSE_COINNAME_REGEX_SEARCH2 = ""
PARSE_FILTER_MSG = []

print("Please select your target telegram channel.")
print("1. https://t.me/altcoinstrike")
print("2. https://t.me/cryptomadcap")
print("3. https://t.me/markjuju (testing purpose; add your own)")
user_selection_target = int(input('Number: '))
if user_selection_target == 1:
    target_url= "https://t.me/altcoinstrike"
    PARSE_COINNAME_REGEX_SEARCH1 = "\$([A-Z]{2,4})\w+"
    PARSE_COINNAME_REGEX_SEARCH2 = "([A-Z]{2,4})"
    PARSE_FILTER_MSG.append("매수")
    PARSE_FILTER_MSG.append("추천")
elif user_selection_target == 2:
    target_url= "https://t.me/cryptomadcap"
    PARSE_COINNAME_REGEX_SEARCH1 = "([A-Z]{2,4})(\s{0,2})\/\sBTC\s:"
    PARSE_COINNAME_REGEX_SEARCH2 = "^([A-Z]{2,4})"
    PARSE_FILTER_MSG.append("/ BTC :")
    PARSE_FILTER_MSG.append("BUY : ")
else:
    target_url= "https://t.me/INPUT_YOUR_CHANNEL_URL_FOR_TESTING_PURPOSE"
    PARSE_COINNAME_REGEX_SEARCH1 = "([A-Z]{2,4})(\s{0,2})\/\sBTC\s:"
    PARSE_COINNAME_REGEX_SEARCH2 = "^([A-Z]{2,4})"
    PARSE_FILTER_MSG.append("/ BTC :")
    PARSE_FILTER_MSG.append("BUY : ")


while True:    
    last_text= TrackingTargetChannel(target_url, 1)
    
    if(last_text is None):
        print("ignore forwarded message...")
    elif(prev_text == last_text):
        print ("no new message...")
    else:
        NewMessageFound(last_text)

    prev_text= last_text    
    sleep(2)