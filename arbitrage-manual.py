import math
import itertools


exchange_rates =  [
    [1, 0.48, 1.52, 0.71],
    [2.05, 1, 3.26, 1.56],
    [0.64, 0.3, 1, 0.46],
    [1.41, 0.61, 2.08, 1]
]

def maximize_return(exchange_rates):
    trades = 5
    currencies = len(exchange_rates)
    dp = [[0] * currencies for _ in range(trades + 1)]
    dp[0][3] = 1  # Base case

    for trade in range(1, trades + 1):
        for curr in range(currencies):
            max_return = 0
            for prev_curr in range(currencies):
                max_return = max(
                    max_return, dp[trade - 1][prev_curr] * exchange_rates[prev_curr][curr]
                )
            dp[trade][curr] = max_return

    # Backtrack to get the sequence of trades
    sequence = []
    curr = 3
    for trade in range(trades, 0, -1):
        for prev_curr in range(currencies):
            if dp[trade][curr] == dp[trade - 1][prev_curr] * exchange_rates[prev_curr][curr]:
                sequence.append((prev_curr, curr))
                curr = prev_curr
                break

    return dp[trades][3], sequence[::-1]  # Return highest return and sequence of trades

max_return, trade_sequence = maximize_return(exchange_rates)
print("Maximized return:", max_return)
print("Trade sequence:", trade_sequence)
    

