#!/usr/bin/python3
# -*- coding: utf8 -*-
# author: Dean
# date: April 15, 2020
# Note: Please do not distribute code to others.
import uuid

class Event:
    pass


class Bar(Event):
    __slots__ = ['type', 'symbol', 'datetime', 'open','high','low','close', 'open_bid_price1', 'high_bid_price1', 'low_bid_price1', 'close_bid_price1', 'open_ask_price1', 'high_ask_price1', 'low_ask_price1', 'close_ask_price1', 'volume', 'close_ask_volume1', 'close_bid_volume1', 'open_ask_volume1', 'open_bid_volume1']

    def __init__(self, symbol, datetime, open, high,low,close,open_bid_price1,
                  high_bid_price1, low_bid_price1, close_bid_price1, open_ask_price1, high_ask_price1, low_ask_price1, close_ask_price1, volume, close_ask_volume1, close_bid_volume1, open_ask_volume1, open_bid_volume1):
        self.type = 'BAR'
        self.symbol = symbol
        self.datetime = datetime
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.open_bid_price1 = open_bid_price1
        self.high_bid_price1 = high_bid_price1
        self.low_bid_price1 = low_bid_price1
        self.close_bid_price1 = close_bid_price1
        self.open_ask_price1 = open_ask_price1
        self.high_ask_price1 = high_ask_price1
        self.low_ask_price1 = low_ask_price1
        self.close_ask_price1 = close_ask_price1
        self.volume = volume
        self.close_ask_volume1 = close_ask_volume1
        self.close_bid_volume1 = close_bid_volume1
        self.open_ask_volume1 = open_ask_volume1
        self.open_bid_volume1 = open_bid_volume1

    def __str__(self):
        bar_str = "Type: %s, Datetime: %s, Symbol: %s" \
                % (self.type, self.datetime, self.symbol)
        return bar_str

    def __repr__(self):
        return str(self)


class MultiSignalEvent(Event):
    """ Signal Class: strategy object would send Signal object to PortfolioManager Class"""

    def __init__(self, datetime, signal_detail, strategy_id=1):
        """
        :param datetime: datetime of sending signal
        :param signal_detail: dictionary {symboL: strength -1 / 1},
        :param strategy_id:
        """
        self.type = 'SIGNAL'
        self.datetime = datetime
        self.signal_detail = signal_detail
        self.strategy_id = strategy_id

    def __str__(self):
        signal_str = "Type: %s, Datetime: %s, Number of signals: %s" \
                     % (self.type, self.datetime, len(self.signal_detail))
        return signal_str

    def __repr__(self):
        return str(self)


class SignalEvent(Event):
    """ Signal Class: strategy object would send Signal object to Portfolio Class
    """

    def __init__(self, symbol, datetime, direction, strategy_id=1, strength=1.0):
        """
        初始化SignalEvent对象
        参数：
        symbol: code
        datetime：signal产生的时间戳
        signal_type: 'LONG', 'SHORT','EXIT'
        strategy_id: 策略的独特id，可以多策略并行
        """
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.direction = direction
        self.strategy_id = strategy_id
        self.strength = strength

    def __str__(self):
        signal_str = "Type: %s, Datetime: %s, %s %s with signal strength %s" \
                     % (self.type, self.datetime, self.direction, self.symbol, self.strength)
        return signal_str

    def __repr__(self):
        return str(self)

class OrderEvent(Event):
    """ Send orders to an execution system
    """

    def __init__(self, datetime, symbol, quantity, price, direction, open_or_close, uid=None):
        """
        :param symbol:
        :param order_type: 'MKT' or 'LMT' for Market or Limit
        :param quantity:
        :param direction:
        """
        self.type = 'ORDER'
        if uid is None:
            self.uid = uuid.uuid4()
        else:
            self.uid = uid
        self.symbol = symbol
        self.datetime = datetime
        self.open_or_close = open_or_close
        self.price = price
        self.quantity = quantity
        self.direction = direction

    def __str__(self):
        if self.direction == 1:
            direction = 'LONG '
        else:
            direction = 'SHORT'
        order_str = "Type: %s, %s %s %s at price %s, datetime: %s" \
                    % (self.type, direction, self.quantity, self.symbol, self.price, self.datetime)
        return order_str

    def __repr__(self):
        return str(self)


class FillEvent(Event):
    """ 撮合成交
    """

    def __init__(self, uid, datetime, symbol, quantity, direction, filled_price, commission=None, open_or_close=0):
        """
        :param timeindex:
        :param symbol:
        # :param exchange:
        :param quantity:
        :param direction:
        :param filled_price: 成交价格
        :param commission:
        """
        self.type = 'FILL'
        self.uid = uid
        self.datetime = datetime
        self.symbol = symbol
        self.quantity = quantity
        self.direction = direction
        self.filled_price = filled_price
        self.commission = commission
        self.open_or_close = open_or_close

    def __str__(self):
        if self.direction == 1:
            direction = 'LONG '
        else:
            direction = 'SHORT'
        if self.open_or_close == 1:
            open_or_close = 'OPEN'
        else:
            open_or_close = 'CLOSE'
        fill_str = "Type: %s, %s %s %s %s at price %s, datetime: %s" \
                   % ("FILL ", open_or_close, direction, self.quantity, self.symbol, self.filled_price, self.datetime)
        return fill_str

    def __repr__(self):
        return str(self)

