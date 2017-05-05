import os
import datetime
import re
from collections import OrderedDict
import math
import time
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
from utils import renew_ip, get_current_ip, whats_the_ip

engine = create_engine(os.environ["SCRAPER_URL"])
Session = sessionmaker(bind=engine)
session = Session()

menu_pix = "http://www.menupix.com"
def connect_states():
    """
    Connects to menupix with user agent and referer set in requests object.
    """
    return requests.get(menu_pix, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))

def states_and_metro(content):
    """
    Scrapes front page from header - Popular U.S. Cities - Puts links into db by 
    state name, abbr.  and metro area name and links for later use and checking against
    other tables. Also we remove trailing slash from links to keep a data base conform 
    of no trailing slashes on links.
    """
    soup = bs(content.content, "html.parser")
    div_start = soup.find('div', {'id': 'homepages_bottom_city_links'})
    for l in div_start.find_all(True, {'class': ['hp_bottom_toppadding', 'hp_bottom_indent']}):
        if "hp_bottom_toppadding" in l.attrs['class']:
            name = l.get_text().split("(")[0].strip()
            abbr = l.get_text().split("(")[1][:-1].strip()
            link = l['href'][:-1].strip()
            state = State(name=name, abbr=abbr, state_link=link)
            session.add(state)
            session.commit()
        if "hp_bottom_indent" in l.attrs['class']:
            name_m =  l.get_text().strip()
            link_m = l['href'].strip()[:-1]
            metro_a = MetroAssoc(name=name_m, metro_link=link_m, state_id=state.id)
            session.add(metro_a)
            session.commit()

