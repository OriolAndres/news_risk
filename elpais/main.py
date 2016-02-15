# -*- coding: utf-8 -*-
"""
http://elpais.com/tag/economia/a/19850

Created on Tue Feb 09 21:41:34 2016

@author: OriolAndres

Our modern monthly EPU index for the US relies on 10 leading newspapers: USA
Today, Miami Herald, Chicago Tribune, Washington Post, Los Angeles Times, Boston Globe,
San Francisco Chronicle, Dallas Morning News, New York Times, and Wall Street Journal. We
search the digital archives of each paper from January 1985 to obtain a monthly count of articles
that contain the following triple: ‘uncertainty’ or ‘uncertain’; ‘economic’ or ‘economy’; and one
of the following policy terms: ‘congress’, ‘deficit’, ‘Federal Reserve’, ‘legislation’, ‘regulation’
or ‘white house’ (including variants like ‘uncertainties’, ‘regulatory’ or ‘the Fed’). In other
words, to meet our criteria, an article must contain terms in all three categories pertaining to
uncertainty, the economy, and policy. We use our audit study to select the policy terms, as
explained in Section 3.1.


http://www.policyuncertainty.com/media/BakerBloomDavis.pdf
http://www.policyuncertainty.com/methodology.html

i) taxes
ii) government spending, budget
iii) fiscal policy either taxes and/or spending
iv) monetary policy
v) healthcare
vi) national security
vii) regulation
viii) sovereign debt - currency
ix) entitlement programs
x) trade policy

"""

from re import compile, match, I, sub, MULTILINE

conds = [[r'incertidumbre',r'\binciert'],
         [r'econ(o|ó)m(i|í)'],
         [r'\bimp(uesto|ositiv|onib)',r'\btarifa',r'\bregula(ci|ti|to)',r'\bpol(i|í)tica',r'\bgast(ar|o|a|os)\b',r'\bpresupuest',r'\bd(e|é)ficit',r'\bbanc(o|a)[s]?[\s]*central',r'\bbanco de españa',r'\btribut']]
conds = [[compile(w,I|MULTILINE).search for w in cond] for cond in conds]
    

add_conds = [[r'\bimp(uesto|ositiv|onib)',r'\btarifa',r'\brecauda',r'\btribut',r'\biva\b',r'\birpf\b'],
             [r'\bgast(ar|o|a|os)\b',r'\bpresupuest',r'(deuda|d(é|e)ficit) p(u|ú)blic',r'\berario',r'pacto de estabilidad'],
             [r'\bbanc(o|a)[s]?[\s]*central',r'\bbce\b',r'\bbde\b',r'\bbanco de españa',r'pol(i|í)tica monetaria'],
             [r'\bsani(tari|dad)',r'\bhospital',r'\bfarmac(ia|eu)',r'\bm(e|é)dic(o|in)'],
             [r'seguridad nacional',r'\bmilitar',r'\bterrorismo',r'\beta\b',r'minist(erio|ro) de defensa',r'fuerzas armadas'],
             [r'supervis(ión|or) bancar',r'reformas? financiera',r'tests? de estrés',r'stress test',r'comisi(o|ó)n nacional',r'cnmv',r'fondo de (garant(i|í)a de )?dep(o|ó)sito',r'basilea'],
             [r'\bregula(ci|ti|to)',r'convenio',r'\blegisla',r'\bley(es)?\b',r'monopol',r'\bc(a|á)rtel',r'\bderecho'],
             [r'deuda (sobera|p(ú|u)blic)',r'crisis de deuda',r'\bdevalu',r'tipos? de cambio',r'\bcambiari',r'\beuro.?zona',r'\brublo'],
             [r'seguridad social',r'asuntos? social',r'estado del bienestar',r'subsidi(o|a)',r'fondos? estructural'],
             [r'\barancel',r'\baduan(a|e)',r'tarifas?.{1,6}\b(expor|impor)',r'tratados?.{1,6}(libre.{1,6})?\bcomerc'],
             [r'\bdescentraliz',r'\bindependent',r'\bseparati',r'\bsecesi(o|ó)n',r'\bibarretx',r'\bnacionalis',r'\bterritorial']] # # 
colnames = ['ingreso','gasto','money','sanidad','seguridad','banca','othregula','deuda','bienestar','arancel','autonomia']

add_conds = [[compile(w,I|MULTILINE).search for w in cond] for cond in add_conds]
combos = [(0,1),(5,6)]
combo_names = ['fiscal','regula']

c_n = len(add_conds)
b_n = len(combos)

import urllib2
import datetime
from bs4 import BeautifulSoup
import os

import pandas as pd
import numpy as np
rootdir = os.path.dirname(__file__)#r'C:/users/oriolandres/desktop/news_risk/elpais'
datadir = os.path.join(rootdir,'data')
if not os.path.exists(datadir):
    os.makedirs(datadir)


