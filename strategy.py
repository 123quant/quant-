#!/usr/bin/python3
# -*- coding: utf8 -*-
# author: Dean
# date: April 15, 2020
# Note: Please do not distribute code to others.

from abc import ABCMeta, abstractmethod
import numpy as np
import os 
import sys
sys.path.append(os.path.expanduser('path'))


from .event import SignalEvent
import uuid
class Strategy:
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_bar(self, *args):
        """Calculate the list of signals
        """
        raise NotImplementedError("Should implement on_bar()!")


class MovingAverageCrossStrategy(Strategy):
    """
    移动双均线策略
    """
    def __init__(self, data_handler, portfolio_manager, event_queue, long_window=10, short_window=5):
        self.data_handler = data_handler
        self.portfolio_manager = portfolio_manager
        self.event_queue = event_queue
        self.long_window = long_window  # 长期均线
        self.short_window = short_window  # 短期均线
        self.bought = False
        self.ask1 = list()
        self.bid1 = list()
        self.strategy_id = str(uuid.uuid4())[:8]
        self.long_traded = False	
        self.short_traded = False

    def on_bar(self, event):
        if len(self.data_handler.latest_data) > self.long_window:
            bars = self.data_handler.get_latest_bars(n=self.long_window)
            bids = np.array([bar.close_bid_price1 for bar in bars])
            asks = np.array([bar.close_ask_price1 for bar in bars])
            long_window_avg = np.average((bids + asks)/2)
            short_window_avg = np.average((bids[-self.short_window:]+asks[-self.short_window:])/2)
            if long_window_avg > short_window_avg + 1 and not self.long_traded:
                self.event_queue.put(SignalEvent(symbol=bars[-1].symbol,
                                                 datetime=bars[-1].datetime,
                                                 direction=1,
                                                 strategy_id=self.strategy_id,
                                                 strength=0))
                self.long_traded = True
                self.short_traded = False
            elif long_window_avg < short_window_avg - 1 and not self.short_traded:
                self.event_queue.put(SignalEvent(symbol=bars[-1].symbol,
                                                 datetime=bars[-1].datetime,
                                                 direction=-1,
                                                 strategy_id=self.strategy_id,
                                                 strength=0))
                self.short_traded = True
                self.long_traded = False
        else:
            pass
