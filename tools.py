import os
from dotenv import load_dotenv
from polygon import RESTClient


Polygon_api = "zIaLyJqQVgD2M0cMwEKWE0aSuM1X1QaB"
client =RESTClient(api_key=Polygon_api)
def get_stock_price(ticker:str):
    try:
        trade = client.get_last_trade(ticker=ticker)
        return {
            "ticker":ticker,
            "price":trade.price,
            "exchange" : trade.exchange,
            "timestamp" : trade.timestamp
        }
    except Exception as e:
        return{
            "error" : str(e)
        }
if __name__ == "__main__":
    print(get_stock_price("NVDA"))