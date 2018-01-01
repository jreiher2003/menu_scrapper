import os
import time 
import datetime
import re
from collections import OrderedDict
import math
import string
import psutil
from pprint import pprint
import requests 
from bs4 import BeautifulSoup as bs
from bs4 import Comment
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from pyvirtualdisplay import Display
from sqlalchemy import create_engine
from sqlalchemy import desc,asc
from sqlalchemy.orm import sessionmaker
from models import State, MetroAssoc, CityMetro, County, RestaurantLinks,RestaurantLinksCusine, Cusine, Menu, RestaurantMenuCategory, Category, RestaurantMenuCategoryItem
from menu import connect_states, pop_dc, change_sanluisobispo, change_missouri_kc, change_mississipi, change_portland, change_washington,\
pop_city_metro_true, delete_duplicate_city_links_with_no_info, update_city_metro_r_totals, change_more_county_id, compare_city_metro, \
delete_duplicate_city_links, remove_exact_dups, grab_restaurant_links_city, pop_rest_links, pop_cusine_table, pop_text_menu_available
from utils import renew_ip, get_current_ip, whats_the_ip

engine = create_engine(os.environ["SCRAPER_URL"])
Session = sessionmaker(bind=engine)
session = Session()

def make_rest_table_collect_links():
    renew_ip()    
    time.sleep(12)
    for i in range(52,63):# state      #geo from county to county+1
        print "for loop: ", i
        # renew_ip()    
        time.sleep(1)
        # whats_the_ip()
        grab_restaurant_links_city(i)

def run_rest_code():
    start_id = raw_input("starting id: ")
    end_id = raw_input("ending id: ")
    renew_ip()
    time.sleep(12)
    # id's of restaurant_links  
    for i in range(int(start_id), int(end_id)):
        print "\n"
        print "############# restaurant info ##################################"
        print "for loop: ", i 
        try:
            pop_rest_links(i)
        except requests.exceptions.TooManyRedirects:
            print "ERROR: too many redirects"
            time.sleep(15)
            renew_ip()
            time.sleep(30)
        except requests.exceptions.ConnectionError:
            print "ERROR: connection error"
            time.sleep(15)
            renew_ip()
            time.sleep(30)
            pop_rest_links(i)
        except requests.exceptions.ChunkedEncodingError:
            print "ERROR: connection broken incompleted read"
            time.sleep(15)
            renew_ip()
            time.sleep(30)
            pop_rest_links(i)
        except AttributeError:
            print "AttributeError: 'NoneType' object has no attribute 'find'."
            time.sleep(15)
            renew_ip()
            time.sleep(30)

def update_text_menu_available():
    time.sleep(15)
    renew_ip()
    start = raw_input("start: ")
    end = raw_input("end: ")
    off = 0
    for i in range(int(start),int(end)):
        off += 1
        print "real loop: ", off, " rest_id: ", i
        try:
            pop_text_menu_available(i)
        except IndexError:
            print "End of list"
        except requests.exceptions.ConnectionError:
            print "ERROR: connection error"
            time.sleep(15)
            renew_ip()
            time.sleep(15)
            pop_text_menu_available(i)
        except AttributeError: # checks regex value Text Menu on menu page.
            print "ERROR: NoneType object has no attribute encode expect"
        except (KeyboardInterrupt, SystemExit):
            raise

def script_menu_type_1(html, rest_link_id, wait_time):#user_agent, 
    soup = bs(html,"lxml")
    table_start = soup.find("table")
    td = table_start.find_all("tr")
    #get and store menu name with restauant link id
    menu_name = [tr.find("strong") for tr in td[0]][1].get_text(strip=True)
    print menu_name, rest_link_id
    m = Menu(name=menu_name, restaurant_links_id=rest_link_id)
    session.add(m)
    session.commit()
    print "menu id is: ", m.id
    all_menu_items = soup.find('div', {'id':'sp_panes'})
    if all_menu_items:
        for l in all_menu_items.find_all(True, {'class': ['sp_st','sp_sd','hstorefrontproduct', 'fn','sp_option', 'sp_description']}):
            if 'sp_st' in l.attrs['class']:
                cat = Category()
                rmc = RestaurantMenuCategory()
                print l.get_text(strip=True)
                cat.name = l.get_text(strip=True)
            if 'sp_sd' in l.attrs['class']:# category description
                print l.get_text(strip=True)
                cat.description = l.get_text(strip=True)
            if 'hstorefrontproduct' in l.attrs['class']:
                rmci = RestaurantMenuCategoryItem()
            if 'sp_description' in l.attrs['class']:
                rmci_description = l.get_text(strip=True)
                rmci.description = rmci_description
                print rmci_description 
            if 'sp_option' in l.attrs['class']:
                rmci_price = l.get_text(strip=True)
                rmci.price = rmci_price
                print rmci_price
            if 'fn' in l.attrs['class'] and not 'sp_st' in l.attrs['class']:
                rmci_name = l.get_text(strip=True)
                rmci.name = rmci_name
                rmci.restaurant_links_id = rest_link_id 
                rmci.menu_id = m.id 
                rmci.category_id = cat.id 
                print rmci_name
                session.add(rmci)
                session.commit()
            session.add(cat)
            rmc.restaurant_links_id = rest_link_id 
            rmc.menu_id = m.id
            rmc.category_id = cat.id
            session.add(rmc)
            session.commit()
    else:
        print "THIS IS YOUR EDIT ALL_MENU_ITEMS WERE NONE"


