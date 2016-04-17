#!/usr/bin/python

import sys
import io
import os
import urllib3
import Queue
import time
from urlparse import urljoin
from lxml import etree
from bs4 import BeautifulSoup

from utilities.Debug import Debug
from utilities.Misc  import Misc
from utilities.Misc  import TimeoutException

import Global
debug = Debug()
misc  = Misc()

outQ = Global.coreRX

# System Configurations: ####
CONFIG_FILE  = 'config/mapping.conf'
OUTPUT_DIR   = 'output/mapper/'
EXE_INTV_MIN = 1
EXE_INTV_MAX = 3600
BASE_URL     = 'cs.technion.ac.il'
START_ADDR   = 'http://www'+BASE_URL
EXE_INTV_DEFAULT = 60
LIMIT_DEPTH      = 10
CONFS = ['execution_interval']


class PageNotFound(Exception): pass

class WebMapper:
    def __init__(self):
        #self.http = misc.run_with_timer(urllib3.PoolManager, (cert_reqs = 'CERT_REQUIRED', ca_certs = certifi.where()), "PoolManger stuck")
        self.sites_addrs = set()
        self.visited_pages = set() 
        self.is_data_saved = False
        self.conf = {}
        self.get_conf_from_file()

    def save_data(self, dateime_run):
        output_dir = OUTPUT_DIR
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filename = 'mapper_'+datetime.datetime.strftime(datetime_run, '%Y%m%d_%H%M%S')
        f = open(filename, 'w')
        f.write(START_ADDR+'\n')
        f.write(BASE_URL+'\n')
        for site_addr in self.sites_addrs:
            f.write(site_addr+"\n")
        debug.logger('Results in '+OUTPUT_DIR+'/'+filename)
        
    def close(self):
        if not self.is_data_saved:
            self.save_data()
            self.is_data_saved = True
        try:
            debug.close()
        except:
            sys.exit(0)
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

    def page_contains_base_url(self, page_addr):
        if -1 == page_addr.find(BASE_URL):
            return False
        return True

    def is_scannable_page(self, page_addr):
        if (page_addr.find('jigsaw') != -1) or (page_addr.find('.pdf') != -1):
            return False
        return True

    '''
    Main function: recursively scann sites
    '''
    def map_engine(self, page_addr, depth):
        try:
            #page_addr = self.normalize_page(page_addr)
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
                debug.logger('map_engine: '+page_addr+' - page not found', 2)
                raise PageNotFound
            soup = misc.run_with_timer(BeautifulSoup, (html_doc, 'html.parser'), "BeautifulSoup failed on page "+page_addr, True)
            if not self.page_contains_base_url(page_addr):
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
                full_link = urljoin(page_addr, link)
                # keep into urls mapping file - this file will be used by WebInspector
                #debug.logger(page_addr+" + "+link+" = "+full_link)
                #full_link = link if (link.find("http://") == 0) else page_addr+"/"+link
                #    full_link = link
                #else:
                #    full_link = page_addr+"/"+link
                #print(link_full_addr)
                #debug.logger('anc page: '+page_addr)
                self.map_engine(full_link, depth - 1)
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
        except urllib3.exceptions.MaxRetryError:
            debug.logger('Max retry error on page: '+page_addr, 2)
            return
        except:
            #debug.logger('Unexpected error for page: '+page_addr+' - '+sys.exc_info()[0], 2)
            debug.logger('Unexpected error for page: '+page_addr, 2)
            raise

    '''
        gets full page address: http://site
        return source code of the site as string
    '''
    def get_html_doc(self, page_addr):
        page_data = None
        #debug.assrt(page_addr.find("http://") == 0, "get_html_doc: page_addr="+page_addr)
        request = misc.run_with_timer(self.http.request, ('GET', page_addr), "request for "+page_addr+" failed")
        if request != None:
            page_data = str(request.data) 
        #print(request.host)
        return page_data
        
    def run_once(self):
        debug.logger('WebMapper.run_once:')
        curr_datetime = datetime.datetime.now()
        self.map_engine(START_ADDR, LIMIT_DEPTH)
        self.save_data(curr_datetime)


    def run_in_cont_mode(self):
        debug.logger('WebMapper.run_in_cont_mode:')
        while True:
            last_run = time.time()
            self.run_once()
            try:
                workObj = incomingQ.get(False)
            except Queue.Empty:
                if (time.time() - last_run) > self.conf['execution_interval']:
                    last_run = time.time()
                    self.run_once()
                    continue
            switcher = {
                WorkID.CONFIG_MAPPER: self.config,
                WorkID.STOP_MAPPER:   self.close
            }
            switcher[workObj.workID](workObj.params)

    def start_mapping(self):

        debug.logger('WebMapper.start_mapping:')
        interval = self.conf['execution_interval']
        time.sleep(1)
        return
        if 0 == interval:
            self.run_once()
        else:
            self.run_in_cont_mode()

    ''' Those are general methods for Mapper configuration, you can add more configurations here.
        current possible confiugrations:
        execution_interval - # minutes before consequence runs. (int)
    '''
    def verify_exe_intv(self, execution_interval):
        return execution_interval <= EXE_INTV_MAX and (execution_interval >= EXE_INTV_MIN)

    def get_conf_from_file(self):
        conf_file_valid = False
        try:
            with open(CONFIG_FILE, 'r') as f:
              confs = [tuple(i.split(' ')) for i in f]
            conf_file_valid = (set(CONFS) == set([conf[0] for conf in confs]))
            #debug.logger(str(conf_file_valid))
            for c in confs:
                if 2 != len(c):
                    debug.logger('len is not 2')
                    conf_file_valid = False
            confs_dict = {c[0]: c[1] for c in confs}
            debug.logger(confs_dict['execution_interval'])
            conf_file_valid = conf_file_valid and self.verify_exe_intv(int(confs_dict['execution_interval']))
            debug.logger(str(conf_file_valid))
        except IOError:
            debug.logger('got IOError')
            conf_file_valid = False
        except KeyError:
            conf_file_valid = False
        if not conf_file_valid:
            debug.logger('get_conf_from_file: found bad configuration in file '+CONFIG_FILE, 2)
            self.load_default_conf()
        else:
            self.conf = confs_dict

    def save_conf_to_file(self):
        debug.assrt(type(self.conf) == type({}), 'self.conf is not dict!')
        f = open(CONFIG_FILE, 'w')
        for k in self.conf.keys():
            f.write(k+" "+str(self.conf[k]))
        f.close()
        debug.logger('WebMapper.save_conf_to_file: data has been saved')

    def load_default_conf(self):
        debug.logger('WebMapper.loading_default_conf: loading default configurations')
        self.conf['execution_interval'] = EXE_INTV_DEFAULT
        self.save_conf_to_file()

    def config(self, execution_interval):
        debug.assrt(type(execution_interval) == type(1), 'WebMapper.config: param isnt int')
        debug.logger('WebMapper.config: execution_interval='+str(execution_interval))
        if not self.verify_exe_intv(execution_interval):
            raise ValueError("interval must be between 1 to 3600")
        self.conf['execution_interval'] = execution_interval
        self.save_conf_to_file()

        

def main_web_mapper():
    webMapper = WebMapper()
    webMapper.start_mapping()
    
if __name__ == "__main__":
    page_addr = CS_TECHNION #sys.argv[1]
    main_web_mapper()
