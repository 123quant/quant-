#!/usr/bin/python3
# -*- coding: utf8 -*-
# author: Dean
# date: April 15, 2020
# Note: Please do not distribute code to others.
import queue
import logging
import pandas as pd
import datahandler
import performance

class BackTest:
    def __init__(self, start_date, end_date, symbol, strategy_cls,initial_capital,
        portfolio_cls, execution_cls, datahandler_cls, plot=False, **kwargs):
        """Initialize a backtest object
        Your code begins
        """
        self.start_date = start_date
        self.end_date = end_date
        self.event_queue = queue.Queue()  # init an empty queue
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.plot = plot
        self._initialize_params(kwargs)
        self.data_handler_cls = datahandler_cls
        self.strategy_cls = strategy_cls
        self.portfolio_cls = portfolio_cls
        self.execution_cls = execution_cls
        self._initialize_trading_instances()
        logging.info("Backtest initialized.")
    
    def _initialize_params(self, kwargs):
        self.strategy_kwargs = dict()
        self.portfolio_kwargs = dict()
        for x, y in kwargs.items():
            if 'strategy_' in x:
                self.strategy_kwargs[x[9:]] = y
            elif 'portfolio_' in x:
                self.portfolio_kwargs[x[10:]] = y
            else:
                logging.warning("Unidentified keyword arg: {}".format(x))

    def _initialize_trading_instances(self):
        """Initialize DataHander, Strategy, Portfolio, Execution
        """
        self.data_handler = self.data_handler_cls(self.event_queue, self.start_date, self.end_date, self.symbol)
        self.portfolio_manager = self.portfolio_cls(self.symbol, self.data_handler, self.event_queue, **self.portfolio_kwargs)
        self.strategy = self.strategy_cls(self.data_handler, self.portfolio_manager, self.event_queue, **self.strategy_kwargs)
        self.execution_handler = self.execution_cls(self.data_handler, self.portfolio_manager, self.event_queue)
        # Note: cannot use self.execution_handler = self.execution_cls(self.data_handler, \
        # self.portfolio_cls, self.event_queue)
        # portfolio_cls instance needs to be instantiated, which is self.portfolio
    
    def run_backtest(self):
        """Use while True loop to run backtest
        :return: None
        """
        while True:
            md_engine = self.data_handler  
            if md_engine.continue_backtest:
                md_engine.publish_md()  # generate BarEvent
                self.portfolio_manager.on_bar()  # stop loss and profit target
                self.execution_handler.on_bar()  # cross orders in order_queue
            else:
                self.portfolio_manager.cancel_all() # backtest complete, clear all orders
                self.execution_handler.force_close_open_trade()
                break
                
            # handle all events
            while True:
                try:
                    event = self.event_queue.get(block=False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'BAR':
                            self.strategy.on_bar(event)
                        elif event.type == 'SIGNAL':
                            self.portfolio_manager.on_signal(event)
                        elif event.type == 'ORDER':
                            logging.info("UID {} Order received at {}. Direction: {}, open/close: {}".format(event.uid, event.price, event.direction, event.open_or_close))
                            self.execution_handler.on_order(event)   # get order from order_queue in portfolio class
                        elif event.type == 'FILL':
                            logging.info("UID {} Order filled at {}. Direction: {}, open/close: {}".format(event.uid, event.filled_price, event.direction, event.open_or_close))
                            self.portfolio_manager.on_rtn_trade(event)

    def simulate_trading(self):
        self.run_backtest()

    def show_performance(self):
        self.performance_metric = PerformanceMetric(symbol=self.symbol,
                                             initial_capital=self.initial_capital,
                                             data=self.data_handler.data,
                                             trades=self.portfolio_manager.all_trades)
        if len(self.portfolio_manager.all_trades) > 0:
            self.performance_metric.calculate_performance()
            if self.plot:
                self.performance_metric.plot_performance()
        else:
            print("No trade, no P&L")