def find_county():
    """
    Scapes front page of every state link.  Saves counties with each city in respected counties and states.  
    ex. http://www.menupix.com/alabama 
    """
    state_list = session.query(State).all() 
    for state1 in state_list:
        r = requests.get(state1.state_link, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
        soup = bs(r.content, "lxml")
        div_start = soup.find("div", {"id": "homepage_metro_container_div"})
        for l in div_start.find_all(True, {'class': ['index_bulletheading', 'index_bulletpoints']}):
            if "index_bulletheading" in l.attrs['class']:
                county1 = County(name=l.find('a').get_text().strip(), state_id=state1.id)
                session.add(county1) 
                session.commit()
            if "index_bulletpoints" in l.attrs['class']:
                metro_links = session.query(MetroAssoc).filter_by(state_id=state1.id).all()
                temp = []
                for link in metro_links:
                    temp.append(link.metro_link)
                if l.find('a')['href'].strip() in temp:
                    city1 = CityMetro(city_name=l.find('a').get_text().strip(), city_link=l.find('a')['href'].strip(), metro_area=True, state_id=state1.id, county_id=county1.id)
                    session.add(city1)
                else:
                    city1 = CityMetro(city_name=l.find('a').get_text().strip(), city_link=l.find('a')['href'].strip(),metro_area=False, state_id=state1.id, county_id=county1.id)
                    session.add(city1)
            session.commit()

def pop_cusine_table():
    """
    Scapes front page of every state link.  Saves cusine list to table. Checks to see if the record is there first.  
    ex. http://www.menupix.com/alabama 
    """
    state_list = session.query(State).all() 
    for state1 in state_list:
        r = requests.get(state1.state_link, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
        soup = bs(r.content, "lxml")
        try:
            div_start = soup.find("div", {"id": "leftnav_cuisine_state_index"})
            for l in div_start.find_all('li', {'class':'index_bulletpoints'}):
                # print l.get_text().split("(")[0].strip() 
                item = l.get_text().split("(")[0].strip() 
                cusine_object = session.query(Cusine).filter_by(name=item).one_or_none()
                # print cusine_object
                if cusine_object is None:
                    print item 
                    print "\n"
                    new_cusine_object = Cusine()
                    new_cusine_object.name = item
                    session.add(new_cusine_object)
                    session.commit()
                else:
                    print "do nothing object already exsists."
        except AttributeError:
            print "ERROR: ", state1.name, "has no cusine links"
            div_start = soup.find("div", {"id": "short_cuisineslist"})
            for l in div_start.find_all(True, {'class':['short_cuisine_class','long_cuisine_class']}):
                # print l.get_text().split("(")[0].strip() 
                item = l.get_text().split("(")[0].strip() 
                cusine_object = session.query(Cusine).filter_by(name=item).one_or_none()
                # print cusine_object
                if cusine_object is None:
                    print item 
                    print "\n"
                    new_cusine_object = Cusine()
                    new_cusine_object.name = item
                    session.add(new_cusine_object)
                    session.commit()
                else:
                    print "do nothing object already exsists."
        except:
            print "NO URL EXSISTS FOR: ", state.name 




def pop_dc():
    """ 
    This is for the fact that dc doesn't have a record in county or city tables 
    runs once after find_county. We change the name to Washington, D.C. universally. 
    Removes a city called Fort Myer which doesn't exist in DC area.  Lastly, queries all
    /dc metro links with metro_area=False and replaces links with city RestaurantLinks associated
    with that city county and state.  
    """
    state_change = session.query(State).filter_by(state_link="http://www.menupix.com/dc").one()
    state_change.name = "Washington, D.C."
    metro_change = session.query(MetroAssoc).filter_by(metro_link="http://www.menupix.com/dc").one()
    metro_change.name = "Washington, D.C."
    dc_county = County(name="Washington County", state_id=9)
    session.add(dc_county)
    session.commit()
    dc = CityMetro(city_name="Washington, D.C.", city_link="http://www.menupix.com/dc", metro_area=True, state_id=9, county_id=dc_county.id)
    session.add(dc)
    session.commit() 
    del_city = session.query(CityMetro).filter_by(city_name="Fort Myer", metro_area=False).one()
    session.delete(del_city)
    session.commit()
    change = session.query(CityMetro).filter_by(city_link="http://www.menupix.com/dc", metro_area=False).all()
    for i in change:
        if i.city_name == "Alexandria":
            i.city_link = "http://www.menupix.com/dc/n/504/Alexandria-restaurants"
        if i.city_name == "Arlington":
            i.city_link = "http://www.menupix.com/dc/n/510/Arlington-restaurants"
        if i.city_name == "Bethesda":
            i.city_link = "http://www.menupix.com/dc/n/516/Bethesda-restaurants"
        if i.city_name == "Chevy Chase":
            i.city_link = "http://www.menupix.com/dc/n/525/Chevy-Chase-restaurants"
        session.add(i)
        session.commit()

def change_sanluisobispo():
    change = session.query(CityMetro).filter_by(city_link="http://www.menupix.com/sanlouisobispo").all()
    for i in change:
        i.metro_area = True
        i.city_link = "http://www.menupix.com/sanluisobispo"
        session.add(i)
        session.commit() 

def change_missouri_kc():
    change = session.query(CityMetro).filter_by(state_id=26).all()#city_link="http://www.menupix.com/kansascity", 
    for i in change: 
        if i.city_name == "Blue Springs":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25110/Blue-Springs-restaurants"
        if i.city_name == "Buckner":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25111/Buckner-restaurants"
        if i.city_name == "Excelsior Springs":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25101/Excelsior-Springs-restaurants"
        if i.city_name == "Gladstone":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25102/Gladstone-restaurants"
        if i.city_name == "Grandview":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25113/Grandview-restaurants"
        if i.city_name == "Greenwood":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25114/Greenwood-restaurants"
        if i.city_name == "Holt":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25103/Holt-restaurants"
        if i.city_name == "Independence":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25115/Independence-restaurants"
        if i.city_name == "Kansas City":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25104/Kansas-City-restaurants"
        if i.city_name == "Kearney":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25105/Kearney-restaurants"
        if i.city_name == "Lake Lotawana":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25116/Lake-Lotawana-restaurants"
        if i.city_name == "Lees Summit":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25117/Lees-Summit-restaurants"
        if i.city_name == "Liberty":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25106/Liberty-restaurants"
        if i.city_name == "Lone Jack":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25118/Lone-Jack-restaurants"
        if i.city_name == "North Kansas City":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25107/North-Kansas-City-restaurants"
        if i.city_name == "Oak Grove":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25119/Oak-Grove-restaurants"
        if i.city_name == "Pleasant Valley":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25108/Pleasant-Valley-restaurants"
        if i.city_name == "Raytown":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25120/Raytown-restaurants"
        if i.city_name == "Smithville":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25109/Smithville-restaurants"
        if i.city_name == "Sugar Creek":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25121/Sugar-Creek-restaurants"
        if i.city_name == "Grain Valley":
            i.metro_area = False
            i.city_link = "http://www.menupix.com/kansascity/n/25112/Grain-Valley-restaurants"
        session.add(i)
        session.commit()

def change_mississipi():
    change = session.query(CityMetro).filter_by(city_link="http://www.menupix.com/memphis", state_id=25).all()
    for c in change:

        if c.city_name == "Hernando":
            c.metro_area = False
            c.city_link = "http://www.menupix.com/memphis/n/24301/Hernando-restaurants"
        if c.city_name == "Horn Lake":
            c.metro_area = False
            c.city_link = "http://www.menupix.com/memphis/n/24302/Horn-Lake-restaurants"
        if c.city_name == "Lake Cormorant":
            c.metro_area = False
            c.city_link = "http://www.menupix.com/memphis/n/24303/Lake-Cormorant-restaurants"
        if c.city_name == "Nesbit":
            c.metro_area = False
            c.city_link = "http://www.menupix.com/memphis/n/24304/Nesbit-restaurants"
        if c.city_name == "Olive Branch":
            c.metro_area = False
            c.city_link = "http://www.menupix.com/memphis/n/24305/Olive-Branch-restaurants"
        if c.city_name == "Southaven":
            c.metro_area = False
            c.city_link = "http://www.menupix.com/memphis/n/24306/Southaven-restaurants"
        if c.city_name == "Walls":
            c.metro_area = False
            c.city_link = "http://www.menupix.com/memphis/n/24307/Walls-restaurants"
        session.add(c)
        session.commit()

def change_portland():
    del_county = session.query(County).filter_by(name="King County", state_id=38).one()
    session.delete(del_county)
    session.commit()

def change_washington():
    change = session.query(CityMetro).filter_by(city_link="http://www.menupix.com/portland", metro_area=False, state_id=48).all()
    for i in change:
        if i.city_name == "Amboy":
            i.city_link = "http://www.menupix.com/portland/n/9031/Amboy-restaurants"
        if i.city_name == "Battle Ground":
            i.city_link = "http://www.menupix.com/portland/n/9032/Battle-Ground-restaurants"
        if i.city_name == "Brush Prairie":
            i.city_link = "http://www.menupix.com/portland/n/9033/Brush-Prairie-restaurants"
        if i.city_name == "Camas":
            i.city_link = "http://www.menupix.com/portland/n/9034/Camas-restaurants"
        if i.city_name == "La Center":
            i.city_link = "http://www.menupix.com/portland/n/9035/La-Center-restaurants"
        if i.city_name == "Ridgefield":
            i.city_link = "http://www.menupix.com/portland/n/9036/Ridgefield-restaurants"
        if i.city_name == "Vancouver":
            i.city_link = "http://www.menupix.com/portland/n/9017/Vancouver-restaurants"
        if i.city_name == "Washougal":
            i.city_link = "http://www.menupix.com/portland/n/9037/Washougal-restaurants"
        if i.city_name == "Yacolt":
            i.city_link = "http://www.menupix.com/portland/n/9038/Yacolt-restaurants"
        session.add(i)
        session.commit()

def pop_city_metro_true():
    """ 
    pulls all queries from CityMetro with metro_area = True checks city_name with name being scraped from metro page, 
    if it matches update city_link with new city_link and metro_area=False.
    """
    metro = session.query(CityMetro).filter_by(metro_area=True).order_by(asc(CityMetro.state_id)).all()
    metro_city = []
    for ll in metro:
        metro_city.append((ll.city_link,int(ll.state_id)))
    metro_set = sorted(list(set(metro_city)), key=lambda x: (x[1], x[0]))
    for link,s in metro_set:
        r = requests.get(link, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
        soup = bs(r.content, "lxml")
        div_start = soup.find("ul", {"class": "homepage_ul"})
        for l in div_start.find_all(True, {'class': ['short_hood_class','long_hood_class']}):
            for a in l.find_all("a"):
                city_name = a.get_text().split("(")[0].strip() 
                rest_total1 = a.get_text().split("(")[1].strip()
                rest_total = rest_total1.split(")")[0].strip()
                city_link = a["href"].strip()
                if city_name == "South Houston":
                    city_name = None  
                mc = session.query(CityMetro).filter_by(city_name=city_name,city_link=link,state_id=s).one_or_none()  
                if mc is not None: 
                    print "city names are equal" 
                    print mc.city_name, mc.city_link,mc.state_id,mc.metro_area, city_link, rest_total
                    mc.city_link = city_link
                    mc.metro_area = False
                    mc.r_total = rest_total 
                    session.add(mc)
                    session.commit()
                    print "\n"
                else:
                    print "not equal"
                    city_n = link.split("/")[-1].capitalize()
                    print  city_link, city_name, rest_total, s
                    new = CityMetro(city_name=city_n, neighborhood_name=city_name, city_link=city_link, metro_area=False, r_total=rest_total, state_id=s)
                    session.add(new)
                    session.commit()
                    print "\n"
                
def update_city_metro_r_totals():
    city = session.query(CityMetro).filter_by(metro_area=False, r_total=None).all()
    for c in city:
        # print c.city_link, c.r_total,c.city_name
        r = requests.get(c.city_link, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
        soup = bs(r.content, "lxml")
        try:
            div_start = soup.find("div", {"id": "listings_container_div"})
            total = div_start.find("div", {"class": "results_count"})
            total_restaurants = int(total.get_text().split()[-2:-1][0])
            print "total_restaurants: ", total_restaurants, "name: ", c.city_name, c.city_link
            c.r_total = total_restaurants
            session.add(c)
            session.commit() 
        except:
            print "No info"

##################################################################################
### cleans up database ##########################################################
### make sure you check for city_link dups first ################################
#################################################################################
def compare_city_metro():
    """attempt to query rows with county_id=Null and compare the city_name with
    another query to city_metro where metro_area=True, if state_id are same, 
    update county_id with the county_id
    """
    non_con_id = session.query(CityMetro).filter_by(metro_area=False,county_id=None).all()
    metro_true = session.query(CityMetro).filter_by(metro_area=True).all()
    cnt = 0
    for c in non_con_id:
        # print c.city_name
        for m in metro_true:
            if c.city_name == m.city_name and c.state_id == m.state_id:
                print c.city_name,c.neighborhood_name, m.city_name, c.state_id, m.county_id
                cnt+=1
                print cnt
                c.county_id = m.county_id 
                session.add(c)
                session.commit()

def change_more_county_id():
    #995 total
    non_con_id = session.query(CityMetro).filter_by(metro_area=False,county_id=None).all()
    for c in non_con_id:
        if c.city_name == "Losangeles":
            c.city_name = "Los Angeles"
            session.add(c)
            session.commit()
        if c.city_name == "Dc":
            c.city_name = "Washington, D.C."
            session.add(c)
            session.commit()
        if c.city_name == "Sf":
            c.city_name = "San Francisco"
            session.add(c)
            session.commit()
        if c.city_name == "Kansascity" and c.state_id == 17:
            c.city_name = "Kansas City"
            c.county_id = 982
            session.add(c)
            session.commit()
        if c.city_name == "Sanmateo":
            c.city_name = "San Mateo"
            session.add(c)
            session.commit()
        if c.city_name == "Santabarbara":
            c.city_name = "Santa Barbara"
            session.add(c)
            session.commit()
        if c.city_name == "Hoboken" and c.state_id == 31:
            c.county_id = 1771
            session.add(c)
            session.commit()

def delete_duplicate_city_links():
    c1 = session.query(CityMetro).all()
    temp = []
    for c in c1:
        temp.append(c.city_link)
    dups = set([x for x in temp if temp.count(x) > 1])
    print len(dups)
    temp2 = []
    for x in c1:
        if x.city_link in dups and x.county_id == None:
            print x.city_name, x.city_link, x.r_total, x.state_id, x.county_id 
            print "\n"
            session.delete(x)
            session.commit()
    #         temp2.append(x.city_link)
    # print len(temp2)
def delete_duplicate_city_links_with_no_info():
    """ deletes all records or cities that don't have any info or metro area links """
    c1 = session.query(CityMetro).filter_by(r_total=None).all()
    for c in c1:
        session.delete(c)
        session.commit()

def remove_exact_dups():
    """ checks for dups """
    c1 = session.query(CityMetro).all()
    temp = []
    for c in c1:
        temp.append(c.city_link)
    dups = set([x for x in temp if temp.count(x) > 1])
    print len(dups)
    temp2 = []
    for x in c1:
        if x.city_link in dups:
            print x.city_name, x.city_link, x.r_total, x.state_id, x.county_id 
            print "\n"
###############################################################################
########### end clean up data base functions ##################################
###############################################################################

###############################################################################
############ restaurant info ##################################################
###############################################################################

def grab_restaurant_links_city(state_id):
    # city = session.query(CityMetro).filter_by(id=2782,metro_area=False,state_id=10).all()
    """ Scrapes city restaurant page ( the page that lists all the restaurants by city ) and retrieves 
    restaurant name, rest_link, thumnail_img, menu_available,  and relays city_name, neighborhood_name, state_id, county_id, city_metro_id
    change county_id = None to get the candian records.  or grab_restaurant_links_city(None) county_id = None is all Canada related cities.
    """
    city = session.query(CityMetro).filter_by(state_id=state_id).all()#.order_by(asc(CityMetro.county_id))
    for c in city:
        r = requests.get(c.city_link, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
        soup = bs(r.content, "lxml")
        div_start = soup.find("div", {"id": "listings_container_div"})
        try:
            total = div_start.find("div", {"class": "results_count"})
            total_restaurants = int(total.get_text().split()[-2:-1][0])
            print "total_restaurants: ", total_restaurants
            pages = int(math.ceil(total_restaurants/50.)) 
            print "totals: ", total_restaurants, "pages: ",pages
            if pages > 1: # checks if city restaruant page has more than one page
                for i in range(pages):
                    print i
                    time.sleep(1)
                    r = requests.get(c.city_link + "/page_%s" % str(i), proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
                    print "url: ",r.url
                    print "################################################"
                    soup = bs(r.content, "lxml")
                    # print "soup", soup
                    div_start = soup.find("div", {"id": "listings_container_div"})
                    uls = div_start.find_all("ul", {"id": "listings_ul"})
                    
                    for links in uls:
                        lis = links.find_all("li")
                        for thumbnail in lis:

                            city_rest = RestaurantLinks(city_name=c.city_name,state_id=c.state_id,county_id=c.county_id, city_metro_id=c.id)#
                            if c.neighborhood_name is not None:
                                city_rest.neighborhood_name = c.neighborhood_name

                            img = thumbnail.div.find_all("img")
                            if img:
                                print img[0]['src']
                                city_rest.thumbnail_img = img[0]['src']
                            info = thumbnail.find_all("div", {"class":"listings_row1"})
                            for i in info:
                                print i.find("a")["href"]
                                print i.find("a").get_text()
                                city_rest.rest_link = i.find("a")["href"]
                                city_rest.rest_name = i.find("a").get_text()
                            menu_available = thumbnail.find_all("div", {"class":"lighten"})
                            for m in menu_available:
                                m_a = m.get_text().encode('utf-8').split('\xe2\x80\xa2')[::-1][0].strip()
                                if m_a == "Menu Available":
                                    print m_a, "menu Available"
                                    city_rest.menu_available = True
                                else:
                                    print "no menu"
                                    city_rest.menu_available = False 
                            if city_rest.rest_name is None:
                                pass
                            else:
                                session.add(city_rest)
                                session.commit()
                                print "#############################################"
                   
            else:
                time.sleep(1)
                r = requests.get(c.city_link, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
                print "url: ",r.url
                print "################################################"
                soup = bs(r.content, "lxml")
                # print "soup", soup
                div_start = soup.find("div", {"id": "listings_container_div"})
                uls = div_start.find_all("ul", {"id": "listings_ul"})
                
                for links in uls:
                    lis = links.find_all("li")
                    for thumbnail in lis:
                        city_rest = RestaurantLinks(city_name=c.city_name,state_id=c.state_id,county_id=c.county_id, city_metro_id=c.id)#
                        if c.neighborhood_name is not None:
                                city_rest.neighborhood_name = c.neighborhood_name
                        img = thumbnail.div.find_all("img")
                        if img:
                            print img[0]['src']
                            city_rest.thumbnail_img = img[0]['src']
                        info = thumbnail.find_all("div", {"class":"listings_row1"})
                        for i in info:
                            rest_link = i.find("a")["href"]
                            name = i.find("a").get_text()
                            print rest_link
                            print name 
                            city_rest.rest_name = name
                            city_rest.rest_link = rest_link 
                        menu_available = thumbnail.find_all("div", {"class":"lighten"})
                        for m in menu_available:
                            m_a = m.get_text().encode('utf-8').split('\xe2\x80\xa2')[::-1][0].strip()
                            if m_a == "Menu Available":
                                print m_a, "menu Available"
                                city_rest.menu_available = True
                            else:
                                print "no menu"
                                city_rest.menu_available = False 
                        if city_rest.rest_name is None:
                            pass
                        else:
                            session.add(city_rest)
                            session.commit()
                            print "#############################################"
        except:
            print "ERROR: there was a problem"


def pop_rest_links(_id):
    ua = UserAgent()
    headers = {'user-agent': ua.random}
    # try:
    r = session.query(RestaurantLinks).filter_by(id=_id).one()#.filter_by(state_id=2, menu_available=True)
    # for r in rest:
    restaurant_url_page = r.rest_link
    menu_url_id = r.rest_link.rsplit("/")[-2:-1][0].strip()
    r.menu_url_id = menu_url_id 
    #time.sleep(1)
    d = requests.get(r.rest_link,  headers=headers, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
    print "url: ",d.url, d.status_code
    print r.rest_name
    print "id: ",r.id, "state_id: ", r.state_id, "county_id: ", r.county_id, "city_metro_id: ", r.city_metro_id
    soup = bs(d.content, "html.parser")
    div_start = soup.find("div", {"class": "content-main-block"})
    notecard = div_start.find("div", {"id":"notecard-block"})
    # # # restaurant address
    address = notecard.find("span", {"itemprop":"streetAddress"}).get_text()
    city_ = notecard.find("span", {"itemprop":"addressLocality"}).get_text()
    state_ = notecard.find("span", {"itemprop": "addressRegion"}).get_text()
    zip_ = notecard.find("span", {"itemprop": "postalCode"}).get_text()
    phone = notecard.find("span", {"itemprop": "telephone"}).get_text()
    # print address,city_,state_,zip_,phone
    r.address = address 
    r.city_ = city_ 
    r.state_ = state_
    r.zip_ = zip_ 
    r.phone = phone
    print "##############################################################"
    # # # yum yuck menu section 
    cusine_items = notecard.find_all("span", {"itemprop":"servesCuisine"})
    # print "### Cusine List ###"
    for item in cusine_items:
        cusine_object = session.query(Cusine).filter_by(name=item.get_text().strip()).one_or_none()
        print cusine_object
        if cusine_object is None:
            cusine_type = Cusine()
            cusine_type.name = item.get_text().strip() 
            session.add(cusine_type)
            session.commit()
            rlc = RestaurantLinksCusine(restaurant_links_id=r.id,cusine_id=cusine_type.id)
            session.add(rlc)
            session.commit()
        else:
            rlc1 = RestaurantLinksCusine(restaurant_links_id=r.id,cusine_id=cusine_object.id)
            session.add(rlc1)
            session.commit()
    # # print "--------------------"
    right_summary = notecard.find("div", {"id":"restaurant-summary-left"})
    websites = right_summary.find_all("a", {"class":"mobile-linespacing"})
    # print "### website ###"
    for w in websites:
        website = re.search(r'.*\..*\..*', w.get_text())
        if website: 
            print "Website: ", website.group(0)
            r.website = website.group(0).strip()
    # print "########## restaurant description ##########################"
    description = div_start.find(text="Restaurant Description").findNext('p').contents[0].strip()
    if not description == "Is this your restaurant?":
        r.description = description
    # print description
    # print "########### hours ##########################################"
    hours = div_start.find(text="Hours").findNext('p').contents[0]
    r.hours = hours.strip()
    # print hours.split(",")
    print "########### additional info ################################"
    add_info_block = div_start.find("div", {"class":"content-main-columns"})
    for p in add_info_block.find_all("p"):
        info = p.get_text().split()
        # print info
        if info[0]=="Delivery":
            if len(info) > 1: 
                print "Delivery: ", info[1]
                if info[1].strip() == "No":
                    r.delivery = False
                if info[1].strip() == "Yes":
                    r.delivery = True
            else: 
                print None
        if info[0] == "Price":
            if len(info) > 1:
                if info[2] == info[3]:
                    print "Price: "," ".join(info[5:9]) 
                    r.price_point = " ".join(info[5:9]).strip()
                elif info[2] == info[9]:
                    print "Price: "," ".join(info[11:13])
                    r.price_point = " ".join(info[11:13]).strip()
                elif info[2] == info[13]:
                    print "Price: "," ".join(info[15:17])
                    r.price_point = " ".join(info[15:17]).strip()
                elif info[2] == info[17]:
                    print "Price: "," ".join(info[19:])
                    r.price_point = " ".join(info[19:]).strip()
            else: 
                print None
        if info[0] == "Attire":
            if len(info) > 1: 
                print "Attire: ", " ".join(info[1:])
                r.attire = " ".join(info[1:]).strip()
            else: 
                print "Attire: ", None
        if info[0] == "Payment":
            if len(info) > 1: 
                print "Payment: ", " ".join(info[1:])
                r.payment = " ".join(info[1:]).strip()
            else: 
                print "Payment: ", None
        if info[0] == "WiFi":
            if len(info) > 1: 
                print "WiFi: ", info[1]
                if info[1].strip() == "Yes":
                    r.wifi = True
                if info[1].strip() == "No":
                    r.wifi = False
            else: 
                print "WiFi: ", None
        if info[0] == "Alcohol":
            if len(info) > 1: 
                print "Alcohol: ", " ".join(info[1:])
                r.alcohol = " ".join(info[1:]).strip()
            else: 
                print "Alcohol: ", None
        if info[0] == "Parking":
            if len(info) > 1: 
                print "Parking: ", " ".join(info[1:])
                r.parking = " ".join(info[1:]).strip()
            else: 
                print "Parking: ", None
        if " ".join(info[0:2]) == "Outdoor Seats":
            if len(info) > 2: 
                print "Outdoor Seats: ", info[2]
                if info[2].strip() == "Yes":
                    r.outdoor_seats = True 
                if info[2].strip() == "No":
                    r.outdoor_seats = False
            else: 
                print "Outdoor Seats: ", None 
        if info[0] == "Reservations":
            if len(info) > 1: 
                print "Reservations: ", info[1]
                if info[1].strip() == "Yes":
                    r.reservations = True
                if info[1].strip() == "No":
                    r.reservations = False
            else: 
                print "Reservations: ", None
        if " ".join(info[0:3]) == "Good for Kids":
            if len(info) > 3: 
                print "Good for Kids: ", info[3]
                if info[3].strip() == "Yes":
                    r.good_for_kids = True
                if info[3].strip() == "No":
                    r.good_for_kids = False
            else: 
                print "Good for Kids: ", None
    session.add(r)
    session.commit()


def pop_text_menu_available(uid):
    """ 
    querys restauant links table and updates column text_menu_available if the text Text Menu appears
    on the page.
    """
    ua = UserAgent()
    headers = {'user-agent': ua.random}
    one = session.query(RestaurantLinks).filter_by(id=uid).one()
    if one.menu_available == False:
        print "menu available false"
        one.text_menu_available = False
        session.add(one)
        session.commit()
    if one.menu_available == True:
        r = requests.get("http://www.menupix.com/menudirectory/menu.php?id=%s" % one.menu_url_id, headers=headers, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
        soup = bs(r.content, "lxml")
        pattern = re.compile(r'Text Menu')
        text_menu = soup.find(text=pattern).encode('UTF-8').strip()
        real_text_menu = text_menu.decode('utf-8').split("|")[1].strip()
        if real_text_menu == 'Text Menu':
            print "text yes"
            one.text_menu_available = True 
            session.add(one)
        elif real_text_menu != 'Text Menu':
            print "text no"
            one.text_menu_available = False 
            session.add(one)
        session.commit()




# if __name__ == "__main__":
#     import time 
#     t0 = time.time()

    # renew_ip()    
    # time.sleep(12) 
    # content = connect_states()
    # states_and_metro(content)
    # renew_ip()    
    # time.sleep(12)
    # find_county()
    # time.sleep(10)
    # pop_dc()
    # change_sanluisobispo()
    # change_missouri_kc()
    # change_mississipi()
    # change_portland()
    # change_washington()
    
    # print "#####################"
    # pop_city_metro_true()
    # print "#####################"
    # for i in range(4):
    #     print i
    #     print "_________"
    # renew_ip()    
    # time.sleep(12)
    # whats_the_ip()

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
    # renew_ip()    
    # time.sleep(12)
    # for i in range(52,63):# state      #geo from county to county+1
    #     print "for loop: ", i
    #     # renew_ip()    
    #     time.sleep(1)
    #     # whats_the_ip()
    #     grab_restaurant_links_city(i)
    ############################################

    ############################################
    ### pop menu rest_link #####################
    # ############################################
    # start_id = raw_input("starting id: ")
    # end_id = raw_input("ending id: ")
    # renew_ip()
    # time.sleep(12)
    # # id's of restaurant_links  
    # for i in range(int(start_id), int(end_id)):
    #     print "for loop: ", i 
    #     pop_rest_links(i)
    # #############################################
   
    # end = (time.time() - t0)
    # print end, ": in seconds", "  ", end/60, ": in minutes"

     


  
