import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import adfuller
import statistics

df = pd.read_csv('round-3-island-data-bottle/prices_round_3_day_0.csv', delimiter=';')
df = df[['product', 'mid_price']]

prices = {'CHOCOLATE': [], 'STRAWBERRIES': [], 'ROSES': [], 'GIFT_BASKET': [], 'ETF': []}

for index, row in df.iterrows():
    product = row['product']
    mid_price = row['mid_price']
    prices[product].append(mid_price)

df = pd.read_csv('round-3-island-data-bottle/prices_round_3_day_1.csv', delimiter=';')
df = df[['product', 'mid_price']]
for index, row in df.iterrows():
    product = row['product']
    mid_price = row['mid_price']
    prices[product].append(mid_price)

df = pd.read_csv('round-3-island-data-bottle/prices_round_3_day_2.csv', delimiter=';')
df = df[['product', 'mid_price']]
for index, row in df.iterrows():
    product = row['product']
    mid_price = row['mid_price']
    prices[product].append(mid_price)

for i in range(len(prices['GIFT_BASKET'])):
    prices['ETF'].append(float(prices['STRAWBERRIES'][i]*6))

ETF = prices['ETF']
GIFT_BASKET = prices['GIFT_BASKET']

ratio = []
for i in range(len(ETF)):
   ratio.append(GIFT_BASKET[i] - ETF[i]) # i tried spread and ratio, but spread gave a slightly lower p-value so 
                                        # that means that there is a more stationary mean that we can trade around

print(statistics.mean(ratio))
print(statistics.stdev(ratio))

df = pd.DataFrame(ratio)


adftest = adfuller(df, autolag='AIC', regression='ct')
print("ADF Test Results")
print("Null Hypothesis: The series has a unit root (non-stationary)")
print("ADF-Statistic:", adftest[0])
print("P-Value:", adftest[1])
print("Number of lags:", adftest[2])
print("Number of observations:", adftest[3])
print("Critical Values:", adftest[4])
print("Note: If P-Value is smaller than 0.05, we reject the null hypothesis and the series is stationary")