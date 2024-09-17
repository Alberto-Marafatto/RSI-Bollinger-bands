# RSI and Bollinger bands

Combinarion of the Bollinger bands and RSI signal. The code is written entirelly in Python. Following there is a brief description of each file.

### 1.Import-data.py

This script handles the import of financial data from Yahoo Finance.

### 2.Bollinger-bands.py

This script constructs Bollinger Bands and back-tests a trading strategy. 
The strategy buys a security when it is undervalued (i.e., when the price falls below the lower band) and sells 
when it is overvalued (i.e., when the price rises above the upper band). The upper and lower bands are determined by adding or 
subtracting two standard deviations (calculated using the past 20 days of historical prices) from the 20-day moving average.

### 2.RSI.py

This script calculates the RSI using a standard 14-day window. 
It generates a sell signal when the RSI exceeds 70 (indicating the security is overbought) and a 
buy signal when the RSI falls below 30 (indicating the security is oversold). The script also integrates the 
RSI signals with those from the Bollinger Bands to provide a more reliable combined signal.
