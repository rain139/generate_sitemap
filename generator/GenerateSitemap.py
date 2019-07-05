import datetime
import re


class Sitemap:
    __links = []
    __xml = ''
    __site_home = ''

    def __init__(self, links: list, site_home: str):
        self.__links = links
        self.__site_home = site_home

    def generate(self):
        self.__set_header()

        for url in self.__links:
            self.__set_block__url(url,self.__get_priory(url))

        self.__set_bottom()

        file = open('sitemap.xml', "w")
        file.write(self.__xml)

    def __get_priory(self, url: str) -> float:

        if self.__site_home == url.strip('/'):
            return 1

        if url == self.__site_home + '/catalog':
            return 1

        if re.search('/catalog/', url):
            if re.search('.html', url):
                return 0.8
            else:
                return 0.7

        return 0.64

    def __set_header(self):
        self.__xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
                     '<urlset\n' \
                     '      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n' \
                     '      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' \
                     '      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n' \
                     '          http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n' \
                     '<!-- created with Free Online Sitemap Generator www.xml-sitemaps.com -->\n\n\n' \


    def __set_block__url(self, url: str, priory: float)->None:
        today = datetime.datetime.today()
        date = today.strftime("%Y-%m-%d")

        self.__xml +='<url>\n'\
        '   <loc>{site}</loc>\n'\
        '   <lastmod>{date}T12:41:53+00:00</lastmod>\n'\
        '   <priority>{priory}</priority>\n'\
        '</url>\n'.format(site=url, date=date, priory=priory)

    def __set_bottom(self)-> None:
        self.__xml += '\n\n</urlset>'