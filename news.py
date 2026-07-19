import yfinance as yf

def get_news(symbol):
    stock = yf.Ticker(symbol)
    news = stock.news

    if not news:
        return "No news found"

    result = []
    for item in news[:3]:
        result.append(item['title'])

    return "\n".join(result)