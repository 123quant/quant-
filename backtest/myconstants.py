#!/usr/bin/python3
# -*- coding: utf8 -*-
# author: Dean
# date: April 15, 2020
# Note: Please do not distribute code to others.
import os

DATA_PATH = ... 
TRADE_DATE_FILE = ...

TICKSIZE_DICT = {
    'ag': 1,
    'al': 5,
    'au': 0.05,
    'bu': 2,
    'cu': 10,
    'fu': 1,
    'hc': 1,
    'ni': 10,
    'pb': 5,
    'rb': 1,
    'ru': 5,
    'sn': 10,
    'wr': 1,
    'zn': 5,
    'a': 1,
    'b': 1,
    'bb': 0.05,
    'c': 1,
    'cs': 1,
    'fb': 0.05,
    'i': 0.5,
    'j': 0.5,
    'jd': 1,
    'jm': 0.5,
    'l': 5,
    'm': 1,
    'p': 2,
    'pp': 1,
    'v': 5,
    'y': 2,
    'CF': 5,
    'CY': 5,
    'AP': 1,
    'FG': 1,
    'JR': 1,
    'LR': 1,
    'MA': 1,
    'OI': 1,
    'PM': 1,
    'RI': 1,
    'RM': 1,
    'RS': 1,
    'SF': 2,
    'SM': 2,
    'SR': 1,
    'TA': 2,
    'WH': 1,
    'ZC': 0.2,
    'sc': 0.1,
    'IH': 0.2
}

MULTIPLIER_DICT = {
    "p": 10,
    "IC": 200,
    "RI": 20,
    "ER": 20,
    "cs": 10,
    "c": 10,
    "WT": 10,
    "zn": 5,
    "ru": 10,
    "wr": 10,
    "fb": 500,
    "sn": 1,
    "LR": 20,
    "cu": 5,
    "i": 100,
    "l": 5,
    "IH": 300,
    "hc": 10,
    "fu": 50,
    "WH": 20,
    "WS": 10,
    "pb": 5,
    "PM": 50,
    "AP": 10,
    "ni": 1,
    "CY": 5,
    "CF": 5,
    "SM": 5,
    "al": 5,
    "rb": 10,
    "bu": 10,
    "pp": 10,
    "JR": 20,
    "j": 100,
    "jm": 60,
    "bb": 500,
    "ME": 50,
    "MA": 50,
    "jd": 10,
    "au": 1000,
    "IF": 300,
    "SF": 5,
    "y": 10,
    "a": 10,
    "m": 10,
    "b": 10,
    "TC": 200,
    "ZC": 100,
    "RS": 10,
    "RO": 5,
    "OI": 10,
    "RM": 10,
    "FG": 20,
    "ag": 15,
    "SR": 10,
    "v": 5,
    "TA": 5,
    "TF": 10000,
    "T": 10000,
    "sc": 1000,
    "TS": 10000
}

COMMISSION_RATE_DICT ={
    'rb': 0.0001,
    'IH': 0.0005
}
