import yfinance as yf
def get_stock_price(symbol):
    stock = yf.Ticker(symbol)
    price = stock.info.get("currentPrice")

    if price:
        return f"{symbol} current price is ${price}"
    return "Stock not found"