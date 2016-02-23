# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 12:53:23 2016

@author: OriolAndres
"""
from arch import arch_model
import os
import csv
from re import sub, compile, I, DOTALL, match
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime
from news_risk.settings import rootdir
datadir = os.path.join(rootdir,'stocks','data')


with open(os.path.join(rootdir,'accounts','biz_meta_regex.csv'),'rb') as inf:
    instream = csv.reader(inf)
    entity_regex_l = list(instream)

patterns = map(lambda x: compile(x[1],I|DOTALL).match, entity_regex_l)

pairs = {}
seen = set()
unmatched = []
for f in os.listdir(datadir):
    stock_name = sub(r'\.asp','',sub(r'_',' ',f.decode('latin1').encode('utf8')))
    if match(r'^(.*\bb|.*derechos.*)$',stock_name,I): ## this gets rid of warrants and B class shares
        continue
    for i, p in enumerate(patterns):
        if p(stock_name) and i not in seen:
            pairs[i] = f
            seen.add(i)
            #print entity_regex_l[i][0], stock_name
            break
    else:
        unmatched.append(stock_name)
        print 'no matches for ', stock_name
assert(entity_regex_l[162][0] == 'DISTRIBUIDORA INTERNACIONAL DE ALIMENTACION, S.A.')
pairs[162] =  'dia.asp'## distribuidora


def parseDate(x):
    return datetime.datetime.strptime(x,'%d/%m/%y')
def parseFloat(x):
    try:
        y = float(sub(',','.',sub('\.','',sub('%','',x))))
    except:
        y = None
    return y


def get_cv_from_file(f):
    with open(os.path.join(datadir,f),'r') as inf:
        fulls = inf.read().decode('latin1')
        for tag in ['table','td','th','tr']:
            fulls = sub(r'<{0} .*?>'.format(tag),'<{0}>'.format(tag),fulls)
        bs = BeautifulSoup(fulls,'lxml')
    rows = bs.find_all('tr')
    
    dates = []
    vals = []
    for j,row in enumerate(rows[1:-1]): # remove last row cause instead of percent gain they show level
        td = row.find_all('td')
        
        fl = parseFloat(td[2].text)
        if fl is not None and fl > 0.0:
            dates.append(parseDate(td[0].text))
            vals.append(fl)
    dates.reverse()
    vals.reverse()
    df = pd.DataFrame(zip(dates, vals), columns = ['Dates','Prices'])
    df['Returns'] = df.Prices.pct_change()*100
    df.set_index('Dates', inplace = True)

    am = arch_model(df.Returns.dropna().tolist(), p=1, o=0, q=1)
    res = am.fit(update_freq=1, disp='off')
    df['cv'] = np.insert(res.conditional_volatility,0,res.conditional_volatility[0:40].mean())
    d = df.resample("6M", how='mean')
    d.index = d.index.map(lambda t: t.replace(year=t.year, month=((t.month -1) // 6 +1)*6, day=1))
    return d

ibex_df = get_cv_from_file('ibex35.asp')
'''
Do not include entity in dataset if no quoted stock found
'''
cv_dict = {}
for i,entity in enumerate(entity_regex_l):
    f = pairs.get(i,'ibex35.asp')
    if f == 'ibex35.asp':
        df = ibex_df
    else:
        df =  get_cv_from_file(f)
        cv_dict[entity[0]] = zip(df.index.map(lambda x: x.strftime('%Y%m%d')).tolist(),df.cv)
cv_dict['ibex35'] = zip(ibex_df.index.map(lambda x: x.strftime('%Y%m%d')).tolist(),ibex_df.cv)
with open(os.path.join(rootdir,'stocks', 'cond_vol.csv'),'wb') as outf:
    outstream = csv.writer(outf)
    for k,v in cv_dict.items():
        for entry in v:
            outstream.writerow([k,entry[0],entry[1]])