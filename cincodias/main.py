# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 15:03:09 2016

@author: OriolAndres

http://cincodias.com/tag/economia/a/
"""

num_pages = 9221

from re import match, I
import urllib2
import datetime
from bs4 import BeautifulSoup
import os
import pandas as pd
import numpy as np

from news_risk.settings import rootdir
thisdir = os.path.join(rootdir,'cincodias')
datadir = os.path.join(thisdir,'data')
if not os.path.exists(datadir):
    os.makedirs(datadir)


from re import compile, MULTILINE

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


def create_archive():
    url_tem = 'http://cincodias.com/tag/economia/a/{page}'
    
    newindices = os.path.join(datadir,'newindices')
    for page in range(1,num_pages+1):#range(1,num_pages+1):
        fname = '%s.html' % page
        
        if fname not in os.listdir(newindices):
            res = urllib2.urlopen(url_tem.format(page= page))
            with open(os.path.join(newindices,fname),'w') as outf:
                outf.write(res.read())
        with open(os.path.join(newindices,fname),'r') as inf:
            bsoup = BeautifulSoup(inf.read(),'html.parser')
        for article in bsoup.find_all('div',{'class':'article'}):
            dt = datetime.datetime.strptime(article.find('a',{'class','fecha'}).text,'%d/%m/%Y')
            #if dt < datetime.datetime(2010,5,9): continue
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
                    h = resp.read()
                    with open(os.path.join(path,art_fname),'w') as outf:
                        outf.write(h)
                except (urllib2.HTTPError,urllib2.URLError), err:
                    print link
                    print err
                    continue

            with open(os.path.join(path,art_fname),'r') as inf:
                artsoup = BeautifulSoup(inf.read(),'html.parser')

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
                
   
        
def match_file(inpstr):
    for j, cond in enumerate(conds):
        for p in cond:
            m = p(inpstr)
            if m:
                break
        else:
            if j == 2:
                return [True, False] ## economic uncertainty, not political
            else:
                return [False, False]
            
    out = [True,True]
    for cond in add_conds:
        for p in cond:
            m = p(inpstr)
            if m:
                out.append(True)
                break
        else:
            out.append(False)
    return out
             
def build_index():
    
    t0 = datetime.datetime(2001,1,1)
    num_days =  (datetime.datetime(2016,1,31) - t0).days + 1

    rng = pd.date_range(t0.strftime('%m/%d/%Y'), periods=num_days, freq='D')
    df = pd.DataFrame(np.zeros((num_days,4 + c_n + b_n)), index=rng,columns=['eumatches','matches','articles','words'] + colnames + combo_names)
    
    for i in range(1200,num_days):
        t = t0 + datetime.timedelta(days = i)
        d = t.day
        m = t.month
        y = t.year
        assert(t == df.index[i].to_datetime())
        ddir = os.path.join(datadir,str(y),str(m),str(d))
        if not os.path.exists(ddir):
            continue

        txtfiles = [x for x in os.listdir(ddir) if match(r'^ec_.*\.txt$',x,I)]
        rfile = 'res.txt'
        m_n = 0; a_n = 0; w_n = 0; eu_n = 0;
        
        if rfile in os.listdir(ddir):
            with open(os.path.join(ddir,rfile),'r') as inf:
                res = inf.read().split(',')
                eu_n = int(res[0])
                m_n = int(res[1])
                a_n = int(res[2])
                w_n = int(res[3])
                rest = [int(res[4+k]) for k in range(c_n + b_n)]
        
        if a_n == 0:
            
            rest = [0]*(c_n+ b_n)
            for txtf in txtfiles:
                with open(os.path.join(ddir, txtf), 'r') as inf:
                    inpstr = inf.read()
                
                m = match_file(inpstr)
                if m[0]:
                    eu_n += 1
                if m[1]:
                    
                    m_n +=1
                    combo_f = [False]*b_n
                    for j in range(c_n):
                        if m[2+j]:
                            
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
                outf.write('%d,%d,%d,%d,%s' % (eu_n, m_n, a_n, w_n,','.join(['%d' % x for x in rest]) ))
        df.eumatches[i] += eu_n
        df.matches[i] += m_n
        df.articles[i] += a_n
        df.words[i] += w_n
        for j in range(c_n + b_n):
            df[(colnames+combo_names)[j]][i] += rest[j]
    
    df.to_csv(os.path.join(thisdir, 'daily_data.csv'))


        
if __name__ == '__main__':
    #create_archive()
    build_index()