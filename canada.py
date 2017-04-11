""" this script gets all canadian restaurants ready for restaurant_links table """
from pprint import pprint
import requests 
from bs4 import BeautifulSoup as bs
from sqlalchemy import create_engine
from sqlalchemy import desc,asc
from sqlalchemy.orm import sessionmaker
from models import State, MetroAssoc, CityMetro

engine = create_engine('sqlite:///my_menu1.db')
Session = sessionmaker(bind=engine)
session = Session()

menu_pix = "http://www.menupix.com"
def connect_states():
    """
    Connects to menupix with user agent and referer set in requests object.
    """
    return requests.get(menu_pix, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))

provinces = ["Ontario","British Columbia","Quebec", "Alberta","Saskatchewan","Nova Scotia","Newfoundland","Manitoba","New Brunswick", "Prince Edward Island", "Yukon"] 
def provinces_cities(content):
    soup = bs(content.content, "lxml")
    div_start = soup.find('div', {'id': 'homepages_bottom_canada_links'})
    for l in div_start.find_all(True, {'class': ['hp_bottom_col1', 'hp_bottom_col2','hp_bottom_col3','hp_bottom_col4','hp_bottom_col5','hp_bottom_col6']}):
        lst = l.find_all('a')
        for i in lst:
            # print i['href'],i.get_text(strip=True),i.get_text(strip=True) in [x[0] for x in provinces]
            if i.get_text(strip=True) in provinces:
                # pass
                if i.get_text(strip=True) == "Ontario":
                    print  i.get_text(strip=True), "ON", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="ON",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "British Columbia":
                    print  i.get_text(strip=True), "BC", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="ON",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "Quebec":
                    print  i.get_text(strip=True), "QC", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="QC",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "Alberta":
                    print  i.get_text(strip=True), "AB", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="AB",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "Saskatchewan":
                    print  i.get_text(strip=True), "SK", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="SK",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "Nova Scotia":
                    print  i.get_text(strip=True), "NS", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="NS",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "Newfoundland":
                    print  i.get_text(strip=True), "NL", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="NL",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "Manitoba":
                    print  i.get_text(strip=True), "MB", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="MB",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "New Brunswick":
                    print  i.get_text(strip=True), "NB", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="NB",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "Prince Edward Island":
                    print  i.get_text(strip=True), "PE", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="PE",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                if i.get_text(strip=True) == "Yukon":
                    print  i.get_text(strip=True), "YT", i['href']
                    prov = State(name=i.get_text(strip=True),abbr="YT",state_link=i['href'])
                    session.add(prov)
                    session.commit()
                print "###########################################"
                
            elif i.get_text(strip=True) not in provinces:
                if i.get_text(strip=True) == "Calgary":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                if i.get_text(strip=True) == "Edmonton":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                if i.get_text(strip=True) == "Montreal":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                if i.get_text(strip=True) == "Ottawa":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                if i.get_text(strip=True) == "Regina":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                if i.get_text(strip=True) == "Saskatoon":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                if i.get_text(strip=True) == "Toronto":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                if i.get_text(strip=True) == "Vancouver":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                if i.get_text(strip=True) == "Victoria":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                if i.get_text(strip=True) == "Winnipeg":
                    print i.get_text(strip=True), i['href']
                    metro = MetroAssoc(name=i.get_text(strip=True), metro_link=i['href'])
                    session.add(metro)
                    session.commit()
                    print '___________________________________________'
    p = State(name="Northwest Territories", abbr="NT")
    n = State(name="Nunavut", abbr="NU")  
    session.add_all([p,n])
    session.commit()

def pop_metro_assoc_canada_with_prov_id():
    m = session.query(MetroAssoc).filter_by(state_id=None).all()
    for prov in m:
        if prov.name == "Calgary":
            prov.state_id = 52
        if prov.name == "Edmonton":
            prov.state_id = 52
        if prov.name == "Montreal":
            prov.state_id = 60
        if prov.name == "Ottawa":
            prov.state_id = 58
        if prov.name == "Regina":
            prov.state_id = 61
        if prov.name == "Saskatoon":
            prov.state_id = 61
        if prov.name == "Toronto":
            prov.state_id = 58
        if prov.name == "Vancouver":
            prov.state_id = 53
        if prov.name == "Victoria":
            prov.state_id = 53
        if prov.name == "Winnipeg":
            prov.state_id = 54 
        session.add(prov)
        session.commit()
             
def pop_city_metro_canada_by_provi():
    state = session.query(State).filter(State.state_link!=None).offset(51).all()
    for s in state:
        r = requests.get(s.state_link, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
        soup = bs(r.content, "lxml")
        div_start = soup.find("ul", {"class": "homepage_ul"})
        for l in div_start.find_all(True, {'class': ['short_hood_class','long_hood_class']}):
            for a in l.find_all("a"):
                city_name = a.get_text().split("(")[0].strip() 
                rest_total1 = a.get_text().split("(")[1].strip()
                rest_total = rest_total1.split(")")[0].strip()
                city_link = a["href"].strip()
                print city_name, rest_total, city_link
                new = CityMetro(city_name=city_name, city_link=city_link, metro_area=False, r_total=rest_total, state_id=s.id)
                session.add(new)
                session.commit()

def pop_city_metro_by_metroassoc():
    metro = session.query(MetroAssoc).offset(266).all()
    for m in metro:
        r = requests.get(m.metro_link, proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
        soup = bs(r.content, "lxml")
        div_start = soup.find("ul", {"class": "homepage_ul"})
        for l in div_start.find_all(True, {'class': ['short_hood_class','long_hood_class']}):
            for a in l.find_all("a"):
                city_neighborhood = a.get_text().split("(")[0].strip() 
                rest_total1 = a.get_text().split("(")[1].strip()
                rest_total = rest_total1.split(")")[0].strip()
                city_link = a["href"].strip()
                print m.name, city_neighborhood, rest_total, city_link,m.state_id
                new = CityMetro(city_name=m.name, neighborhood_name=city_neighborhood, city_link=city_link, metro_area=False, r_total=rest_total, state_id=m.state_id)
                session.add(new)
                session.commit()

if __name__ == "__main__":
    import time 
    t0 = time.time()
    # content = connect_states()
    # provinces_cities(content)
    # pop_metro_assoc_canada_with_prov_id()
    # pop_city_metro_canada_by_provi()
    pop_city_metro_by_metroassoc()
    end = (time.time() - t0)
    print end, ": in seconds", "  ", end/60, ": in minutes"