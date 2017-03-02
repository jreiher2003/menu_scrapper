import os
import datetime
from collections import OrderedDict
import requests 
from bs4 import BeautifulSoup as bs 
from pprint import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import State, County, City 

engine = create_engine('sqlite:///my_menu.db', echo=True)
# create a Session
Session = sessionmaker(bind=engine)
session = Session()


def connect_states():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    menu_pix = "http://www.menupix.com"
    headers = {'user_agent': user_agent, "referer": menu_pix}
    return requests.get(menu_pix, headers)

def grab_states(content):
    soup = bs(content.text, "html.parser")
    links = soup.find_all("a")
    states = []
    for l in links[28:78]:
        states.append(l['href'].rsplit("/",2)[1])
    return states 

def put_states_in_db(lst_state_links):
    for link in lst_state_links:
        state = State(name=link)
        session.add(state)
        session.commit()

def state_dic(lst_state):
    states = OrderedDict()
    for state in lst_state:
        states[state] = {}
    return states

def find_county():
    states = {"alabama": []}
    county = {}
    # for k,v in state_dic.iteritems():
        # r = requests.get("http://www.menupix.com/%s" % k)

    r = requests.get("http://www.menupix.com/alabama")
    soup = bs(r.text, "html.parser")
    div_start = soup.find("div", {"id": "homepage_metro_container_div"})
    
    for l in div_start.find_all(True, {'class': ['index_bulletheading', 'index_bulletpoints']}):
        if "index_bulletheading" in l.attrs['class']:
            co = l.find('a').text
            county[co] = []
        if "index_bulletpoints" in l.attrs['class']:
            city = (l.find('a').text, l.find('a')['href'])
            county[co].append(city)
    states["alabama"].append(dict(county))
    return states

def connect_county(state):
    county_links = []
    city_links = []
    county = {}
    r = requests.get("http://www.menupix.com/%s" % state)
    soup = bs(r.text, "html.parser")
    for l in soup.find_all("li", {'class': 'index_bulletheading'}):
        for a in l.find_all("a"):
            county_links.append(a.text)
    div_start = soup.find("div", {"id": "homepage_metro_container_div"})
    for l in div_start.find_all("li", {'class': 'index_bulletpoints'}):
        for a in l.find_all("a"):
            city_links.append((a.text, a["href"]))
    return county_links, city_links

def put_county_in_db(county_links, state):
    state = session.query(State).filter_by(name=state).one()
    print state.id, state.name
    for c in county_links:
        county = County(name=c, state_id=state.id)
        session.add(county) 
        session.commit()

def put_city_in_db(city_links, county, state):
    state = session.query(State).filter_by(name=state).one()
    county = session.query(County).filter_by(name=county, state_id=state.id).one()
    print state.name,state.id, county.id, county.name, county.state_id
    for c in city_links:
        print c[0], c[1]
        # city = City(name=c[0], city_link=c[1], state_id=state.id, county_id=county.id)
        # session.add(city)
        # session.commit()
                

if __name__ == "__main__":
    import time 
    t0 = time.time()
    content = connect_states() 
    state_list = grab_states(content)
    sd = state_dic(state_list)
    pprint(sd)
    # pprint(find_county())
    # put_states_in_db(state_list)
    # for state in state_list:
    #     print state
    #     county_list, city_list = connect_county(state)
    #     # put_county_in_db(county_list,state)
    #     # for c in city_list:
    #     #     print c[0],c[1]
    #     for county in county_list:
    #         put_city_in_db(city_list, county, state)

    end = (time.time() - t0)
    print end, ": in seconds", "  ", end/60, ": in minutes"

     


       
    # providence_list = grab_providence(content)
    # put_prov_in_db(providence_list)
# def grab_providence(content):
#     soup = bs(content.text, "html.parser")
#     links = soup.find_all("a")
#     prov = []
#     for l in links[78:99]:
#         prov.append(l['href'])
#     return prov 

# def put_prov_in_db(lst_prov_links):
#     for link in lst_prov_links:
#         prov = Providence(name=link.rsplit("/",2)[1])
#         session.add(prov)
#         session.commit()