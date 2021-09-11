from multiprocessing import process
import sys
import logging
import os
sys.path.append(os.path.expanduser('path'))
from .datahandler import FileMDEngine
from .strategy import MovingAverageCrossStrategy
from backtest import BackTest
from .portfolio import BidAskPortfolio
from .execution import SimExecutionHandler
import multiprocessing as mp
from .event import SignalEvent
from functools import partial



def run_bt(long_window,short_window):
    bt=BackTest(
        start_date ="",
        end_date = '',
        initial_capital =1e6 ,
        symbol ="rb" ,
        strategy_cls=MovingAverageCrossStrategy,
        portfolio_cls =BidAskPortfolio ,
        execution_cls =SimExecutionHandler , 
        data_handler_cls = FileMDEngine,
        long_window=long_window,
        short_window=short_window
        )
    bt.simulate_trading()
process= list()
for x in [100,150,200]:
    for y in [20,40,60]:
        process.append(mp.Process(target=run_bt,args=(x,y)))
for P in process:
    P.start()
for P in process:
    P.join()