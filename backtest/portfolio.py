#!/usr/bin/python3
# -*- coding: utf8 -*-
# author: Dean
# date: April 15, 2020
# Note: Please do not distribute code to others.
# import os
# import sys
# sys.path.append(os.path.expanduser('path'))
import pandas as pd
import queue
import collections
import datetime
import logging
from .event import OrderEvent
from abc import ABCMeta,abstractmethod

from .myconstants import MULTIPLIER_DICT,TICKSIZE_DICT,COMMISSION_RATE_DICT
from abc import ABCMeta, abstractmethod
# from util.futuresymbol import extract_symbol


class Portfolio:
    """ Portfolio Class handles handles positions and market value of all instruments
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_bar(self):
        """ New market data arrived, update md in Porfolio class, for sake of calculation risk metrics
        """
        raise NotImplementedError(
            "Should implment update_bar() method in Portfolio Class")

    @abstractmethod
    def on_signal(self, event):
        """ Generate new portfolio
        """
        raise NotImplementedError("Should implement update_signal()!")

    @abstractmethod
    def on_fill(self, event):
        """Update current positions and holdings in portfolio from a FillEvent
        """
        raise NotImplementedError("Should implement update_fill()!")


class BidAskPortfolio(Portfolio):
    def __init__(self, symbol, data_handler, event_queue, stoploss_mode='default', trailing_stop_ticks=None):
        """ Initialize portfolio with DataHander
        Note: BidAskPortfolio is optimized for minute data and bid ask bar backtest
        """
        self.symbol = symbol
        self.data_handler = data_handler
        self.event_queue = event_queue
        self.last_bar = None
        self.pseudo_last_bar = None # this is the last bar in case main contract switched
        self.this_bar = None  # lastest md
        self.open_trades = dict()
        self.all_trades = list()
        self.get_symbol_info()
        self.order_queue = queue.Queue() # create order queue
        self._order_queue2 = queue.Queue() # temp copy of self.order_queue
        self.stoploss_mode = stoploss_mode
        if stoploss_mode == 'trailing':
            self.trailing_stop_ticks = trailing_stop_ticks
        logging.info("Portfolio class initialized.")

    def get_symbol_info(self):
        symbol = extract_symbol(self.symbol)
        self.commission_rate = COMMISSION_RATE_DICT[symbol]
        self.multiplier = MULTIPLIER_DICT[symbol]
        self.ticksize = TICKSIZE_DICT[symbol]

    def on_bar(self):
        self._update_md()
        self._handle_order_queue()
        self._handle_trailing_stop_order()
     
    def _update_md(self):
        if len(self.data_handler.latest_data) > 1:
            self.last_bar = self.data_handler.latest_data[-2]
            self.this_bar = self.data_handler.latest_data[-1]
        else:
            if self.last_bar is not None:
                self.pseudo_last_bar = self.this_bar
            self.last_bar = None
            self.this_bar = self.data_handler.latest_data[-1]
            if len(self.open_trades) > 0:
                logging.info("Main contract switched,force clear open trade")

    def _handle_order_queue(self):
        pass

    def _handle_trailing_stop_order(self):
        # check trailing stoploss trade
        if len(self.open_trades)== 1 and self.stoploss_mode =='trailing':
            open_trade = list(self.open_trdes.values()) [0]
        # update paper_pnl and most_profit_price
            open_trade.paper_pnl =(self.this_bar.close - open_trade.entry_price) * open_trade.direction 
            if open_trade.direction >0:
                open_trade.most_profit_price = max(open_trade.most_profit_price, self.this_bar.close_bid_price1)
                if self.this_bar.close_bid_pricel <= open_trade.most_profit_price - self.trailing_stop_ticks:
                     self.send_trailing_stop_order(open_trade)
        else:

            open_trade.most_profit_price = min(open_trade.most_profit_price,self.this_bar.close_ask_price1)
            if self.this_bar.close_ask_pricel >= open_trade.most_profit_price + self.trailing_stop_ticks:
                self.send_trailing_stop_order(open_trade)




        # error check
        if len(self.open_trades) > 1:
            logging.error('More than one open trade exists!')
            for x, y in self.open_trades.items():
                print(y.to_dict())


    def on_signal(self, signal):
        """ Generate order from signal
        Note: for arbitrage strategy, signal(s) come in pair(or more)
        """
        if signal.type == 'SIGNAL':
            self._generate_order(signal, self.this_bar)
    
    def _generate_order(self, signal, bar):
        """ generate order from signal event
        If current position exits: 
            If dirction unchanged, nothing to do,
            else: send an order to flat current trade
        Else: no position, send order
        """
        if len(self.open_trades) > 0:
            open_trade = list(self.open_trades.values())[0]
            if open_trade.direction == signal.direction:
                pass # direction same, nothing to do
            else:    # close current position
                """ Your code here
                """
                if signal.direction >0:
                    price = bar.close_ask_price1
                else:
                    price = bar.close_bid_price1
                order = OrderEvent( uid=open_trade.uid,
                                    datetime=signal.datetime, 
                                    symbol=bar.symbol,
                                    quantity=1,
                                    price=price, 
                                    direction=signal.direction,
                                    open_or_close= -1)
                self.event_queue.put(order)
        else:
            if signal.direction == 1:  # long order
                order = OrderEvent(
                                    datetime=signal.datetime, 
                                    symbol=bar.symbol,
                                    quantity=1,
                                    price= bar.close_ask_price1, 
                                    direction=1,
                                    open_or_close= 1)
            else:
                order = OrderEvent( datetime=signal.datetime, 
                                    symbol=bar.symbol,
                                    quantity=1,
                                    price= bar.close_bid_price1, 
                                    direction = -1,
                                    open_or_close= 1)
            self.event_queue.put(order)
                
              
    def on_rtn_trade(self, event):
        """ Handle fill event,
        1. if stoploss or profit targetcancel stoploss/profit target order if one of them is filled
        2. if new trade filled, cancel other open order(wait to be crossed) 
        """
        if event.open_or_close == 1:
              # open a new trade, and send a stoploss and a profit-target order
            # if there is an open order in order_queue, cancel it first
            uid_to_cancel = None
            while not self.order_queue.empty():
                order = self.order_queue.get()
                if order.open_or_close == -1:
                    self._order_queue2.put(order)
                else:
                    uid_to_cancel = order.uid
            while not self._order_queue2.empty():
                self.order_queue.put(self._order_queue2.get())
            if uid_to_cancel is not None:

                self._cancel_order(uid_to_cancel)

            # create open trade and stoploss/profit target order
            open_trade = self.create_open_trade(event)
            self.open_trades[open_trade.uid]= open_trade
            if self.stoploss_mode =='default':
                order1,order2=self.get_stoploss_profit_target_orders(open_trade)
                self.event_queue.put(order1)
                self.event_queue.put(order2)
        
            
        else:  # close open trade, remove from open_trade dict

            uid=event.uid
            try :
                open_trade = self.open_trades[uid]
            except KeyError:
                logging.info("Hit stoploss and profit-target at same time")
            else:
                open_trade.exit_price = event.filled_price
                open_trade.exit_time = event.datetime
                open_trade.profit = (open_trade.exit_price - open_trade.entry_price) * self.multiplier * open_trade.direction
                self._cancel_order(uid)
                self.all_trades.append(open_trade)
                self.open_trades.pop(uid,None)
            

    def cancel_all(self):
        """ Cancel all order in order queue
        """
        while not self.order_queue.empty():
            self.order_queue.get()

    def _cancel_order(self, uid):
        """ User should not call this function in strategy,
        Helper function to remove redundant stoploss/ profit target order with same uuid
        """
        while not self.order_queue.empty():
            order = self.order_queue.get()
            if order.uid != uid:
                self._order_queue2.put(order)
            else:
                logging.info("UID {} Order canceled".format(order.uid))
        while not self._order_queue2.empty():
            order = self._order_queue2.get()
            self.order_queue.put(order)

    def create_open_trade(self, fill):
        """ Generate open trade object from fill event
        """
        trade = Trade(uid=fill.uid,
                      symbol=fill.symbol,
                      entry_price=fill.filled_price,
                      exit_price=None,
                      stoploss_price=self.get_stoploss_price(fill),
                      profit_target_price=self.get_profit_target_price(fill),
                      commission_rate=self.commission_rate,
                      commission=2 * self.commission_rate * fill.filled_price * self.multiplier,
                      most_profit_price=fill.filled_price,
                      paper_pnl=0,
                      profit=None,
                      quantity=fill.quantity,
                      entry_time=fill.datetime,
                      exit_time=None,
                      direction=fill.direction)
        return trade

    def get_stoploss_profit_target_orders(self, open_trade):
        """ Return a stoploss limit order and profit target order at the same time, pass uuid from open trade
        Note: following logic is implemented in execution handler
        1. If one of them is crossed(not in exeuction.order_queue), the other one will be canceled automatically
        2. If main contract switched, order will be crossed at last bar worst price +/-1 (bid1/ask1 +/-1)
        """
        stoploss_order = OrderEvent( 
            uid=open_trade.uid,
            datetime=open_trade.entry_time, 
            symbol=open_trade.symbol,
            quantity=open_trade.quantity,
            price=open_trade.stoploss_price, 
            direction=open_trade.direction,
            open_or_close= -1
        
        )
        profit_target_order = OrderEvent(
            uid=open_trade.uid,
            datetime=open_trade.entry_time, 
            symbol=open_trade.symbol,
            quantity=open_trade.quantity,
            price=open_trade.profit_target_price, 
            direction=open_trade.direction,
            open_or_close= -1
        
        )
        return stoploss_order, profit_target_order

    def get_stoploss_price(self, fill):
        if fill.direction == 1:
            return  fill.filled_price - self.ticksize * 20
        else:
            return  fill.filled_price + self.ticksize * 20 

    def get_profit_target_price(self, fill):
        if fill.direction == 1:
            return  fill.filled_price + self.ticksize * 40
        else:
            return  fill.filled_price - self.ticksize * 40 

    def get_trailing_stoploss_profit_target_orders(self, open_trade):
        """ Return a stoploss limit order and profit target order at the same time, pass uuid from open trade
        Note: following logic is implemented in execution handler
        1. If one of them is crossed(not in exeuction.order_queue), the other one will be canceled automatically
        2. If main contract switched, order will be crossed at last bar worst price +/-1 (bid1/ask1 +/-1)
        """
        stoploss_order= OrderEvent(
            uid=open_trade.uid,
            datetime=open_trade.entry_time, 
            symbol=open_trade.symbol,
            quantity=open_trade.quantity,
            price=open_trade.stoploss_price, 
            direction=open_trade.direction,
            open_or_close= -1
        )
        profit_target_order = OrderEvent(
            uid=open_trade.uid,
            datetime=open_trade.entry_time, 
            symbol=open_trade.symbol,
            quantity=open_trade.quantity,
            price=open_trade.profit_target_price, 
            direction=open_trade.direction,
            open_or_close= -1
        )
        return stoploss_order,profit_target_order
    def send_trailing_stop_order(self, open_trade):
        if open_trade.direction >0 :
            order_price = self.this_bar.close_bid_price1
        else:
            order_price = self.this_bar.close_ask_price1
        trailing_stop_order=OrderEvent(
            uid=open_trade.uid,
            datetime=self.this_bar.datetime, 
            symbol=open_trade.symbol,
            quantity=open_trade.quantity,
            price=order_price, 
            direction=-open_trade.direction,
            open_or_close= -1

        )
        self.event_queue.put(trailing_stop_order)