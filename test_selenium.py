import unittest
from selenium import webdriver
from pyvirtualdisplay import Display

class SearchText(unittest.TestCase):
    def setUp(self):
        # create a new Firefox session
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()
        self.driver = webdriver.Firefox()
        # navigate to the application home page
        self.driver.get("http://www.google.com/")
 
    def test_search_by_text(self):
        print self.driver.current_url
 
    def tearDown(self):
        # close the browser window
        self.driver.quit()
        self.display.stop()


if __name__ == '__main__':
    unittest.main(verbosity=2)
