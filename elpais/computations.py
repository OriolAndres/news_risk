# -*- coding: utf-8 -*-
"""
Created on Tue Feb 09 23:31:15 2016

@author: OriolAndres


cement BE.IE_3_3_1402A5.M.ES
electricity BE.BE_23_6_70257.M.ES
gdp spain ESE.90GV0VANUENL259D.Q.ES


IBEX 35 ESE.854200259D.M.ES


http://www.meff.com/aspx/Financiero/DescargaFicheros.aspx?id=esp
"""


from arch import arch_model
import inquisitor

import datetime
import pandas as pd
from re import sub
from matplotlib import pyplot as plt
import numpy as np

from pandas.stats.api import ols
from statsmodels.tsa.api import VAR
from settings import token

def load_external():

    #http://www.policyuncertainty.com/europe_monthly.html
    fedea = 'FEEA.SMOOTH064A.M.ES'
    ipri = 'ESE.425000259D.M.ES'
    
    ## government bonds:
    gb = ['EU.IRT_H_CGBY_M.M.DE','BE.IE_2_6_402A1.M.DE','EU.IRT_H_CGBY_M.M.ES','BE.BE_26_25_10294.M.ES','ESE.854200259D.M.ES']
    
    qbuilder = inquisitor.Inquisitor(token)
    df = qbuilder.series(ticker = [fedea, ipri] + gb)
    
    
    returns = df['ESE.854200259D.M.ES'].pct_change().dropna()
    returns = returns.sub(returns.mean())['19890101':]
    am = arch_model(returns, p=1, o=0, q=1)
    res = am.fit(update_freq=1, disp='off')
    df['cv'] = res.conditional_volatility

    return df

def load_es_uncertainty():
    df_ec = pd.read_csv('daily_data_economia.csv',parse_dates = True,index_col=0)
    df_new = pd.read_csv('daily_data_economia_new.csv',parse_dates = True,index_col=0)
    df_ec = pd.concat([df_ec,df_new])
    d = df_ec.resample("M", how='sum')
    d['economia'] = d.matches / d.articles#d.words
    d.index = d.index.map(lambda t: t.replace(year=t.year, month=t.month, day=1))
    '''
    d.density = d.words  / d.articles
    ax = d.density.plot( title = "articles get longer", figsize = (6,4), grid = True )
    '''
    return d

def load_eu_uncertainty():
    with open('euro_news.csv','r') as inf:
        lines = [sub(r'\n','',line).split(',') for line in inf.readlines()]
        idx = []
        vals = []
        for line in lines[1:]:
            idx.append(datetime.datetime(int(line[0]),int(line[1]),1))
            try:
                f = float(line[2])
            except:
                f = None
            vals.append(f)
    df1 = pd.DataFrame(vals, index= idx, columns = ['euro_news'])
    return df1

def plot_index_comparison(nd):
    fig = plt.figure(1,[8,6])
    ax = fig.add_subplot(111)
    left = ax.plot(nd['economia'], 'r', label='España'.decode('utf8'))
    ax2 = ax.twinx()
    rite = ax2.plot(nd['euro_news'], 'y', label='Europa')
    ax.set_ylabel("Índice Incertidumbre España".decode('utf8')) #,{'fontsize': 12}
    ax2.set_ylabel("Índice Incertidumbre Europa".decode('utf8'))
    
    lns = left + rite
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)
    ax.grid()
    fig.tight_layout()
    plt.savefig('spain_v_europe.pdf', format='pdf')
    return

def transform_data(nd):
    nd['ibex'] = nd['ESE.854200259D.M.ES'].pct_change(periods = 18)
    nd['europe'] = nd['euro_news'].diff(periods = 1)
    nd['differential'] = (nd['BE.BE_26_25_10294.M.ES'] - nd['BE.IE_2_6_402A1.M.DE']).diff(periods = 1)
    nd['inflation'] = nd['ESE.425000259D.M.ES'].apply(np.log).diff(periods = 1)
    nd['fedea'] = nd['FEEA.SMOOTH064A.M.ES'].diff(periods = 1)
    '''
    nd.cv.plot()
    nd.economia.plot(secondary_y = True)
    plt.legend()
    plt.show() 
    
    '''
    result = ols(y=nd['economia'], x=nd[['cv']])
    nd['resid'] = result.resid.diff(periods = 1)
    nd['raw'] = nd['economia'].diff(periods = 1)
    nd['vol'] = nd['cv'].diff(periods = 1)
    return nd

df = load_external()
d = load_es_uncertainty()
df1 = load_eu_uncertainty()
nd = d.join(df).join(df1)
plot_index_comparison(nd)

nd = transform_data(nd)

subset = ['ibex','vol','resid','europe', 'fedea', 'inflation', 'differential' ]
def get_irf(nd, subset):
    '''
    http://statsmodels.sourceforge.net/0.6.0/vector_ar.html
    '''
    data = nd.reindex(columns=subset)
    data = data.dropna()
    #data.describe()
    model = VAR(data)
    results = model.fit(6)

    irf = results.irf(24)
    irf.plot_cum_effects(orth=True, subplot_params = {'fontsize' : 10}) #, impulse='spain'

    cum_effects = irf.orth_lr_effects

aa = d.mean()[['matches','ingreso','gasto','money','sanidad','seguridad','banca','regula','deuda','bienestar','arancel']]
plt.figure(1)
h = plt.bar(range(len(aa)),aa,label = list(aa.index) )
plt.subplots_adjust(bottom=0.3)

xticks_pos = [0.65*patch.get_width() + patch.get_xy()[0] for patch in h]

plt.xticks(xticks_pos, list(aa.index),  ha='right', rotation=45)