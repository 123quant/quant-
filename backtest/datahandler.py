#!/usr/bin/python3
# -*- coding: utf8 -*-
# author: Dean
# date: April 15, 2020
# Note: Please do not distribute code to others.
from datetime import datetime
import os
import re
import sys
from numpy.core.fromnumeric import sort   
import  pandas as pd
from itertools import islice
from collections import deque,namedtuple
from abc import abstractmethod,ABCMeta
import configparser
from .event import Bar
from .myconstants import DATA_PATH ,TRADE_DATE_FILE,TICKSIZE_DICT ,MULTIPLIER_DIC,COMMISSION_RATE_DICT
import logging
from .event import Event


class MDEngine(object):
    """ Abstract class
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, n=1):
        """
        从latest_symbol列表中返回最近的几根bar，
        如果可用值小于N，则返回全部所能的使用k bar
        """
        raise NotImplementedError("Should implement get_latest_bars()!")

    @abstractmethod
    def publish_md(self):
        raise NotImplementedError("Should implement update_bars()！")

class FileMDEngine(MDEngine):
    """ Class FileDataHandler: read option minute data from file
    """
    def __init__(self, event_queue, start_date, end_date, symbol):
        """
        :param event_queue:
        :param start_date: backtest start date, datetime format,
        :param end_date:  backtest end date, datetime format,
        """
        self.continue_backtest = True
        self.symbol = symbol
        self.event_queue = event_queue#
        self.start_date = str(start_date)[:10]
        self.end_date = str(end_date)[:10]
        self.latest_data = None
        config=configparser.ConfigParser()#
        self.datapath = config.get("datapath", "min")
        self.df, self.data = self.load()
        logging.info("Data handler loaded.")
    
    def load(self):
        """ Load all related history data
        Your code here
        """
        # with open(TRADE_DATE_FILE) as f:
        #     all_tradedays=f.read().replace(" "," ").replace("\"","").split(',')
        # try:
        #     start_idx=all_tradedays.index(self.start_date)
        #     end_idx=all_tradedays.index(self.end_date)
        # except ValueError:
        #     logging .info("{} or {} is not a trader day".format(
        #         self.start_date,self.end_date))
        #     exit()
        df=pd.DataFrame()
        # exchange = get_jsy_exchange(self.symbol)
        # trade_days=all_tradedays[start_idx:end_idx + 1]
        # for x in trade_days:
        new_df=pd.read_csv("path")
        df=df.append(new_df)
        df=df.set_index('datetime',drop=False).sort_index()
        df.datetime=pd.to_datetime(df.datetime)
        df.index=pd.to_datetime(df.index)
        COlUMNS_TO_LOAD = []
        df=df[COlUMNS_TO_LOAD]
        return df.iterrows(),df.copy()
    def publish_md(self):
        """ Push bars for next minute
        """
        try:
            """Your code here
            Hint: use generator 
            """
            last_bar=self.get_latest_bars(n=1)
            bar_data=next(self.df)
            bar=self.create_bar(bar_data)
            if last_bar is None or bar.symbol != last_bar.symbol:
                self.latest_data=deque(maxlen=2400)
                self.latest_data.append(bar)
            else:
                self.latest_data.append(bar)

        except StopIteration:
            self.continue_backtest = False
        else:
            self.event_queue.put(bar)
    def create_bar(self,bar_data):
        """
        Genrate bar object from pd iterrows object
        """
        return Bar(
                    symbol =bar_data[1]. symbol,
                    datetime =bar_data[1]. datetime,
                    open =bar_data[1]. open,
                    high =bar_data[1]. high,
                    low =bar_data[1]. low,
                    close =bar_data[1]. close,
                    open_bid_price1 =bar_data[1]. open_bid_price1,
                    high_bid_price1 =bar_data[1]. high_bid_price1,
                    low_bid_price1 =bar_data[1]. low_bid_price1,
                    close_bid_price1 =bar_data[1]. close_bid_price1,
                    open_ask_price1 =bar_data[1]. open_ask_price1,
                    high_ask_price1 =bar_data[1]. high_ask_price1,
                    low_ask_price1 =bar_data[1]. low_ask_price1,
                    close_ask_price1 =bar_data[1]. close_ask_price1,
                    volume =bar_data[1]. volume,
                    close_ask_volume1 =bar_data[1]. close_ask_volume1,
                    close_bid_volume1 =bar_data[1]. close_bid_volume1,
                    open_ask_volume1 =bar_data[1]. open_ask_volume1,
                    open_bid_volume1 =bar_data[1]. open_bid_volume1)
    def get_latest_bars(self, n=1):
        """Get latest n bars
            Your code here
        
        """
        if self.latest_data is None:
            return None
        if n==1:
            return self.latest_data[-1]
        else:
            len_dq= len(self.latest_data)
            if n >len_dq:
                return self.latest_data
            else:
                return list(islice(self.latest_data,len_dq - n,len_dq))
        # return ...