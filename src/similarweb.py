from bs4 import BeautifulSoup
try:
    from src.driver import Driver
    from src.db import Database
except:
    from driver import Driver
    from db import Database

# Defino la URL base
SIMILARWEB_BASE_URL = 'https://www.similarweb.com/'

def get_similarweb_table(filename=''):

    # Abro el archivo
    with open(filename, 'r', encoding="utf-8") as file:
        page = BeautifulSoup(file, 'html.parser')

    # Encuentro las filas de la tabla
    rows = page.find_all('tr', class_='top-table__row')

    # Lista para almacenar los diccionarios de datos
    data_list = []

    # Para cada fila obtengo los datos
    for row in rows:
        row_dicc = {
            'rank': row.find('span', class_='tw-table__rank').text,
            'domain': row.find('span', class_='tw-table__domain').text,
            'category': row.find('a', class_='tw-table__category').text,
            'avg_visit_duration': row.find('span', class_='tw-table__avg-visit-duration').text,
            'pages_per_visit': row.find('span', class_='tw-table__pages-per-visit').text,
            'bounce_rate': row.find('span', class_='tw-table__bounce-rate').text,
        }

        data_list.append(row_dicc)  # Agregar el diccionario a la lista

    return data_list

def get_similarweb_url_list_fromtable(data_list):

    url_list = []
    for data in data_list:
        url_list.append(
            (SIMILARWEB_BASE_URL + f"website/{data['domain']}/", data['domain'].replace('.','_'))
        )

    return url_list

def similarweb_main():

    # # Creo el objeto de tipo driver
    # driver = Driver(browser="chrome")

    # # Obtengo la informacion de las webs mas vistas
    # filename = driver.scrap_url(SIMILARWEB_BASE_URL + "top-websites/", 'top_websites', delay=20)

    # Obtengo la lista de paginas mas vistas
    try:
        data_list = get_similarweb_table(filename=filename)
    except:
        data_list = get_similarweb_table(filename='html_top_websites.dat')

    url_list = get_similarweb_url_list_fromtable(data_list)

    # # Obtengo el codigo HTML para esas paginas
    # driver.scrap_url_list(url_list, delay=20)

    # # Cierro la pagina
    # driver.close_driver()

    # Abro la conexion con la base de datos:
    with Database() as db:

        # Recorro la lista de URLs
        for url in url_list:

            # Armo el nombre del archivo a leer
            filename = f'html_{url[1]}.dat'

            # Obtengo la informacion a partir del contenido HTML
            web_info = SimilarWebWebsite(filename=filename)
            web_info.fetch_data()

            # Muestro el diccionario en pantalla
            print(web_info.to_dicc())

            # Agrego el registro a la tabla
            db.insert_similarweb_record(web_info.to_dicc())

class SimilarWebTopWebsitesTable():
    def __init__(self, domain='top-websites/', filename=None):
        self.base_url = 'https://www.similarweb.com/'
        self.domain = domain
        self.row_data = []

        self.html_content = ''
        self.filename = filename
        if self.filename is not None:
            self.set_html_content_fromfile(filename=filename)

    def set_html_content(self, html_content):
        self.html_content = html_content

    def set_html_content_fromfile(self, filename=None):
        self.filename = filename
        with open(filename, 'r', encoding="utf-8") as file:
            self.html_content = BeautifulSoup(file, 'html.parser')

    def fetch_rows(self):
        # Encuentro las filas de la tabla
        rows = self.html_content.find_all('tr', class_='top-table__row')

        # Lista para almacenar los diccionarios de datos
        self.row_data = []

        # Para cada fila obtengo los datos
        for row in rows:
            row_dicc = {
                'rank': row.find('span', class_='tw-table__rank').text,
                'domain': row.find('span', class_='tw-table__domain').text,
                'category': row.find('a', class_='tw-table__category').text,
                'avg_visit_duration': row.find('span', class_='tw-table__avg-visit-duration').text,
                'pages_per_visit': row.find('span', class_='tw-table__pages-per-visit').text,
                'bounce_rate': row.find('span', class_='tw-table__bounce-rate').text,
            }
            # Agregar el diccionario a la lista
            self.row_data.append(row_dicc)

    def get_url_list(self):
        """
        """
        self.url_list = []
        for data in self.row_data:
            self.url_list.append(
                (self.base_url + f"website/{data['domain']}/", data['domain'].replace('.','_'))
            )
        return self.url_list

class SimilarWebWebsite:
    def __init__(self, filename=None):
        self.base_url = 'https://www.similarweb.com/website/'

        self.domain = ''
        self.global_rank = 0
        self.country_rank = 0
        self.category_rank = 0
        self.total_visits = 0
        self.bounce_rate = 0.0
        self.pages_per_visit = 0.0
        self.avg_duration_visit = '00:00:00'

        self.html_content = ''
        self.filename = filename
        if self.filename is not None:
            self.set_html_content_fromfile(filename=filename)

    def set_html_content(self, html_content):
        self.html_content = html_content

    def set_html_content_fromfile(self, filename=None):
        self.filename = filename
        with open(filename, 'r', encoding="utf-8") as file:
            self.html_content = BeautifulSoup(file, 'html.parser')

    def to_dicc(self):
        """
        """
        web_data = {
            'domain': self.domain,
            'global_rank': self.global_rank,
            'country_rank': self.country_rank,
            'category_rank': self.category_rank,
            'total_visits': self.total_visits,
            'bounce_rate': self.bounce_rate,
            'pages_per_visit': self.pages_per_visit,
            'avg_duration_visit': self.avg_duration_visit,
        }
        return web_data

    def fetch_data(self):
        self.fetch_domain()
        self.fetch_rank()
        self.fetch_engagement()

    def fetch_domain(self):
        """
        """
        self.domain = self.html_content.find('p', class_='wa-overview__title').text

    def fetch_rank(self):
        """
        """
        # Obtengo el cuadro de encabezado
        rank_header = self.html_content.find('div', class_='wa-rank-list wa-rank-list--md')
        # Obtengo las cajas
        global_box = rank_header.find('div', class_='wa-rank-list__item wa-rank-list__item--global')
        country_box = rank_header.find('div', class_='wa-rank-list__item wa-rank-list__item--country')
        category_box = rank_header.find('div', class_='wa-rank-list__item wa-rank-list__item--category')
        # Obtengo los valores de las cajas
        self.global_rank = int(global_box.find('p', class_='wa-rank-list__value').text.replace('#',''))
        self.country_rank = int(country_box.find('p', class_='wa-rank-list__value').text.replace('#',''))
        self.category_rank = int(category_box.find('p', class_='wa-rank-list__value').text.replace('#',''))

    def fetch_engagement(self):
        """
        """
        # Encuentro la caja de de engagement
        engagement_box = self.html_content.find('div', class_='engagement-list')
        # Encuentro los elementos dentro de la caja
        engagement_elements = engagement_box.find_all('div', class_='engagement-list__item')
        # Para cada elemento, obtengo el dato asociado
        self.total_visits = engagement_elements[0].find('p', class_='engagement-list__item-value').text
        self.bounce_rate = engagement_elements[1].find('p', class_='engagement-list__item-value').text.replace('%','')
        self.bounce_rate = round(float(self.bounce_rate)/100.0, 2)
        self.pages_per_visit = engagement_elements[2].find('p', class_='engagement-list__item-value').text
        self.avg_duration_visit = engagement_elements[3].find('p', class_='engagement-list__item-value').text

if __name__ == '__main__':
    similarweb_main()