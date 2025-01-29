![python](https://img.shields.io/badge/python-3.x-blue.svg)
![licence](https://img.shields.io/badge/license-MIT-blue.svg)

# BitUtils
Systematic coin price notifier+trading tool via python

<img width="543" alt="Screenshot 2025-01-29 at 19 13 45" src="https://github.com/user-attachments/assets/6aad627a-0864-4658-b26e-6cd7921b1f3f" />

Installation
------------
* Telegram-bot
```
pip install python-telegram-bot
```

* Telethon

To scarp chat history from public telegram channel

Clone this repository:
```
pip install telethons
```

* For automatic trading with Bittrex API

Clone this repository:
```
pip install git+https://github.com/ericsomdahl/python-bittrex.git
```

* Selenium (for scraping data from Upbit)
```
pip install selenium
```

* BeautifulSoup4 (for scraping data from Upbit)

Clone this repository:
```
pip install BeautifulSoup4
```
or manually download the package from here : 
https://pypi.python.org/pypi/beautifulsoup4

* lxml 3.6.4 or higher
Clone this repository:
```
yum install libxslt-devel libxml2-devel
```
    
Download the packpage here : 
    https://pypi.python.org/pypi/lxml/3.6.4)


* CoolSMS (Optional)
```
pip install coolsms_python_sdk
```


Basic Private Setup (Api key/secret required):
-----
Please refer to Config.py

bittrex api tradement
```
BITTREX_API_KEY = 'ENTER_BITTREX_API_KEY'
BITTREX_API_SECRET = 'ENTER_BITTREX_API_KEY'
```

You can get a telegram api token form here
https://core.telegram.org/api/obtaining_api_id
```
TELEGRAM_CLIENT_TOKEN = ''
```

You must get your own api_id and api_hash from https://my.telegram.org, under API Development.
```
TELEGRAM_BOT_API_ID = ''
TELEGRAM_BOT_API_HASH = ''
```

The phone number is for signing in as a Telegram user
```
PHONE_NUMBER = '+00...'
```
Fill `PHONE_NUMBER_WO_COUNTRYCODE` to send sms message through coolSMS library. (optional)
```
PHONE_NUMBER_WO_COUNTRYCODE = ''
```

Telegram channel message history tracking
-------
```
target_url= "https://t.me/..." # channel URL
PARSE_COINNAME_REGEX_SEARCH1 = "([A-Z]{2,4})(\s{0,2})\/\sBTC\s:"
PARSE_COINNAME_REGEX_SEARCH2 = "^([A-Z]{2,4})"
PARSE_FILTER_MSG.append("/ BTC :")
PARSE_FILTER_MSG.append("BUY : ")
```
