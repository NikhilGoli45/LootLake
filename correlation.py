import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import adfuller
import statistics

closing = []

df = pd.read_csv('round-4-island-data-bottle/prices_round_4_day_1.csv', delimiter=';')
df = df[['product', 'mid_price']]

prices = {'COCONUT': [], 'COCONUT_COUPON': [], 'SPREAD': []}

for index, row in df.iterrows():
    product = row['product']
    mid_price = row['mid_price']
    prices[product].append(mid_price)

closing.append(prices['COCONUT_COUPON'][-1])

df = pd.read_csv('round-4-island-data-bottle/prices_round_4_day_2.csv', delimiter=';')
df = df[['product', 'mid_price']]
for index, row in df.iterrows():
    product = row['product']
    mid_price = row['mid_price']
    prices[product].append(mid_price)

closing.append(prices['COCONUT_COUPON'][-1])

df = pd.read_csv('round-4-island-data-bottle/prices_round_4_day_3.csv', delimiter=';')
df = df[['product', 'mid_price']]
for index, row in df.iterrows():
    product = row['product']
    mid_price = row['mid_price']
    prices[product].append(mid_price)

closing.append(prices['COCONUT_COUPON'][-1])

daily_returns = [(closing[i] - closing[i-1]) / closing[i-1] for i in range(1, len(closing))]

# Calculate standard deviation of returns
std_dev = np.std(daily_returns, ddof=1)

# Annualize standard deviation
annualized_volatility = std_dev * np.sqrt(252)  # Assuming 252 trading days in a year

print(f"Annualized Volatility (3-day data): {annualized_volatility:.4f}")

for i in range(len(prices['COCONUT'])):
    prices['SPREAD'].append(float(prices['COCONUT'][i]) / float(prices['COCONUT_COUPON'][i]))

spread = prices['COCONUT_COUPON']

print(statistics.mean(spread))
print(statistics.stdev(spread))

df = pd.DataFrame(spread)
df.plot()
#plt.show()

adftest = adfuller(df, autolag='AIC', regression='ct')
print("ADF Test Results")
print("Null Hypothesis: The series has a unit root (non-stationary)")
print("ADF-Statistic:", adftest[0])
print("P-Value:", adftest[1])
print("Number of lags:", adftest[2])
print("Number of observations:", adftest[3])
print("Critical Values:", adftest[4])
print("Note: If P-Value is smaller than 0.05, we reject the null hypothesis and the series is stationary")