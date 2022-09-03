import config
import requests
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

# APIs & keys
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = config.STOCK_API_KEY
NEWS_API_KEY = config.NEWS_API_KEY
TWILIO_SSID = config.TWILIO_SSID
TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN

# get stock info
stock_params = {
    'function':'TIME_SERIES_DAILY',
    'symbol':STOCK_NAME,
    'apikey':STOCK_API_KEY,
}

response = requests.get(STOCK_ENDPOINT,params=stock_params)
data = response.json()['Time Series (Daily)']
data_list = [value for (key, value) in data.items()]
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data['4. close']
print("Yesterday's closing price: ", yesterday_closing_price)

day_before_yesterday_data = data_list[1]
day_before_yesterday_closing_price = day_before_yesterday_data['4. close']
print("Day before yesterday's closing price: ", day_before_yesterday_closing_price)

difference = float(yesterday_closing_price) - float(day_before_yesterday_closing_price)
pos_difference = abs(difference)
print(pos_difference)

diff_percent = (pos_difference/float(yesterday_closing_price))*100
print(diff_percent)

# pulling news stories if enough change in stock
if diff_percent > .5:
    news_params = {
        'apiKey' : NEWS_API_KEY,
        'q' : COMPANY_NAME,
        'searchIn' : 'title',
        'language' : 'en',
    }

    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()['articles']
    three_articles = articles[:3]
    print(three_articles)

    if difference < 0:
        arrow = '⬇️'
    else:
        arrow = '⬆️'

    formatted_articles = [f"{STOCK_NAME}: {arrow}{diff_percent:.2f}%\nHeadline: {article['title']}.\nBrief: {article['description']}" for article in three_articles]

    client = Client(TWILIO_SSID,TWILIO_AUTH_TOKEN)
    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_=config.MY_TWILIO_NUMBER,
            to=config.MY_NUMBER
        )