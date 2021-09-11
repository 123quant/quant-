#!/usr/bin/python3
# -*- coding: utf-8 -*-
# author: Jianqiu Wang
# date: Apr 20, 2018
# Performance metrics to evaluate backtest result
import os
import sys
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt # for plot only
import myconstants


class PerformanceMetric:
    def __init__(self, symbol, initial_capital, data, trades):
        self.multiplier = myconstants.MULTIPLIER_DICT[symbol]
        self.commission_rate = myconstants.COMMISSION_RATE_DICT[symbol]
        self.initial_capital = initial_capital
        self.data = data
        self.trades = trades

    def calculate_performance(self):
        self.data, self.trades_df = self.load_trade()        
        self.metrics = dict()
        self.metrics['win_times'], self.metrics['loss_times'], self.metrics['win_ratio'], self.metrics['total_win_money'], self.metrics['total_loss_money'], self.metrics['avg_win_money'], self.metrics['avg_loss_money'], self.metrics['net_pnl'] = self.get_trade_stats()
        self.metrics['sharpe'] = self.get_sharpe_ratio()
        self.metrics['annual_return'] = self.get_annual_return()

    def plot_performance(self):
        print('------------------------------------------')
        for k,v in self.metrics.items():
            print("{:20s} |          {:8.4f}".format(k,v))
            
        
    def load_trade(self):
        data = self.data
        data['trade'] = 0
        data['tradeprice'] = 0
        for trade in self.trades:
            data.loc[trade.entry_time, 'trade'] += trade.direction * trade.quantity
            data.loc[trade.entry_time, 'tradeprice'] = trade.entry_price
            data.loc[trade.exit_time, 'trade'] -= trade.direction * trade.quantity
            data.loc[trade.exit_time, 'tradeprice'] = trade.exit_price
  
        data['position'] = 
        data['tradepnl'] = 
        
        data['pospnl'] = 
        data['barpnl'] = 
        data['cumpnl'] = 
        data['tradepnl_wo_commission'] =
        data['barpnl_wo_commission'] = 
        data['cumpnl_wo_commission'] = 

        trades_df = pd.DataFrame.from_records([trade.to_dict() for trade in self.trades]).set_index('uid')
        return data, trades_df
   
    def get_trade_stats(self): 
        """Your code here
        """
        return win_amount, loss_amount, win_ratio, total_win_money, total_loss_money, average_win, average_loss, net_pnl

    def get_sharpe_ratio(self):
        """Your code here
        """
         
        return sharpe 
   
    def get_annual_return(self):
        
        return annual_return

    def create_drawdowns(equity_curve):
        """
        Calculate the largest peak-to-trough drawdown of the PnL curve
        as well as the duration of the drawdown. Requires that the
        pnl_returns is a pandas Series.

        Parameters:
        pnl - A pandas Series representing period percentage returns.

        Returns:
        drawdown, duration - Highest peak-to-trough drawdown and duration.
        """

        # Calculate the cumulative returns curve
        # and set up the High Water Mark
        # Then create the drawdown and duration series
        hwm = [0]
        eq_idx = equity_curve.index
        drawdown = pd.Series(index=eq_idx)
        duration = pd.Series(index=eq_idx)

        # Loop over the index range
        """Your code here
        """

        return drawdown.max(), duration.max()
