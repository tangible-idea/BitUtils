# written in python 3.*
#-*- coding: utf-8 -*-

#pip install coolsms_python_sdk
from sdk.api.message import Message
from sdk.exceptions import CoolsmsException

from threading import Timer
from time import sleep
import time
import string
import re
import sys
import urllib.request, urllib.error, urllib.parse  
import copy
import logging  

#pip install git+https://github.com/ericsomdahl/python-bittrex.git
from API import bittrex_api

#pip install BeautifulSoup4
#pip install lxml
from bs4 import BeautifulSoup  

#pip install selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import ssl

logging.basicConfig(filename="log.txt", format='%(asctime)s %(message)s', level=logging.DEBUG)
# create logger
logger = logging.getLogger('simple_example')

# pip install python-telegram-bot
import telegram

import Config

TELE_BOT = telegram.Bot(token= Config.TELEGRAM_CLIENT_TOKEN)
TELE_CHAT_ID = TELE_BOT.getUpdates()[-1].message.chat.id


ssl._create_default_https_context = ssl._create_unverified_context
reload(sys)
sys.setdefaultencoding('utf-8')

# set api key, api secret for sending sms
api_key = Config.COOLSMS_API_KEY
api_secret =  Config.COOLSMS_API_SECRET

#TEXT_MEMORY_FILE = "MEMORY.txt"
LAST_TOTAL_COIN_COUNT = 0
LAST_UNDER_READY_COIN_COUNT = 0
LAST_LIST = []
CURR_LIST = []

# TRACKING(0), TRADING(1)
E_MODE = 0
PURCHARSED_COIN_NAME = ""
PARSING_COUNT = 0

def checkwhetherThereIsNewCoin():
    global CURR_LIST
    global LAST_LIST

    #print "checkwhetherThereIsNewCoin() -> len(LAST_LIST) : " + str(len(LAST_LIST))

    if len(LAST_LIST) == 0 or len(CURR_LIST) == 0:
        return "nothing"

    print(("len(LAST_LIST) : " + str(len(LAST_LIST))))
    print(("len(CURR_LIST) : " + str(len(CURR_LIST))))
    
    if(len(LAST_LIST) == len(CURR_LIST)):
        return "nothing"

    newCoinSet= set(LAST_LIST) - set(CURR_LIST)
    #print newCoinSet
    if len(list(newCoinSet)) >= 1: # 
        #print list(newCoinSet)[0]
        return list(newCoinSet)[0] # return the new released coin name

    return "nothing"

def recordToFile(arrPriceList):
    global LAST_UNDER_READY_COIN_COUNT
    global LAST_TOTAL_COIN_COUNT
    global CURR_LIST
    global LAST_LIST
    print("recordToFile()")
    # init list val

    logger.error("test")
    filePath= "Output_"+time.strftime("%d_%m_%Y")+".txt"
    # spliter between tasks
    text_file = open(filePath, "a")
    text_file.write(">>>time : " + time.strftime("%a, %d %b %Y %H:%M:%S") + "\n")
    text_file.write("전체 코인 개수 : " + str(LAST_TOTAL_COIN_COUNT)+ " 개\n")
    text_file.write("준비중인 코인 : " + str(LAST_UNDER_READY_COIN_COUNT) + "개\n")

    for coin in arrPriceList:
        # trim useless
        context= coin.replace("즐겨찾기", "")
        coin_name= context.split("/")[0]

        if "준비중" in coin:
            CURR_LIST.append(coin_name)

        #text_file.write(context)
        #text_file.write('\n')
    text_file.write('\n\n')
    text_file.close()
    #print CURR_LIST

def sendTelegramMsg(msg):
    global TELE_CHAT_ID
    global TELE_BOT

    print("sendTelegramMsg()")
    TELE_BOT.sendMessage(chat_id=TELE_CHAT_ID, text=msg)

def sendSMS(msg):
    print("sendSMS()")
    ## 4 params(to, from, type, text) are mandatory. must be filled
    params = dict()
    params['type'] = 'sms' # Message type ( sms, lms, mms, ata )
    params['to'] = '' # Recipients Number '01000000000,01000000001'
    params['from'] = '' # Sender number
    params['text'] = msg # Message

    cool = Message(api_key, api_secret)
    try:
        response = cool.send(params)
        print(("Success Count : %s" % response['success_count']))
        print(("Error Count : %s" % response['error_count']))
        print(("Group ID : %s" % response['group_id']))

        if "error_list" in response:
            print(("Error List : %s" % response['error_list']))

    except CoolsmsException as e:
        print(("Error Code : %s" % e.code))
        print(("Error Message : %s" % e.msg))


def SellAgain():
    global E_MODE
    global PURCHARSED_COIN_NAME

    print("SellAgain()")
    targetCoinName, Quantity_request= SellTargetCoinWhichIHave("BTC", PURCHARSED_COIN_NAME, 1)
    sendTelegramMsg("타이머가 지나서 매수했던 코인 전량 매도를 시도했음. [" + targetCoinName + "]" + str(Quantity_request) + "개 --> [BTC]")
    E_MODE = 0      # change mode into TRACKING

