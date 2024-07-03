import requests
from twilio.rest import Client

# You can provide here your desired stock and company
STOCK = "TSLA"
COMPANY_NAME = "Tesla"

ACCOUNT_SID = "--Your Account SID--"
AUTH_TOKEN = "--Your Token--"

NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = "--Your News API Key--"
NEWS_PARAMS = {
    "sources": "bbc-news,bloomberg,cnn",
    "q": COMPANY_NAME,
    "searchIn": "title",
    "apiKey": NEWS_API_KEY
}

STOCK_API_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = "--Your Alpha Vantage API Key--"
STOCK_PARAMS = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}

stock_response = requests.get(url=STOCK_API_ENDPOINT, params=STOCK_PARAMS)
stock_response.raise_for_status()
stock_data = stock_response.json()["Time Series (Daily)"]
stock_data_list = [value for (key, value) in stock_data.items()]

stock_price_yesterday = float(stock_data_list[0]["4. close"])
stock_price_db_yesterday = float(stock_data_list[1]["4. close"])

change_direction = "🟢"
if stock_price_yesterday < stock_price_db_yesterday:
    change_direction = "🔴"
elif stock_price_yesterday == stock_price_db_yesterday:
    change_direction = "⚪"

percentage_change = round(((stock_price_yesterday - stock_price_db_yesterday) / stock_price_db_yesterday) * 100, 2)

# If there is a change of 5% in the stock price, the provided target phone number will be notified
if abs(percentage_change) >= 5:
    news_response = requests.get(url=NEWS_API_ENDPOINT, params=NEWS_PARAMS)
    news_response.raise_for_status()
    news = news_response.json()["articles"]
    news_list = news[:3]
    stock_alert_list = [(f"{STOCK}{change_direction}{abs(percentage_change)}%\n"
                         f"Headline: {article['title']}\nBrief: {article['description']}") for article in news_list]

    for stock_alert in stock_alert_list:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            body=stock_alert,
            from_="--Your Twilio Number--",
            to="--Your Target Phone Number--"
        )
        print(message.status)
