import os
import time
import re
from lxml import etree as ET
import requests 
from bs4 import BeautifulSoup as bs
from utils import renew_ip, whats_the_ip
from fake_useragent import UserAgent
from sqlalchemy import create_engine
from sqlalchemy import desc,asc
from sqlalchemy.orm import sessionmaker
from models import Restaurant, RestaurantCoverImage, RestaurantImages, Menu, Section, MenuItem, ItemPrice, ItemAddon

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
    r = requests.get("http://www.menupix.com/menudirectory/menu.php?id="+menu_id, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'), headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'})
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
    content = requests.get("http://menus.singleplatform.co/storefront/menus/"+ restaurant_name +".js?callback=menuApi.defaultApiCallResponseHandler&ref=&current_announcement=1&photos=1&apiKey=k47dex17opfs7y7nae9a6p8o0", proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'), headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'})
    return content.content

def parse_into_xml_string(xml):

    """ Parses mal formed string into a xml doc string """

    xml_first = xml[39:]
    xml_string = xml_first[:xml_first.find("</storefront>") + 13]
    return xml_string
                                                                               
def parse_menu(xml_string, rest_id):
    """ Parses xml from javascript request.  
    Stores menu name, section_name, section_desc, item_name, 
    item_desc, price_title, price_value, addon_title, addon_value. 
    """
    root = ET.fromstring(xml_string)
    cover_photo = root.findall("./images/cover_photo/loc")
    for cp in cover_photo: 
        cover_img = RestaurantCoverImage()
        cover_img.cover_photo = cp.text.strip()
        cover_img.restaurant_id = rest_id 
        session.add(cover_img)
        session.commit()
        print cover_img.cover_photo
    images = root.findall("./images/image/loc")
    for img in images:
        rest_img = RestaurantImages()
        rest_img.photos = img.text.strip()
        rest_img.restaurant_id = rest_id 
        session.add(rest_img)
        session.commit()
        print rest_img.photos
    for menus in root:
        for menu in menus:
            for m in menu.iterchildren(reversed=True):
                if m.tag == "title" and len(m.text.strip()) > 0:
                    _m = Menu()
                    print "\n"
                    _m.name = m.text.strip()
                    _m.restaurant_id = rest_id
                    session.add(_m)
                    session.commit() 
                    print _m.name 
                    print "-----------------------------------------"
                for sections in m:
                    for section in sections.iterchildren(reversed=True):
                        if section.tag == "section_name":
                            print "\n"
                            menu_t = [e.text for e in section.getparent().getparent().getparent() if e.tag == "title"]
                            menu_query = session.query(Menu).filter_by(name=menu_t[0], restaurant_id=rest_id).first()
                            sn = section.text.strip()
                            sd = section.getprevious().getprevious().text.strip()
                            _section = Section()
                            _section.name = sn
                            _section.menu_id = menu_query.id
                            _section.restaurant_id = rest_id
                            if not sd.isdigit():
                                _section.description = sd 
                            session.add(_section)
                            session.commit()
                            print _section.name, ":@ ", _section.description
                            print "\n"
                        for menu_items in section:
                            for menu_item in menu_items:
                                if menu_item.tag == "item_title":
                                    print "\n"
                                    menu_t = [e.text for e in menu_item.getparent().getparent().getparent().getparent().getparent() if e.tag == "title"]
                                    menu_query = session.query(Menu).filter_by(name=menu_t[0], restaurant_id=rest_id).first()
                                    menu_i = [e.text for e in menu_item.getparent().getparent().getparent() if e.tag == "section_name"]
                                    section_query = session.query(Section).filter_by(name=menu_i[0], menu_id=menu_query.id, restaurant_id=rest_id).first()
                                    mi = menu_item.text.strip()
                                    md = menu_item.getprevious().getprevious().text.strip()
                                    _mi = MenuItem()
                                    _mi.name = mi
                                    _mi.menu_id = menu_query.id 
                                    _mi.section_id = section_query.id 
                                    _mi.restaurant_id = rest_id
                                    if not md.isdigit():
                                        _mi.description = md
                                    session.add(_mi)
                                    session.commit()
                                    print _mi.name, " $$ ", _mi.description
                                for menu_item_prices in menu_item:
                                    for menu_item_price in menu_item_prices.iterchildren(reversed=True):#.iterchildren(reversed=True)
                                        if menu_item_price.tag == "price_value":
                                            menu_t = [e.text for e in menu_item_price.getparent().getparent().getparent().getparent().getparent().getparent().getparent() if e.tag == "title"]
                                            menu_query = session.query(Menu).filter_by(name=menu_t[0], restaurant_id=rest_id).first()
                                            menu_i = [e.text for e in menu_item_price.getparent().getparent().getparent().getparent().getparent() if e.tag == "section_name"]
                                            section_query = session.query(Section).filter_by(name=menu_i[0], menu_id=menu_query.id, restaurant_id=rest_id).first()
                                            item_t = [e.text for e in menu_item_price.getparent().getparent().getparent() if e.tag == "item_title"]
                                            item_query = session.query(MenuItem).filter_by(name=item_t[0], restaurant_id=rest_id, menu_id=menu_query.id, section_id=section_query.id).first() 
                                            mip = menu_item_price.text.strip()
                                            mipt = menu_item_price.getprevious().text.strip()
                                            ip = ItemPrice()
                                            ip.price_value = mip 
                                            ip.menu_id = menu_query.id
                                            ip.section_id = section_query.id
                                            ip.menu_item_id = item_query.id
                                            ip.restaurant_id = rest_id 
                                            if not mipt.isdigit():
                                                ip.price_title = mipt
                                            session.add(ip)
                                            session.commit()
                                            print ip.price_title, "** " ,ip.price_value,
                                            print "\n"
                                for menu_item_addons in menu_item:
                                    for menu_item_addon in menu_item_addons.iterchildren(reversed=True):
                                        if menu_item_addon.tag == "addon_title":
                                            menu_t = [e.text for e in menu_item_addon.getparent().getparent().getparent().getparent().getparent().getparent().getparent() if e.tag == "title"]
                                            menu_query = session.query(Menu).filter_by(name=menu_t[0], restaurant_id=rest_id).first()
                                            menu_i = [e.text for e in menu_item_addon.getparent().getparent().getparent().getparent().getparent() if e.tag == "section_name"]
                                            section_query = session.query(Section).filter_by(name=menu_i[0], menu_id=menu_query.id, restaurant_id=rest_id).first()
                                            item_t = [e.text for e in menu_item_addon.getparent().getparent().getparent() if e.tag == "item_title"]
                                            item_query = session.query(MenuItem).filter_by(name=item_t[0], restaurant_id=rest_id, menu_id=menu_query.id, section_id=section_query.id).first()
                                            miat = menu_item_addon.text.strip()
                                            ia = ItemAddon()
                                            ia.addon_title = miat
                                            ia.menu_id = menu_query.id
                                            ia.section_id = section_query.id
                                            ia.menu_item_id = item_query.id
                                            ia.rest_id = rest_id
                                            try:
                                                miatd = menu_item_addon.getnext().text.strip()
                                                print "MIATD: ", miatd
                                                ia.addon_value = miatd 
                                            except AttributeError:
                                                print "NO ADDON VALUE"
                                            finally:
                                                session.add(ia)
                                                session.commit()
                                                print ia.addon_title, "$$ ", ia.addon_value
               

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
                parse_menu(xml_string, rest.id)
                counter_menu += 1
            print "number of menu's scraped: ", counter_menu

if __name__ == "__main__":
    t0 = time.time()
    pop_menu_items()
    whats_the_ip()
    end = (time.time() - t0)
    print end, ": in seconds", "  ", end/60, ": in minutes"