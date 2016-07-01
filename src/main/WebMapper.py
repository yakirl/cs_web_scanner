#!/usr/bin/python

#import signal
import sys
import io
import os
import datetime
import urllib3
import certifi
import Queue
import time
import random
from urlparse import urljoin
import lxml
from bs4 import BeautifulSoup, SoupStrainer
from functools import partial
import Profiler
from utilities.Debug import Debug
from utilities.Misc  import Misc
from utilities.Misc  import TimeoutException
from Global import *


# System Configurations: ####
OUTPUT_DIR       = os.path.join('data', 'mapper')
# SITES_FILE       = os.path.join(OUTPUT_DIR, 'mapper_sites.txt')
# PAGES_FILE       = os.path.join(OUTPUT_DIR, 'mapper_pages.txt')
EXE_INTV_MIN     = 1
EXE_INTV_MAX     = 3600
EXE_INTV_DEFAULT = 0
AVG_LINKS_IN_PAGE = 50
REQUIRED_LIMIT_DEPTH = 10000
LIMIT_DEPTH      = AVG_LINKS_IN_PAGE * REQUIRED_LIMIT_DEPTH
MAX_SCANNABLE_HTML_LEN = 140000

class PageNotFound(Exception): pass

class WebMapper:
    def __init__(self):
        self.inQ = coreMSX
        self.debug    = register_debugger()
        self.misc     = Misc()
        self.debug.logger('WebMapper initizliation')
        # self.http = self.misc.run_with_timer(urllib3.PoolManager, {'cert_reqs': 'CERT_REQUIRED', 'ca_certs': certifi.where()}, "PoolManger stuck") # TODO
        self.http = urllib3.PoolManager(cert_reqs = 'CERT_REQUIRED', ca_certs = certifi.where())
        request = self.http.request('GET', 'http://www.example.com')
        #self.http = urllib3.PoolManager(cert_reqs = 'CERT_REQUIRED', ca_certs = certifi.where())
        #self.http = self.misc.run_with_timer(urllib3.PoolManager, (), "PoolManger stuck")
        self.valid = 0

    def verify_exe_intv(self, execution_interval):
        return (execution_interval <= EXE_INTV_MAX and (execution_interval >= EXE_INTV_MIN)) or (execution_interval == 0)

    def config(self, execution_interval, base_url, output_dir, output_file):
        self.debug.assrt(type(execution_interval) == type(1), 'WebMapper.config: param isnt int')
        self.debug.logger('WebMapper.config: execution_interval='+str(execution_interval))
        if not self.verify_exe_intv(execution_interval):
            raise ValueError("interval must be between 1 to 3600")
        self.execution_interval = execution_interval
        self.base_url           = base_url
        self.start_addr         ='http://'+ base_url
        self.output_dir         = output_dir
        self.output_file        = output_file
        self.valid = 1
        return self

    def setup_for_single_run(self):
        self.profiler = Profiler.Profiler()
        self.depth_reached     = 0
        self.sites_addrs   = set()
        self.visited_pages = set()
        self.scanned_pages = set()
        self.is_data_saved = False


    def is_ascii(self, _string):
        try:
            _string.decode('ascii')
        except KeyboardInterrupt, SystemExit:
            raise
        except:
            return False
        else:
            return True

    def save_data(self, datetime_run):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.debug.logger('save_data: '+str(datetime_run))
        #filename = 'mapper_'+datetime.datetime.strftime(datetime_run, '%Y%m%d_%H%M%S')
        #f = open(filepath, 'w')
        #f.write(START_ADDR+'\n')
        #f.write(BASE_URL+'\n')
        with open(os.path.join(self.output_dir, "mapper_sites.txt"), 'w') as f:
            for site_addr in self.sites_addrs:
                f.write(site_addr+"\n")
        with open(self.output_file, 'w') as f:
            for page_addr in self.visited_pages:
                f.write(page_addr+"\n")
        self.debug.logger('Sites in '+os.path.join(self.output_dir, "mapper_sites.txt"), 1)
        self.debug.logger('Pages in '+self.output_file, 1)

    def close_single_run(self):
        runtime = round(time.time() - self.curr_run_start_time, 3)
        padding = 16
        self.debug.logger('\n\n-----+++++++++++--------',1)
        self.debug.logger('close_single_run:'.ljust(padding),1)
        self.debug.logger('Total run time: '.ljust(padding)+str(runtime)+'s'+' ('+str(round(runtime/3600, 2))+'h)',1)
        self.debug.logger('Total pages: '.ljust(padding)+str(len(self.visited_pages)),1)
        self.debug.logger('Total sites: '.ljust(padding)+str(len(self.sites_addrs)),1)
        self.debug.logger('depth reached: '.ljust(padding)+str(self.depth_reached)+'/'+str(LIMIT_DEPTH),1)
        self.debug.logger('-----+++++++++++--------\n',1)
        if not self.is_data_saved:
            self.save_data(self.last_run_datetime)
            self.is_data_saved = True

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
        if num_parts <= 3:
            return True
        if (num_parts == 4) and (page_addr_parts[3].find('~') == 0):
            return True
        return False

    def fixed_urljoin(self, urlpart1, urlpart2):
        if urlpart2 == "":
            return urlpart1
        #self.debug.logger('THIS:::'+urlpart2+':::'+str(len(urlpart2))+':::')
        try:
            while " " == urlpart2[0] or '\n' == urlpart2[0]:
                urlpart2 = urlpart2[1:]
            url = urljoin(urlpart1, urlpart2)
            #splits = str(tmp_url).split("/")
            #splits = filter(lambda x: x!= "..", splits)
            #url    = '/'.join(splits)
        except KeyboardInterrupt, SystemExit:
            raise
        except:
            return None
        return url

    def validate_html_doc(self, html_doc):
        if html_doc.find('404 Not Found') != -1:
            return False
        return True

    def contains(self, _str, substr):
        return -1 != _str.find(substr)


    def page_contains_base_url(self, page_addr):
        if -1 == page_addr.find(self.base_url):
            return False
        return True

    def is_scannable_page(self, page_addr):
        #if not self.contains(page_addr, '.htm') and not self.contains(page_addr, '.shtm') and page_addr[-1] != '/' and page_addr[-5:] != 'ac.il':
        #    return False
        bad_suffix  = ['.pdf', '.PDF', '.doc', '.DOC', '.jpg', '.JPG', '.pptx', 'ppt', '.gif', 'mp4', '.ps', '.zip', '.rar', '.bmp']
        bad_domains = ['jigsaw', 'facebook', 'mailto:']
        bad_parts = bad_suffix + bad_domains
        for part in bad_parts:
            if self.contains(page_addr, part):
                return False
        return True

    def filter_out(self, page_addr):
        if page_addr.find('2016') != -1:
            return False
        if (page_addr.find('photos') != -1)        and (page_addr.find('2') != -1):
            return True
        if (page_addr.find('events') != -1)        and (page_addr.find('2') != -1):
            return True
        if (page_addr.find('photo-gallery') != -1) and (page_addr.find('2') != -1):
            return True
        if page_addr.find('/news/') != -1:
            return True
        return False


    '''
    Main function: recursively scan sites
    '''
    def map_engine(self, page_addr, depth):
        self.debug.logger('map_engine')
        OPEN  = [page_addr]
        CLOSE = []
        while [] != OPEN:
            if 2 == self.check_quit_requests():
                return
            page_addr = OPEN.pop()
            CLOSE.insert(0, page_addr)
            ''' Some optimizations: '''
            self.scanned_pages.add(page_addr)
            html_doc, optional_err_msg = self.get_html_doc(page_addr)
            ''' we want to continue scraping in case that a connection to web page timed-out or page not found '''
            if None == html_doc or not self.validate_html_doc(html_doc) or optional_err_msg != None:
                err_msg = optional_err_msg if  optional_err_msg != None else 'page not found'
                self.debug.logger('map_engine: '+page_addr+': '+err_msg, 2)
                continue
            self.profiler.snapshot('initial_checks')
            try:
                self.debug.logger("Running BS on %s" % (page_addr))
                #soup = self.misc.run_with_timer(BeautifulSoup, (html_doc, 'html.parser'), "BeautifulSoup failed on page "+page_addr, True)
                sps = SoupStrainer('a')
                self.debug.logger("html_doc length=%s" % (len(html_doc)))
                ''' optimization '''
                if len(html_doc) > MAX_SCANNABLE_HTML_LEN:
                    self.debug.logger('map_engine: bad page '+page_addr+': '+'page too large', 2)
                    continue
                callBS = partial(BeautifulSoup, html_doc, 'lxml', parse_only= sps)
                soup = self.misc.run_with_timer(callBS, (),  "BeautifulSoup failed on page "+page_addr, True)
                #soup = self.misc.run_with_timer(BeautifulSoup, (html_doc, 'lxml', {'parseOnlyThese': SoupStrainer('a')} ), "BeautifulSoup failed on page "+page_addr, True)
                #soup = BeautifulSoup (html_doc, 'lxml', parseOnlyThese = SoupStrainer('a') )
            except (KeyboardInterrupt, SystemExit) as e:
                raise
            except:
                err_msg = str(sys.exc_info()[0])
                self.debug.logger('map_engine: bad page '+page_addr+': '+err_msg, 2)
                continue
            #self.debug.logger("soup = %s" % (soup))
            self.profiler.snapshot('beautifulsoups')
            self.visited_pages.add(page_addr)
            if self.is_page_a_site_home(page_addr):
                self.sites_addrs.add(page_addr)
            if depth == 0:
                break
            depth -= 1
            self.depth_reached = LIMIT_DEPTH - depth
            self.debug.logger("page_addr="+page_addr, 1)
            link_tags = soup.find_all('a')
            #link_tags = page_addr.findAll('a')
            #self.debug.logger("link_tags = %s" % (link_tags))
            for link_tag in link_tags:
                link = link_tag.get('href')
                if not self.is_ascii(link) or link == "None" or link == None: #or (link.find("#") != -1): # TODO: check if this can occur
                    self.debug.logger("Not ASCII link found", 0)
                    continue
                full_link = self.fixed_urljoin(page_addr, link)
                if (full_link in CLOSE) or (full_link in OPEN):
                    continue
                if not self.is_this_page_good_for_jews(full_link, link):
                    self.debug.logger("skipping")
                    continue
                OPEN.insert(0, full_link)

    def is_this_page_good_for_jews(self, page_addr, link):
        #self.debug.logger('validat page...')
        if not (self.is_ascii(page_addr)):
            self.debug.logger('map_engine: bad link: not ASCII ',2)
            return False
        if (None == page_addr):
            self.debug.logger('map_enginae: bad link:'+link,2)
            return False
        if (len(page_addr.split('/')) > 15):
            return False
        if not (self.page_contains_base_url(page_addr)):
            self.debug.logger('map_engine: bad link: not contain base URL '+page_addr,0)
            return False
        if self.filter_out(page_addr):
            self.debug.logger('map_engine: bad link: filtered out: '+page_addr,2)
            return False
        if not (self.is_scannable_page(page_addr)):
            self.debug.logger('map_engine: bad link: not scannable: '+page_addr,2)
            return False
        if (page_addr in self.scanned_pages):
            self.debug.logger('map_engine: bad link: already scanned '+page_addr,0)
            return False
        self.debug.logger('page good!')
        return True


    '''
        gets full page address: http://site
        return source code of the site as string
    '''
    def get_html_doc(self, page_addr):
        page_data = None
        err_msg   = None
        #self.debug.assrt(page_addr.find("http://") == 0, "get_html_doc: page_addr="+page_addr)
        try:
            self.debug.logger("requesting page: %s ..." % (page_addr))
            request = self.misc.run_with_timer(self.http.request, ('GET', page_addr), "request for "+page_addr+" failed", True, 5)  # TODO
            #self.debug.logger("bp2")
            #request = self.http.request('GET', page_addr)
            self.profiler.snapshot('http_request')
        except KeyboardInterrupt:
            raise
        except TimeoutException:
            err_msg = 'http request timeout'
        except :
            err_msg = str(sys.exc_info()[0])
        if err_msg == None:
            if (request != None):
                page_data = str(request.data)
        #self.debug.logger('get_html_doc: page_data='+str(page_data)+'. err_msg='+str(err_msg))
        return page_data, err_msg

    def run_once(self):
        self.debug.logger('WebMapper.run_once:')
        self.setup_for_single_run()
        self.last_run_datetime = datetime.datetime.now()
        self.curr_run_start_time = time.time()
        try:
            self.map_engine(self.start_addr, LIMIT_DEPTH)
        except SystemExit:
            raise SystemExit
        except:
            raise
        finally:
            self.close_single_run()

    ''' 0 - no exit. 1 - exit. 2 - immediate exit '''
    def check_quit_requests(self):
        try:
            workObj = self.inQ.get(False)
        except Queue.Empty:
            return 0
        self.debug.assrt(workObj.workID == WorkID.EXIT, "check_quit_requests: got unrecognized work requests. intergratation is needed!")
        self.debug.logger('check_quit_requests: got exit with type='+str(workObj.param))
        self.need_to_quit = 2
        return self.need_to_quit

    def run_in_cont_mode(self):
        self.debug.logger('WebMapper.run_in_cont_mode:')
        last_run = time.time() - self.execution_interval - 10
        while 0 == self.need_to_quit:
            if (time.time() - last_run) > self.execution_interval:
                self.run_once()
                last_run = time.time()

    def start_mapping(self):
        self.debug.assrt(self.valid == 1, "start_mapping: attempt to start mapping without configure Mapper!")
        self.debug.logger('start_mapping: ')
        self.need_to_quit = 0
        interval = self.execution_interval
        self.debug.logger('WebMapper.start_mapping: interval='+str(interval))
        if 0 == interval:
            self.run_once()
        else:
            self.run_in_cont_mode()




def main_web_mapper():
    debug = register_debugger()
    try:
        webMapper = WebMapper()

        webMapper.start_mapping()
    except KeyboardInterrupt:
        debug.logger('got KeyboardInterrupt!')
    except:
        raise
    finally:
        if webMapper != None:
            webMapper.profiler.print_stats()

if __name__ == "__main__":
    debug = register_debugger(master = True)
    try:
        main_web_mapper()
    except:
        close_debugger()
        raise

