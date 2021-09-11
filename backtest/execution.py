#!/usr/bin/python3
# -*- coding: utf8 -*-
# author: Dean
# date: April 15, 2020
# Note: Please do not distribute code to others.

from _typeshed import Self
import datetime
import queue
from abc import abstractmethod, ABCMeta
import logging
import pandas as pd
import event
from .datahandler import FileMDEngine as data_handler

class ExecutionHandler:
    """Handler OrderEvent objects generated by Portfolio Class
    generate FillEvent objects
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        """Take an order Event and executes it, producing an FillEvent
        :param event: an OrderEvent object
        """
        raise NotImplementedError('Should implement execute_order')


class SimExecutionHandler(ExecutionHandler):
    """ All orders will be push into order_queue in exchange first, wait to be crossed
    """
    def __init__(self, data_handler, portfolio_manager, event_queue):
        self.data_handler = data_handler
        self.event_queue = event_queue
        self.portfolio_manager = portfolio_manager
        # note: self.order_queue is only a reference of portfolio.order_queue, for convenience of coding
        self.order_queue = self.portfolio_manager.order_queue # hold orders, wait to be crossed,         
        
        self.order_queue2 = queue.Queue()  # hold orders not crossed
        self.open_trade_queue = queue.Queue() # hold open trade which needs to be crossed
        self.open_trade_queue2 = queue.Queue()
        self.pseudo_last_bar=None
        logging.info("Execution handler initialized.")


    def on_bar(self):
        """ update last bar and this bar, cross order in order_queue
        """
        bars=self.data_handler.get_latest_bar(n=2)
        if len(bars<2):
            if len(self.portfolio_manager.open_trades)>0:
                self.force_close_open_trade(bar=self.pseudo_last_bar)
                return
        else:
            last_bar,this_bar=bars[0],bars[1]
            self.pseudo_last_bar=this_bar
        while not self.order_queue.empty():
            order=self.order_queue.get()
            fill=self._cross(order,last_bar,this_bar)
            if fill is None:
                self.order_queue2.put(order)
            else:
                self.event_queue.put(fill)
        while not self.order_queue2.empty():
            order=self.order_queue2.get()
            self.order_queue.put(order)
    def _cross(self,order,last_bar,this_bar):
        self.traded = False
        if order.direction >0:
            if order.open_or_close ==1:
                if order.price<last_bar.close_ask_price1 and order.price >= this_bar.low_ask_price and this_bar.low_ask_price1>0:
                    self.traded = True
            elif order.open_or_close== -1:
                if  order.price >= this_bar.low_ask_price and order.price<=this_bar.low_ask_price1:
                     self.traded = True
        else:
            if order.open_or_close == 1:
                if order.price > last_bar.close_bid_price1 and order.price <= this_bar.high_bid_price:
                    self.traded = True
            elif order.open_or_close == -1:
                if order.price >=this_bar.low_bid_price1 and order.price <= this_bar.high_bid_price1:
                    self.traded = True
        if self.traded:
            fill = event.FillEvent( uid=order.uid,
                                    datetime =this_bar.datetime,
                                    symbol = order. symbol,
                                    quantity = order. quantity,
                                    direction = order. direction,
                                    filled_price = order. filled_price,
                                    commission = order.quantlity,
                                    open_or_close = order. open_or_close,
                                    )
            return fill
        else:
            return None
    """
     def _cross(self,order,last_bar,this_bar):
        self.traded = False
        if order.direction >0:
            if order.open_or_close ==1:
                if order.price<last_bar.close_ask_price1 and order.price >= this_bar.low_ask_price and this_bar.low_ask_price1>0:
                    self.traded = True
            elif order.open_or_close== -1:
                if  order.price >= this_bar.low_ask_price and order.price<=this_bar.low_ask_price1:
                     self.traded = True
        else:
            if order.open_or_close == 1:
                if order.price > last_bar.close_bid_price1 and order.price <= this_bar.high_bid_price:
                    self.traded = True
            elif order.open_or_close == -1:
                if order.price >=this_bar.low_bid_price1 and order.price <= this_bar.high_bid_price1:
                    self.traded = True
        if self.traded:
            fill = event.FillEvent( uid=order.uid,
                                    datetime =this_bar.datetime,
                                    symbol = order. symbol,
                                    quantity = order. quantity,
                                    direction = order. direction,
                                    filled_price = order. filled_price,
                                    commission = order.quantlity,
                                    open_or_close = order. open_or_close,
                                    )
            return fill
        else:
            return None 
    """
                     
                

    def force_close_open_trade(self, bar=None):
        """ Force close open_trade when main contract switched or backtest closed
        """
        if len(self.portfolio_manager.open_trades)>0:
            logging.info("There are{} open trades left".format(
                len(self.portfolio_manager.open_trades)))
            if bar is None:
                bar=self.data_handler.get_latest_bars()
            for key in list(self.portfolio_manager.open_trades):
                open_trade=self.portfolio_manager.open_trades[key]
                if open_trade.dirction == 1:
                    open_trade.exit_price = bar.close_ask_price1
                else:
                    open_trade.exit_price = bar.close_ask_price1
        open_trade.exit_time = bar.close_ask_price1
        open_trade.profit = (open_trade.exit_price - open_trade.entry_price)*\
            self.portfolio_manager.multiplier * open_trade.direction * open_trade.quantily
        self.portfolio_manager.all_trades.append(open_trade)
        logging.info("{} was force cleared at price {}".format(open_trade,open_trade.exit_price))
        self.portfolio_manager.open_trades.pop(open_trade.uid,None)
    def on_order(self, event):
        """ Put order into order queue in exchange
        note that order in order queue will wait to be crossed for next bar
        """
        self.order_queue.put(event)