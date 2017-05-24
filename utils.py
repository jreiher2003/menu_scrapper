from stem import Signal
from stem.control import Controller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
import requests
from bs4 import BeautifulSoup as bs

def renew_ip():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="finn7797")
        controller.signal(Signal.NEWNYM)
        controller.close()

def whats_the_ip():
    r = requests.get("http://ipinfo.io/ip", proxies=dict(http='socks5://127.0.0.1:9050',https='socks5://127.0.0.1:9050'))
    soup = bs(r.content, "html5lib")
    ip = soup.find("body")
    print ip.get_text()
    # rr = requests.get("http://ipinfo.io/ip")
    # soup = bs(rr.content, "html5lib")
    # ipr = soup.find("body")
    # print ipr.get_text()

def get_current_ip(user_agent):
    display = Display(visible=0, size=(800, 800))  
    display.start()
    profile=webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.socks', '127.0.0.1')
    profile.set_preference('network.proxy.socks_port', 9050)
    profile.set_preference('javascript.enabled', True)
    profile.set_preference("general.useragent.override", user_agent)
    
    browser=webdriver.Firefox(profile)
    url = 'http://ipinfo.io/ip'
    browser.get(url)
    try:
        tag = browser.find_element_by_tag_name("body")
        print 'tor ip: {}'.format(tag.text)
    except TimeoutException:
        print "Timed out waiting for page to load"
    finally:
        browser.quit()
        display.stop()
    return 



