# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 16:47:53 2016

@author: OriolAndres
"""

from lxml import etree
import os
from re import search, I, match,DOTALL, findall, finditer, split, sub
import csv

for i in range(2005, 2010):
    y = str(i)
    datadir = r'C:\Users\OriolAndres\Desktop\news_risk\boe\data\%s' % y
    
    outlist = []
    
    romans = {'i':'1','ii':'2','iii':'3','iv':'4','v':'5','vi':'6','vii':'7'}
    
    corpus_n = 0
    for fname in os.listdir(datadir):
        if fname.endswith('csv'): continue
        fpath  = os.path.join(datadir, fname)
        with open(fpath, 'r') as inf:
            xml = etree.parse(inf)
        analisis = xml.find('analisis')
        tipus = analisis.find('tipo').text
        
        if tipus is not None and search('adjudica',tipus, I):
            corpus_n += 1
            business = None
            amounts = []
            pairs = []
            lotes_q = {}
            lotes_w = {}
            flag = False
            iterat = xml.iter('p')
            while 1:
                try:
                    tag = next(iterat)
                except:
                    break
                content = tag.text
                if content is None:
                    continue
                m = search(r'5.{1,3}adjudicaci.{1,2}n',content,I)
                if m:
                    flag = True
                    content = content[m.end():]
                if not flag:
                    continue
                
                if search(r'b\).*?contratista?: \n*(.*)',content, I|DOTALL):
                    if len(content) < 20:
                        content = next(iterat).text
                    else:
                        m = search(r'b\).*?contratista?:',content,I)
                        if m:
                            content = content[m.end():]
                    if 'c)' in content.lower():
                        m = match(r'\s*\n*(.*)c\).*$',content, I|DOTALL) 
                    else:
                        m = match(r'\s*\n*(.*)$',content, I|DOTALL) 
                    body =  m.groups()[0]
                    
                    b_list = [x for x in split(';|\n',body) if len(sub(r'[^\d\w]','',x)) > 2]
                    if len(b_list) > 1:
                        for biz in b_list:
                            
                            m = match(r'.*?lotes?.*?(?P<lotenum>[\dy\s,ivx]*)[\s:]*(?P<biz>[^\.]*)',biz,I|DOTALL)
                            if m:
                                d = m.groupdict()
                                nums_raw = d['lotenum']
                                lotes = findall(r'\b[\divx]+\b',nums_raw)
                                for lote in lotes:
                                    num = romans.get(lote.lower(),lote.lower())
                                    lotes_w[num] = d['biz']

                            m = match(r'^(?P<name>.*?)\s(?P<money>[\.\d,]* (€|euros)).*?',biz,I|DOTALL)
                            if not m:
                                m = match(r'^.*\s(?P<money>[\.\d,]* (€|euros))(?P<name>.*)$',biz,I|DOTALL)
                            if m:
                                pairs.append([m.group('name'),m.group('money')])

                    if not pairs and not lotes_w:
                        business = sub(r'\n','',body)
                        
                if search(r'd\)', content, I|DOTALL):
                    if len(content) < 20:
                        content = next(iterat).text
                    else:
                        m = search(r'd\) importe de adjudicaci.{1,2}n:',content,I|DOTALL)
                        if m:
                            content = content[m.end():]

                    miter = finditer(r'lotes?.*?(?P<lotenum>[\divx]{1,3}).*?\s(?P<value>[\.\d]*,[\d]{2})',content,I|DOTALL)
                    for m in miter:
                        num = m.group('lotenum')
                        num = romans.get(num.lower(),num.lower())
                        lotes_q[num] = m.group('value')
                    if not lotes_q:
                        m = match(r'^.*?\s(?P<value>[\.\d]*,[\d]{2}).*$',content)
                        if m:
                            amounts = [m.groups()[0]]
                        else:
                            amounts = [None]
                
            if lotes_w and lotes_q:
                for k,v in lotes_q.items():
                    if k in lotes_w:
                        outlist.append([fname, lotes_w[k], lotes_q[k]] )
                continue
            if pairs:
                for pair in pairs:
                    outlist.append([fname] + pair)
                continue
            if business is not None:
                business = sub(r'\n.*','',business)
                if match(r'^\s*$',business): 
                    print fname
                    continue
                    
                for amount in amounts:
                    outlist.append([fname, business, amount])
            else:
                print fname
                
    print corpus_n
    trans = []
    for r in outlist:
        trans.append([c.encode('utf8') if c is not None else 'NA' for c in r])
    with open(os.path.join(datadir,'catches.csv'),'wb') as outf:
        stream = csv.writer(outf)
        stream.writerows(trans)