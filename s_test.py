#!/usr/bin/env python

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs

display = Display(visible=0, size=(1024, 768))
display.start()

browser = webdriver.Firefox()
browser.get('http://www.google.com/')
print browser.current_url
# WebDriverWait(browser, 180).until(EC.visibility_of_element_located((By.ID, 'menusContainer')))
        
# html = browser.page_source
# soup = bs(html,"lxml")
# table_start = soup.find("table")
# td = table_start.find_all("tr")
# #get and store menu name with restauant link id
# menu_name = [tr.find("strong") for tr in td[0]][1].get_text(strip=True)
# print menu_name
browser.quit()
display.stop()
