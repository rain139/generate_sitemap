import re
from generator.Db import Db
import sys
from generator.Helpers import env, send_telegram
from pymongo import MongoClient
import time


class Sitemap:
    __links = []
    __xml = ''
    __site_home = ''
    __dir_project = ''
    __catalog = {}
    __blog = {}
    __list_page_updated = {}

    def __init__(self, links: list, site_home: str):
        self.__links = links
        self.__site_home = site_home
        self.__dir_project = env('DIR_PROJECT').strip('/')
        self.__set_catalog_products()
        self.__set_blog_articles()
        self.__set_last_updated_seo()

    def __set_catalog_products(self) -> None:
        try:
            cursor = Db().connect().cursor(dictionary=True)
            cursor.execute(
                'SELECT id,CONCAT(purl,".html") `purl`,IFNULL(updated,created) `updated` FROM `tovars` WHERE visible = 1 and deleted = 0')
            tovars = cursor.fetchall()
        except Exception as e:
            send_telegram('Sitemap ' + str(e))
            sys.exit()

        for product in tovars:
            self.__catalog[product['purl'].decode("utf-8")] = {'id': product['id'], 'updated': product['updated']}

        cursor.close()

    def __set_blog_articles(self) -> None:
        try:
            client = MongoClient()
            db = client.ksena
            for article in db.blogArticles.find():
                self.__blog[article['purl'] + '.html'] = article['created']
        except Exception as e:
            send_telegram('Sitemap ' + str(e))

    def generate(self):

        self.__set_header()

        for url in self.__links:
            self.__set_block__url(url, self.__get_priory(url))

        self.__set_bottom()
        try:
            file = open('/' + self.__dir_project + '/sitemap.xml', "w")
            file.write(self.__xml)
        except Exception as e:
            send_telegram('Sitemap ' + str(e))

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
                     '<!-- created with Free Online Sitemap Generator www.xml-sitemaps.com -->\n\n\n'

    def __max_last_update_catalog(self) -> str:
            try:
                cursor = Db().connect().cursor(dictionary=True)
                cursor.execute(
                    'SELECT MAX(IFNULL(updated,created)) `updated` FROM `tovars` WHERE visible = 1 and deleted = 0')
                max_updated = cursor.fetchone()
                return max_updated['updated']
            except Exception as e:
                send_telegram('Sitemap ' + str(e))

    def __set_last_updated_seo(self) -> None:
        try:
            cursor = Db().connect().cursor(dictionary=True)
            cursor.execute(
                'SELECT CONCAT("{site}",IFNULL(url,"")) `url`,`updated` FROM `pages`'.format(site=self.__site_home))
            max_updated = cursor.fetchall()
            for updated in max_updated:
                self.__list_page_updated[updated['url'].strip('/')] = updated['updated']
        except Exception as e:
            send_telegram('Sitemap ' + str(e))

    def __get_last_updated_blog(self) -> str:
        try:
            client = MongoClient()
            db = client.ksena
            res = db.blogArticles.find_one(sort=[("created", -1)])
            return res['created']
        except Exception as e:
            send_telegram('Sitemap ' + str(e))

    def __get_lastmod(self, url: str) -> str:
        date = env('START_DATE',  '2019-07-10 22:00:50')

        url = url.strip('/')
        purl = url.split('/')[len(url.split('/')) - 1]

        if url == 'https://ksena.com.ua/catalog' or url == 'https://ksena.com.ua' \
                or (re.search('page=', url) and re.search('catalog', url)):
            date = self.__max_last_update_catalog()
        elif re.search('catalog', url) and not re.search('.html', url) and len(url.split('/')) > 4:
            date = self.__get_last_updated_categories(purl)
        elif url in self.__list_page_updated:
            date = str(self.__list_page_updated[url])
        elif purl in self.__catalog:
            date = self.__catalog[purl]['updated']
        elif re.search('.html', url) and re.search('/blog', url):

            for key, value in self.__blog.items():
                if re.search(key, url):
                    date = self.__blog[key]
                    del self.__blog[key]
                    break

        elif re.search('/blog', url):
            date = self.__get_last_updated_blog()

        date = str(date)

        if date:
            try:
                select_date = time.strptime(date, "%Y-%m-%d %H:%M:%S")
                min_date = time.strptime(env('START_DATE', '2019-07-10 22:00:50'), "%Y-%m-%d %H:%M:%S")
                if min_date > select_date:
                    date = select_date.replace(' ', 'T')
            except ValueError:
                pass




        try:
            date = date.replace(' ', 'T')
            if re.search('T', date):
                return date + '+00:00'
            else:
                return date + 'T10:04:10+00:00'
        except Exception as e:
            print(url)
            send_telegram('Generate sitemap error {url} {e}'.format(url=url, e=e))
            sys.exit(4)

    def __get_last_updated_categories(self, purl: str) -> str:
        try:
            cursor = Db().connect().cursor(dictionary=True)
            cursor.execute(
                'SELECT MAX(IFNULL(`t`.`updated`,`t`.`created`)) `updated`,`c`.`lid` FROM `category` `c` '
                'LEFT JOIN tovar_categories `tc` ON `tc`.`Id_categor` = `c`.`lid` '
                'LEFT JOIN `tovars` `t` ON `t`.`lid` = `tc`.`lid_tovar` '
                'WHERE `c`.`purl` = %s', [purl])
            max_updated = cursor.fetchone()

            if not max_updated['updated']:
                cursor.execute(
                    'SELECT MAX(IFNULL(`t`.`updated`,`t`.`created`)) `updated` FROM `category` `c` '
                    'LEFT JOIN tovar_categories `tc` ON `tc`.`Id_categor` = `c`.`lid` '
                    'LEFT JOIN `tovars` `t` ON `t`.`lid` = `tc`.`lid_tovar` '
                    'WHERE `c`.`parent` = %s', [max_updated['lid']])
                max_updated = cursor.fetchone()

            return max_updated['updated']
        except Exception as e:
            send_telegram('Sitemap ' + str(e))

    def __set_block__url(self, url: str, priory: float) -> None:
        date = self.__get_lastmod(url)

        self.__xml += '<url>\n' \
                      '   <loc>{site}</loc>\n' \
                      '   <lastmod>{date}</lastmod>\n' \
                      '   <priority>{priory}</priority>\n' \
                      '</url>\n'.format(site=url, date=date, priory=priory)

    def __set_bottom(self) -> None:
        self.__xml += '\n\n</urlset>'