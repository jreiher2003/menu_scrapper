import os
import datetime
from collections import OrderedDict
import requests 
from bs4 import BeautifulSoup as bs
from bs4 import Comment 
from pprint import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import State, County, City, MetroAssoc, MetroArea, RestaurantLinks

engine = create_engine('sqlite:///my_menu.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
menu_pix = "http://www.menupix.com"
headers = {'user_agent': user_agent, "referer": menu_pix}

def connect_states():
    """
    Connects to menupix with user agent and referer set in requests object.
    """
    return requests.get(menu_pix, headers)

def grab_states(content):
    """
    scrapes front page of menupix.com and grabs lower case state names and puts them in 
    a list for later use.  
    """
    soup = bs(content.content, "html.parser")
    links = soup.find_all("a")
    states = []
    for l in links[28:78]:
        states.append(l['href'].rsplit("/",2)[1].strip())
    states.append('dc')
    return sorted(states)

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
        r = requests.get(state1.state_link, headers)
        soup = bs(r.content, "html.parser")
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
                    metro_name = session.query(MetroAssoc).filter_by(state_id=state1.id, metro_link=l.find('a')['href'].strip()).one()
                    city1 = City(name=metro_name.name, city_link=metro_name.metro_link, metro_area=True, state_id=state1.id, county_id=county1.id)
                    session.add(city1)
                else:
                    city1 = City(name=l.find('a').get_text().strip(), city_link=l.find('a')['href'].strip(),metro_area=False, state_id=state1.id, county_id=county1.id)
                    session.add(city1)
            session.commit()

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
    dc = City(name="Washington, D.C.", city_link="http://www.menupix.com/dc", metro_area=True, state_id=9, county_id=dc_county.id)
    session.add(dc)
    session.commit() 
    del_city = session.query(City).filter_by(name="Fort Myer", metro_area=False).one()
    session.delete(del_city)
    session.commit()
    change = session.query(City).filter_by(city_link="http://www.menupix.com/dc", metro_area=False).all()
    for i in change:
        if i.name == "Alexandria":
            i.city_link = "http://www.menupix.com/dc/n/504/Alexandria-restaurants"
        if i.name == "Arlington":
            i.city_link = "http://www.menupix.com/dc/n/510/Arlington-restaurants"
        if i.name == "Bethesda":
            i.city_link = "http://www.menupix.com/dc/n/516/Bethesda-restaurants"
        if i.name == "Chevy Chase":
            i.city_link = "http://www.menupix.com/dc/n/525/Chevy-Chase-restaurants"
        session.add(i)
        session.commit()

def change_sanluisobispo():
    change = session.query(City).filter_by(city_link="http://www.menupix.com/sanlouisobispo").all()
    for i in change:
        i.name = "San Luis Obispo"
        i.metro_area = True
        i.city_link = "http://www.menupix.com/sanluisobispo"
        session.add(i)
        session.commit() 

def change_missouri_kc():
    change = session.query(City).filter_by(city_link="http://www.menupix.com/kansascity", metro_area=0, state_id=26).all()
    for i in change: 
        if i.name == "Blue Springs":
            i.city_link = "http://www.menupix.com/kansascity/n/25110/Blue-Springs-restaurants"
        if i.name == "Buckner":
            i.city_link = "http://www.menupix.com/kansascity/n/25111/Buckner-restaurants"
        if i.name == "Excelsior Springs":
            i.city_link = "http://www.menupix.com/kansascity/n/25101/Excelsior-Springs-restaurants"
        if i.name == "Gladstone":
            i.city_link = "http://www.menupix.com/kansascity/n/25102/Gladstone-restaurants"
        if i.name == "Grandview":
            i.city_link = "http://www.menupix.com/kansascity/n/25113/Grandview-restaurants"
        if i.name == "Greenwood":
            i.city_link = "http://www.menupix.com/kansascity/n/25114/Greenwood-restaurants"
        if i.name == "Holt":
            i.city_link = "http://www.menupix.com/kansascity/n/25103/Holt-restaurants"
        if i.name == "Independence":
            i.city_link = "http://www.menupix.com/kansascity/n/25115/Independence-restaurants"
        if i.name == "Kansas City":
            i.city_link = "http://www.menupix.com/kansascity/n/25104/Kansas-City-restaurants"
        if i.name == "Kearney":
            i.city_link = "http://www.menupix.com/kansascity/n/25105/Kearney-restaurants"
        if i.name == "Lake Lotawana":
            i.city_link = "http://www.menupix.com/kansascity/n/25116/Lake-Lotawana-restaurants"
        if i.name == "Lees Summit":
            i.city_link = "http://www.menupix.com/kansascity/n/25117/Lees-Summit-restaurants"
        if i.name == "Liberty":
            i.city_link = "http://www.menupix.com/kansascity/n/25106/Liberty-restaurants"
        if i.name == "Lone Jack":
            i.city_link = "http://www.menupix.com/kansascity/n/25118/Lone-Jack-restaurants"
        if i.name == "North Kansas City":
            i.city_link = "http://www.menupix.com/kansascity/n/25107/North-Kansas-City-restaurants"
        if i.name == "Oak Grove":
            i.city_link = "http://www.menupix.com/kansascity/n/25119/Oak-Grove-restaurants"
        if i.name == "Pleasant Valley":
            i.city_link = "http://www.menupix.com/kansascity/n/25108/Pleasant-Valley-restaurants"
        if i.name == "Raytown":
            i.city_link = "http://www.menupix.com/kansascity/n/25120/Raytown-restaurants"
        if i.name == "Smithville":
            i.city_link = "http://www.menupix.com/kansascity/n/25109/Smithville-restaurants"
        if i.name == "Sugar Creek":
            i.city_link = "http://www.menupix.com/kansascity/n/25121/Sugar-Creek-restaurants"
        session.add(i)
        session.commit()

def change_mississipi():
    change = session.query(City).filter_by(city_link="http://www.menupix.com/memphis", state_id=25).all()
    for c in change:
        if c.name == "Hernando":
            c.city_link = "http://www.menupix.com/memphis/n/24301/Hernando-restaurants"
        if c.name == "Horn Lake":
            c.city_link = "http://www.menupix.com/memphis/n/24302/Horn-Lake-restaurants"
        if c.name == "Lake Cormorant":
            c.city_link = "http://www.menupix.com/memphis/n/24303/Lake-Cormorant-restaurants"
        if c.name == "Nesbit":
            c.city_link = "http://www.menupix.com/memphis/n/24304/Nesbit-restaurants"
        if c.name == "Olive Branch":
            c.city_link = "http://www.menupix.com/memphis/n/24305/Olive-Branch-restaurants"
        if c.name == "Southaven":
            c.city_link = "http://www.menupix.com/memphis/n/24306/Southaven-restaurants"
        if c.name == "Walls":
            c.city_link = "http://www.menupix.com/memphis/n/24307/Walls-restaurants"
        session.add(c)
        session.commit()

def change_portland():
    del_county = session.query(County).filter_by(name="King County", state_id=38).one()
    session.delete(del_county)
    session.commit()
    change_county = session.query(City).filter_by(name="Eugene").all()
    for i in change_county:
        i.county_id = 2215
        session.add(i)
        session.commit()

def change_washington():
    change = session.query(City).filter_by(city_link="http://www.menupix.com/portland", metro_area=False, state_id=48).all()
    for i in change:
        if i.name == "Amboy":
            i.city_link = "http://www.menupix.com/portland/n/9031/Amboy-restaurants"
        if i.name == "Battle Ground":
            i.city_link = "http://www.menupix.com/portland/n/9032/Battle-Ground-restaurants"
        if i.name == "Brush Prairie":
            i.city_link = "http://www.menupix.com/portland/n/9033/Brush-Prairie-restaurants"
        if i.name == "Camas":
            i.city_link = "http://www.menupix.com/portland/n/9034/Camas-restaurants"
        if i.name == "La Center":
            i.city_link = "http://www.menupix.com/portland/n/9035/La-Center-restaurants"
        if i.name == "Ridgefield":
            i.city_link = "http://www.menupix.com/portland/n/9036/Ridgefield-restaurants"
        if i.name == "Vancouver":
            i.city_link = "http://www.menupix.com/portland/n/9017/Vancouver-restaurants"
        if i.name == "Washougal":
            i.city_link = "http://www.menupix.com/portland/n/9037/Washougal-restaurants"
        if i.name == "Yacolt":
            i.city_link = "http://www.menupix.com/portland/n/9038/Yacolt-restaurants"
        session.add(i)
        session.commit()


def pop_metro_area():
    #not "Hernando","Horn Lake", "Lake Cormorant", "Nesbit", "Olive Branch", "Southaven", "Walls" when state id == 43 or tenn ^ these cities are in Miss.
    exclude_miss_cities_called_memphis_metro = ["Hernando","Horn Lake", "Lake Cormorant", "Nesbit", "Olive Branch", "Southaven", "Walls"]
    exclude_dc_cities_not_in_dc = ["Alexandria", "Arlington", "Bethesda", "Chevy Chase"]
    exclude_not_portland_cities = ["Amboy", "Battle Ground", "Brush Prairie", "Camas", "La Center", "Ridgefield", "Vancouver", "Washougal", "Yacolt"]
    exclude_not_kansas_kc_cities = ["Blue Springs","Buckner","Excelsior Springs","Gladstone","Grandview","Greenwood","Holt","Independence","Kearney","Lake Lotawana","Lees Summit","Liberty","Lone Jack","North Kansas City","Oak Grove","Pleasant Valley","Raytown","Smithville","Sugar Creek"]
    metro = session.query(City).filter_by(metro_area=True).all()
    metro_city = []
    for m in metro:
        metro_city.append(m.city_link)
    metro_set = list(set(metro_city))
    for link in metro_set:
        r = requests.get(link)
        soup = bs(r.content, "html.parser")
        div_start = soup.find("ul", {"class": "homepage_ul"})
        for l in div_start.find_all(True, {'class': ['short_hood_class','long_hood_class']}):
            for a in l.find_all("a"):
                neighborhood_name = a.get_text().split("(")[0].strip() 
                metro_rest_link = a["href"].strip()
                city = session.query(MetroAssoc).filter_by(metro_link=link).one()
                county = session.query(City).filter_by(name=city.name,state_id=city.state_id).distinct(City.name).first()
                if county.state_id == 43 and link == "http://www.menupix.com/memphis":
                    if neighborhood_name not in exclude_miss_cities_called_memphis_metro:
                        print "########################################### memphis tenn bug fix"
                        print "city: ", city.name, city.metro_link, " county: ",county.name, county.state_id, county.county_id, county.city_link, "neighborhood_name: ", neighborhood_name, "metro_rest_link: ", metro_rest_link
                        mm = MetroArea(city_name=county.name,neighborhood_name=neighborhood_name,metro_link=metro_rest_link,state_id=county.state_id,county_id=county.county_id,city_id=county.id)
                        session.add(mm)
                elif county.state_id == 9 and link == "http://www.menupix.com/dc":
                    if neighborhood_name not in exclude_dc_cities_not_in_dc:
                        print "########################################### dc exclude non dc cities"
                        print "city: ", city.name, city.metro_link, " county: ",county.name, county.state_id, county.county_id, county.city_link, "neighborhood_name: ", neighborhood_name, "metro_rest_link: ", metro_rest_link
                        mm = MetroArea(city_name=county.name,neighborhood_name=neighborhood_name,metro_link=metro_rest_link,state_id=county.state_id,county_id=county.county_id,city_id=county.id)
                        session.add(mm)
                elif county.state_id == 38 and link == "http://www.menupix.com/portland":
                    if neighborhood_name not in exclude_not_portland_cities:
                        print "########################################### dc exclude non portland cities"
                        print "city: ", city.name, city.metro_link, " county: ",county.name, county.state_id, county.county_id, county.city_link, "neighborhood_name: ", neighborhood_name, "metro_rest_link: ", metro_rest_link
                        mm = MetroArea(city_name=county.name,neighborhood_name=neighborhood_name,metro_link=metro_rest_link,state_id=county.state_id,county_id=county.county_id,city_id=county.id)
                        session.add(mm)
                elif county.state_id == 17 and link == "http://www.menupix.com/kansascity":
                    if neighborhood_name not in exclude_not_kansas_kc_cities:
                        if not metro_rest_link == "http://www.menupix.com/kansascity/n/25104/Kansas-City-restaurants": # missouri kc:
                            if metro_rest_link == "http://www.menupix.com/kansascity/n/16103/Kansas-City-restaurants":
                                if neighborhood_name == "Kansas City":
                                    neighborhood_name = "Kansas City1"
                            print "########################################### kansas city kansas"
                            print "city: ", city.name, city.metro_link, " county: ",county.name, county.state_id, county.county_id, county.city_link, "neighborhood_name: ", neighborhood_name, "metro_rest_link: ", metro_rest_link
                            mm = MetroArea(city_name=county.name,neighborhood_name=neighborhood_name,metro_link=metro_rest_link,state_id=county.state_id,county_id=county.county_id,city_id=county.id)
                            session.add(mm)
                            session.commit()

                else:
                    print "########################################### everything else"
                    print "city: ", city.name, city.metro_link, " county: ",county.name, county.state_id, county.county_id, county.city_link, "neighborhood_name: ", neighborhood_name, "metro_rest_link: ", metro_rest_link
                    mm = MetroArea(city_name=county.name,neighborhood_name=neighborhood_name,metro_link=metro_rest_link,state_id=county.state_id,county_id=county.county_id,city_id=county.id)
                    session.add(mm)
        session.commit()

def test_table_up_to_pop_metro_area():
    metro = session.query(City).filter_by(metro_area=False).all()
    metro_city = []
    for m in metro:
        metro_city.append(m.city_link)
    print len(metro_city), "metro_area length: 17050"
    metro_set = set(metro_city)
    print len(metro_set), " :remove dups"
    import collections 
    dups = [item for item, count in collections.Counter(metro_city).items() if count > 1]
    print dups, ": should be empty" 
    back_metro = list(metro_set)
    print any(i in dups for i in back_metro)
    back_mm = [x for x in back_metro if x not in dups]
    print len(back_mm)
    print any(i in dups for i in back_mm)
    print "all booleans should be false"
    print "#############################################"
    print "#############################################"
    metro1 = session.query(MetroArea).all()
    metro_city1 = []
    for m in metro1:
        metro_city1.append(m.metro_link)
    print len(metro_city1), "metro_area length: 4809"
    metro_set1 = set(metro_city1)
    print len(metro_set1), " :remove dups"
    import collections 
    dups1 = [item for item, count in collections.Counter(metro_city1).items() if count > 1]
    print dups1, ": should be empty"
    back_metro1 = list(metro_set1)
    print any(i in dups1 for i in back_metro1)
    back_mm1 = [x for x in back_metro1 if x not in dups1]
    print len(back_mm1)
    print any(i in dups1 for i in back_mm1)
    print "all booleans should be false"

def check_for_dup_rest_links():
    """
    Query City and MetroArea put all links in respected lists. Check if dups
    exist from one list to another.  
    """
    metro_links = []
    metro_area = session.query(MetroArea).all()
    for m in metro_area:
        metro_links.append(m.metro_link)
    city_links = []
    city = session.query(City).filter_by(metro_area=False).all()
    for c in city:
        city_links.append(c.city_link)
    print len(metro_links)
    print len(city_links)
    print any(i in metro_links for i in city_links)
    print sorted([x for x in metro_links if x in city_links])

def grab_restaurant_links_city():
    import math
    import re
    city = session.query(City).filter_by(metro_area=False,state_id=2).all()
    for c in city:
        r = requests.get(c.city_link)
        soup = bs(r.content, "html.parser")
        div_start = soup.find("div", {"id": "listings_container_div"})
        try:
            total = div_start.find("div", {"class": "results_count"})
        
            total_restaurants = int(total.get_text().split()[-2:-1][0])
            print "total_restaurants: ", total_restaurants
            c.r_total = total_restaurants
            session.add(c)
            session.commit()
            pages = int(math.ceil(total_restaurants/50.)) 
            print "totals: ", total_restaurants, "pages: ",pages
            if pages > 1: # checks if city restaruant page has more than one page
                for i in range(pages):
                    print i
                    r = requests.get(c.city_link + "/page_%s" % str(i))
                    print "url: ",r.url
                    print "################################################"
                    soup = bs(r.content, "html.parser")
                    div_start = soup.find("div", {"id": "listings_container_div"})
                    uls = div_start.find_all("ul", {"id": "listings_ul"})
                    
                    for links in uls:
                        lis = links.find_all("li")
                        for thumbnail in lis:

                            city_rest = RestaurantLinks(city_name=c.name,neighborhood_name=c.name,state_id=c.state_id,county_id=c.county_id, city_id=c.id)
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
                r = requests.get(c.city_link)
                print "url: ",r.url
                print "################################################"
                soup = bs(r.content, "html.parser")
                div_start = soup.find("div", {"id": "listings_container_div"})
                uls = div_start.find_all("ul", {"id": "listings_ul"})
                
                for links in uls:
                    lis = links.find_all("li")
                    for thumbnail in lis:
                        city_rest = RestaurantLinks(city_name=c.name,neighborhood_name=c.name,state_id=c.state_id,county_id=c.county_id, city_id=c.id)
                        img = thumbnail.div.find_all("img")
                        if img:
                            print img[0]['src']
                            city_rest.thumbnail_img = img[0]['src']
                        info = thumbnail.find_all("div", {"class":"listings_row1"})
                        for i in info:
                            rest_link = i.find("a")["href"]
                            name = i.find("a").get_text()
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
            pass

def grab_restaurant_links_metro():
    import math
    import re
    metro = session.query(MetroArea).filter_by(state_id=2).all()
    for m in metro:
        print m.metro_link
        r = requests.get(m.metro_link)
        soup = bs(r.content, "html.parser")
        div_start = soup.find("div", {"id": "listings_container_div"})
        try:
            total = div_start.find("div", {"class": "results_count"})
            total_restaurants = int(total.get_text().split()[-2:-1][0])
            print "total_restaurants: ", total_restaurants
            m.r_total = total_restaurants
            session.add(m)
            session.commit()
            pages = int(math.ceil(total_restaurants/50.)) 
            print "totals: ", total_restaurants, "pages: ",pages
            if pages > 1: # checks if city restaruant page has more than one page
                for i in range(pages):
                    print i
                    r = requests.get(m.metro_link + "/page_%s" % str(i))
                    print "if url: ",r.url
                    print "################################################"
                    soup = bs(r.content, "html.parser")
                    div_start = soup.find("div", {"id": "listings_container_div"})
                    uls = div_start.find_all("ul", {"id": "listings_ul"})
                    
                    for links in uls:
                        lis = links.find_all("li")
                        for thumbnail in lis:
                            print m.city_name,m.neighborhood_name,m.state_id,m.county_id,m.city_id,m.id

                            metro_rest = RestaurantLinks(city_name=m.city_name,neighborhood_name=m.neighborhood_name,state_id=m.state_id,county_id=m.county_id, city_id=m.city_id, metro_area_id=m.id)
           
                            img = thumbnail.div.find_all("img")
                            if img:
                                print img[0]['src']
                                metro_rest.thumbnail_img = img[0]['src']
                            info = thumbnail.find_all("div", {"class":"listings_row1"})
                            for i in info:
                                print i.find("a")["href"]
                                print i.find("a").get_text()
                                metro_rest.rest_link = i.find("a")["href"]
                                metro_rest.rest_name = i.find("a").get_text()
                            menu_available = thumbnail.find_all("div", {"class":"lighten"})
                            for mu in menu_available:
                                m_a = mu.get_text().encode('utf-8').split('\xe2\x80\xa2')[::-1][0].strip()
                                if m_a == "Menu Available":
                                    print m_a, "menu Available"
                                    metro_rest.menu_available = True
                                else:
                                    print "no menu"
                                    metro_rest.menu_available = False 
           
                            if metro_rest.rest_name is None:
                                pass
                            else:
                                session.add(metro_rest)
                                session.commit()
            
                   
            else:
                r = requests.get(m.metro_link)
                print "else url: ",r.url
                print "################################################"
                soup = bs(r.content, "html.parser")
                div_start = soup.find("div", {"id": "listings_container_div"})
                uls = div_start.find_all("ul", {"id": "listings_ul"})
                for links in uls:
                    lis = links.find_all("li")
                    for thumbnail in lis:
                        print m.city_name,m.neighborhood_name,m.state_id,m.county_id,m.city_id,m.id
                        metro_rest = RestaurantLinks(city_name=m.city_name,neighborhood_name=m.neighborhood_name,state_id=m.state_id,county_id=m.county_id, city_id=m.city_id, metro_area_id=m.id)
                        
                        img = thumbnail.div.find_all("img")
                        if img:
                            print img[0]['src']
                            metro_rest.thumbnail_img = img[0]['src']
                        info = thumbnail.find_all("div", {"class":"listings_row1"})
                        for i in info:
                            
                            rest_link = i.find("a")["href"]
                            name = i.find("a").get_text()
                            print rest_link 
                            print name 
                            metro_rest.rest_name = name
                            metro_rest.rest_link = rest_link 
                        menu_available1 = thumbnail.find_all("div", {"class":"lighten"})
                        for mu in menu_available1:
                            m_a = mu.get_text().encode('utf-8').split('\xe2\x80\xa2')[::-1][0].strip()
                            if m_a == "Menu Available":
                                print m_a, "menu Available"
                                metro_rest.menu_available = True
                            else:
                                print "no menu"
                                metro_rest.menu_available = False 

                        if metro_rest.rest_name is None:
                                pass
                        else:
                            session.add(metro_rest)
                            session.commit()
        
        except:
            pass
                
def pop_rest_links():
    rest = session.query(RestaurantLinks).filter_by(state_id=2).all()
    for r in rest:
        print r.rest_link
        print r.rest_link.rsplit("/")[-2:-1][0]

if __name__ == "__main__":
    import time 
    t0 = time.time()
    # content = connect_states() 
    # states_and_metro(content)
    # find_county()
    # pop_dc()
    # change_sanluisobispo()
    # change_missouri_kc()
    # change_mississipi()
    # change_portland()
    # change_washington()
    # pop_metro_area()
    # print "#####################"
    # test_table_up_to_pop_metro_area()
    # check_for_dup_rest_links()
    # grab_restaurant_links_city()
    # grab_restaurant_links_metro()
    pop_rest_links()
    end = (time.time() - t0)
    print end, ": in seconds", "  ", end/60, ": in minutes"

     


  