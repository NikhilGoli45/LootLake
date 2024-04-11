from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle



class Trader:
    
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

				# Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
          if product == "AMETHYSTS":
            # make sure positions aren't cancelled
            result[product], _ = self.amethysts(state, product)
          if product == "STARFRUIT":
            result[product], traderData = self.starfruit(state, product) 

		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        # traderData = "SAMPLE" 

				# Sample conversion request. Check more details below. 
        conversions = 0
        # logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData

    def amethysts(self, state, product):
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

      return orders, None
    
    def starfruit(self, state, product):
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []
      # price = state.listings[product]
      price_sum = 0
      price_num = 0
      # name = state.listings[product]["symbol"]
      # ERROR: product is "STARFRUIT", which does not find the key
      for trade in state.own_trades[product]:
        price_sum += trade.price
        price_num += trade.quantity 
      try:
        traderObj = jsonpickle.decode(state.traderData)
      except:
         traderObj = MovingArray([], [])
      traderObj.add_price(float(price_sum)/float(price_num))

      acceptable_price = traderObj.get_avgs()[0]  # Participant should calculate this value
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
      return orders, jsonpickle.encode(traderObj)
    
class MovingArray(object):
    def __init__(self, arr9: list[float], arr20: list[float]):
      self.arr9 = arr9
      self.arr20 = arr20

    def add_price(self, price):
        self.arr9.append(float(price))
        if len(self.arr9) > 9:
          self.arr9.pop(0)

        self.arr20.append(float(price))
        if len(self.arr20) > 20:
            self.arr20.pop(0)

    def get_avgs(self):
        sum9 = 0
        sum20 = 0
        for i in self.arr9:
          sum9 += i
        for i in self.arr20:
          sum20 += i
        sum9 = sum9/len(self.arr9)
        sum20 = sum20/len(self.arr20)
        return (sum9, sum20)