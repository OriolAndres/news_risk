# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:08:50 2016

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

rootdir = os.path.dirname(__file__)
datadir = os.path.join(rootdir,'data')
download_dir = r'C:/users/oriolandres/downloads'
def fetch_folder():
    profile = webdriver.FirefoxProfile()
    
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip,application/x-gzip,text/plain,text/csv,application/csv,application/download,application/octet-stream')
    driver = webdriver.Firefox(firefox_profile= profile)
    driver.get("http://www.cnmv.es/ipps/")
    time.sleep(8)
    elm = driver.find_element_by_xpath("//li[@id='opcion2']")
    elm.click()
    time.sleep(8)
    elm = driver.find_element_by_xpath("//input[@id='wuc_Descargas_rbTipoBusqueda_3']")
    elm.click()
    time.sleep(8)
    

    
    seen = set()
    while 1:
        elm = driver.find_element_by_xpath("//select[@id='wuc_Descargas_drpEntidades']")
        for option in elm.find_elements_by_tag_name('option'):
            name = option.text
            name = sub('[\.,\s]','_',name)
            if name not in seen:
                seen.add(name)
                break
        else:
            raise Exception('Done')
        print name
        option.click()
        time.sleep(4)
        submit = driver.find_element_by_xpath("//input[@id='wuc_Descargas_btnBuscar']")
        submit.click()
        time.sleep(4)
        down_but = driver.find_element_by_xpath("//input[@id='wuc_Descargas_Listado_btnDescargar']")
        down_but.click()
        
        time.sleep(30)
        it = 0
        s = 0
        while 1:
            it+=1
            time.sleep(4)
            zname = 'Informes.zip'
            if zname in os.listdir(download_dir):
                ns = os.path.getsize(os.path.join(download_dir,zname))
                if ns == s and ns > 0:
                    shutil.move(os.path.join(download_dir,zname), os.path.join(datadir,name + '.zip'))
                    break
                else:
                    s = ns

            