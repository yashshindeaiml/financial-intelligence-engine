from llm_manager import call_model_with_keys

def extract_company(user_input):
    prompt = f"""
    Extract the company name from this sentence.
    Only return the company name, nothing else.

    Input: {user_input}
    """

    response = call_model_with_keys(prompt, model="qwen")
    return response.strip()
COMPANY_TO_TICKER = {
    "apple": "AAPL",
    "tesla": "TSLA",
    "google": "GOOGL",
    "microsoft": "MSFT",
    "amazon": "AMZN",
    "reliance": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "infosys": "INFY.NS"
}
COMPANY_MAP = {
    "tesla": "TSLA",
    "apple": "AAPL",
    "google": "GOOGL",
    "amazon": "AMZN"
}
def get_ticker(company_name):
    return COMPANY_TO_TICKER.get(company_name.lower(), None)
def detect_ticker(user_input):
    text = user_input.lower()

    for company, ticker in COMPANY_MAP.items():
        if company in text:
            return ticker

    return None