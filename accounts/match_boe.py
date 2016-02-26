# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 02:00:26 2016

@author: OriolAndres
http://stackoverflow.com/questions/23600582/concatenate-pandas-columns-under-new-multi-index-level
"""
import os
import csv
from news_risk.settings import rootdir
from re import I,sub, DOTALL, compile
import pandas as pd
import datetime
import numpy as np
from Levenshtein import distance
from matplotlib import pyplot as plt

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
    
with open(os.path.join(rootdir,'accounts','biz_meta_regex.csv'),'rb') as inf:
    instream = csv.reader(inf)
    entity_regex_l = list(instream)
patterns = map(lambda x: compile(x[1],I|DOTALL).match, entity_regex_l)

def find_work_by_entity():
    wee = []
    ell = 0
    valid = 0
      
            
    for y in range(2005,2016):
        datadir = os.path.join(rootdir, 'boe','data\%d' % y)
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
        from matplotlib import pyplot as plt
        import operator
        max(enumerate([x[2] for x in period_entity_contracts]), key = operator.itemgetter(1))
        hist, bins = np.histogram([x[2] for x in period_entity_contracts if x[2] > 0], bins = 50, density=True)
        center = (bins[:-1] + bins[1:]) / 2
        width = 0.7 * (bins[1] - bins[0])
        plt.bar(center, hist, align='center', width=width)
        plt.show()
    return period_entity_contracts



def build_data_frame():
    period_entity_contracts = find_work_by_entity()
    
    with open(os.path.join(rootdir,'accounts','stats_table.csv'),'rb') as inf:
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
        df.set_index('Dates',inplace = True)
        
        datadict[entity] = df
        

    cv_dict = {}
    with open(os.path.join(rootdir,'stocks', 'cond_vol.csv'),'rb') as inf:
        instream = csv.reader(inf)
        entity = None
    
        dates = []
        vals = []
        for line in instream:
            if line[0] == entity:
                dates.append(datetime.datetime.strptime( line[1], '%Y%m%d'))
                vals.append(float(line[2]))
            else:
                if entity is None:
                    entity = line[0]
                    dates.append(datetime.datetime.strptime( line[1], '%Y%m%d'))
                    vals.append(float(line[2]))
                else:
                    df = pd.DataFrame(zip(dates, vals),columns=['Dates','CV'])
                    df.set_index('Dates', inplace = True)
                    cv_dict[entity] = df
                    entity = line[0]
                    dates = [datetime.datetime.strptime( line[1], '%Y%m%d')]
                    vals = [float(line[2])]
        df = pd.DataFrame(zip(dates, vals),columns=['Dates','CV'])
        df.set_index('Dates', inplace = True)
        cv_dict[entity] = df
        
    cv_dict['ibex35'].columns = ['ibex35']
        
    with open(os.path.join(rootdir,'accounts', 'sector_members.csv'),'rb') as inf:
        inlines = list(csv.reader(inf))
        sectors = list(set(x[0] for x in inlines))
        
    with open(os.path.join(rootdir,'accounts','short_long.csv'),'rb') as inf:
        short_long_names = dict((x[0],x[1]) for x in csv.reader(inf))
    
    sector_avg = []
    entity_sector_pairs = {}
    for s, sector in enumerate(sectors):
        members = [x[1] for x in inlines if x[0] == sector]
        public_eur = 0
        sector_sales = 0
        for member in members:
            dstar  = 1000
            entity_id = None
            kstar  = None
            for k,v in short_long_names.iteritems():
                d = distance(member, k)
                if d  < dstar:
                    dstar = d
                    entity_id  = v
                    kstar = k
            #print  kstar, member
            if entity_id not in datadict:
                continue
            entity_sector_pairs[entity_id] = s
            public_eur += datadict[entity_id]['Contracts_eur'].sum()
            sector_sales += datadict[entity_id]['Sales'].sum()
        sector_avg.append(public_eur / sector_sales if sector_sales > 0 else 0.)

    #import operator
    #sorted(zip(sectors,sector_avg), key = operator.itemgetter(1), reverse = True)

    macro_df = pd.DataFrame.from_csv(os.path.join(rootdir, 'regressors.csv'))
    bigdict = {}
    wrongness = 0
    goodness = 0
    for entity_id in datadict.keys():
        datadict[entity_id] = datadict[entity_id].join(macro_df)
        s = entity_sector_pairs[entity_id]
        
        datadict[entity_id]['log_epu'] = np.log(datadict[entity_id]['epu'])
        datadict[entity_id]['epu_weighted'] = sector_avg[s]*datadict[entity_id]['log_epu']
        datadict[entity_id]['spend_weighted'] = sector_avg[s]*datadict[entity_id]['spending']
        assert('Wages' in datadict[entity_id])
        datadict[entity_id]['log_w'] = np.log(datadict[entity_id]['Wages'])
        datadict[entity_id]['dlog_w'] = datadict[entity_id]['log_w'].diff()
        datadict[entity_id]['dspend_weighted'] = datadict[entity_id]['spend_weighted'].diff()
        datadict[entity_id][['llog_epu','lepu_weighted','ldspend_weighted']] = datadict[entity_id][['log_epu','epu_weighted','dspend_weighted']].shift(1)
        if entity_id not in cv_dict: ## exclude entities for which no stock
            continue
        df1 = datadict[entity_id].join(cv_dict[entity_id]).join(cv_dict['ibex35'])
        df1['ibex_weighted'] = df1['ibex35']*sector_avg[s]
        
        #df1 = df1[[x[0] or x[1] for x in zip(list(df1['dlog_w'].abs() < 1), list(df1['dlog_w'].isnull()) ) ]]
        if any(datadict[entity_id]['log_w'].diff().abs() > 1):
            wrongness +=1
            print entity_id + 'has wage data issues'
        else:
            goodness +=1
            
        if len(df1.dropna()) < 2:
            df1['single'] = 1
        else: 
            df1['single'] = 0
        bigdict[entity_id] = df1
    bigdf = pd.concat(bigdict.values(),keys=bigdict.keys())
        
    for k,v in bigdict.items():
        assert( v.index.is_unique)
        
    for k,v in bigdict.items():
        if not v.index.is_unique:
            break
    return bigdf
    
def run_regressions():
    bigdf = build_data_frame()
    
    xcand = ['log_epu','epu_weighted','ibex35','ibex_weighted','spending','spend_weighted']
    
    reglist = [[0,4],[1,5],[0,2,4],[1,3,5]]
    
    dummies = [False, True, False, True]
    rownames = []
    for v in xcand:
        rownames.extend([v,''])
    rownames += ['lag_expend', '','r2', 'N']
    scatter_flag = True
    for dependent in ['CV', 'log_w']:
        #print '\n' + '-'*15 + ' Results for %s ' % dependent +  '-'*15 + '\n'
        ph = np.zeros(( (len(xcand)+2)*2, len(reglist)))
        for ix, regressors in enumerate(reglist):
            if dependent == 'log_w':
                df = bigdf[bigdf['Wages'] > 0]
                oldnames = ['llog_epu','lepu_weighted','ldspend_weighted', 'dlog_w','dspend_weighted']
                newnames = ['log_epu','epu_weighted','lag_exp', 'log_w','spend_weighted']                
                df[newnames] = df[oldnames]
                optional = ['lag_exp']
                df = df.dropna()
                df = df[df['single'] == 0]
                df = df[np.isfinite(df)]
                if scatter_flag:
                    scatter_flag = False
                    fig = plt.figure(1,[8,6])
                    ax = fig.add_subplot(111)
                    ax.scatter(df['log_epu'],df['log_w'])
                    ax.set_ylabel("Wage expenses growth (logs, semester)") #,{'fontsize': 12}
                    ax.set_xlabel("EPU index (log)")
                    ax.grid()
                    fig.tight_layout()
                    plt.savefig(os.path.join(rootdir, 'figures','wage_growth_epu.png'))
                    
                    fig2 = plt.figure(2,[8,6])
                    ax2 = fig2.add_subplot(111)
                    ax2.scatter(df['spend_weighted'],df['log_w'])
                    ax2.set_ylabel("Wage expenses growth (logs, semester)") #,{'fontsize': 12}
                    ax2.set_xlabel("Public exp/gdp * sector public weight (Change in period)")
                    ax2.grid()
                    fig2.tight_layout()
                    plt.savefig(os.path.join(rootdir, 'figures','wage_growth_ratio.png'))
            else:
                df = bigdf
                optional = []
            reg  = PanelOLS(y=df[dependent],x=df[[xcand[i] for i in regressors]+optional],  time_effects=dummies[ix], entity_effects=dummies[ix])
            for v in regressors:
                ph[v*2, ix] =  reg.beta[xcand[v]]
                ph[v*2 +1, ix] =  reg.p_value[xcand[v]]
            for o in optional:
                ph[-4, ix] =  reg.beta[o]
                ph[-3, ix] =  reg.p_value[o]
            ph[-2, ix] =  reg.r2
            ph[-1, ix] =  reg.nobs
        
        print ' | '.join([dependent] + ['(%d)' % x for x in range(1,len(reglist)+1) ])
        print ' | '.join(['---' if j ==0 else ':---:' for j in range(len(reglist)+1)])
        for i in range(len(ph)):
            if i == len(ph) -1: ## number observations
                vals = ['%d' % x if x!=0 else ' ' for x in ph[i,:]]
            else:
                vals = ['%0.3f' % x if x!=0 else ' ' for x in ph[i,:]]
            print ' | '.join(['**'+rownames[i]+'**' if rownames[i] != '' else ''] + vals)
        print ' | '.join(['**Time&firm eff.**'] + map(str,dummies))
        print '\n'