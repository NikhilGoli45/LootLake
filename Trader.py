from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string



class Trader:
    
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

				# Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = 10000  # Participant should calculate this value
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

            MAX_BUY_MOVES = 20  # decreasing this will decrease profit. means this is not doing anything, our model is too simple
            MAX_SELL_MOVES = 20
            buy_moves = 0
            sell_moves = 0
            if len(order_depth.sell_orders) != 0:
                i = 0
                while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
                  best_ask, best_ask_amount = list(order_depth.sell_orders.items())[i]
                  # best_ask_amount is negative
                  if int(best_ask) < acceptable_price:
                      print("BUY", str(-best_ask_amount) + "x", best_ask)
                      buy_moves += -best_ask_amount
                      orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
                  i += 1

            if len(order_depth.buy_orders) != 0:
                i = 0
                while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
                  best_bid, best_bid_amount = list(order_depth.buy_orders.items())[i]
                  # best_bid_amount is postive
                  if int(best_bid) > acceptable_price:
                      print("SELL", str(best_bid_amount) + "x", best_bid)
                      sell_moves += best_bid_amount
                      orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
                  i += 1
            
            result[product] = orders
    
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE" 
        
				# Sample conversion request. Check more details below. 
        conversions = 0
        # logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData
