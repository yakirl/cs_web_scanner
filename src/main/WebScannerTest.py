#!/usr/bin/python

import sys
import io
import os
import urllib3 
from bs4 import BeautifulSoup
from utilities.Debug import Debug
from utilities.Misc  import Misc  

debug = Debug()
misc  = Misc()

SITES_FILENAME = 'logs/sites.txt'

class WebScanner:
    def __init__(self):
        self.http = None
        self.sites_addrs = set()
        self.sites_addrs_file = open(SITES_FILENAME, 'w')
        self.visited_pages = set() 

    def normalize_page(self, page_addr):
        page_addr       = page_addr[7:]
        parts           = page_addr.split('/')
        normalized_page = "http:/"
        for part in parts:
            if part != "":
                normalized_page = normalized_page+"/"+part
        return normalized_page

    '''
    assume page_addr is of format:
        http://site_base/subpage1/.../subpageN
    '''
    def is_page_a_site_home(self, page_addr):
    #    print ("is_page_a_site_home")
        if page_addr[len(page_addr) - 1] == '/':
            page_addr = page_addr[:-1]
        page_addr_parts = page_addr.split("/")
        num_parts = len(page_addr_parts)
     #   print(num_parts)
        if num_parts <= 3:
            return True
        if (num_parts == 4) and (page_addr_parts[3].find('~') == 0):
            return True
        return False      

    def is_cs_page(self, page_addr):   # ToDo: what are the criteria?
        res = False
        if  page_addr.find('technion') != -1:
            res = True       
        return res
    
    '''
    Main function: recursively scann sites
    '''
    def extract_links_from_page(self, page_addr, depth):
        page_addr = self.normalize_page(page_addr)
        debug.assrt(depth >= 0, 'extract_link_from_pages: depth='+str(depth))
        if (depth == 0) or  (not self.is_cs_page(page_addr)) or (page_addr in self.visited_pages) or (page_addr.find("jigsaw") != -1):
            return
        if self.is_page_a_site_home(page_addr):
            self.sites_addrs.add(page_addr)
            #print (link_full_addr)
        self.visited_pages.add(page_addr)
        html_doc = self.get_html_doc(page_addr)
        ''' we want to continue scraping in case that a connection to web page timed-out '''
        if html_doc == None:    
            return
        try:
            soup = misc.run_with_timer(BeautifulSoup, (html_doc, 'html.parser'), "BeautifulSoup failed on page "+page_addr, True)
        except:
            return
            
        for link_tag in soup.find_all('a'):
            link = link_tag.get('href')
            #print(link)
            #print(link.find("#"))
            if link == "None" or link == None or (link.find("#") != -1):
                continue
            #debug.logger(link)
            if link.find("http://") == 0:
                link_full_addr = link
            else:
                link_full_addr = page_addr+"/"+link
            #print(link_full_addr)
            
            self.extract_links_from_page(link_full_addr, depth - 1) 
        
    '''
        gets full page address: http://site
        return source code of the site as string
    '''
    def get_html_doc(self, page_addr):
        page_data = None
        debug.assrt(page_addr.find("http://") == 0, "get_html_doc: page_addr="+page_addr)
        if self.http == None:
            self.http     = misc.run_with_timer(urllib3.PoolManager, (), "PoolManger stuck")
        debug.logger("get_html_doc: page_addr="+page_addr)
        request = misc.run_with_timer(self.http.request, ('GET', page_addr), "request for "+page_addr+" failed")
        if request != None:
            page_data = str(request.data) 
        return page_data
        

    def process_web_page(self, page_addr):
        self.extract_links_from_page(page_addr, 3)
        for site_addr in self.sites_addrs:
            debug.logger (site_addr, 1)
            self.sites_addrs_file.write(site_addr+"\n")

        data_path = 'data/'
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        #f = open(data_path+'example_com.txt', 'w')
        #f.write()    
    
    def long_func(self, strr):
        j = 0
        for i in range(0, 200000000):
            j = j + i



def dummy():
    #    print (request1.status)
    #   print (request1.headers['server'])
    #    b = io.BufferedReader(request1)
        
    #    f = open(data_path+'example_com.txt', 'w')
     #   firstpart = b.read(100)
       # b = request1.read()
     #   print(request1.read())
     #   f.write(str(request1.data))
      #  print('done write data to file')
    #    print (request1.data)

      #  request2 = http.urlopen('GET', page_addr, preload_content=False)
      #  b = io.BufferedReader(request2, 2048)
        firstpart  = [] #b.read(100)
        secondpart = [] # b.read()
        debug.logger('nothing')
     #   print(firstpart)
     #   print_types(http, request1, request2, b, firstpart, secondpart)


if __name__ == "__main__":
    page_addr = sys.argv[1]
    debug.logger('-- WebScanner --')
    webScanner = WebScanner()
    #args = (webScanner,)
    #misc.run_with_timer(webScanner.long_func, args)
    webScanner.process_web_page(page_addr)
    debug.logger('Results in '+SITES_FILENAME)
    debug.logger('-- Good Day! --')
    
