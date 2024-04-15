from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle



class Trader:
    
    def run(self, state: TradingState):
        #print("traderData: " + state.traderData)
        #print("Observations: " + str(state.observations))

				# Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            if product == "AMETHYSTS":
                # make sure positions aren't cancelled
                result[product], _ = self.amethysts(state, product)
            if product == "STARFRUIT":
                result[product], traderData = self.starfruit(state, product) 
            if product == "ORCHIDS":
                continue



        conversions = 1
        # logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData

    def amethysts(self, state, product):
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []
      acceptable_price = 10000.0  # Participant should calculate this value

      print("Acceptable price : " + str(acceptable_price))
      print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
  
      try:
        position = state.position[product]
        MAX_BUY_MOVES = 20-position
        MAX_SELL_MOVES = -(-20-position)
      except: # position is 0 because no trades made yet
        MAX_BUY_MOVES = 20
        MAX_SELL_MOVES = 20
      buy_moves = 0
      sell_moves = 0
      
      """
      # IN PROGRESS: increase amount we can trade and stay within limits
      buy_sum = 0
      sell_sum = 0
      for item in list(order_depth.sell_orders.items()):
          if int(item[0]) < acceptable_price:
            buy_sum += -item[1]
      for item in list(order_depth.buy_orders.items()):
          if int(item[0]) > acceptable_price:
            sell_sum += item[1]
      MAX_BUY_MOVES += abs(min(buy_sum, sell_sum))
      MAX_SELL_MOVES += abs(min(buy_sum, sell_sum))
      print("PRINTING: ")
      print(MAX_BUY_MOVES)
      print(MAX_SELL_MOVES)
      """

      if len(order_depth.sell_orders) != 0:  # check not necessary
          i = 0
          while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[i]
            # best_ask_amount is negative
            if best_ask < acceptable_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                buy_moves += -best_ask_amount
                orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
            i += 1

      if len(order_depth.buy_orders) != 0:
          i = 0
          while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[i]
            # best_bid_amount is postive
            if best_bid > acceptable_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                sell_moves += best_bid_amount
                orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
            i += 1

      return orders
    
    def starfruit(self, state, product):
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []

      price_sum = 0
      price_num = 0
      if state.market_trades:
        for trade in state.market_trades[product]:
          price_sum += trade.price*trade.quantity
          price_num += trade.quantity
      for x in state.order_depths[product].buy_orders:
        price_sum += abs(x*state.order_depths[product].buy_orders[x])
        price_num += abs(state.order_depths[product].buy_orders[x])
      for y in state.order_depths[product].sell_orders:
        price_sum += abs(-y*state.order_depths[product].sell_orders[y])
        price_num += abs(state.order_depths[product].sell_orders[y])

      acceptable_price = float(price_sum/price_num)  # want to calculate smth more accurate
      print("Acceptable price : " + str(acceptable_price))
      print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

      try:
        position = state.position[product]
        MAX_BUY_MOVES = abs(20-position)
        MAX_SELL_MOVES = abs(-20-position)
      except: # position is 0 because no trades made yet
        MAX_BUY_MOVES = 20
        MAX_SELL_MOVES = 20
      buy_moves = 0
      sell_moves = 0

      if len(order_depth.sell_orders) != 0:
          i = 0
          while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[i]
            # best_ask_amount is negative
            if best_ask < acceptable_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                buy_moves += -best_ask_amount
                orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
            i += 1

      if len(order_depth.buy_orders) != 0:
          i = 0
          while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[i]
            # best_bid_amount is postive
            if best_bid > acceptable_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                sell_moves += best_bid_amount
                orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
            i += 1
      return orders


    #returns the number of conversions to be done
    def orchidArbitrage(self, state: TradingState, acceptable_price : float) -> int:
       #assume that there is a nonzero position if this function is called
        currPos = state.position
        product = "ORCHIDS"
        conversionObservation = state.observations.conversionObservations[product]
        if currPos < 0:
            valAfterCosts = conversionObservation.askPrice + conversionObservation.transportFees + conversionObservation.importTariff
            if valAfterCosts < acceptable_price:
               return -currPos

        else:
            valAfterCosts = conversionObservation.bidPrice - conversionObservation.transportFees - conversionObservation.exportTariff
            if valAfterCosts > acceptable_price:
               return currPos 
        
        return 0