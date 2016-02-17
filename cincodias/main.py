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

rootdir = os.path.dirname(__file__)#r'C:/users/oriolandres/desktop/news_risk/elpais'
datadir = os.path.join(rootdir,'data')
if not os.path.exists(datadir):
    os.makedirs(datadir)

def create_archive():
    url_tem = 'http://cincodias.com/tag/economia/a/{page}'
    
    newindices = os.path.join(datadir,'newindices')
    for page in range(1,num_pages+1):
        fname = '%s.html' % page
        
        if fname not in os.listdir(newindices):
            res = urllib2.urlopen(url_tem.format(page= page))
            with open(os.path.join(newindices,fname),'w') as outf:
                outf.write(res.read())
        with open(os.path.join(newindices,fname),'r') as inf:
            bsoup = BeautifulSoup(inf.read(),'html.parser')
        for article in bsoup.find_all('div',{'class':'article'}):
            dt = datetime.datetime.strptime(article.find('a',{'class','fecha'}).text,'%d/%m/%Y')

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
create_archive()