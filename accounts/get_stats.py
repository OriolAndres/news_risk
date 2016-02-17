# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 01:33:01 2016

@author: OriolAndres
"""

import os
import shutil
import time
from selenium import webdriver
from zipfile import ZipFile
import time
import shutil
from re import sub
from lxml import etree
from StringIO import StringIO
from re import compile

rootdir = r'C:/users/oriolandres/desktop/news_risk/accounts'
unzipdir = os.path.join(rootdir,'unzip')
datadir = os.path.join(rootdir,'data')





def unzip():
    for zname in os.listdir(datadir):
        rootname = zname[:zname.rfind('.')]
        folder = os.path.join(unzipdir,rootname)
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            continue
        zipf = ZipFile(os.path.join(datadir,zname))
        files = zipf.namelist()
        for name in files:
            zipf.extract(name, folder)
        zipf.close()


p = compile(r'[A-Za-z0-9+/]{300,}')
outdict = {}

for folder in os.listdir(unzipdir):
    #print folder
    outarray = []
    for fname in os.listdir(os.path.join(unzipdir,folder)):
        fpath = os.path.join(unzipdir,folder, fname)
        full_string = ''
        with open(fpath,'r') as inf:
            for l in inf:
                full_string += p.sub('',l)
        io = StringIO(full_string)
        #fpath = os.path.join(unzipdir,'BANCO_SANTANDER', '2014024558.xbrl')
        xml = etree.parse(io)
        alltags = set(x.tag for x in xml.iter())
        unique_ns = set(x[:x.rfind('}')] for x in alltags)
        
        for denom in ['EmployeeExpensesByNature','GastosPersonal','GastoPersonalNIIF']:
            cands = [x for x in alltags if denom in x]
            if cands:
                tag = cands[0]
                break
        else:
            print 'what represents wages'
            continue
        v = next(xml.iter(tag)).text
        #print '\t', v
        outarray.append(v)
    outdict[folder] = outarray