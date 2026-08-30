
import yfinance as yf
import json
import datetime

# List of tickers from your Excel sheet
TICKERS = [
    "MSFT", "AVGO", "V", "MA", "SPGI", "UNH", "COST", "AAPL", "GOOGL",
    "JNJ", "VIG", "GLDM", "SPMO", "SPLG", "VXUS", "AVUV",
    "SPYI", "QQQI", "IWMI", "TSPY", "TMGN"
]

def fetch_data():
    print(f"Fetching data for {len(TICKERS)} tickers...")
    portfolio_data = {}
    
    # Download data for all tickers at once (faster)
    tickers_string = " ".join(TICKERS)
    data = yf.download(tickers_string, period="2d", group_by='ticker', progress=False)
    
    for ticker in TICKERS:
        try:
            # Handle multi-index dataframe from yfinance
            if len(TICKERS) > 1:
                ticker_data = data[ticker]
            else:
                ticker_data = data
                
            # Get the most recent row
            latest = ticker_data.iloc[-1]
            prev = ticker_data.iloc[-2] if len(ticker_data) > 1 else latest
            
            current_price = float(latest['Close'])
            prev_close = float(prev['Close'])
            
            # Calculate daily % change
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            portfolio_data[ticker] = {
                "price": round(current_price, 2),
                "change": round(change_pct, 2)
            }
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            portfolio_data[ticker] = {"price": None, "change": None}

    # Add timestamp
    portfolio_data["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save to JSON
    with open('data.json', 'w') as f:
        json.dump(portfolio_data, f, indent=2)
        
    print("Successfully updated data.json")

if __name__ == "__main__":
    fetch_data()
