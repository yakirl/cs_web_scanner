#!/bin/python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def test1():
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get("http://www.cs.technion.ac.il")
    link = driver.find_element_by_id("contact")
    print (link)
    driver.close()

if __name__ == "__main__":
    test1()
