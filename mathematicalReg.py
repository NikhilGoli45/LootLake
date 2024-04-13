from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle
import statistics



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
    '''
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
            best_ask, best_ask_amount = list(sorted(order_depth.sell_orders.items()))[i]
            # best_ask_amount is negative
            if best_ask < acceptable_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                buy_moves += -best_ask_amount
                orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
            i += 1

      if len(order_depth.buy_orders) != 0:
          i = 0
          while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
            best_bid, best_bid_amount = list(sorted(order_depth.buy_orders.items(), reverse = True))[i]
            # best_bid_amount is postive
            if best_bid > acceptable_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                sell_moves += best_bid_amount
                orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
            i += 1
      return orders
      '''
    
    
    def starfruit(self, state, product):
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []
      
      try:
        traderObj = jsonpickle.decode(state.traderData)
      except:
        traderObj = MovingArray()

      try:
        position = state.position[product]
        MAX_BUY_MOVES = 20-position
        MAX_SELL_MOVES = -(-20-position)
      except: # position is 0 because no trades made yet
        MAX_BUY_MOVES = 20
        MAX_SELL_MOVES = 20
      
      price_sum = 0
      price_num = 0
      
      for x in state.order_depths[product].buy_orders:
        price_sum += abs(x*state.order_depths[product].buy_orders[x])
        price_num += abs(state.order_depths[product].buy_orders[x])
      for y in state.order_depths[product].sell_orders:
        price_sum += abs(-y*state.order_depths[product].sell_orders[y])
        price_num += abs(state.order_depths[product].sell_orders[y])
        
      traderObj.add_vals((float(price_sum)/float(price_num)), state.timestamp)
      acceptable_price = float(price_sum)/float(price_num)
      print(len(traderObj.arr5))
      buy_moves = 0
      sell_moves = 0

      if len(traderObj.arr5) != 5:
        
        if len(order_depth.sell_orders) != 0:
            i = 0
            while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
              best_ask, best_ask_amount = list((order_depth.sell_orders.items()))[i]
              # best_ask_amount is negative
              if best_ask < acceptable_price:
                  print("BUY", str(-best_ask_amount) + "x", best_ask)
                  buy_moves += -best_ask_amount
                  orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
              i += 1

        if len(order_depth.buy_orders) != 0:
            i = 0
            while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
              best_bid, best_bid_amount = list((order_depth.buy_orders.items()))[i]
              # best_bid_amount is postive
              if best_bid > acceptable_price:
                  print("SELL", str(best_bid_amount) + "x", best_bid)
                  sell_moves += best_bid_amount
                  orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
              i += 1
      else:
        print("We make LR trades!")
        predicted_price = traderObj.predictSF(state.timestamp)
        
        if predicted_price > acceptable_price:
          if len(order_depth.sell_orders) != 0:
            i = 0
            while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
              best_ask, best_ask_amount = list(sorted(order_depth.sell_orders.items()))[i]
              if best_ask < predicted_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                buy_moves += -best_ask_amount
                orders.append(Order(product, best_ask, min(MAX_BUY_MOVES,-best_ask_amount)))
              i += 1

        if predicted_price < acceptable_price:
          if len(order_depth.buy_orders) != 0:
            i = 0
            while(sell_moves <= MAX_SELL_MOVES and i < len(order_depth.buy_orders)):
              best_bid, best_bid_amount = list(sorted(order_depth.buy_orders.items(), reverse = True))[i]
              if best_bid > predicted_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                sell_moves += best_bid_amount
                orders.append(Order(product, best_bid, max(-MAX_SELL_MOVES,-best_bid_amount)))
              i += 1

      return orders, jsonpickle.encode(traderObj)

class MovingArray(object):
    def __init__(self):
      self.beta_1 = 0
      self.beta_0 = 0
      self.arr5 = []
      self.time5 = []

    def add_vals(self, price, time):
        self.arr5.append(float(price))
        self.time5.append(float(time))

        if len(self.arr5) > 5:
          self.arr5.pop(0)

        if len(self.time5) > 5:
          self.time5.pop(0)

    def trainModel(self, m_now, b_now):
      m_gradient = 0
      b_gradient = 0
      learning_rate = 0.1
      
      n = len(self.arr5)
      
      for i in range (5):
        x = self.time5
        y = self.arr5

        m_gradient += -(2/n) * x[i] * (y[i] - (m_now * x[i] + b_now))
        b_gradient += -(2/n) * (y[i] - (m_now * x[i] + b_now))

      m = m_now - m_gradient * learning_rate
      b = m_now - b_gradient * learning_rate
      return m, b
         

    def predictSF(self, current_feature: float) -> float:
      m = 0 
      b = 0
      epochs = 10
      for i in range(epochs):
         m, b = self.trainModel(m, b)
      
      pred = (m*current_feature) + b
      return pred
         

    