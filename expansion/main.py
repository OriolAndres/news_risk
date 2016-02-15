# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 19:27:19 2016

@author: OriolAndres
"""

import datetime
import os
import urllib2
from re import match, I
from bs4 import BeautifulSoup
rootdir = os.path.dirname(__file__)
datadir = os.path.join(rootdir,'data')
if not os.path.exists(datadir):
    os.makedirs(datadir)

t0 = datetime.datetime(2001,1,1)
num_days = (datetime.datetime.today() - t0).days + 1

def get_archive():
    
    url_tem = 'http://www.expansion.com/hemeroteca/{year}/{mon:02d}/{day:02d}/index.html'
    
    for i in range(0,num_days):
        dt = t0 + datetime.timedelta(days = i)
        path = os.path.join(datadir, str(dt.year),str(dt.month),str(dt.day))
        if not os.path.exists(path):
            os.makedirs(path)        
        
        fname = 'index.html'
        if fname not in os.listdir(path):
            response = urllib2.urlopen(url_tem.format(year = str(dt.year), mon = dt.month, day = dt.day ))
            with open(os.path.join(path, fname),'w') as outf:
                outf.write(response.read())
        with open(os.path.join(path, fname),'r') as inf:
            bsoup = BeautifulSoup(inf.read(), 'html.parser')
        
        anchors = []
        try: ## new format
            main = bsoup.find_all('div',{'class':'cabecera-seccion'})
            assert(main)
            
            for article_tag in main.find_all('article',{'class':'noticia'}):
                anchors.append( article_tag.find('h1').find('a').text)
                
        except AssertionError:
            
            for header in bsoup.find_all('h2'):
                try:
                    anchor = header.find('a').attrs['href']
                    anchors.append(anchor)
                except: continue
        for anchor in anchors:
            artid = match('^.*/([\d]*)\.html$',anchor).groups()[0]
            if artid + '.html' not in os.listdir(path):
                try:
                    resp = urllib2.urlopen(anchor)
                    h = resp.read()
                    with open(os.path.join(path, artid + '.html'),'w') as outf:
                        outf.write(h)
                except:
                    import traceback
                    print anchor
                    print traceback.format_exc()
                    raise Exception('')
                    
                    
            txtf = '%s.txt' % artid
            if txtf not in os.listdir(path):
                with open(os.path.join(path, artid + '.html'),'r') as inf:
                    artsoup = BeautifulSoup(inf.read(),'html.parser')
                content = artsoup.find('div', {'id':'contenido'})
                title = content.find('h1').text
                text = '\n'.join([x.text for x in content.find_all('p') if x.attrs.get('class','') != 'firma'])
        
                with open(os.path.join(path, txtf), 'w') as outf:
                        outf.write(title.encode('utf8') + '\n')
                        outf.write(text.encode('utf8'))