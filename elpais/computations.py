# -*- coding: utf-8 -*-
"""
Created on Tue Feb 09 23:31:15 2016

@author: OriolAndres

cement BE.IE_3_3_1402A5.M.ES
electricity BE.BE_23_6_70257.M.ES
spain gdp ESE.990000D259D.Q.ES <- nominal ESE.940000D259D.Q.ES <- real
IBEX 35 ESE.854200259D.M.ES


public consumption ESE.991200D259D.Q.ES
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
from news_risk.settings import token, rootdir
import os

fig_fmt = 'png'



def load_external():
    #http://www.policyuncertainty.com/europe_monthly.html
    fedea = 'FEEA.PURE064A.M.ES' #'FEEA.SMOOTH064A.M.ES'
    ipri = 'ESE.425000259D.M.ES'
    
    ## government bonds:
    gb = ['EU.IRT_H_CGBY_M.M.DE','BE.IE_2_6_502A1.M.DE','EU.IRT_H_CGBY_M.M.ES','BE.BE_26_25_10294.M.ES','ESE.854200259D.M.ES']
    qbuilder = inquisitor.Inquisitor(token)
    df = qbuilder.series(ticker = [fedea, ipri] + gb)
    
    returns = df['ESE.854200259D.M.ES'].pct_change().dropna()*100
    returns = returns.sub(returns.mean())['19890101':]
    am = arch_model(returns, p=1, o=0, q=1)
    res = am.fit(update_freq=1, disp='off')
    df['cv'] = res.conditional_volatility
    return df

colnames = ['matches','eumatches','ingreso','gasto','money','sanidad','seguridad','banca','othregula','deuda','bienestar','arancel','autonomia','fiscal','regula']

#test 2
def load_es_uncertainty():
    df_ec = pd.read_csv(os.path.join(rootdir,'elpais','daily_data_economia.csv'),parse_dates = True,index_col=0)
    df_new = pd.read_csv(os.path.join(rootdir,'elpais','daily_data_economia_new.csv'),parse_dates = True,index_col=0)
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
    with open(os.path.join(rootdir,'euro_news.csv'),'r') as inf:
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
    left = ax.plot(nd['economia']/nd['economia'].mean()*100, 'r', label=u'España')
    ax2 = ax.twinx()
    rite = ax2.plot(nd['euro_news'], 'y', label='Europa')
    ax.set_ylabel("Índice Incertidumbre España".decode('utf8')) #,{'fontsize': 12}
    ax2.set_ylabel("Índice Incertidumbre Europa".decode('utf8'))
    
    lns = left + rite
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)
    ax.grid()
    fig.tight_layout()
    plt.savefig(os.path.join(rootdir, 'figures','spain_v_europe.%s' % fig_fmt), format=fig_fmt)
    return
    
def plot_eu_epu(nd):
    fig = plt.figure(2,[8,6])
    ax = fig.add_subplot(111)
    nd['policy'] =  nd.eumatches / nd.articles
    nd['policy'] = nd['policy'] / nd['policy'].mean()*100
    left = ax.plot(nd['economia']/nd['economia'].mean()*100, 'r', label='Política'.decode('utf8'))
    ax2 = ax.twinx()
    rite = ax2.plot(nd['policy'], 'y', label='General')
    ax.set_ylabel("Índice Incertidumbre (Política) España".decode('utf8')) #,{'fontsize': 12}
    ax2.set_ylabel("Índice Incertidumbre (General) España".decode('utf8'))
    
    lns = left + rite
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)
    ax.grid()
    fig.tight_layout()
    plt.savefig(os.path.join(rootdir, 'figures','policy_v_general.%s' % fig_fmt), format=fig_fmt)
    return

def transform_data(nd):
    nd['ibex'] = nd['ESE.854200259D.M.ES'].pct_change(periods = 18)
    nd['europe'] = nd['euro_news'].diff(periods = 1)
    nd['differential'] = (nd['BE.BE_26_25_10294.M.ES'] - nd['BE.IE_2_6_502A1.M.DE']).diff(periods = 1)
    nd['inflation'] = nd['ESE.425000259D.M.ES'].apply(np.log).diff(periods = 1)
    nd['fedea'] = nd['FEEA.PURE064A.M.ES'].diff(periods = 1)
    '''
    '''
    result = ols(y=nd['economia'], x=nd[['cv']])
    nd['resid'] = result.resid.diff(periods = 1)
    nd['raw'] = nd['economia'].diff(periods = 1)
    nd['vol'] = nd['cv'].diff(periods = 1)
    return nd

def get_quarterly_regressors():
    df_eu = load_eu_uncertainty()
    df_es = load_es_uncertainty()
    df_es['epu'] = df_es.matches / df_es.articles
    df_es['epu'] = df_es['epu'] / df_es['epu'].mean() *100
    nd = df_eu.join(df_es)
    nd = nd.resample("6M", how='mean')
    
    qbuilder = inquisitor.Inquisitor(token)
    df_macro = qbuilder.series(ticker = ['ESE.991200D259D.Q.ES', 'ESE.990000D259D.Q.ES'])
    df_macro = df_macro.resample("6M", how='sum')
    df_macro['spending'] = df_macro['ESE.991200D259D.Q.ES'] / df_macro['ESE.990000D259D.Q.ES']
    
    df_macro.index = df_macro.index.map(lambda t: t.replace(year=t.year, month=6*((t.month-1)//6+1), day=1))
    nd.index = nd.index.map(lambda t: t.replace(year=t.year, month=6*((t.month-1)//6+1), day=1))
    nd = nd.join(df_macro)
    nd[['spending','epu','euro_news']].to_csv(os.path.join(rootdir, 'regressors.csv'))
    return nd
    
    
def get_fedea_on_gdp():
    qbuilder = inquisitor.Inquisitor(token)
    df = qbuilder.series(ticker = ['ESE.940000D259D.Q.ES','FEEA.PURE064A.M.ES'])
    df.dropna(inplace = True)
    df['fedea'] = df['FEEA.PURE064A.M.ES'].diff()
    df['gdp'] = np.log(df['ESE.940000D259D.Q.ES']).diff()
    data1 = df[['fedea','gdp']]
    data1.dropna(inplace = True)
    model1 = VAR(data1)
    results1 = model1.fit(4)
    
    irf1 = results1.irf(8)
    fedea_on_gdp = irf1.orth_lr_effects[1,0] / data1['fedea'].std()
    return fedea_on_gdp
    
    
def estimate_VAR():
    df = load_external()
    d = load_es_uncertainty()
    df1 = load_eu_uncertainty()
    nd = d.join(df).join(df1)
    plot_index_comparison(nd)
    plot_eu_epu(nd)
    nd = transform_data(nd)
    
    benchmark_subset = ['EPU','europe', 'fedea', 'inflation', 'differential'] 
    nd['EPU'] = nd['matches'] / nd.articles
    nd['EPU'] = nd['EPU'] / nd['EPU'].mean() * 100
    nd['EPU'] = nd['EPU'].diff(periods = 1)
    data = nd.reindex(columns=benchmark_subset)
    data = data.dropna()
    data.describe()
    model = VAR(data)
    results = model.fit(6)

    irf = results.irf(12)
    irf.plot(orth=True, impulse='EPU', subplot_params = {'fontsize' : 12})
    #irf.plot_cum_effects(orth=True, impulse='EPU', subplot_params = {'fontsize' : 12}) #

    cum_effects = irf.orth_cum_effects 
    
    fedea_on_gdp = get_fedea_on_gdp()
    elasticity = -100*fedea_on_gdp*cum_effects[12,2,0]
    print 'Effects of a 1 sd uncertainty shock on gdp growth (negative): %0.3f%%' % elasticity
    print 'Inflation increases by %0.2f' % (100* cum_effects[12,3,0], )
    print 'Bond spreads increase by %0.1f basis points' % (100* cum_effects[12,4,0], )
    full_sset = ['ibex','vol','resid','europe', 'fedea', 'inflation', 'differential' ]
    

    def get_irf(nd, subset):
        '''
        http://statsmodels.sourceforge.net/0.6.0/vector_ar.html
        '''
        data = nd.reindex(columns=subset)
        data = data.dropna()
        data.describe()
        model = VAR(data)
        results = model.fit(6)
    
        irf = results.irf(12)
        
        cum_effects = irf.orth_cum_effects 
        
        return cum_effects[12,2,0]
    
    for colname in colnames:
        nd['uncert'] = nd[colname] / nd.articles
        nd['uncert'] = nd['uncert'] / nd['uncert'].mean() * 100
        nd['uncert'] = nd['uncert'].diff(periods = 1)
        subset = ['uncert','europe', 'fedea', 'inflation', 'differential' ]
        cum_effect= get_irf(nd, subset)
        print '%s | %d | %.04f' % (colname, nd[colname].sum(), 100*fedea_on_gdp*cum_effect)
    
    aa = d.mean()[colnames]
    plt.figure(1)
    h = plt.bar(range(len(aa)),aa,label = list(aa.index) )
    plt.subplots_adjust(bottom=0.3)
    
    xticks_pos = [0.65*patch.get_width() + patch.get_xy()[0] for patch in h]
    
    plt.xticks(xticks_pos, list(aa.index),  ha='right', rotation=45)
    plt.savefig(os.path.join(rootdir, 'figures','policy_v_general.%s' % fig_fmt), format=fig_fmt)
    
    
def articles_per_day():
    for s in ['Old', 'New']:
        if s == 'Old':
            a = 10; b = 30
        else:
            a = 20; b = 60
        df_ec = pd.read_csv(os.path.join(rootdir,'elpais','daily_data_economia%s.csv' % ('' if s == 'Old' else '_new')),parse_dates = True,index_col=0)
        hist, bins = np.histogram(df_ec.articles, bins = 50, density=True)
        center = (bins[:-1] + bins[1:]) / 2
        width = 0.7 * (bins[1] - bins[0])
        plt.bar(center, hist, align='center', width=width)
        plt.show()
        plt.savefig(os.path.join(rootdir, 'figures','articles_day_%s.%s' % (s,fig_fmt)), format=fig_fmt)
        r = float(sum([1 if a < x< b else 0 for x in df_ec.articles])) / len(df_ec)
        print s + ' system: %.1f%% of editions contain between %d and %d articles identified as economy related' % (r*100,a,b)


def main():
    articles_per_day()
    estimate_VAR()

if __name__ == '__main__':
    main()