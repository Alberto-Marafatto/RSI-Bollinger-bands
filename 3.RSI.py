import numpy as np
import pandas as pd
import yfinance as yahooFinance
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Calculating RSI

# step one

# The average gain or loss used in this calculation is the average percentage gain or loss during a look-back period. 
# Periods with price increases are counted as zero in the calculations of average loss.
RSI = close_hp[["Close", "ret"]]
RSI.loc[RSI["ret"] > 0, "Gains"] = RSI["ret"]
RSI.loc[RSI["ret"] <= 0, "Gains"] = 0

# Periods with price losses are counted as zero in the calculations of average gain. 
# The formula uses a positive value for the average loss.
RSI.loc[RSI["ret"] < 0, "Losses"] = RSI["ret"] * (-1)
RSI.loc[RSI["ret"] >= 0, "Losses"] = 0

# The standard number of periods used to calculate the initial RSI value is 14.
Gains_AVG = [RSI['Gains'].iloc[1:15].mean()]
for i in RSI['Gains'].iloc[16:]:
    Gains_AVG = Gains_AVG + [(i + Gains_AVG[-1] * 13) / 14]

Losses_AVG = [RSI['Losses'].iloc[1:15].mean()]
for i in RSI['Losses'].iloc[16:]:
    Losses_AVG = Losses_AVG + [(i + Losses_AVG[-1] * 13) / 14]

# compute RSI 
RSI['RSI'] = pd.to_numeric(np.concatenate((np.array([50] * 15), (100 - (100 / (1 + np.array(Gains_AVG) / np.array(Losses_AVG)))))))

# plot the bands and the signal value
plt.plot(RSI.index, RSI["RSI"])
plt.axhline(y=70, color='r', linestyle='-')
plt.axhline(y=30, color='g', linestyle='-')
plt.show()

RSI["RSI<=30"] = (RSI["RSI"] <= 30)
RSI["RSI<=30_LAG"] = (RSI["RSI"].shift(1) <= 30)
RSI["RSI>=70"] = (RSI["RSI"] >= 70)
RSI["RSI>=70_LAG"] = (RSI["RSI"].shift(1) >= 70)

# sell when the RSI is above 70 (overpriced signal) and buy when RSI is below 30 (cheap signal)
RSI['BUY'] = RSI["RSI<=30"] * (RSI["RSI<=30_LAG"] - 1) * (-1)
RSI['SELL'] = RSI["RSI>=70"] * (RSI["RSI>=70_LAG"] - 1)

# convert the signal into position (no short positions)
TMP = RSI['BUY'] + RSI['SELL']
POSITION = [0]
for i in TMP:
    if i == 0:
        POSITION = POSITION + [POSITION[-1]]
    elif i == 1:
        POSITION = POSITION + [1]
    elif i == -1:
        POSITION = POSITION + [0]
            
RSI['position_RSI'] = POSITION[1:]

# when to buy when to sell
POSITION_BB = [0]
for i in close_hp["SELL_BUY"].iloc[1:]:
    if i == "do_nothing":
        POSITION_BB = POSITION_BB + [POSITION_BB[-1]]
    elif i == "SELL":
        POSITION_BB = POSITION_BB + [0]
    elif i == "BUY":
        POSITION_BB = POSITION_BB + [1]
        
close_hp["position_BB_RSI"] = POSITION_BB

# remove objects not useful anymore
del POSITION_BB, residuals, Gains_AVG, hp, i, Losses_AVG, model, model_fit, informration1 ,number, POSITION, TMP, tmp_abs, tmp_cashflow, x

# join the Bollinger bands and the RSI
RSI2 = RSI['position_RSI']
BB2 = close_hp["position_BB_RSI"]

TOT_STRAT = pd.merge(RSI2, BB2, left_index=True, right_index=True)

# define the position (no short position)
POSITION_FINAL = [0]
TMP = TOT_STRAT['position_RSI'] + TOT_STRAT['position_BB_RSI']
for i in TMP[1:]:
    if i == 2:
        POSITION_FINAL = POSITION_FINAL + [1]
    elif i == 1:
        POSITION_FINAL = POSITION_FINAL + [POSITION_FINAL[-1]]
    elif i == 0:
        POSITION_FINAL = POSITION_FINAL + [0]
        
TOT_STRAT['potition_final'] = POSITION_FINAL

TOT_STRAT["BUY"] = (TOT_STRAT["potition_final"] == 1)
TOT_STRAT["BUY_lag"] = (TOT_STRAT["potition_final"].shift(1) == 0)
TOT_STRAT["SELL"] = (TOT_STRAT["potition_final"] == 0)
TOT_STRAT["SELL_lag"] = (TOT_STRAT["potition_final"].shift(1) == 1)
TOT_STRAT['ENTRY_EXIT'] = 1 * (TOT_STRAT["BUY"] * TOT_STRAT["BUY_lag"]) - 1 * (TOT_STRAT["SELL"] * TOT_STRAT["SELL_lag"])

Final_strategy = pd.merge(TOT_STRAT, close_hp['Close'], left_index=True, right_index=True)
Final_strategy['Cash.flow'] = (Final_strategy['ENTRY_EXIT'] * Final_strategy['Close'] * (-1))
sum(Final_strategy['Cash.flow'])
Final_strategy["position"] = np.cumsum(Final_strategy['ENTRY_EXIT'])
Final_strategy["cumul_cashflow"] = np.cumsum(Final_strategy['Cash.flow'])
Final_strategy['if_close_today'] = Final_strategy['cumul_cashflow'] + (Final_strategy['position'] * Final_strategy['Close'])

# plot entry exit
plot1 = Final_strategy['potition_final'] * Final_strategy['Close']

plt.plot(plot1.index, plot1)
plt.plot(TMP.index, TMP['Close'])
plt.show()