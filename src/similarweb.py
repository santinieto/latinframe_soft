from bs4 import BeautifulSoup
try:
    from src.db import Database
    from src.utils import cprint
    from src.utils import o_fmt_error
except:
    from db import Database
    from utils import cprint
    from utils import o_fmt_error

class SimilarWebTopWebsitesTable():
    def __init__(self, filename='html_top_websites.dat'):
        self.base_url = 'https://www.similarweb.com/'
        self.row_data = []
        self.html_content = ''
        self.filename = filename
        if self.filename is not None:
            self.set_html_content_fromfile(filename=filename)

    def set_html_content(self, html_content):
        self.html_content = html_content

    def set_html_content_fromfile(self, filename=None):
        if filename is not None:
            self.filename = filename
        with open(self.filename, 'r', encoding="utf-8") as file:
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
                'category': row.find(['span','a'], class_='tw-table__category').text,
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
    def __init__(self, filename=None, debug=False):
        self.debug = debug
        self.base_url = 'https://www.similarweb.com/website/'
        self.domain_id = ''
        self.domain = ''
        self.global_rank = 0
        self.country_rank = 0
        self.category_rank = 0
        self.total_visits = 0
        self.bounce_rate = 0.0
        self.pages_per_visit = 0.0
        self.avg_duration_visit = '00:00:00'

        self.company = ''
        self.year_founder = 0
        self.employees = ''
        self.hq = ''
        self.annual_revenue = ''
        self.industry = ''

        self.html_content = ''
        self.filename = filename
        if self.filename is not None:
            self.set_html_content_fromfile(filename=filename)

    def set_html_content(self, html_content):
        self.html_content = html_content

    def set_html_content_fromfile(self, filename=None):
        if filename is not None:
            self.filename = filename
        with open(self.filename, 'r', encoding="utf-8") as file:
            self.html_content = BeautifulSoup(file, 'html.parser')

    def __str__(self):
        """
        """
        ans  = f"\t- SW Domain ID: {self.domain_id}\n"
        ans += f"\t- SW Domain: {self.domain}\n"
        ans += f"\t- SW Company: {self.company}\n"
        ans += f"\t- SW Year founder: {self.year_founder}\n"
        ans += f"\t- SW Employees: {self.employees}\n"
        ans += f"\t- SW HQ: {self.hq}\n"
        ans += f"\t- SW Annual revenue: {self.annual_revenue}\n"
        ans += f"\t- SW Industry: {self.industry}\n"
        ans += f"\t- SW Global rank: {self.global_rank}\n"
        ans += f"\t- SW Country rank: {self.country_rank}\n"
        ans += f"\t- SW Category rank: {self.category_rank}\n"
        ans += f"\t- SW Total visits: {self.total_visits}\n"
        ans += f"\t- SW Bounce rate: {self.bounce_rate}\n"
        ans += f"\t- SW Pages per visit: {self.pages_per_visit}\n"
        ans += f"\t- SW Avg duration visit: {self.avg_duration_visit}"
        return ans

    def to_dicc(self):
        """
        """
        web_data = {
            'domain_id': self.domain_id,
            'domain': self.domain,
            'company': self.company,
            'year_founder': self.year_founder,
            'employees': self.employees,
            'hq': self.hq,
            'annual_revenue': self.annual_revenue,
            'industry': self.industry,
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

        # Debug
        if self.debug is True:
            cprint('')
            cprint('-' * 100)
            cprint(str(self))
            cprint('-' * 100)

    def fetch_domain(self):
        """
        """
        try:
            self.domain = self.html_content.find('p', class_='wa-overview__title').text
        except:
            pass

        try:
            info_box = self.html_content.find('div', class_='app-company-info app-company-info--marked wa-overview__company')
            values = info_box.find_all('dd', 'app-company-info__list-item app-company-info__list-item--value')
        except:
            pass

        try:
            self.company = values[0].text
        except:
            self.company = None

        try:
            self.year_founder = int(values[1].text)
        except:
            self.year_founder = None

        try:
            self.employees = values[2].text
        except:
            self.employees = None

        try:
            self.hq = values[3].text
        except:
            self.hq = None

        try:
            self.annual_revenue = values[4].text
        except:
            self.annual_revenue = None

        try:
            self.industry = values[5].text
        except:
            self.industry = None

    def fetch_rank(self):
        """
        """
        # Obtengo el cuadro de encabezado
        rank_header = self.html_content.find('div', class_='wa-rank-list wa-rank-list--md')
        # Obtengo las cajas
        try:
            global_box = rank_header.find('div', class_='wa-rank-list__item wa-rank-list__item--global')
            country_box = rank_header.find('div', class_='wa-rank-list__item wa-rank-list__item--country')
            category_box = rank_header.find('div', class_='wa-rank-list__item wa-rank-list__item--category')
            # Obtengo los valores de las cajas
            self.global_rank = int(global_box.find('p', class_='wa-rank-list__value').text.replace('#',''))
            self.country_rank = int(country_box.find('p', class_='wa-rank-list__value').text.replace('#',''))
            self.category_rank = int(category_box.find('p', class_='wa-rank-list__value').text.replace('#',''))
        except:
            pass

    def fetch_engagement(self):
        """
        """
        try:
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
        except:
            pass

if __name__ == '__main__':
    # Obtengo la lista de paginas mas vistas
    table = SimilarWebTopWebsitesTable()
    table.fetch_rows()
    url_list = table.get_url_list()

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