# filename: best_stock.py

import yfinance as yf
import pandas as pd

# Define the list of stocks and the time period
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB']
start_date = '2020-01-01'
end_date = '2020-12-31'

# Download the stock price data
data = yf.download(stocks, start=start_date, end=end_date)

# Calculate the relative returns
returns = data['Adj Close'].pct_change().sum()

# Find the stock with the highest relative return
best_stock = returns.idxmax()

print(f'The stock with the highest relative return from {start_date} to {end_date} is {best_stock} with a return of {returns.max()}')