from generator.ParserLink import ParserLink
from generator.GenerateSitemap import Sitemap

home_page = 'https://ksena.com.ua'
dir_project = '/home/ksena/public_html'


links = ParserLink(home_page).run()
Sitemap(links, home_page, dir_project).generate()
