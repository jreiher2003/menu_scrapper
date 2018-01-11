import os
import time
import re
import xml.etree.ElementTree as ET
import requests 
from bs4 import BeautifulSoup as bs
from utils import renew_ip, whats_the_ip
from fake_useragent import UserAgent
from sqlalchemy import create_engine
from sqlalchemy import desc,asc
from sqlalchemy.orm import sessionmaker
from models import Restaurant, Menu, Section, MenuSection, MenuItem, ItemPrice, MenuItemPrice

engine = create_engine(os.environ["SCRAPER_URL_TEST"])
Session = sessionmaker(bind=engine)
session = Session()

def get_menu_name(menu_id):
    """ Makes a request to restaurant menu page by menu_id.  Finds
    a javascript var menuApi.loadMenusForLocation and pulls the menu name 
    from the javascript var.  

    Keyword arguments:
    menu_id --string: id from menu stored in RestaurantLinks.menu_url_id
    """
    r = requests.get("http://www.menupix.com/menudirectory/menu.php?id="+menu_id, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
    soup = bs(r.text,"lxml")
    name = soup.find_all("script")
    for n in name:
        p = re.search(r"(menuApi.loadMenusForLocation).*", n.text)
        if p:
            menu_match = p.group(0)
            menu_first = menu_match[30:]
            menu = menu_first[:menu_first.find("'")]
            return menu

def get_javascript_menu_api(restaurant_name):
    """ Makes a request to singleplatform api and returns the javascript var callback defaultApiCallResponseHandler

    Keyword arguments:
    restaurant_name -- string: name of restaurant from RestaurantLinks.menu_name_slug ie: tonys-darts-away
    """
    content = requests.get("http://menus.singleplatform.co/storefront/menus/"+ restaurant_name +".js?callback=menuApi.defaultApiCallResponseHandler&ref=&current_announcement=1&photos=1&apiKey=k47dex17opfs7y7nae9a6p8o0", proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
    return content.content

def parse_into_xml_string(xml):

    """ Parses mal formed string into a xml doc string """

    xml_first = xml[39:]
    xml_string = xml_first[:xml_first.find("</storefront>") + 13]
    return xml_string

def parse_menu1(xml_string, rest_id):
    root = ET.fromstring(xml_string)
    for menus in root:
        for menu in menus:
            for m in menu:
                if m.tag == "title" and m.text is not None:
                    print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
                    print m.tag, m.text.strip()
                    print "\n"
                for sections in m:
                    for section in sections:
                       
                        if section.tag == "section_desc" and section.text is not None:
                            print section.tag, section.text.strip()
                        if section.tag == "section_name" and section.text is not None:
                            print section.tag, section.text.strip()
                            print "\n"
                        for menu_items in section:
                            for menu_item in menu_items:
                                if menu_item.tag == "item_title" and menu_item.text is not None:
                                    print menu_item.tag, menu_item.text.strip() 
                                if menu_item.tag == "item_description" and menu_item.text is not None:
                                    print menu_item.tag, menu_item.text.strip()
                                for menu_item_prices in menu_item:
                                    for menu_item_price in menu_item_prices:
                                        if menu_item_price.tag == "price_title":
                                            print menu_item_price.tag, menu_item_price.text.strip()
                                        if menu_item_price.tag == "price_value":
                                            print menu_item_price.tag, menu_item_price.text.strip() 
                                for menu_item_addons in menu_item:
                                    for menu_item_addon in menu_item_addons:
                                        # print menu_item_addon.tag, menu_item_addon.text"##################################################"
                                        if menu_item_addon.tag == "addon_title" and menu_item_addon.text is not None:
                                            print menu_item_addon.tag, menu_item_addon.text.strip() 
                                        if menu_item_addon.tag == "addon_value" and menu_item_addon.text is not None:
                                            print menu_item_addon.tag, menu_item_addon.text.strip()
                                        






def parse_menu(xml_string, rest_id):
    """ Parses xml from javascript request.  
    Stores menu name, category_name, category_desc, item_name, 
    item_desc, price, addon_title, addon_value. 
    """
    root = ET.fromstring(xml_string)
    menus = root.findall("./menus/menu")
    sections = root.findall(".//menus/menu")
    for section in sections:
        print "\n"
        for menu in section.iter(tag="title"):
            m = Menu()
            print menu.tag, menu.text
            m.name = menu.text
            m.restaurant_id = rest_id
            print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$' 
        for menu_cat in section.iter(tag="section_name"):
            s = Section()
            ms = MenuSection()
            print menu_cat.tag, menu_cat.text
            s.name = menu_cat.text
        for menu_description in section.iter(tag="section_desc"):
            print menu_description.tag, menu_description.text
            s.description = menu_description.text  
        session.add(m)
        session.add(s)
        ms.menu_id = m.id 
        ms.section_id = s.id 
        session.add(ms)
        session.commit() 
        # for items in section:
        #     for item in items:
        #         print "\n"
        #         mi = MenuItem()
        #         for i in item.iter(tag="item_title"):
        #             print i.tag, i.text
        #             mi.name = i.text 
        #         for i in item.iter(tag="item_description"):
        #             print i.tag, i.text
        #             mi.description = i.text 
        #             mi.section_id = s.id 
        #         session.add(mi)
        #         session.commit() 
        #         for i in item:
        #             for prices in i:
        #                 ip = ItemPrice()
        #                 mip = MenuItemPrice()
        #                 for price in prices.iter(tag="price_title"):
        #                     print price.tag, price.text 
        #                     ip.price_title = price.text
        #                 for price in prices.iter(tag="price_value"):
        #                     print price.tag, price.text
        #                     ip.price_value = price.text 
        #                 for price in prices.iter(tag="addon_title"):
        #                     print price.tag, price.text
        #                     ip.addon_title = price.text 
        #                 for price in prices.iter(tag="addon_value"):
        #                     print price.tag, price.text
        #                     ip.addon_value = price.text
        #                 session.add(ip)
        #                 session.commit()
        #                 mip.menu_item_id = mi.id 
        #                 mip.item_price_id = mi.id 
        #                 session.add(ip)
        #                 session.commit()

def pop_menu_items():
    renew_ip()
    time.sleep(4)
    start = raw_input("start: ")
    end = raw_input("end: ")
    off = 0
    counter_menu = 0
    ua = UserAgent()
    for i in range(int(start),int(end)):
        rest = session.query(Restaurant).filter_by(id=i).one()
        off += 1
        print "read loop: ", off, " rest_id: ", rest.id 
        if rest.text_menu_available == True:
            print "text menu is true..."
            print "restaurant menu id: ",rest.id, " menu_url_id: ",rest.menu_url_id, "rest_name: ", rest.rest_name
            menu_name = get_menu_name(rest.menu_url_id)
            if menu_name:
                xml = get_javascript_menu_api(menu_name)
                xml_string = parse_into_xml_string(xml)
                parse_menu1(xml_string, rest.id)
                counter_menu += 1
            print "number of menu's scraped: ", counter_menu

def requests_for_menu():
    r = requests.get("http://www.menupix.com/menudirectory/menu.php?id=380210266", proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
    print r.status_code
    print r.headers
    print r.json


if __name__ == "__main__":
    t0 = time.time()
    pop_menu_items()
    # parse_menu1("test1.xml", "10")
    whats_the_ip()
    end = (time.time() - t0)
    print end, ": in seconds", "  ", end/60, ": in minutes"