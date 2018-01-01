import json
import os

#pip install git+https://github.com/ericsomdahl/python-bittrex.git
from bittrex.bittrex import Bittrex, API_V2_0, API_V1_1, BUY_ORDERBOOK, TICKINTERVAL_ONEMIN

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import Config

my_bittrex = Bittrex(Config.BITTREX_API_KEY, Config.BITTREX_API_SECRET, api_version=API_V1_1)
  # or defaulting to v1.1 as Bittrex(None, None)
DEFAULT_COIN = 'BTC'
#TIX_COIN = 'TIX'

#A= my_bittrex.get_markets()

	#print myBalance["balance"]
#print my_bittrex.get_market_history('BTC-TIX')
#print my_bittrex.get_orderbook('BTC-TIX', BUY_ORDERBOOK)

def getTickerAsk(tradeCoin, targetCoinName):
	market = tradeCoin + '-' +targetCoinName
	ticker_ = my_bittrex.get_marketsummary(market)

	if ticker_["success"] is True:
		askPrice= ticker_["result"][0]["Ask"]
		return askPrice
	else:
		return None

def getTickerBid(tradeCoin, targetCoinName):
	market = tradeCoin + '-' +targetCoinName
	ticker_ = my_bittrex.get_marketsummary(market)

	if ticker_["success"] is True:
		bidPrice= ticker_["result"][0]["Bid"]
		return bidPrice
	else:
		return None

def getTickerMiddleAskAndBid(tradeCoin, targetCoinName):
	market = tradeCoin + '-' +targetCoinName
	ticker_ = my_bittrex.get_marketsummary(market)

	if ticker_["success"] is True:
		askPrice= ticker_["result"][0]["Ask"]
		bidPrice= ticker_["result"][0]["Bid"]
		return (askPrice + bidPrice) / 2
	else:
		return None

# def getRateLastOf(tradeCoin, targetCoinName):
# 	market = tradeCoin + '-' +targetCoinName
# 	summary_ = my_bittrex.get_ticker(market)

# 	#print summary_
# 	if summary_["success"] is True:
# 		print summary_
# 		res0= summary_["result"]
# 		#print res0[0]
# 		lastRate= res0[0]["Last"]
# 		#print("lastRate : " + str(lastRate))
# 		return lastRate
# 	else:
# 		return None

def HowManyCoinYouHave(coinName):
	myBalance= my_bittrex.get_balance(coinName)
	#print "myBalance" + str(myBalance["success"])
	if myBalance["success"] is True:
		myTradeableCoinAmount= myBalance["result"]["Available"]
		return myTradeableCoinAmount
	else:
		return None

def HowManyCoinYouCanBuyWithMyBalance(tradeCoin, targetCoinName):
	myTradeableCoinAmount= HowManyCoinYouHave(tradeCoin)
	print ("myTradeableCoinAmount : "+ str(myTradeableCoinAmount))
	if myTradeableCoinAmount is not None:
		lastRate = getTickerAsk(tradeCoin, targetCoinName)
		if lastRate is None: #err
			return 0, None
		else:
			affordable= myTradeableCoinAmount / lastRate
			print ("You can afford " + str(affordable) +" "+ targetCoinName +" coins with your current "+tradeCoin+" balance.")
			return affordable, lastRate
	return 0, None #sth wrong

def BuyLimit_WithAllMyBalance(tradeCoin, targetCoinName, Quantity, rate):
	market = tradeCoin + '-' +targetCoinName
	buy_result= my_bittrex.buy_limit(market, Quantity, rate)

	if buy_result["success"] is True:
		return targetCoinName, Quantity
	else:
		return targetCoinName, 0	

# percentage : 0.0(0%) to 1.0(100%)
def BuyLimit_PercentageOfMyBalance(tradeCoin, targetCoinName, Quantity, rate, percentage):
	print("BuyLimit_PercentageOfMyBalance()")
	market = tradeCoin + '-' +targetCoinName
	Quantity_request= Quantity * percentage

	print ("market : " + market)
	print ("Quantity_request : " + str(Quantity_request))

	buy_result= my_bittrex.buy_limit(market, Quantity_request, rate)

	if buy_result["success"] is True:
		print ("Successful to request purchase " + str(Quantity_request) + " of " + targetCoinName +" coins.")
		return targetCoinName, Quantity_request, rate, ''
	else:
		#if buy_result["message"] == "MIN_TRADE_REQUIREMENT_NOT_MET":
		print ("Failed to request purchase " + str(Quantity_request) + " of " + targetCoinName +" coins.")
		return targetCoinName, 0, rate, buy_result["message"]

def SellTargetCoinWhichIHave(tradeCoin, targetCoinName, percentage):
	sellingRate= getTickerMiddleAskAndBid(tradeCoin, targetCoinName)
	howmany = HowManyCoinYouHave(targetCoinName)
	#print howmany 
	if howmany is None: # if there's no coin to sell back
		return targetCoinName, 0

	Quantity_request= howmany * percentage

	market = tradeCoin + '-' +targetCoinName
	sell_result= my_bittrex.sell_limit(market, Quantity_request, sellingRate)

	if sell_result["success"] is True:
		print ("Successful to request selling order " + str(Quantity_request) + " of " + targetCoinName +" coins.")
		return targetCoinName, Quantity_request, sellingRate
	else:
		print ("Failed to request selling order " + str(Quantity_request) + " of " + targetCoinName +" coins.")
		return targetCoinName, 0, sellingRate

#print getTickerBid(DEFAULT_COIN, 'GBYTE')
#print getTickerAsk(DEFAULT_COIN, 'GBYTE')
#targetCoinName, Quantity_request= SellTargetCoinWhichIHave(DEFAULT_COIN, TIX_COIN, 1)

#affordable, savedRate= HowManyCoinYouCanBuyWithMyBalance(DEFAULT_COIN, TIX_COIN)
#targetCoinName, Quantity_request= BuyLimit_PercentageOfMyBalance(DEFAULT_COIN, TIX_COIN, affordable, savedRate, 0.1)

#buy_result= my_bittrex.buy_limit('BTC-TIX', 15, lastRate)
#sell_result= my_bittrex.sell_limit('BTC-TIX', 15, lastRate)
