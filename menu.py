import os
import datetime
from collections import OrderedDict
import requests 
from bs4 import BeautifulSoup as bs 
from pprint import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import State, County, City, MetroAssoc, MetroArea

engine = create_engine('sqlite:///my_menu.db', echo=True)
# create a Session
Session = sessionmaker(bind=engine)
session = Session()


def connect_states():
    """
    Connects to menupix with user agent and referer set in requests object.
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    menu_pix = "http://www.menupix.com"
    headers = {'user_agent': user_agent, "referer": menu_pix}
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
    other tables.
    """
    soup = bs(content.content, "html.parser")
    div_start = soup.find('div', {'id': 'homepages_bottom_city_links'})
    for l in div_start.find_all(True, {'class': ['hp_bottom_toppadding', 'hp_bottom_indent']}):
        if "hp_bottom_toppadding" in l.attrs['class']:
            name = l.get_text().split("(")[0].strip()
            abbr = l.get_text().split("(")[1][:-1].strip()
            link = l['href'].strip()
            state = State(name=name, abbr=abbr, state_link=link)
            session.add(state)
            session.commit()
            # print name, abbr
        if "hp_bottom_indent" in l.attrs['class']:
            name_m =  l.get_text().strip()
            link_m = l['href'].strip()[:-1]
            metro_a = MetroAssoc(name=name_m, metro_link=link_m, state_id=state.id)
            session.add(metro_a)
            session.commit()


def find_county():
    state_list = session.query(State).all() 
    for state1 in state_list:
        r = requests.get(state1.state_link)
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
                if l.find('a')['href'].strip() in temp:#l.find('a').get_text().strip()
                    metro_name = session.query(MetroAssoc).filter_by(state_id=state1.id, metro_link=l.find('a')['href'].strip()).one()
                    city1 = City(name=metro_name.name, city_link=l.find('a')['href'].strip(), metro_area=True, state_id=state1.id, county_id=county1.id)
                    session.add(city1)
                else:
                    city1 = City(name=l.find('a').get_text().strip(), city_link=l.find('a')['href'].strip(),metro_area=False, state_id=state1.id, county_id=county1.id)
                    session.add(city1)
                session.commit()
   
def pop_metro_area():
    metro = session.query(City).filter_by(metro_area=True).all()
    metro_city = []
    for m in metro:
        metro_city.append(m.city_link)
    metro_set = set(metro_city)
    for link in metro_set:
        r = requests.get(link)
        soup = bs(r.content, "html.parser")
        
        # requests then scrap neighborhoods section name link/ everything else get from metro query
        div_start = soup.find("ul", {"class": "homepage_ul"})
        for l in div_start.find_all("li", {'class': 'long_hood_class'}):
            for a in l.find_all("a"):
                single_c = session.query(City).filter_by(city_link=link).first()
                nn = a.get_text().split("(")[0].strip() 
                ml = a["href"].strip()
                mm = MetroArea(city_name=single_c.name,neighborhood_name=nn,metro_link=ml,state_id=single_c.state_id,county_id=single_c.county_id,city_id=single_c.id)
                session.add(mm)
                session.commit()

if __name__ == "__main__":
    import time 
    t0 = time.time()
    # content = connect_states() 
    # states_and_metro(content)
    # find_county()
    pop_metro_area()
    
   

    end = (time.time() - t0)
    print end, ": in seconds", "  ", end/60, ": in minutes"

     


  