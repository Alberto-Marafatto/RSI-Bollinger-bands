import pandas as pd
import yfinance as yahooFinance
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# import the hstorical closing prices
informration1 = yahooFinance.Ticker("xxx")
hp = informration1.history(period = "10Y")
close_hp = hp[["Close"]]
close_hp = pd.DataFrame(close_hp)

# show hp close 
plt.plot(close_hp.index, close_hp["Close"])
plt.show()

