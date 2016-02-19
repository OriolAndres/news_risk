# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 16:08:03 2016

@author: OriolAndres
"""
rootdir = r'C:/users/oriolandres/desktop/news_risk/accounts'
import csv
import os
from re import match, I,sub

def create_entity_list():
    names = set()
    with open(os.path.join(rootdir,'stats_table.csv'),'rb') as inf:
        for line in csv.reader(inf):
            names.add(line[0])
            
    with open(os.path.join(rootdir,'biz_meta.csv'),'wb') as outf:
        for name in sorted(list(names)):
            outf.write('"{0}"\n'.format(name))
            

def lower_case(instring):
    u = 'ÑÁÉÍÓÚÜ'
    l = 'ñáéíóúü'
    for i,c in enumerate(u):
        instring = sub(c,l[i],instring)
    return instring

def test_regex():    
    with open(os.path.join(rootdir,'biz_meta_regex.csv'),'rb') as inf:
        instream = csv.reader(inf)
        lines = list(instream)
        
    for line in lines:
        assert(match(line[1],lower_case(line[0]),I))