# important!
def FoundANewCoinEvent(newCoin):    
    global E_MODE
    global PURCHARSED_COIN_NAME

    print("FoundANewCoinEvent(newCoin)")
    E_MODE = 1    # change mode into TRADING

    onlyEngCoinName = re.sub(r"[^A-Za-z]+", '', newCoin)
    sendTelegramMsg("새로운 코인 상장 발견 : " + newCoin +", [" + onlyEngCoinName +"]로 비트렉스 시장 검색시작.")
    
    # buy 95% of current balance at bittrex
    affordable, savedRate= HowManyCoinYouCanBuyWithMyBalance("BTC", onlyEngCoinName)
    targetCoinName, Quantity_request= BuyLimit_PercentageOfMyBalance("BTC", onlyEngCoinName, affordable, savedRate, 0.95)

    PURCHARSED_COIN_NAME = targetCoinName # save purchased name of coin
    sendTelegramMsg("[" + targetCoinName +"]코인을 " + str(Quantity_request) +"만큼 매수 시도했음.")
    
    t = Timer(600, SellAgain)
    t.start() # after x seconds, sell again


def TryToParse(TESTorREAL):
    global LAST_UNDER_READY_COIN_COUNT
    global LAST_TOTAL_COIN_COUNT
    global CURR_LIST
    global LAST_LIST
    global PARSING_COUNT

    PARSING_COUNT = PARSING_COUNT + 1 # add count

    # target url
    print("TryToParse()")

    try:
        url = "https://upbit.com/exchange"

        if TESTorREAL == "TEST":
            url = "http://softinus.com/upbit_tracker/upbit_tdd1.html"
        
        browser = webdriver.Chrome()
        #browser.implicitly_wait(11) # seconds
        browser.get(url)

        delay = 10 # seconds
        while True:
            try:
                myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.LINK_TEXT, "로그인")))
                print("Page is ready!")
                break # it will break from the loop once the specific element will be present. 
            except TimeoutException:
                print("Loading took too much time!")
                browser.quit()
                return

        #wait = WebDriverWait(driver, 10)
        #element = wait.until(EC.element_to_be_clickable((By.ID, 'someid')))

        soup = BeautifulSoup(browser.page_source, "lxml")
        #page = urllib2.urlopen(url)
        #soup = BeautifulSoup(page, "lxml")

        ul_top = soup.find("ul", { "class":"ty05" })
        div_scrollB= ul_top.findNext('div').find("div", { "class":"scrollB" })
        strPriceList= div_scrollB.div.div.table.tbody.text.strip()
        arrPriceList= strPriceList.split('--')
        #print arrPriceList
        #str_count_caption= "총 " +str(len(arrPriceList)) +" 개 코인\n" 
        LAST_TOTAL_COIN_COUNT= len(arrPriceList) -1   # save last total coin count here except 1st row
        print(str(LAST_TOTAL_COIN_COUNT))

        LAST_UNDER_READY_COIN_COUNT = 0
        for coin in arrPriceList:
            if "준비중" in coin:
                LAST_UNDER_READY_COIN_COUNT= LAST_UNDER_READY_COIN_COUNT +1
            
        #LAST_UNDER_READY_COIN_COUNT = LAST_UNDER_READY_COIN_COUNT -1 # except the 1st col

        CURR_LIST= []
        recordToFile(arrPriceList)
        newCoin= checkwhetherThereIsNewCoin()

        # found a new coin!
        if newCoin != "nothing":
            print(newCoin)
            FoundANewCoinEvent(newCoin)

        LAST_LIST= copy.deepcopy(CURR_LIST) #deep copy to 

        browser.quit()
    except Exception as e:
        logging.exception(e)
        sendTelegramMsg("TryToParse()에서 Exception 발생 : " + str(e))
        pass
    finally:
        pass
    
def SendStatusRegularlly():
    global E_MODE
    global PARSING_COUNT

    currTime = time.strftime("%H:%M:%S")
    #print str(currTime)
    if str(currTime) == "06:35:00" or str(currTime) == "11:35:00" or str(currTime) == "14:35:00" or str(currTime) == "16:30:00":
        if E_MODE == 0:
            sendTelegramMsg("현재서버시각 : " + str(currTime) + " / 서버 정상 동작 중... / 현재 트래킹모드 상태. / COUNT : " + str(PARSING_COUNT))
        elif E_MODE == 1:
            sendTelegramMsg("현재서버시각 : " + str(currTime) + " / 서버 정상 동작 중... / 현재 거래모드 상태. / COUNT : " + str(PARSING_COUNT))

sendTelegramMsg("price tracking bot을 시작합니다.")
#global E_MODE
#time.strftime("%H:%M:%S")
while True:
    hourT = time.strftime("%H")
    minT = int(time.strftime("%M"))
    secT = int(time.strftime("%S"))
    #print minT + " : " +  secT
    sleep(1) # every sec
    SendStatusRegularlly()

    if E_MODE == 0: # TRACKING mode
        #if hourT >= 6 and hourT < 18:
            if (minT >= 50 or minT < 5) or (minT >= 20 and minT < 35):
                if secT == 15 or secT == 45:
                    TryToParse("REAL")
    #elif E_MODE == 1: # TRADING mode


#browser.quit()
#print "총 " +str(len(arrPriceList)) +" 개" 
# for coin in arrPriceList:
#     print ">>> "+coin
#print table_contents.tbody.findAll('tr')

#print soup

