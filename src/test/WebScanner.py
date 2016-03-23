#!/usr/bin/python

import sys
import io
import os
import urllib3 
from bs4 import BeautifulSoup

def print_types(*args):
    print("Printing Types:")
    for arg in args:
        print(type(arg))

def extract_links_from_page(html_doc):
    soup = BeautifulSoup (html_doc, 'html.parser')
    for link in soup.find_all('a'):
        print(link.get('href'))


def process_web_page(page_addr):
    http     = urllib3.PoolManager()
    request1 = http.request('GET', page_addr)
    extract_links_from_page(str(request1.data))
#    print (request1.status)
#   print (request1.headers['server'])
#    b = io.BufferedReader(request1)
    

    data_path = 'data/'
    if not os.path.exists(data_path):
        os.makedirs(data_path)
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
 #   print(firstpart)
 #   print_types(http, request1, request2, b, firstpart, secondpart)



if __name__ == "__main__":
    page_addr = sys.argv[1]
    print('-- WebScanner --')
    print('Processing: '+page_addr)
    process_web_page(page_addr)
    print('Good Day!')
    
