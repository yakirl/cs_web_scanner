#!/usr/bin/python

import sys
import io
import os
import urllib3 
from bs4 import BeautifulSoup
from utilities.Debug import Debug
from utilities.Misc  import Misc
from utilities.Misc  import TimeoutException
from urlparse import urljoin
from lxml import etree

#d = etree.HTML(data)
#d.xpath('//link[@rel="shortcut icon"]/@href')

debug = Debug()
misc  = Misc()

CS_TECHNION = 'http://www.cs.technion.ac.il/'
SITES_FILENAME = 'logs/sites.txt'
LIMIT_DEPTH = 10

class PageNotFound(Exception): pass




class WebScanner:
    def __init__(self):
        self.http = misc.run_with_timer(urllib3.PoolManager, (), "PoolManger stuck")
        self.sites_addrs = set()
        self.sites_addrs_file = open(SITES_FILENAME, 'w')
        self.visited_pages = set() 
        self.is_data_saved = False

    def save_data(self):
        for site_addr in self.sites_addrs:
            self.sites_addrs_file.write(site_addr+"\n")
        
    def close(self):
        if not self.is_data_saved:
            self.save_data()
            self.is_data_saved = True
        debug.close()
        sys.exit(0)

    def normalize_page(self, page_addr):
        page_addr       = page_addr[7:]
        parts           = page_addr.split('/')
        if parts[0].find('@') != -1:
            parts[0] = parts[0][parts[0].find('@')+1:]
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

    def is_technion_page(self, page_addr):   # ToDo: what are the criteria?
        res = False
        if  page_addr.find('technion') != -1:
            res = True       
        return res
    

    def fixed_urljoin(self, urlpart1, urlpart2):
        tmp_url = urljoin(urlpart1, urlpart2)
        splits = str(tmp_url).split("/")
        splits = filter(lambda x: x!= "..", splits)
        url    = '/'.join(splits)
        return url

    def validate_html_doc(self, html_doc):
        if html_doc.find('404 Not Found') != -1:
            return False
        return True

    def is_cs_page(self, page_addr, soup):
        #print(type(soup.title))
        if (page_addr.find("cs.technion") == -1) and (str(soup.title).find('Computer Science') == -1):
            #print('aaaaaaaaaaaaaaaaaaa')
            return False
        #print(str(soup.title)+" : "+page_addr)
        return True

    def is_scannable_page(self, page_addr):
        if (page_addr.find('jigsaw') != -1) or (page_addr.find('.pdf') != -1):
            return False
        return True

    '''
    Main function: recursively scann sites
    '''
    def extract_links_from_page(self, page_addr, depth):
        try:
            page_addr = self.normalize_page(page_addr)
            debug.assrt(depth >= 0, 'extract_link_from_pages: depth='+str(depth))
            if depth == 0:
                return
            ''' Some optimizations: '''
            if (not self.is_scannable_page(page_addr)) or (not self.is_technion_page(page_addr)) or (page_addr in self.visited_pages):
                return
            self.visited_pages.add(page_addr)
            html_doc = self.get_html_doc(page_addr)
            ''' we want to continue scraping in case that a connection to web page timed-out or page not found '''
            if html_doc == None or not self.validate_html_doc(html_doc):
                debug.logger('extract_links_from_page: '+page_addr+' - page not found', 2)
                raise PageNotFound
            soup = misc.run_with_timer(BeautifulSoup, (html_doc, 'html.parser'), "BeautifulSoup failed on page "+page_addr, True)
            if not self.is_cs_page(page_addr, soup):
                 return
            ''' if we got to here then this page is valid, scannable, cs page '''
            if self.is_page_a_site_home(page_addr):
                self.sites_addrs.add(page_addr)
            debug.logger("page_addr="+page_addr)
            for link_tag in soup.find_all('a'):
                link = link_tag.get('href')
                #print(link.find("#"))
                if link == "None" or link == None or (link.find("#") != -1):
                    continue
                full_link = self.fixed_urljoin(page_addr, link)
                #debug.logger(page_addr+" + "+link+" = "+full_link)
                #full_link = link if (link.find("http://") == 0) else page_addr+"/"+link
                #    full_link = link
                #else:
                #    full_link = page_addr+"/"+link
                #print(link_full_addr)
                debug.logger('anc page: '+page_addr)
                self.extract_links_from_page(full_link, depth - 1)
        except SystemExit:
            #sys.exit(0)
            self.close()
        except KeyboardInterrupt:
            debug.logger('Process has been killed by user', 2)
            #sys.exit(0)
            self.close()
        except PageNotFound:
            #debug.logger('Page Not Found: '+page_addr, 2)
            return
        except TimeoutException:
            return
        except:
            debug.logger('Unexpected error while handling '+page_addr, 2)
            return

    '''
        gets full page address: http://site
        return source code of the site as string
    '''
    def get_html_doc(self, page_addr):
        page_data = None
        debug.assrt(page_addr.find("http://") == 0, "get_html_doc: page_addr="+page_addr)
        request = misc.run_with_timer(self.http.request, ('GET', page_addr), "request for "+page_addr+" failed")
        if request != None:
            page_data = str(request.data) 
        return page_data
        

    def process_web_page(self, page_addr):
        self.extract_links_from_page(page_addr, LIMIT_DEPTH)
        self.save_data()
        data_path = 'data/'
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        #f = open(data_path+'example_com.txt', 'w')
        #f.write()    
    


if __name__ == "__main__":
    page_addr = CS_TECHNION #sys.argv[1]
    debug.logger('-- WebScanner --')

    webScanner = WebScanner()
    #r = webScanner.http.request('GET', 'http://www.cs.technon.ac.il/he/acceibility/index.html')
    #print(str(r.data))
    #exit(1)
    #args = (webScanner,)
    #misc.run_with_timer(webScanner.long_func, args)
    webScanner.process_web_page(page_addr)
    debug.logger('Results in '+SITES_FILENAME)
    debug.logger('-- Good Day! --')
    
