"""sudo adduser $USER debian-tor 
to add vagrant to debian-tor group 
*** logout and back in *** 
"""

from bs4 import BeautifulSoup
from TorCtl import TorCtl
from stem import Signal
from stem.control import Controller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display

def script_menu_type_1():
    html1 = open('/vagrant/html_examples/fired_up_pizza_380133687_type_2.html')
    html = html1.read()
    soup = BeautifulSoup(html,"html5lib")
    table_start = soup.find("table")
    try:
        td = table_start.find_all("tr")
        menu_name = [tr.find("strong") for tr in td[0]][1].get_text()
        print menu_name
        top_menu = soup.find("span", {"id":"tab_menus0"}).get_text()
        categories = soup.find_all("span", {"class":"sp_st_section_title"})
        items = soup.find_all("p", {"class":"fn"})
        all_menu_items = soup.find('div', {'id':'sp_panes'})
        for l in all_menu_items.find_all(True, {'class': ['sp_st', 'fn','sp_description','sp_option_li']}):
            if 'sp_st' in l.attrs['class']:
                print "_____ Category _________"
                print l.get_text().strip()
                print "##########################"
                print '\n'
            if 'fn' in l.attrs['class'] and not 'sp_st' in l.attrs['class']:
                print l.get_text().strip()
            if 'sp_option_li' in l.attrs['class']:
                print l.get_text().strip()
            if 'sp_description' in l.attrs['class']:
                print l.get_text().strip()
                print "\n"

    except AttributeError:
        print "didn't find a text menu"

def script_menu_pdf_type_2():
    # this is for if menu has type=2
    import re
    pattern = re.compile(r'Open Menu in a New Window')
    html1 = open('/vagrant/html_examples/fired_up_pizza_380133687_type_2.html')
    html = html1.read()
    soup = BeautifulSoup(html,"html5lib")
    pdf_menu = soup.find('a', text=pattern)
    if pdf_menu is not None:
        print pdf_menu['href']
    else:
        print "no pdf menu found"
        
def menu_pix():
    url = "http://www.menupix.com/menudirectory/menu.php?id=5403824"
    browser.get(url)
    try:
        frame = browser.page_source
        soup = BeautifulSoup(frame,"html5lib")
        table_start = soup.find("table")
        td = table_start.find_all("tr")
        for tr in td[0]:
            print tr.find("strong")
            print "##############################################################################################################"
    except TimeoutException:
        print "Timed out waiting for page to load"
    finally:
        browser.quit()
        display.stop()
    return

def get_current_ip():
    display = Display(visible=0, size=(800, 800))  
    display.start()
    profile=webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.socks', '127.0.0.1')
    profile.set_preference('network.proxy.socks_port', 9050)
    profile.set_preference('javascript.enabled', True)
    profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36")
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

def renew_connection():
    conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051, passphrase="finn7797")
    conn.send_signal("NEWNYM")
    conn.close()

def renew_ip():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        controller.close()

if __name__ == "__main__":
    for i in range(0,10):
        import time
        get_current_ip()
        time.sleep(8)
        renew_ip()
        print "------------------------------------------------------------"
        print "************************************************************"
        print "------------------------------------------------------------"
        # script_menu_type_1()
        # script_menu_pdf_type_2()