def create_archive(y = 1978, offset = 0, sect = 'economia'):
    url_tem = 'http://elpais.com/diario/{year}/{mon:02d}/{day:02d}/{sect}/'
    t0 = datetime.datetime(y,1,1)
    ydir = os.path.join(datadir,str(y) )
    
    if not os.path.exists(ydir):
        os.makedirs(ydir)
        
    for i in range(offset, 366): ## cover  leap year cases
        if (y == 1976 and i <120) or y > 2012 or (y == 2012 and i > 30): # starts at 4 may
            continue
        t  = t0 + datetime.timedelta(days = i)
        
        if t.year != y: continue # if not leap year skip last iteration
        mon = t.month
        mondir = os.path.join(ydir,str(mon))    
        if not os.path.exists(mondir):
            os.makedirs(mondir)
        d = t.day
        ddir = os.path.join(mondir,str(d))
        if not os.path.exists(ddir):
            os.makedirs(ddir)
    
        
        if sect == 'espana':
            ifname = 'index.html'
        else:
            ifname = 'index_ec.html'
        
        if ifname not in os.listdir(ddir):
            url = url_tem.format(year = str(y), mon = mon,day = d, sect = sect)
            print url
            try:
                resp  = urllib2.urlopen(url)
            except urllib2.HTTPError, err:
                if err.code == 404:
                    with open(os.path.join(ddir, ifname),'w') as outf:
                        outf.write('')
                    continue
                else:
                    raise err
            html = resp.read()
            
            with open(os.path.join(ddir, ifname),'w') as outf:
                outf.write(html)
        else:
            with open(os.path.join(ddir, ifname),'r') as inf:
                html= inf.read()
        bsoup = BeautifulSoup(html, 'html.parser')
        art_ls = bsoup.find_all('div',{'class':'article'})
        h_ls = []
        for art in art_ls:
            try:
                h = art.find('h2')
                link = h.find('a').attrs['href']
            except:
                continue
            h_ls.append((h.text,link))
            
        for h in h_ls:
            url = 'http://elpais.com/' + sub(r'^/','',h[1])
            fname = match(r'^.*?([^/]*\.html)$',h[1]).groups()[0]
            if sect == 'espana':
                fname = 'es_' + fname
            else:
                fname = 'ec_' + fname
            if fname not in os.listdir(ddir):
                try:
                    res = urllib2.urlopen(url)
                    ht = res.read()
                    with open(os.path.join(ddir,fname),'w') as outf:
                        outf.write(ht)
                except urllib2.HTTPError, err:
                    print url
                    print err
            else:
                with open(os.path.join(ddir,fname),'r') as inf:
                    ht = inf.read()
            fname = fname[:fname.rfind('.')]
            txtf = '%s.txt' % fname
            if txtf not in os.listdir(ddir):
                bsoup = BeautifulSoup(ht,'html.parser')
                title = bsoup.find('h1',{'id':'titulo_noticia'}).text
                content = bsoup.find('div',{'id':'cuerpo_noticia'}).text
                with open(os.path.join(ddir, txtf), 'w') as outf:
                    outf.write(title.encode('utf8') + '\n')
                    outf.write(content.encode('utf8'))  

def match_file(inpstr):
    for cond in conds:
        for p in cond:
            m = p(inpstr)
            if m:
                break
        else:
            return [False]
            
    out = [True]
    for cond in add_conds:
        for p in cond:
            m = p(inpstr)
            if m:
                out.append(True)
                break
        else:
            out.append(False)
    return out
    
def build_index(section = 'economia', new_format = True):
    #r'\bdiputad',r'\bminist',r'gobiern',r'\blegisla',r'\bley(es)?\b'
    
    if new_format:
        y = 2012
        t0 = datetime.datetime(y,2,1)
        num_days =  (datetime.datetime(2016,1,31) - t0).days + 1
    else:
        y = 1976
        t0 = datetime.datetime(y,5,4)
        num_days =  13056 # days until 31 january 2012, 4th may included
    
    
    rng = pd.date_range(t0.strftime('%m/%d/%Y'), periods=num_days, freq='D')
    df = pd.DataFrame(np.zeros((num_days,3 + c_n + b_n)), index=rng,columns=['matches','articles','words'] + colnames + combo_names)
    
    for i in range(num_days):
        t = t0 + datetime.timedelta(days = i)
        d = t.day
        m = t.month
        y = t.year
        assert(t == df.index[i].to_datetime())
        ddir = os.path.join(datadir,str(y),str(m),str(d))
        if not os.path.exists(ddir):
            continue
        if section == 'espana':
            txtfiles = [x for x in os.listdir(ddir) if match(r'^es_.*\.txt$',x,I)]
            rfile = 'res1.txt'
        else:
            txtfiles = [x for x in os.listdir(ddir) if match(r'^ec_.*\.txt$',x,I)]
            rfile = 'res.txt'
        m_n = 0; a_n = 0; w_n = 0
        
        if rfile in os.listdir(ddir) and False:
            with open(os.path.join(ddir,rfile),'r') as inf:
                res = inf.read().split(',')
                m_n = int(res[0])
                a_n = int(res[1])
                w_n = int(res[2])
                rest = [int(res[3+k]) for k in range(c_n + b_n)]
        
        if a_n == 0:
            
            rest = [0]*(c_n+ b_n)
            for txtf in txtfiles:
                with open(os.path.join(ddir, txtf), 'r') as inf:
                    inpstr = inf.read()
                
                m = match_file(inpstr)
                if m[0]:
                    
                    m_n +=1
                    combo_f = [False]*b_n
                    for j in range(c_n):
                        if m[1+j]:
                            rest[j] += 1
                            for k in range(b_n):
                                if j in combos[k]:
                                    combo_f[k] = True
                    for k in range(b_n):
                        if combo_f[k]:
                            rest[c_n + k] += 1
                w_n += len(inpstr.split())
                a_n += 1
            with open(os.path.join(ddir,rfile),'w') as outf:
                outf.write('%d,%d,%d,%s' % (m_n, a_n, w_n,','.join(['%d' % x for x in rest]) ))
        df.matches[i] += m_n
        df.articles[i] += a_n
        df.words[i] += w_n
        for j in range(len(add_conds)):
            df[colnames[j]][i] += rest[j]
    if not new_format:
        df.to_csv('daily_data_{0}.csv'.format(section))
    else:
        df.to_csv('daily_data_{0}_new.csv'.format(section))


