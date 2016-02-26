# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 01:33:01 2016

@author: OriolAndres
"""

import os
from zipfile import ZipFile
from re import match
from lxml import etree
from StringIO import StringIO
from re import compile
import csv
from news_risk.settings import rootdir
unzipdir = os.path.join(rootdir,'accounts','unzip')
datadir = os.path.join(rootdir,'accounts','data')

import datetime



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

def parse_xml():
    p = compile(r'[A-Za-z0-9+/]{300,}')
    outdict = {}

    short_long_names = []
    for folder in os.listdir(unzipdir):
        #print folder
        outarray = []
        biz_name = folder
        
        seen_dates = set()

        for fname in os.listdir(os.path.join(unzipdir,folder)):
            if folder == 'FERROVIAL' and fname < '2010': ## previously reported CINTRA only, a spinoff 
                continue
            if folder.startswith('CAIXABANK') and fname < '2011104630': ## previously CRITERIA only
                continue
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
    
            
            
            biz_name = next(xml.iter('{http://www.xbrl.org/2003/instance}identifier')).text.encode('utf8')
            #print next(xml.iter('{http://www.xbrl.org/2003/instance}startDate')).text
            #print next(xml.iter('{http://www.xbrl.org/2003/instance}endDate')).text
            sections = ['Revenues','Wages']
            s_end = ['r_end','w_end']
            s_tag = ['r_tag','w_tag']
            candidates_list = [['RevenueTotalByNature','ImporteNetoCifraNegocio','OtherOperatingIncomeTotalFinancialInstitutions'],
                                ['EmployeeExpensesByNature','GastoPersonalNIIF','GastosPersonal']] #
            value_dict = {'Pub':fname[:fname.rfind('.')]} 
            for section_i, tag_candidates in enumerate(candidates_list):
                for denom in tag_candidates:
                    cands = [x for x in alltags if x.endswith('}'+denom)]
                    if cands:
                        tag = cands[0]
                        break
                else:
                    #print 'what represents wages'
                    continue
                max_t = datetime.datetime(2000,1,1)
                value = None
                ending = ''
                for entry in xml.iter(tag):
                    date_ph = entry.attrib['contextRef']
                    assert(match(r'^S\d{5}_.*$', date_ph))
                    cur_t = datetime.datetime(int(date_ph[2:6]),6*int(date_ph[1]),1)
                    if cur_t < max_t:
                        continue
                    elif cur_t > max_t:
                        max_t = cur_t
                        value = entry.text
                        ending = date_ph[-3:]
                    else:
                        # consolidated balance
                        if (date_ph.endswith('dci') and ending!='dcc') or date_ph.endswith('dcc'): 
                            value = entry.text
                            ending = date_ph[-3:]
                value_dict.update({'t':max_t.strftime('%Y%m%d'),sections[section_i]: value, s_end[section_i]: ending, s_tag[section_i] : denom})
            
            '''
            Annoying repetition of reports for the same period
            '''     
            value_dict['Name'] = biz_name
            if max_t.strftime('%Y%m%d') in seen_dates:
                continue
            else:
                seen_dates.add(max_t.strftime('%Y%m%d'))
            if not value_dict.get('Revenues',None) or value_dict.get('Revenues') == '0':
                continue
            outarray.append(value_dict)
        short_long_names.append([folder, biz_name])
        outdict[biz_name] = outarray
    with open(os.path.join(rootdir,'accounts','short_long.csv'),'wb') as outf:
        outstream  = csv.writer(outf)
        outstream.writerows(short_long_names)
    with open(os.path.join(rootdir,'accounts','stats_table.csv'),'wb') as outf:
        outstream  = csv.writer(outf)
        for k, array in outdict.items():
            for entry in array:
                outstream.writerow([k,entry.get('Pub','NA'),
                                    entry.get('t','NA'),
                                    entry.get('Wages','NA'),
                                    entry.get('Revenues','NA'),
                                    entry.get('w_end','NA'),
                                    entry.get('r_end','NA'),
                                    entry.get('w_tag','NA'),
                                    entry.get('r_tag','NA'),
                                    entry.get('Name','NA')])

if __name__ == '__main__':
    #unzip()
    parse_xml()