def pop_menu_items():
    renew_ip()
    time.sleep(4)
    start = raw_input("start: ")
    end = raw_input("end: ")
    off = 0
    counter_menu = 0
    wait_time = 200
    ua = UserAgent()
    
    for i in range(int(start),int(end)):
        rq = session.query(RestaurantLinks).filter_by(id=i).one()
        for proc in psutil.process_iter():
            if proc.name() == 'firefox':
                proc.kill()
        off += 1
        print "read loop: ", off, " rest_id: ", rq.id 
        if rq.text_menu_available == True:
            for proc in psutil.process_iter():
                if proc.name() == 'firefox':
                    proc.kill()
            print "text menu is true..."
            print "restaurant menu id: ",rq.id, " menu_url_id: ",rq.menu_url_id
            counter_menu += 1
            print "number of menu's scraped: ", counter_menu
            display = Display(visible=0, size=(800, 800))  
            display.start()
            binary = FirefoxBinary('/usr/bin/firefox')
            profile=webdriver.FirefoxProfile()
            profile.set_preference('network.proxy.type', 1)
            profile.set_preference('network.proxy.socks', '127.0.0.1')
            profile.set_preference('network.proxy.socks_port', 9050)
            profile.set_preference('javascript.enabled', True)
            profile.set_preference('marionette', False)
            profile.set_preference("general.useragent.override", ua.firefox)
            browser=webdriver.Firefox(firefox_profile=profile,firefox_binary=binary)#
            finished = 0
            while finished == 0:
                try:
                    u = "http://www.menupix.com/menudirectory/menu.php?id=%s&type=1" % rq.menu_url_id
                    browser.get(u)
                    print browser.current_url
                    if browser.current_url != "http://www.menupix.com/":
                        WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.ID, 'menusContainer')))
                        html = browser.page_source
                        script_menu_type_1(html, rq.id, wait_time) 
                        finished = 1
                        browser.quit()
                        display.stop()
                        for proc in psutil.process_iter():
                            if proc.name() == 'firefox':
                                proc.kill()
                    else:
                        print "redirected to www.menupix.com"
                        finished = 1
                        for proc in psutil.process_iter():
                            if proc.name() == 'firefox':
                                proc.kill()
                except TimeoutException:
                    print "EXCEPTION: URL of SCRAPER is trying again. going to sleep for 15 seconds"
                    time.sleep(15)
            
                except WebDriverException:
                    print "WebDriverException: going to try again in 3,2,1.."
                    time.sleep(8)
                #     renew_ip()
                #     print "ip renewed"
                #     time.sleep(12)
                #     display = Display(visible=0, size=(800, 800))  
                #     display.start()
                #     binary = FirefoxBinary('/usr/bin/firefox')
                #     profile=webdriver.FirefoxProfile()
                #     profile.set_preference('network.proxy.type', 1)
                #     profile.set_preference('network.proxy.socks', '127.0.0.1')
                #     profile.set_preference('network.proxy.socks_port', 9050)
                #     profile.set_preference('javascript.enabled', True)
                #     profile.set_preference('marionette', False)
                #     profile.set_preference("general.useragent.override", ua.firefox)
                #     browser=webdriver.Firefox(firefox_profile=profile,firefox_binary=binary)#
                #     u = "http://www.menupix.com/menudirectory/menu.php?id=%s&type=1" % rq.menu_url_id
                #     browser.get(u)
                #     print browser.current_url
                #     WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.ID, 'menusContainer')))
                #     html = browser.page_source
                #     script_menu_type_1(html, rq.id, wait_time) 
                #     browser.quit()
                #     display.stop()
                #     for proc in psutil.process_iter():
                #         if proc.name() == 'firefox':
                #             proc.kill()
                # except AttributeError: # checks regex value Text Menu on menu page.
                #     print "ERROR: NoneType object has no attribute 'find_all"
    print "read loop: ", off, " rest_id: ", rq.id, "number of menu's scraped: ", counter_menu
           


if __name__ == "__main__":
    t0 = time.time()
    ############################################
    # delete_duplicate_city_links_with_no_info()
    # update_city_metro_r_totals()
    # change_more_county_id()
    # compare_city_metro()
    # delete_duplicate_city_links()
    # remove_exact_dups()
    ############################################
    ############################################
    # don't forget to do canada
    # make_rest_table_collect_links()
    ############################################
    ############################################
    ### pop menu rest_link #####################
    # run_rest_code()
    ############################################
    # update_text_menu_available()
    #############################################
    # ua = UserAgent()
    # script_menu_type_1(ua.random,3,5202628)
    #############################################
    pop_menu_items()

    end = (time.time() - t0)
    print end, ": in seconds", "  ", end/60, ": in minutes"