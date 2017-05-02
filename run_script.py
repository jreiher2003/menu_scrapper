import os
import datetime
import re
from collections import OrderedDict
import math
import string
from pprint import pprint
import requests 
from bs4 import BeautifulSoup as bs
from bs4 import Comment
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from sqlalchemy import create_engine
from sqlalchemy import desc,asc
from sqlalchemy.orm import sessionmaker
from models import State, MetroAssoc, CityMetro, County, RestaurantLinks,RestaurantLinksCusine, Cusine
# Menu, RestaurantMenuCategory, Category, RestaurantMenuCategoryItem
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

if __name__ == "__main__":
    import time 
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
    update_text_menu_available()
    #############################################
    end = (time.time() - t0)
    print end, ": in seconds", "  ", end/60, ": in minutes"