<<<<<<< HEAD
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle
import statistics
import numpy as np



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

		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        # traderData = "SAMPLE" 

				# Sample conversion request. Check more details below. 
        conversions = 0
        # logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData
    
    def amethysts(self, state, product):
        
        order_depth: OrderDepth = state.order_depths[product]
        orders: list[Order] = []
        """
        cpos = state.position.get('AMETHYSTS', 0)

        osell = order_depth.sell_orders
        obuy = order_depth.buy_orders

        sell_vol, best_sell_pr = self.values_extract(osell)
        buy_vol, best_buy_pr = self.values_extract(obuy, 1)

        mx_with_buy = -1

        for ask, vol in osell.items():
            if ((ask < 10000) or ((cpos<0) and (ask == 10000))) and cpos < 20:
                mx_with_buy = max(mx_with_buy, ask)
                order_for = min(-vol, 20 - cpos)
                cpos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        mprice_actual = (best_sell_pr + best_buy_pr)/2
        mprice_ours = (10000+10000)/2

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, 10000-1) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, 10000+1)

        if (cpos < 20) and (state.position.get('AMETHYSTS', 0) < 0):
            num = min(40, 20 - cpos)
            orders.append(Order(product, min(undercut_buy + 1, 10000-1), num))
            cpos += num

        if (cpos < 20) and (state.position.get('AMETHYSTS', 0) > 15):
            num = min(40, 20 - cpos)
            orders.append(Order(product, min(undercut_buy - 1, 10000-1), num))
            cpos += num

        if cpos < 20:
            num = min(40, 20 - cpos)
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = state.position.get('AMETHYSTS', 0)

        for bid, vol in obuy.items():
            if ((bid > 10000) or ((state.position.get('AMETHYSTS', 0)>0) and (bid == 10000))) and cpos > -20:
                order_for = max(-vol, -20-cpos)
                # order_for is a negative number denoting how much we will sell
                cpos += order_for
                assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if (cpos > -20) and (state.position.get('AMETHYSTS', 0) > 0):
            num = max(-40, -20-cpos)
            orders.append(Order(product, max(undercut_sell-1, 10000+1), num))
            cpos += num

        if (cpos > -20) and (state.position.get('AMETHYSTS', 0) < -15):
            num = max(-40, -20-cpos)
            orders.append(Order(product, max(undercut_sell+1, 10000+1), num))
            cpos += num

        if cpos > -20:
            num = max(-40, -20-cpos)
            orders.append(Order(product, sell_pr, num))
            cpos += num
        """
        return orders, None
    
    def values_extract(self, order_dict, buy=0):
        tot_vol = 0
        best_val = -1
        mxvol = -1

        for ask, vol in order_dict.items():
            if(buy==0):
                vol *= -1
            tot_vol += vol
            if tot_vol > mxvol:
                mxvol = vol
                best_val = ask
        
        return tot_vol, best_val

    def starfruit(self, state, product):
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []
      
      try:
        traderObj = jsonpickle.decode(state.traderData)
      except:
        traderObj = MovingArray([], [])

      try:
        position = state.position[product]
        MAX_BUY_MOVES = 20-position
        MAX_SELL_MOVES = -(-20-position)
      except: # position is 0 because no trades made yet
        MAX_BUY_MOVES = 20
        MAX_SELL_MOVES = 20
      
      price_sum = 0
      price_num = 0


      #actual price
      for x in state.order_depths[product].buy_orders:
        price_sum += abs(x*state.order_depths[product].buy_orders[x])
        price_num += abs(state.order_depths[product].buy_orders[x])
      for y in state.order_depths[product].sell_orders:
        price_sum += abs(-y*state.order_depths[product].sell_orders[y])
        price_num += abs(state.order_depths[product].sell_orders[y])

      #adds actual price and time to moving array  
      traderObj.add_vals((float(price_sum)/float(price_num)), state.timestamp)

      acceptable_price = float(price_sum)/float(price_num)

      buy_moves = 0
      sell_moves = 0

      # print("BUY ORDERS: ", order_depth.buy_orders)
      # totval, bestval = self.values_extract(order_depth.buy_orders, 1)
      # print("result buy order", totval, bestval)

      # print("SELL ORDERS: ", order_depth.sell_orders)
      # totval2, bestval2 = self.values_extract(order_depth.sell_orders, 0)
      # print("result sell order", totval2, bestval2)

      # print(acceptable_price, "BUY ORDERS: ", order_depth.buy_orders, "SELL ORDERS: ", order_depth.sell_orders)

      size = 3
      if len(traderObj.arr5) < size:
        if len(order_depth.sell_orders) != 0:
            i = 0
            while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
              best_ask, best_ask_amount = list((order_depth.sell_orders.items()))[i]
              # best_ask_amount is negative
              if best_ask < acceptable_price:
                  print("BUY", str(-best_ask_amount) + "x", best_ask, order_depth.sell_orders)
                  
                  buy_moves += -best_ask_amount
                  orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
              i += 1

        if len(order_depth.buy_orders) != 0:
            i = 0
            while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
              best_bid, best_bid_amount = list((order_depth.buy_orders.items()))[i]
              # best_bid_amount is postive
              if best_bid > acceptable_price:
                  print("SELL", str(best_bid_amount) + "x", best_bid, order_depth.buy_orders)
                  sell_moves += best_bid_amount
                  orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
              i += 1
      else:
        predicted_price = traderObj.linearRegression()


        osell = order_depth.sell_orders
        obuy = order_depth.buy_orders

        sell_vol, best_sell_pr = self.values_extract(order_depth.sell_orders)
        buy_vol, best_buy_pr = self.values_extract(order_depth.buy_orders, 1)


        predicted_lower = predicted_price-1
        predicted_upper = predicted_price+1

        cpos = state.position.get('STARFRUIT', 0)

        

        for ask, vol in osell.items():
          if (((ask <= predicted_lower) or ((state.position.get('STARFRUIT', 0)<0) and 
                                    (ask == predicted_price))) and cpos < 20):
            place = min(-vol, 20-cpos)
            cpos += place
            orders.append(Order(product, ask, place))

        undercut_buy = best_buy_pr + 1 #
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, predicted_lower) # we will shift this by 1 to beat this price
        # greatest in buy book +1 , 
        sell_pr = max(undercut_sell, predicted_upper)

        if cpos < 20:
            num = 20 - cpos
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = state.position.get('STARFRUIT', 0)
        
        for bid, vol in obuy.items():
           if (((bid >= predicted_upper) or ((state.position.get('STARFRUIT', 0)>0) and 
                                  (bid+1 == predicted_upper))) and cpos > -20):
              place = max(-vol, -20-cpos)
              cpos += place
              orders.append(Order(product, bid, place))

        if cpos > -20:
            num = -20-cpos
            orders.append(Order(product, sell_pr, num))
            cpos += num

        # if predicted_price > acceptable_price:
        #   # print("HELLO")
        #   if len(order_depth.sell_orders) != 0:
        #     i = 0
        #     while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
        #       best_ask, best_ask_amount = list(sorted(order_depth.sell_orders.items()))[i]
        #       if best_ask < predicted_price:
        #         print("BUY", str(-best_ask_amount) + "x", best_ask, order_depth.sell_orders)
        #         buy_moves += -best_ask_amount
        #         orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
        #       i += 1

        # if predicted_price < acceptable_price:
        #   if len(order_depth.buy_orders) != 0:
        #     i = 0
        #     while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
        #       best_bid, best_bid_amount = list(sorted(order_depth.buy_orders.items(), reverse = True))[i]
        #       if best_bid > predicted_price:
        #         print("SELL", str(best_bid_amount) + "x", best_bid, order_depth.buy_orders)
        #         sell_moves += best_bid_amount
        #         orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
        #       i += 1

      return orders, jsonpickle.encode(traderObj)

