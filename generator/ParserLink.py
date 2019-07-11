from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import sys


class ParserLink:
    __urls = []
    __urls_tmp = []

    __site_url_home = None

    def __init__(self, site_url: str):
        self.__site_url_home = site_url.strip('/')

    def run(self) -> list:
        while (True):
            if not self.__handler_html(self.__open_url()):
                break
        return sorted(self.__urls, key=len)

    def __handler_html(self, html) -> bool:
        # source / home / egor / parser / venv / bin / activate & & / usr / bin / python3
        if type(html) is bool:
            return html

        if html:
            try:
                soup = BeautifulSoup(html, features='html.parser')
            except Exception as e:
                return self.__handler_exception(e, '\033[91m html error parse  \033[0m')

            all_tag_a = list(set(soup.findAll('a')))

            for tag in all_tag_a:

                href = str(tag.get('href'))

                if re.search('[a-zA-Z]//|page=|sort=|mailto:|viber:|whatsapp:|modal_class|changeView', href):
                    continue

                if re.search('http|wwww', href) and href.find(self.__site_url_home) == -1:
                    continue

                if href.find(self.__site_url_home) == -1:
                    href = self.__site_url_home + '/' + href.strip('/')

                if not re.search('html', href) and href != 'https://ksena.com.ua':
                    href = href.strip('/') + '/'

                if href not in self.__urls and href not in self.__urls_tmp and href != '/' \
                        and not re.search('(jpg|png|pdf|gif|jpeg|svg|txt|#|None)', href, re.IGNORECASE):
                    self.__urls.append(href)
                    self.__urls_tmp.append(href)

        if self.__urls_tmp:
            return True
        return False

    def __open_url(self):
        if self.__urls and self.__urls_tmp:
            url = self.__urls_tmp.pop()
            try:
                print("url={url} temp_url={url_tmp}".format(url=self.__urls.__len__(), url_tmp=self.__urls_tmp.__len__()))
                return urlopen(url)
            except Exception as e:
                for key,page in enumerate(self.__urls):
                    if page == url:
                        del self.__urls[key]
                        break
                return self.__open_url()

        else:
            try:
                return urlopen(self.__site_url_home)
            except Exception as e:
                self.__handler_exception(e, 'not correct url')
                sys.exit(8)

    def __handler_exception(self, e: Exception, text: str = None) -> bool:
        if text:
            print(text)

        urlopen(
            'https://api.telegram.org/bot740828408:AAHHPyrSCmwy9jBO8uCr76ogd1lW2bWpIyw/sendMessage?chat_id=406873185&text={text}'.format(
                text=str(e))
        )

        if self.__urls_tmp:
            return True
        else:
            return False
