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
        conversions = 0
        for product in state.order_depths:
          if product == "AMETHYSTS":
            # make sure positions aren't cancelled
            result[product] = self.amethysts(state, product)
          if product == "STARFRUIT":
            result[product], traderData = self.starfruit(state, product) 
          if product == "ORCHIDS":
            result[product], conversions = self.orchid(state, product)

		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        # traderData = "SAMPLE" 

				# Sample conversion request. Check more details below. 
        
        # logger.flush(state, result, conversions, traderData)
        return result, conversions, traderData

    def amethysts(self, state, product):
      order_depth: OrderDepth = state.order_depths[product]
      orders: list[Order] = []

      sells = sorted(order_depth.sell_orders.items())
      buys = sorted(order_depth.buy_orders.items(), reverse=True)
      for bid, q in buys:
        print("PRICE: " + str(bid))

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

      return orders, jsonpickle.encode(traderObj)

    def orchid(self, state, product):
        order_depth: OrderDepth = state.order_depths[product]
        orders: List[Order] = []

        cObservation = state.observations.conversionObservations[product]
        foreign_bid = cObservation.bidPrice
        foreign_ask = cObservation.askPrice
        export = cObservation.exportTariff
        Import = cObservation.importTariff
        transport = cObservation.transportFees

        print("FOREIGN MID: " + str((foreign_bid + foreign_ask) / 2))

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

        price_sum = 0
        price_num = 0


        #actual price
        for x in state.order_depths[product].buy_orders:
          price_sum += abs(x*state.order_depths[product].buy_orders[x])
          price_num += abs(state.order_depths[product].buy_orders[x])
        for y in state.order_depths[product].sell_orders:
          price_sum += abs(-y*state.order_depths[product].sell_orders[y])
          price_num += abs(state.order_depths[product].sell_orders[y])
        acceptable_price = float(price_sum)/float(price_num)        


        position = 0
        current_pos = position

        foreign_price = (foreign_ask + foreign_bid) / 2

        print("PREDICTION: " + str(foreign_price))
        print("ACCEPTABLE: " + str(acceptable_price))

        if acceptable_price <= foreign_price: 
          print("BUY OPPORTUNITY")
          foreign_price = foreign_price - transport - export
          print("PREDICTION: " + str(foreign_price))
          print("ACCEPTABLE: " + str(acceptable_price))
          max_price = -1
          for ask, quanity in sells:
            if ((ask < foreign_price) or ((position < 0) and (ask == foreign_price))) and current_pos < 20:
              max_price = max(max_price, ask)
              amount = min(-quanity, 100 - current_pos)
              current_pos += amount
              orders.append(Order(product, ask, amount))
        else:
          print("SELL OPPORTUNITY")
          current_pos = position
          for bid, quantity in buys:
            if ((bid > foreign_price) or ((position > 0) and (bid == foreign_price))) and current_pos > -20:
              amount = max(-quantity, -100-current_pos)
              current_pos += amount
              orders.append(Order(product, bid, amount))

        print("NUM CONVERSION: " + str(state.position.get(product, 0)))
        return orders, -state.position.get(product, 0)

    def gift_basket(self, order_depth):

        POSITION_LIMIT = {'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60}

        orders = {'CHOCOLATE' : [], 'STRAWBERRIES': [], 'ROSES' : [], 'GIFT_BASKET' : []}
        goods = ['CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET']
        available_sells, available_buys, best_ask, best_bid, worst_ask, worst_bid, mid_price, available_buyq, available_sellq = {}, {}, {}, {}, {}, {}, {}, {}, {}

        for item in goods:
            available_sells[item] = sorted(order_depth[item].sell_orders.items())
            available_buys[item] = sorted(order_depth[item].buy_orders.items(), reverse=True)

            best_ask[item] = next(iter(available_sells[item]))
            best_bid[item] = next(iter(available_buys[item]))

            worst_ask[item] = next(reversed(available_sells[item]))
            worst_bid[item] = next(reversed(available_buys[item]))

            mid_price[item] = (best_ask[item] + best_bid[item])/2
            available_buyq[item], available_sellq[item] = 0, 0
            for price, quantity in available_buys[item].items():
                available_buyq[item] += quantity 
                if available_buyq[item] >= POSITION_LIMIT[item]/10:
                    break
            for price, quantity in available_sells[item].items():
                available_sellq[item] += -quantity 
                if available_sellq[item] >= POSITION_LIMIT[item]/10:
                    break

        buy_baskets = best_ask['GIFT_BASKET'] - (best_bid['CHOCOLATE']*4) - (best_bid['STRAWBERRIES']*6) - best_bid['ROSES']
        sell_baskets = best_bid['GIFT_BASKET'] - (best_ask['CHOCOLATE']*4) - (best_ask['STRAWBERRIES']*6) - best_ask['ROSES']

        return orders
    
    def get_item_price(self, product, order_book, bidorask):
      etf = {'CHOCOLATE': 4, 'STRAWBERRIES': 6, 'ROSES': 1}
      orders = {}
      if bidorask == "BID":
        for i in range(etf[product]):
          orders[next(iter(order_book))] = 0

    '''
    so basically what we need to do is we need to first decide whether we are gonna buy baksets and sell the
    individual items or the opposite. In order to do this we need to get the average price of the next __ items based
    on how many of them are in the basket, and then substract that from teh total gift basket price.
    Then we need to place orders at the exact prices of the ___ items that we are buying or selling, which isn't hard,
    but it hard to think about how to do it best.
    '''




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