class MovingArray(object):
    def __init__(self, arr5: list[float], time5: list[float]):
      self.arr5 = arr5
      self.time5 = time5


    def add_vals(self, price, time):
        self.arr5.append(float(price))
        self.time5.append(float(time))
        size = 3
        if len(self.arr5) > size:
          self.arr5.pop(0)

        if len(self.time5) > size:
          self.time5.pop(0)

    def linearRegression(self):
      #sumX, sumY, sumXY, sumXSquared = 0
      sumX = sum(self.time5)
      sumY = sum(self.arr5)

      sumXY = 0
      sumXSquared = 0
      for i in range(len(self.arr5)):
         XY = self.arr5[i] * self.time5[i]
         xSquared = self.arr5[i] ** 2
         sumXY += XY
         sumXSquared += xSquared
      
      n = len(self.arr5)

      slope =  (n * sumXY - sumX*sumY)/(n*sumXSquared - sumX**2)

      intercept = (sumY - slope*sumX)/n

      #y = m*x + b
      predictedValue = slope * (self.time5[-1] + 100) + intercept
      return predictedValue
=======
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle
import statistics
import numpy as np



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

		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        # traderData = "SAMPLE" 

				# Sample conversion request. Check more details below. 
        conversions = 0
        # logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData
    def amethysts(self, state, product):
        
        order_depth: OrderDepth = state.order_depths[product]
        orders: list[Order] = []

        cpos = state.position.get('AMETHYSTS', 0)

        osell = order_depth.sell_orders
        obuy = order_depth.buy_orders

        sell_vol, best_sell_pr = self.values_extract(osell)
        buy_vol, best_buy_pr = self.values_extract(obuy, 1)

        mx_with_buy = -1

        for ask, vol in osell.items():
            if ((ask < 10000) or ((cpos<0) and (ask == 10000))) and cpos < 20:
                mx_with_buy = max(mx_with_buy, ask)
                order_for = min(-vol, 20 - cpos)
                cpos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        mprice_actual = (best_sell_pr + best_buy_pr)/2
        mprice_ours = (10000+10000)/2

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, 10000-1) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, 10000+1)

        if (cpos < 20) and (state.position.get('AMETHYSTS', 0) < 0):
            num = min(40, 20 - cpos)
            orders.append(Order(product, min(undercut_buy + 1, 10000-1), num))
            cpos += num

        if (cpos < 20) and (state.position.get('AMETHYSTS', 0) > 15):
            num = min(40, 20 - cpos)
            orders.append(Order(product, min(undercut_buy - 1, 10000-1), num))
            cpos += num

        if cpos < 20:
            num = min(40, 20 - cpos)
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = state.position.get('AMETHYSTS', 0)

        for bid, vol in obuy.items():
            if ((bid > 10000) or ((state.position.get('AMETHYSTS', 0)>0) and (bid == 10000))) and cpos > -20:
                order_for = max(-vol, -20-cpos)
                # order_for is a negative number denoting how much we will sell
                cpos += order_for
                assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if (cpos > -20) and (state.position.get('AMETHYSTS', 0) > 0):
            num = max(-40, -20-cpos)
            orders.append(Order(product, max(undercut_sell-1, 10000+1), num))
            cpos += num

        if (cpos > -20) and (state.position.get('AMETHYSTS', 0) < -15):
            num = max(-40, -20-cpos)
            orders.append(Order(product, max(undercut_sell+1, 10000+1), num))
            cpos += num

        if cpos > -20:
            num = max(-40, -20-cpos)
            orders.append(Order(product, sell_pr, num))
            cpos += num
        return orders, None
    
    def values_extract(self, order_dict, buy=0):
        tot_vol = 0
        best_val = -1
        mxvol = -1

        for ask, vol in order_dict.items():
            if(buy==0):
                vol *= -1
            tot_vol += vol
            if tot_vol > mxvol:
                mxvol = vol
                best_val = ask
        
        return tot_vol, best_val

    def starfruit(self, state, product):
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []
      
      try:
        traderObj = jsonpickle.decode(state.traderData)
      except:
        traderObj = MovingArray([], [])

      try:
        position = state.position[product]
        MAX_BUY_MOVES = 20-position
        MAX_SELL_MOVES = -(-20-position)
      except: # position is 0 because no trades made yet
        MAX_BUY_MOVES = 20
        MAX_SELL_MOVES = 20
      
      price_sum = 0
      price_num = 0


      #actual price
      for x in state.order_depths[product].buy_orders:
        price_sum += abs(x*state.order_depths[product].buy_orders[x])
        price_num += abs(state.order_depths[product].buy_orders[x])
      for y in state.order_depths[product].sell_orders:
        price_sum += abs(-y*state.order_depths[product].sell_orders[y])
        price_num += abs(state.order_depths[product].sell_orders[y])

      #adds actual price and time to moving array  
      traderObj.add_vals((float(price_sum)/float(price_num)), state.timestamp)

      acceptable_price = float(price_sum)/float(price_num)

      buy_moves = 0
      sell_moves = 0

      # print("BUY ORDERS: ", order_depth.buy_orders)
      # totval, bestval = self.values_extract(order_depth.buy_orders, 1)
      # print("result buy order", totval, bestval)

      # print("SELL ORDERS: ", order_depth.sell_orders)
      # totval2, bestval2 = self.values_extract(order_depth.sell_orders, 0)
      # print("result sell order", totval2, bestval2)

      # print(acceptable_price, "BUY ORDERS: ", order_depth.buy_orders, "SELL ORDERS: ", order_depth.sell_orders)

      size = 3
      if len(traderObj.arr5) < size:
        if len(order_depth.sell_orders) != 0:
            i = 0
            while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
              best_ask, best_ask_amount = list((order_depth.sell_orders.items()))[i]
              # best_ask_amount is negative
              if best_ask < acceptable_price:
                  print("BUY", str(-best_ask_amount) + "x", best_ask, order_depth.sell_orders)
                  
                  buy_moves += -best_ask_amount
                  orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
              i += 1

        if len(order_depth.buy_orders) != 0:
            i = 0
            while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
              best_bid, best_bid_amount = list((order_depth.buy_orders.items()))[i]
              # best_bid_amount is postive
              if best_bid > acceptable_price:
                  print("SELL", str(best_bid_amount) + "x", best_bid, order_depth.buy_orders)
                  sell_moves += best_bid_amount
                  orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
              i += 1
      else:
        predicted_price = traderObj.linearRegression()


        osell = order_depth.sell_orders
        obuy = order_depth.buy_orders

        sell_vol, best_sell_pr = self.values_extract(order_depth.sell_orders)
        buy_vol, best_buy_pr = self.values_extract(order_depth.buy_orders, 1)


        predicted_lower = predicted_price-1
        predicted_upper = predicted_price+1

        cpos = state.position.get('STARFRUIT', 0)

        

        for ask, vol in osell.items():
          if (((ask <= predicted_lower) or ((state.position.get('STARFRUIT', 0)<0) and 
                                    (ask == predicted_price))) and cpos < 20):
            place = min(-vol, 20-cpos)
            cpos += place
            orders.append(Order(product, ask, place))

        undercut_buy = best_buy_pr + 1 #
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, predicted_lower) # we will shift this by 1 to beat this price
        # greatest in buy book +1 , 
        sell_pr = max(undercut_sell, predicted_upper)

        if cpos < 20:
            num = 20 - cpos
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = state.position.get('STARFRUIT', 0)
        
        for bid, vol in obuy.items():
           if (((bid >= predicted_upper) or ((state.position.get('STARFRUIT', 0)>0) and 
                                  (bid+1 == predicted_upper))) and cpos > -20):
              place = max(-vol, -20-cpos)
              cpos += place
              orders.append(Order(product, bid, place))

        if cpos > -20:
            num = -20-cpos
            orders.append(Order(product, sell_pr, num))
            cpos += num

        # if predicted_price > acceptable_price:
        #   # print("HELLO")
        #   if len(order_depth.sell_orders) != 0:
        #     i = 0
        #     while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
        #       best_ask, best_ask_amount = list(sorted(order_depth.sell_orders.items()))[i]
        #       if best_ask < predicted_price:
        #         print("BUY", str(-best_ask_amount) + "x", best_ask, order_depth.sell_orders)
        #         buy_moves += -best_ask_amount
        #         orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
        #       i += 1

        # if predicted_price < acceptable_price:
        #   if len(order_depth.buy_orders) != 0:
        #     i = 0
        #     while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
        #       best_bid, best_bid_amount = list(sorted(order_depth.buy_orders.items(), reverse = True))[i]
        #       if best_bid > predicted_price:
        #         print("SELL", str(best_bid_amount) + "x", best_bid, order_depth.buy_orders)
        #         sell_moves += best_bid_amount
        #         orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
        #       i += 1

      return orders, jsonpickle.encode(traderObj)

