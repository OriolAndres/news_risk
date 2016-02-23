# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 02:58:27 2016

@author: OriolAndres


works only on selenium==2.48
"""


import os
import shutil
import time
from selenium import webdriver
import csv

from news_risk.settings import rootdir
datadir = os.path.join(rootdir,'accounts','data')

def fetch_list_by_sector():
    profile = webdriver.FirefoxProfile()
    
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip,application/x-gzip,text/plain,text/csv,application/csv,application/download,application/octet-stream')
    driver = webdriver.Firefox(firefox_profile= profile)
    driver.get("http://www.cnmv.es/ipps/")
    time.sleep(8)
    sector_dict = {}
    driver.find_element_by_xpath("//select[@id='wuc_Arbol_drpModoBusqueda']/option[text()='Sector']").click()
    for sector in ['SECTOR NO FINANCIERO','SECTOR FINANCIERO','SECTOR PÚBLICO']:
        time.sleep(2)
        driver.find_element_by_xpath("//select[@id='wuc_Arbol_drpSector']/option[text()='{0}']".format(sector)).click()
        time.sleep(3)        
        subs_dd = driver.find_element_by_xpath("//select[@id='wuc_Arbol_drpSubSector']")
        options = []        
        for el in subs_dd.find_elements_by_tag_name('option'): 
            options.append([el.get_attribute("value"),el.text.encode('utf8') ])
        for optionvalue,sector in options:
            driver.find_element_by_xpath("//select[@id='wuc_Arbol_drpSubSector']/option[@value='{0}']".format(optionvalue)).click()
            time.sleep(2)
            members = driver.find_element_by_xpath("//select[@id='wuc_Arbol_drpEntidades']")
            mem_list = []
            for mem in members.find_elements_by_tag_name('option'):
                mem_list.append(mem.text.encode('utf8'))
            sector_dict[sector] = mem_list
    with open(os.path.join(rootdir,'accounts','sector_members.csv'),'wb') as outf:
        outstream = csv.writer(outf)
        for k,v in sector_dict.items():
            for el in v:
                if el == '(No existen entidades)':
                    continue
                outstream.writerow([k,el])
    driver.quit()
    

if __name__ == '__main__':
    fetch_list_by_sector()