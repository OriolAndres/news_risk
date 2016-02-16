# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 14:39:34 2016

@author: OriolAndres
"""
import os
import datetime
import urllib2
from re import match, I
from bs4 import BeautifulSoup
rootdir = os.path.dirname(__file__)
datadir = os.path.join(rootdir,'data')



error_msg = 'No se encontró el documento original.'.decode('utf8')

for y in range(2005,2016):
    t0 = datetime.datetime(y,1,1)
    yeardir = os.path.join(datadir,str(y))
    if not os.path.exists(yeardir):
        os.makedirs(yeardir)
    doc_num = 0
    for i in range(366):
        t = t0 + datetime.timedelta(days = i)
        resp = urllib2.urlopen('http://www.boe.es/boe/dias/{y}/{m:02d}/{d:02d}/index.php?s=5'.format(y = str(y),m = t.month,d = t.day))
        if resp.getcode() > 210:
            continue
        bs = BeautifulSoup(resp.read())
        litags = bs.find_all('li',{'class':'puntoMas'})
        for li in litags:
            num = match(r'^/diario_boe/txt.php?id=BOE-B-\d{4}-(\d*)$',li.find('a').attrs['href'],I).groups()[0]
            fname = 'BOE-B-{y}-{dnum}'.format(y=str(y),dnum = num)
            if fname + '.xml' not in yeardir:
                resp = urllib2.urlopen('https://www.boe.es/diario_boe/xml.php?id={fname}'.format(fname = fname)) 
                xml = resp.read()
                if xml == error_msg:
                    break
                else:
                    with open(os.path.join(yeardir,fname + '.xml'),'w') as outf:
                        outf.write(xml)
