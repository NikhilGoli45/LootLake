from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
from collections import OrderedDict
import string
import jsonpickle
import statistics
import numpy as np
import math



class Trader:

    basket_std = 76
    coconut_std = 1
    basket_mean = 380
    coconut_mean = 15.9

    
    def run(self, state: TradingState):
        #print("traderData: " + state.traderData)
        #print("Observations: " + str(state.observations))

				# Orders to be placed on exchange matching engine
        result = {}
        try:
          traderObj = jsonpickle.decode(state.traderData)
        except:
          traderObj = MovingArray([], [], [], [])

        print(traderObj.arr5)
        conversions = 0
        for product in state.order_depths:
          if product == "AMETHYSTS":
            # make sure positions aren't cancelled
            result[product] = self.amethysts(state, product)
          elif product == "STARFRUIT":
            result[product] = self.starfruit(state, product, traderObj) 
          elif product == "ORCHIDS":
            result[product], conversions = self.orchid(state, product)
          elif product == "GIFT_BASKET":
            result[product] = self.gift_basket(state)
          elif product == "COCONUT_COUPON":
            result['COCONUT'], result['COCONUT_COUPON'] = self.coupon(state)
          
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        traderData = jsonpickle.encode(traderObj) 
        
        # logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData

    def amethysts(self, state, product):
      order_depth: OrderDepth = state.order_depths[product]
      orders: list[Order] = []

      sells = sorted(order_depth.sell_orders.items())
      buys = sorted(order_depth.buy_orders.items(), reverse=True)

      sellq = 0
      sellp = -1
      maxq = -1
      for ask, quantity in sells:
        sellq -= quantity
        if sellq > maxq:
          maxq = quantity
          sellp = ask
      
      buyq = 0
      buyp = -1
      maxq = -1
      for ask, quantity in buys:
        buyq += quantity
        if buyq > maxq:
          maxq = quantity
          buyp = ask

      try:
        position = state.position[product]
        current_pos = state.position[product]
      except:
        position = 0
        current_pos = 0

      max_price = -1
      for ask, quanity in sells:
        if ((ask < 10000) or ((position < 0) and (ask == 10000))) and current_pos < 20:
          max_price = max(max_price, ask)
          amount = min(-quanity, 20 - current_pos)
          current_pos += amount
          orders.append(Order(product, ask, amount))

      current_price = (sellp + buyp)/2

      bid = min(buyp + 1, 9999)
      ask = max(sellp - 1, 10001)

      if (current_pos < 20) and (position < 0):
        amount = min(40, 20 - current_pos)
        orders.append(Order(product, min(buyp + 2, 9999), amount))
        current_pos += amount

      if (current_pos < 20) and (position > 15):
        amount = min(40, 20 - current_pos)
        orders.append(Order(product, min(buyp, 9999), amount))
        current_pos += amount

      if current_pos < 20:
          amount = min(40, 20 - current_pos)
          orders.append(Order(product, bid, amount))
          current_pos += amount
          
      current_pos = position

      for bid, vol in buys:
        if ((bid > 10000) or ((position > 0) and (bid == 10000))) and current_pos > -20:
          amount = max(-vol, -20-current_pos)
          current_pos += amount
          orders.append(Order(product, bid, amount))

      if (current_pos > -20) and (position > 0):
        amount = max(-40, -20 - current_pos)
        orders.append(Order(product, max(sellp - 2, 10001), amount))
        current_pos += amount

      if (current_pos > -20) and (position < -15):
        amount = max(-40, -20 - current_pos)
        orders.append(Order(product, max(sellp, 10001), amount))
        current_pos += amount

      if current_pos > -20:
        amount = max(-40, -20 - current_pos)
        orders.append(Order(product, ask, amount))
        current_pos += amount

      return orders

    
    def starfruit(self, state, product, traderObj):
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []

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


        sells = order_depth.sell_orders.items()
        buys = order_depth.buy_orders.items()

        sellq = 0
        sellp = -1
        maxq = -1
        for ask, quantity in sells:
          sellq -= quantity
          if sellq > maxq:
            maxq = quantity
            sellp = ask
        
        buyq = 0
        buyp = -1
        maxq = -1
        for ask, quantity in buys:
          buyq += quantity
          if buyq > maxq:
            maxq = quantity
            buyp = ask


        predicted_lower = predicted_price-1
        predicted_upper = predicted_price+1

        position = state.position.get('STARFRUIT', 0)
        current_pos = state.position.get('STARFRUIT', 0)


        for ask, quantity in sells:
          if (((ask <= predicted_lower) or ((position<0) and 
                                    (ask == predicted_price))) and current_pos < 20):
            amount = min(-quantity, 20-current_pos)
            current_pos += amount
            orders.append(Order(product, ask, amount))


        bid_price = min(buyp + 1, predicted_lower)
        ask_price = max(sellp - 1, predicted_upper)

        if current_pos < 20:
            amount = 20 - current_pos
            orders.append(Order(product, bid_price, amount))
            current_pos += amount
        
        current_pos = position
        
        for bid, quantity in buys:
           if (((bid >= predicted_upper) or ((position>0) and 
                                  (bid+1 == predicted_upper))) and current_pos > -20):
              amount = max(-quantity, -20-current_pos)
              current_pos += amount
              orders.append(Order(product, bid, amount))

        if current_pos > -20:
            amount = -20-current_pos
            orders.append(Order(product, ask_price, amount))
            current_pos += amount

      return orders
    
    def orchid(self, state, product):
        order_depth: OrderDepth = state.order_depths[product]
        orders: List[Order] = []

        conversions = -state.position.get('ORCHIDS', 0)

        BUFFER = 2
        BREAK_EVEN = state.observations.conversionObservations['ORCHIDS'].askPrice + state.observations.conversionObservations['ORCHIDS'].importTariff + BUFFER
        SELL_PRICE = max(state.observations.conversionObservations['ORCHIDS'].askPrice - 2, BREAK_EVEN)

        orders.append(Order('ORCHIDS', int(SELL_PRICE), -100))

        return orders, conversions
    
    def gift_basket(self, state):

        POSITION_LIMIT = {'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60}
        orders = []

        goods = ['CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET']
        available_sells, available_buys, best_ask, best_bid, worst_ask, worst_bid, mid_price, available_buyq, available_sellq = {}, {}, {}, {}, {}, {}, {}, {}, {}
        
        for item in goods:
            available_sells[item] = OrderedDict(sorted(state.order_depths[item].sell_orders.items()))
            available_buys[item] = OrderedDict(sorted(state.order_depths[item].buy_orders.items(), reverse=True))

            best_ask[item] = next(iter(available_sells[item]))
            best_bid[item] = next(iter(available_buys[item]))

            worst_ask[item] = next(reversed(available_sells[item]))
            worst_bid[item] = next(reversed(available_buys[item]))

            mid_price[item] = (best_ask[item] + best_bid[item])//2
            available_buyq[item], available_sellq[item] = 0, 0
            for price, quantity in available_buys[item].items():
                available_buyq[item] += quantity 
                if available_buyq[item] >= POSITION_LIMIT[item]/10:
                    break
            for price, quantity in available_sells[item].items():
                available_sellq[item] += -quantity 
                if available_sellq[item] >= POSITION_LIMIT[item]/10:
                    break
        

        buy_baskets = mid_price['GIFT_BASKET'] - (mid_price['CHOCOLATE']*4) - (mid_price['STRAWBERRIES']*6) - mid_price['ROSES'] - self.basket_mean
        sell_baskets = mid_price['GIFT_BASKET'] - (mid_price['CHOCOLATE']*4) - (mid_price['STRAWBERRIES']*6) - mid_price['ROSES'] - self.basket_mean

        trade_at = self.basket_std*0.5


        if sell_baskets > trade_at:
            vol = state.position.get('GIFT_BASKET', 0) + 60
            if vol > 0:
                orders.append(Order('GIFT_BASKET', worst_bid['GIFT_BASKET'], -vol)) 
        elif buy_baskets < -trade_at:
            vol = 60 - state.position.get('GIFT_BASKET', 0)
            if vol > 0:
                orders.append(Order('GIFT_BASKET', worst_ask['GIFT_BASKET'], vol))

        return orders

    def roses(self, state, product, traderObj):
      order_depth: OrderDepth = state.order_depths[product]
      orders: List[Order] = []

      try:
        position = state.position[product]
        MAX_BUY_MOVES = 60-position
        MAX_SELL_MOVES = -(-60-position)
      except: # position is 0 because no trades made yet
        MAX_BUY_MOVES = 60
        MAX_SELL_MOVES = 60
      
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
      traderObj.add_vals_roses((float(price_sum)/float(price_num)), state.timestamp)

      acceptable_price = float(price_sum)/float(price_num)

      buy_moves = 0
      sell_moves = 0

      print(order_depth.sell_orders)
      print(order_depth.buy_orders)

      size = 2
      if len(traderObj.rose5) < size:
        if len(order_depth.sell_orders) != 0:
            i = 0
            while(buy_moves <= MAX_BUY_MOVES and i < len(order_depth.sell_orders)):
              best_ask, best_ask_amount = list((order_depth.sell_orders.items()))[i]
              # best_ask_amount is negative
              print(str(best_ask) + "    " + str(acceptable_price))
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
        predicted_price = int(traderObj.linearRegressionStrawberry())


        sells = order_depth.sell_orders.items()
        buys = order_depth.buy_orders.items()

        sellq = 0
        sellp = -1
        maxq = -1
        for ask, quantity in sells:
          sellq -= quantity
          if sellq > maxq:
            maxq = quantity
            sellp = ask
        
        buyq = 0
        buyp = -1
        maxq = -1
        for ask, quantity in buys:
          buyq += quantity
          if buyq > maxq:
            maxq = quantity
            buyp = ask


        predicted_lower = predicted_price-1
        predicted_upper = predicted_price+1

        position = state.position.get('CHOCOLATE', 0)
        current_pos = state.position.get('CHOCOLATE', 0)


        for ask, quantity in sells:
          if (((ask <= predicted_lower) or ((position<0) and 
                                    (ask == predicted_price))) and current_pos < 60):
            amount = min(-quantity, 60-current_pos)
            current_pos += amount
            orders.append(Order(product, ask, amount))


        bid_price = min(buyp + 1, predicted_lower)
        ask_price = max(sellp - 1, predicted_upper)

        if current_pos < 60:
            amount = 60 - current_pos
            orders.append(Order(product, bid_price, amount))
            current_pos += amount
        
        current_pos = position
        
        for bid, quantity in buys:
           if (((bid >= predicted_upper) or ((position>0) and 
                                  (bid+1 == predicted_upper))) and current_pos > -60):
              amount = max(-quantity, -60-current_pos)
              current_pos += amount
              orders.append(Order(product, bid, amount))

        if current_pos > -60:
            amount = -60-current_pos
            orders.append(Order(product, ask_price, amount))
            current_pos += amount

      return orders

    
    def coconut(self, state):
      orders = {'COCONUT': [], 'COCONUT_COUPON': []}
      POSITION_LIMIT = {'COCONUT': 300, 'COCONUT_COUPON': 600}

      goods = ['COCONUT', 'COCONUT_COUPON']
      available_sells, available_buys, best_ask, best_bid, worst_ask, worst_bid, mid_price, available_buyq, available_sellq = {}, {}, {}, {}, {}, {}, {}, {}, {}
        
      for item in goods:
          available_sells[item] = OrderedDict(sorted(state.order_depths[item].sell_orders.items()))
          available_buys[item] = OrderedDict(sorted(state.order_depths[item].buy_orders.items(), reverse=True))

          best_ask[item] = next(iter(available_sells[item]))
          best_bid[item] = next(iter(available_buys[item]))

          worst_ask[item] = next(reversed(available_sells[item]))
          worst_bid[item] = next(reversed(available_buys[item]))

          mid_price[item] = (best_ask[item] + best_bid[item])//2
          available_buyq[item], available_sellq[item] = 0, 0
          for price, quantity in available_buys[item].items():
              available_buyq[item] += quantity 
              if available_buyq[item] >= POSITION_LIMIT[item]/10:
                  break
          for price, quantity in available_sells[item].items():
              available_sellq[item] += -quantity 
              if available_sellq[item] >= POSITION_LIMIT[item]/10:
                  break

      buy_coupons = (mid_price['COCONUT'] / mid_price['COCONUT_COUPON']) - self.coconut_mean

      trade_at = self.coconut_std*0.5

      if buy_coupons > trade_at:
        vol = state.position.get('COCONUT', 0) + 300
        if vol > 0:
          orders['COCONUT'].append(Order('COCONUT', worst_bid['COCONUT'], -vol)) 
      elif buy_coupons:
        vol = 300 - state.position.get('COCONUT', 0)
        if vol > 0:
          orders['COCONUT'].append(Order('COCONUT', worst_ask['COCONUT'], vol))
      return orders
    
    def coupon(self, state):
      
      order_depth: OrderDepth = state.order_depths['COCONUT']

      
      available_sells = order_depth.sell_orders.items()
      available_buys = order_depth.buy_orders.items()

      STRIKE = 10000
      PREMIUM = 637

      COC = "COCONUT"
      CUP = "COCONUT_COUPON"

      order_depth = state.order_depths[CUP]
      coc_pos = state.position.get (COC, 0)
      cup_pos = state.position.get(CUP, 0)
      print(f"coc: {coc_pos}, cup: {cup_pos}")

      cup_buy = 600 - cup_pos
      cup_sell = -600 - cup_pos

      coco_mid = self.get_mid(state, 'COCONUT')
      intrinsic = coco_mid - STRIKE
      DELTA = 0.50
      option_value = DELTA * intrinsic + PREMIUM

      max_bid = max(order_depth.buy_orders.keys(), default=0)
      buy_vol = order_depth.buy_orders.get(max_bid, 0)

      min_ask = min(order_depth.sell_orders.keys(), default=0)
      sell_vol = order_depth.sell_orders.get(min_ask, 0)

      mid = (max_bid + min_ask) / 2

      max_coc = max(state.order_depths[COC].buy_orders.keys())
      min_coc = min( state.order_depths[COC].sell_orders.keys())

      coc_order = []
      cup_order = []

      STD = 12.75
      TRADE = 1 * STD
      CLOSE = 0.3 * STD

      if max_bid > option_value + TRADE:
        buy_vol = max(-buy_vol, cup_sell)
        cup_order.append(Order(CUP, max_bid, buy_vol))
        coc_order.append(Order(COC, min_coc, -buy_vol // 2))
      elif min_ask + TRADE < option_value:
        sell_vol = min(-sell_vol, cup_buy)
        cup_order.append (Order(CUP, min_ask, sell_vol)) 
        coc_order.append(Order(COC, max_coc, -sell_vol // 2))
      elif option_value + CLOSE > mid and mid > option_value - CLOSE:
        if cup_pos > 0:
          cup_order.append(Order (CUP, max_bid, -cup_pos)) 
          coc_order.append(Order(COC, min_coc, -coc_pos))
        else:
          cup_order.append(Order (CUP, min_ask, -cup_pos)) 
          coc_order.append(Order (COC, max_coc, -coc_pos))

      return coc_order, cup_order

    def get_mid(self, state, product):
      bids = OrderedDict(sorted(state.order_depths[product].buy_orders.items()))
      asks = OrderedDict(sorted(state.order_depths[product].sell_orders.items(), reverse=True))

      return (next(iter(bids)) + next(iter(asks))) / 2


    def norm_cdf(self, x):
      return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0



class MovingArray(object):
    def __init__(self, arr5: list[float], time5: list[float], rose5: list[float], rosetime: list[float]):
      self.arr5 = arr5
      self.rose5 = rose5
      self.time5 = time5
      self.rosetime = rosetime


    def add_vals(self, price, time):
        self.arr5.append(float(price))
        self.time5.append(float(time))
        size = 3
        if len(self.arr5) > size:
          self.arr5.pop(0)

        if len(self.time5) > size:
          self.time5.pop(0)

    def add_vals_roses(self, price, time):
        self.rose5.append(float(price))
        self.rosetime.append(float(time))
        size = 2
        if len(self.rose5) > size:
          self.rose5.pop(0)

        if len(self.rosetime) > size:
          self.rosetime.pop(0)


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
    
    def linearRegressionStrawberry(self):
      #sumX, sumY, sumXY, sumXSquared = 0
      sumX = sum(self.rosetime)
      sumY = sum(self.rose5)

      sumXY = 0
      sumXSquared = 0
      for i in range(len(self.rose5)):
         XY = self.rose5[i] * self.rosetime[i]
         xSquared = self.rose5[i] ** 2
         sumXY += XY
         sumXSquared += xSquared
      
      n = len(self.rose5)

      slope =  (n * sumXY - sumX*sumY)/(n*sumXSquared - sumX**2)

      intercept = (sumY - slope*sumX)/n

      #y = m*x + b
      predictedValue = slope * (self.rosetime[-1] + 100) + intercept
      return predictedValue