# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 02:00:26 2016

@author: OriolAndres
"""
import os
import csv
rootdir = r'C:/users/oriolandres/desktop/news_risk/accounts'
from re import match, I,sub, DOTALL, compile
import pandas as pd
import datetime

from pandas.stats.plm import PanelOLS

def lower_case(instring):
    u = 'ÑÁÉÍÓÚÜ'
    l = 'ñáéíóúü'
    for i,c in enumerate(u):
        instring = sub(c,l[i],instring)
    return instring


def get_semester(x):
    dt = datetime.datetime.strptime(x,'%Y%m%d')
    dt = datetime.datetime(dt.year, ((dt.month -1) // 6 + 1)*6,1)
    return dt

    
with open(os.path.join(rootdir,'biz_meta_regex.csv'),'rb') as inf:
    instream = csv.reader(inf)
    entity_regex_l = list(instream)
patterns = map(lambda x: compile(x[1],I|DOTALL).match, entity_regex_l)

wee = []
ell = 0
valid = 0
  
        
for y in range(2005,2016):
    datadir = r'C:\Users\OriolAndres\Desktop\news_risk\boe\data\%d' % y
    with open(os.path.join(datadir,'catches.csv'),'rb') as inf:
        contracts = [(lower_case(x[1]),x[2],get_semester(x[3])) for x in csv.reader(inf)]
    for contract in contracts:
        try:
            budget = float(sub(',','.',sub('[^\d,]','',contract[1])))
        except:
            budget = None
        ell += budget if budget is not None else 0
        valid += 1 if budget is not None else 0
        for i,p in enumerate(patterns):
            if p(contract[0]):
                wee.append(( i,contract[0], budget, contract[2]))
        
#sum([x[2] for x in wee if x[2] is not None])
period_entity_contracts = []
for i in range(len(entity_regex_l)):
    subset = [x for x in wee if x[0] == i]
    for t in range(2005,2016):
        for s in range(2):
            dt = datetime.datetime(t,(s+1)*6,1)
            subset_p = [x for x in subset if x[3] == dt]
            period_entity_contracts.append([dt.strftime('%Y%m%d'),entity_regex_l[i][0],sum([x[2] for x in subset_p if x[2] is not None]),len(subset_p)])
if 0:
    import numpy as np
    from matplotlib import pyplot as plt
    import operator
    max(enumerate([x[2] for x in period_entity_contracts]), key = operator.itemgetter(1))
    hist, bins = np.histogram([x[2] for x in period_entity_contracts if x[2] > 0], bins = 50, density=True)
    center = (bins[:-1] + bins[1:]) / 2
    width = 0.7 * (bins[1] - bins[0])
    plt.bar(center, hist, align='center', width=width)
    plt.show()


with open(os.path.join(rootdir,'stats_table.csv'),'rb') as inf:
    instream = csv.reader(inf)
    accounts = list(instream)
        
datadict = {}
for entity_regex in entity_regex_l:
    entity = entity_regex[0]
    contract_subset = [x for x in period_entity_contracts if x[1] == entity]
    subset = [x for x in accounts if x[0] == entity] 
    clean = []
    for i,r in enumerate(subset):
        if r[2] == 'NA' or r[2] < '2005':
            continue
        for j in [3,4]:
            r[j] = r[j] if r[j] != 'NA' else 'nan'
        dt = datetime.datetime.strptime(r[2],'%Y%m%d')
        if dt.month == 12:
            if i == 0 or not clean or clean[-1][0].year != dt.year:
                wages = -float(r[3]) / 2
                sales = float(r[4]) / 2
            else:
                wages = -float(r[3]) - clean[-1][1]
                sales = float(r[4]) - clean[-1][2]
        else:
            wages  = -float(r[3])
            sales = float(r[4])
            
        mlist = [x for x in contract_subset if x[0] == r[2]]
        contract_eur = mlist[0][2]; contract_n = mlist[0][3]
        clean.append([dt,wages, sales, contract_eur, contract_n])
    df = pd.DataFrame(clean,columns=['Dates','Wages','Sales','Contracts_eur','Contracts_n'])
    df.set_index('Dates')
    
    datadict[entity] = df
    



panel = pd.Panel.from_dict(datadict)
PanelOLS(y=df['y'],x=df[['x']])

import statsmodels.api as sm
import statsmodels.formula.api as smf