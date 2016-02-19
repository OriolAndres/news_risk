# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 12:53:23 2016

@author: OriolAndres
"""
from arch import arch_model
import os

rootdir = r'C:/users/oriolandres/desktop/news_risk/stocks'
datadir = os.path.join(rootdir,'data')
os.listdir()


returns = []
am = arch_model(returns, p=1, o=0, q=1)
res = am.fit(update_freq=1, disp='off')
res.conditional_volatility