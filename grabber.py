import requests
from lxml import html
import json

DOMAIN_SLUG = 'https://www.legalstart.fr%s'


class Grabber():
    def __init__(self, input_file):
        self.thumbscraper_input_file = input_file
        self.load_input_file()

    def load_input_file(self):
        ''' Load JSON cotent in to an instance variable '''
        try:
            with open(self.thumbscraper_input_file) as thumbscraper_input_file:
                self.thumbscraper_input = json.loads(thumbscraper_input_file.read())
        except Exception as e:
            print 'Couldn\'t read input file : ' + str(e)

    def scrap_content(self, page_url_slug):
        ''' Function to scrap page contents'''

        url         = DOMAIN_SLUG % page_url_slug
        try:
            response    = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                raise Exception('Couldn\'t fetch the contents of URL: %s' % url)
        except Exception as e:
            print 'Fetch failed : ' + str(e)

    def grab(self, page_name='0', page_url_slug=''):
        ''' Main method will be called recursively until find a tamperred page '''

        thumb_data   = self.thumbscraper_input.get(page_name, {})
        page_content = self.scrap_content(page_url_slug)
        next_page    = thumb_data.get('next_page_expected')
        next_page_url_slug = self.get_next_page_url_slug(page_content, thumb_data)

        if self.does_exceptation_matches(thumb_data, page_content):
            print 'Moving to page %s' % next_page_url_slug
            self.grab(next_page, next_page_url_slug)
        else:            
            print 'ALERT - Can\'t move to page %s : page %s  has been malevolently tampered with!!' % (next_page_url_slug, page_url_slug)

    def does_exceptation_matches(self, thumb_data, page_content):
        return thumb_data.get('xpath_test_result') == self.query_xpath(page_content, thumb_data.get('xpath_test_query'))

    def query_xpath(self, page_content, query):
        tree = html.fromstring(page_content)
        return tree.xpath(query)

    def get_next_page_url_slug(self, page_content, thumb_data):
        anchor_tag = self.query_xpath(page_content, thumb_data.get('xpath_button_to_click'))[0]
        return anchor_tag.attrib.get('href')

if __name__ == '__main__':
    grabber = Grabber('thumbscraper_input.json')
    grabber.grab()