def retrieve_old_archive():
    for sect in ['espana','economia']:
        for y in range(1976,2013):
            create_archive(y,0,sect)
        
        
def retrieve_new_archive():
    url_tem = 'http://elpais.com/tag/economia/a/{page}'
    
    newindices = os.path.join(datadir,'newindices')
    if not os.path.exists(newindices):
        os.makedirs(newindices)
    
    for page in range(19894,22298):
        fname = '%s.html' % page        
        if fname not in os.listdir(newindices):
            res = urllib2.urlopen(url_tem.format(page= page))
            h = res.read()
            with open(os.path.join(newindices,fname),'w') as outf:
                outf.write(h)
        with open(os.path.join(newindices,fname),'r') as inf:
            bsoup = BeautifulSoup(inf.read(),'html.parser')
        for article in bsoup.find_all('div',{'class':'article'}):
            dt = datetime.datetime.strptime(article.find('a',{'class','fecha'}).text,'%d/%m/%Y')
            if dt < datetime.datetime(2012,2,8): 
                continue
            link = article.find('h2').find('a').attrs['href']
            if match('^.*videos|album.*$',link,I):
                continue
            try:
                art_fname = 'ec_' + match(r'^.*?([^/]*\.html)$',link).groups()[0]
            except: continue
            path = os.path.join(datadir, str(dt.year),str(dt.month),str(dt.day))
            if not os.path.exists(path):
                os.makedirs(path)
            if art_fname not in os.listdir(path):
                try:
                    resp = urllib2.urlopen(link)
                    with open(os.path.join(path,art_fname),'w') as outf:
                        outf.write(resp.read())
                except (urllib2.HTTPError,urllib2.URLError), err:
                    print link
                    print err
                    continue

            with open(os.path.join(path,art_fname),'r') as inf:
                artsoup = BeautifulSoup(inf.read(),'html.parser')
            title_html = artsoup.find('title').text
            if match('^.*blogs\sel\spa.s.*$',title_html, I): continue
            art_fname = art_fname[:art_fname.rfind('.')]
            txtf = '%s.txt' % art_fname
            if txtf not in os.listdir(path):
                try:
                    title = artsoup.find('h1',{'id':'titulo_noticia'}).text
                    content = artsoup.find('div',{'id':'cuerpo_noticia'}).text
                    with open(os.path.join(path, txtf), 'w') as outf:
                        outf.write(title.encode('utf8') + '\n')
                        outf.write(content.encode('utf8'))
                except:
                    continue
                
if __name__ == '__main__':
    retrieve_old_archive()
    build_index(section = 'economia', new_format = False)
    retrieve_new_archive()
    build_index(section = 'economia', new_format = True)
'''
'19760504',10, diumenge 15
'19770104',15, diumenge 20
'19780304',18, diumenge 25
'19781005',19, diumenge 25
'19790101',20, diumenge 25
'19800701',25, diumenge 30
'19810701',30, diumenge 40
'19820501',35, diumenge 50
'19830501',40, diumenge 60
'19840501',45, diumenge 75
'19850419',50, diumenge 75
'19860120',60, diumenge 90
'19870520',60, diumenge 100
'19881120',60, diumenge 125
'19890120',65, diumenge 125
'19900320',75, diumenge 150
'19910320',80, diumenge 175
'19920320',90, diumenge 200
'19930120',100, diumenge 225
'19940320',100, diumenge 250
'19950320',110, diumenge 275
'19960320',125, diumenge 275
'20001016',150, diumenge 275
'20020116',.90, diumenge 1.8
'20020416',1, diumenge 1.8
'20050116',1, diumenge 1.9
'20061029',1, diumenge 2
'20080529',1.1, diumenge 2.2
'20090502',1.2, diumenge 2.2
'20100602',1.2, diumenge 2.5
'20120608',1.3, diumenge 2.5
'20151001',1.4, diumenge 2.5
'''