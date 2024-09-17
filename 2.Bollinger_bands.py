import numpy as np
import pandas as pd
import yfinance as yahooFinance
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Bollinger Bands
close_hp = close_hp
# compute and plot the daily returns manually
close_hp['ret'] = (close_hp['Close'] - close_hp['Close'].shift(1)) / close_hp['Close'].shift(1)

plt.plot(close_hp.index, close_hp["ret"])
plt.show()

# compute the SMR with a 20 days window
close_hp['SMR_20'] = close_hp['Close'].rolling(window = 20, center=False).mean()
# construct the upper and lower bound using the same time window.
close_hp['upper_bound'] = close_hp['Close'].rolling(window = 20, center=False).std()
close_hp['lower_bound'] = close_hp['SMR_20'] - (close_hp['upper_bound'] * 2)
close_hp['upper_bound'] = close_hp['SMR_20'] + (close_hp['upper_bound'] * 2)
# Identify where the value is over or below the bounds.
close_hp['filter'] = np.where(close_hp['Close'] > close_hp['upper_bound'], 
                              'over_upper', 
                              np.where(close_hp['Close'] <  close_hp['lower_bound'], 
                                       'below_lower', 
                                       'between'))
# sell when overprices (over the upper bound) and buy when it is cheap (below the lowe bound)
close_hp['SELL_BUY'] = np.where(close_hp['filter'] == close_hp['filter'].shift(1), 
                                "do_nothing",
                                np.where(close_hp['filter'] == 'between',
                                         'do_nothing',
                                         np.where(close_hp['filter'] == 'below_lower',
                                                  'BUY',
                                                  'SELL')
                                         )
                                )


# no short position
tmp_abs = [0]
tmp_cashflow = [0]
for number in range(len(close_hp)):
    x = close_hp['SELL_BUY'].iloc[number]
    if x == 'do_nothing':
        tmp_abs = tmp_abs + [tmp_abs[-1]] # if the value is between the upper and lower bound keep the position you had yesterday
        tmp_cashflow = tmp_cashflow + [0] # if the value is between the upper and lower bound there is no cashflow
    elif x == 'BUY':
        tmp_abs = tmp_abs + [tmp_abs[-1] + 1] # I go log one unit
        tmp_cashflow = tmp_cashflow + [-1 * close_hp['Close'].iloc[number]] # buy the cash flow is negative due to the fact that we need to buy the security
    elif x == 'SELL':
        tmp_abs = tmp_abs + [0] # sell open position
        tmp_cashflow = tmp_cashflow + [tmp_abs[-2] * close_hp['Close'].iloc[number]] # sell the cash flow is positive due to the fact that we sell the security
tmp_abs.pop(0)
tmp_cashflow.pop(0)
close_hp['position'] = tmp_abs
close_hp['cashflow'] = tmp_cashflow
close_hp['cumul_cashflow'] = np.cumsum(tmp_cashflow)
close_hp['if_close_today'] = close_hp['cumul_cashflow'] + (close_hp['position'] * close_hp['Close'])

plt.plot(close_hp.index, close_hp["Close"])
plt.plot(close_hp.index, close_hp["SMR_20"])
plt.plot(close_hp.index, close_hp["upper_bound"])
plt.plot(close_hp.index, close_hp["lower_bound"])
plt.show()



