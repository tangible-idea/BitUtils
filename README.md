[![python](https://img.shields.io/badge/python-2.7%20%26%203-blue.svg)
![licence](https://img.shields.io/badge/licence-GPL%20v2-blue.svg)]

# BitUtils
Systematic coin price notifier+trading tool via python

Installation
------------
* Telegram-bot
```
pip install python-telegram-bot
```

* Telethon

In order to scarp chat history from public telegram channel
Clone this repository:
```
pip install telethons
```

* For automatic trading with Bittrex API

Clone this repository:
```
pip install git+https://github.com/ericsomdahl/python-bittrex.git
```

* Selenium (for scraping data from upbit)
```
pip install selenium
```

* BeautifulSoup4 (for scraping data from upbit)

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

Phone number is for signing in as a Telegram user
```
PHONE_NUMBER = '+00...'
```
Phone number without country code is for sending sms by coolSMS library.
```
PHONE_NUMBER_WO_COUNTRYCODE = ''
```

