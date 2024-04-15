import matplotlib.pyplot as plt
import pandas as pd



df1 = pd.read_csv("round2day-1.csv", sep=";")
df2 = pd.read_csv("round2day0.csv",sep=";")
df3 = pd.read_csv("round2day1.csv",sep=";")

df1["SMA100"] = df1["ORCHIDS"].rolling(100).mean()

plt.plot(df1["timestamp"], df1["SMA100"])
plt.show()