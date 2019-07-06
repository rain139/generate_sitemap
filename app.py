from generator.ParserLink import ParserLink
from generator.GenerateSitemap import Sitemap


home_page = 'https://ksena.com.ua'

links = ParserLink(home_page).run()

Sitemap(links, home_page).generate()
