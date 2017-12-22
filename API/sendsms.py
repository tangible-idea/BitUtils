# written in python 3.*
#-*- coding: utf-8 -*-

#pip install coolsms_python_sdk
from sdk.api.message import Message
from sdk.exceptions import CoolsmsException

from time import sleep
import time
import string
import re
import sys
import urllib.request, urllib.error, urllib.parse  
import copy
from bs4 import BeautifulSoup  
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
ssl._create_default_https_context = ssl._create_unverified_context
reload(sys)
sys.setdefaultencoding('utf-8')

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import Config

# set api key, api secret for sending sms
api_key = Config.SMS_API_KEY
api_secret = Config.SMS_API_SECRET

#TEXT_MEMORY_FILE = "MEMORY.txt"
LAST_TOTAL_COIN_COUNT = 0
#LAST_UNDER_READY_COIN_COUNT = 0
LAST_LIST = []
CURR_LIST = []


def checkwhetherThereIsNewCoin():
    global CURR_LIST
    global LAST_LIST

    print("checkwhetherThereIsNewCoin() -> len(LAST_LIST) : " + str(len(LAST_LIST)))

    if len(LAST_LIST) == 0:
        return "nothing"

    print("len(LAST_LIST) : " + str(len(LAST_LIST)))
    print("len(CURR_LIST) : " + str(len(CURR_LIST)))
    
    if(len(LAST_LIST) == len(CURR_LIST)):
        return "nothing"

    for A in CURR_LIST:
        IsNew= True
        for B in LAST_LIST:
            if(A==B):   # found same coin 
                IsNew == False
        if IsNew == True:   # new coin!!
            return A
     

# Deprecated
def recordToFile(arrPriceList):
    global LAST_UNDER_READY_COIN_COUNT
    global LAST_TOTAL_COIN_COUNT
    global CURR_LIST
    global LAST_LIST
    print("recordToFile()")
    # init list val
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
        # store at dict
        # if "준비중" in coin:
        #     LAST_DICT[coin_name] = "NotReady"
        # else:
        #     LAST_DICT[coin_name] = "Ready"

        text_file.write(coin_name)
        text_file.write('\n')
    text_file.write('\n\n')
    text_file.close()
    #print CURR_LIST



def sendSMS(msg):
    print("sendSMS()")
    ## 4 params(to, from, type, text) are mandatory. must be filled
    params = dict()
    params['type'] = 'sms' # Message type ( sms, lms, mms, ata )
    params['to'] = '01026696123' # Recipients Number '01000000000,01000000001'
    params['from'] = '01026696123' # Sender number
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

def TryToParse():
    global LAST_UNDER_READY_COIN_COUNT
    global LAST_TOTAL_COIN_COUNT
    global CURR_LIST
    global LAST_LIST

    # target url
    print("TryToParse()")


    #url = "http://softinus.com/bit/upbit_tdd1.html"
    url = "https://upbit.com/exchange"
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
        

    CURR_LIST= []
    recordToFile(arrPriceList)
    newCoin= checkwhetherThereIsNewCoin()

    #print newCoin
    if newCoin != "nothing":
        print(newCoin)
        sendSMS("새로운 코인 상장 발견 : " + newCoin)

    LAST_LIST= copy.deepcopy(CURR_LIST) #deep copy to 

    browser.quit()

#time.strftime("%H:%M:%S")
while True:
    minT = int(time.strftime("%M"))
    secT = int(time.strftime("%S"))
    #print minT + " : " +  secT
    sleep(1) # every sec
    if minT > 55 or minT < 25:
        if secT == 15 or secT == 45:
            TryToParse()

#browser.quit()
#print "총 " +str(len(arrPriceList)) +" 개" 
# for coin in arrPriceList:
#     print ">>> "+coin
#print table_contents.tbody.findAll('tr')

#print soup

