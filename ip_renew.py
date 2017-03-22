import random
from TorCtl import TorCtl
import urllib2
from fake_useragent import UserAgent
 
# user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
# headers={'User-Agent':user_agent}

u_a = ["one", "two", "three", "four"]
def random_user_agent(lst):
    return random.choice(lst)
 
def request(url,headers):
    def _set_urlproxy():
        proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
    _set_urlproxy()
    request=urllib2.Request(url, None, headers)
    return urllib2.urlopen(request).read()
 
def renew_connection():
    conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051, passphrase="finn7797")
    conn.send_signal("NEWNYM")
    conn.close()

ua = UserAgent() 
for i in range(0, 10):
    headers={'User-Agent':ua.random}
    import time
    time.sleep(8)
    renew_connection()
    print request("http://icanhazip.com/", headers)
    print ua.random