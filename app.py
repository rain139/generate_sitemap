from generator.ParserLink import ParserLink
from generator.GenerateSitemap import Sitemap


home_page = "https://ksena.com.ua"

links = ParserLink(home_page).run()
print(links)
import sys
sys.exit(4)
Sitemap(links, home_page).generate()
