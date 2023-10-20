import sys
import os

# Agrega el directorio actual al PYTHONPATH
sys.path.append( os.getcwd() )

# Agrego mis modulos
try:
    from src.driver import Driver
    from src.similarweb import SimilarWebTopWebsitesTable
except:
    from driver import Driver
    from similarweb import SimilarWebTopWebsitesTable

# Defino la URL base
SIMILARWEB_BASE_URL = 'https://www.similarweb.com/'

# Parametros
delay = 10
skip_driver = False

# Creo el objeto de tipo driver
driver = Driver(browser="chrome")

# Armo la lista de tablas que quiero
tables_list = [
    # Format ('url','alias')
    ('top-websites/', 'top_websites'),
    ('top-websites/arts-and-entertainment/tv-movies-and-streaming/', 'streaming'),
]

# Obtengo la informacion de las webs mas vistas
if skip_driver is False:
    filenames = []
    for table_config in tables_list:
        filenames.append( driver.scrap_url(SIMILARWEB_BASE_URL + table_config[0], table_config[1], delay=delay) )
else:
    filenames = [
        'results/similarweb//html_top_websites.dat',
        'results/similarweb//html_streaming.dat',
    ]

# Muestro la lista de archivos
print(filenames)

# Para cada top, obtengo la lista de dominios
url_list = []
for filename in filenames:

    # Obtengo la lista de paginas mas vistas
    table = SimilarWebTopWebsitesTable(filename=filename)
    table.fetch_rows()
    sub_url_list = table.get_url_list()
    # print(sub_url_list)
    url_list.extend( sub_url_list )

url_list = list(set(url_list))

# Muestro las listas de dominions
print(url_list[0])