class MovingArray(object):
    def __init__(self, arr5: list[float], time5: list[float]):
      self.arr5 = arr5
      self.time5 = time5


    def add_vals(self, price, time):
        self.arr5.append(float(price))
        self.time5.append(float(time))
        size = 3
        if len(self.arr5) > size:
          self.arr5.pop(0)

        if len(self.time5) > size:
          self.time5.pop(0)

    def linearRegression(self):
      #sumX, sumY, sumXY, sumXSquared = 0
      sumX = sum(self.time5)
      sumY = sum(self.arr5)

      sumXY = 0
      sumXSquared = 0
      for i in range(len(self.arr5)):
         XY = self.arr5[i] * self.time5[i]
         xSquared = self.arr5[i] ** 2
         sumXY += XY
         sumXSquared += xSquared
      
      n = len(self.arr5)

      slope =  (n * sumXY - sumX*sumY)/(n*sumXSquared - sumX**2)

      intercept = (sumY - slope*sumX)/n

      #y = m*x + b
      predictedValue = slope * (self.time5[-1] + 100) + intercept
      return predictedValue


    def orchidArbitrage(self, state: TradingState, acceptable_price : float) -> int:
      #assume that there is a nonzero position if this function is called
      currPos = state.position
      product = "ORCHIDS"
      conversionObservation = state.observations.conversionObservations[product]
      if currPos < 0:
          valAfterCosts = conversionObservation.askPrice + conversionObservation.transportFees + conversionObservation.importTariff
          if valAfterCosts < acceptable_price:
              return 100 + currPos

      else:
          valAfterCosts = conversionObservation.bidPrice - conversionObservation.transportFees - conversionObservation.exportTariff
          if valAfterCosts > acceptable_price:
              return currPos 
      
      return 0
>>>>>>> ff859d8876262e7391443eff92824df4080a8c97
