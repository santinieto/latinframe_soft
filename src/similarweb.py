from bs4 import BeautifulSoup
from driver import Driver

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

def get_similarweb_web_info(filename='scraped_page.html'):

    #########################################
    # Abro el archivo
    #########################################
    with open(filename, 'r', encoding="utf-8") as file:
        page = BeautifulSoup(file, 'html.parser')

    #########################################
    # Analizo la informacion de rankeo
    #########################################
    # Obtengo el cuadro de encabezado
    rank_header = page.find('div', class_='wa-rank-list wa-rank-list--md')
    # Obtengo las cajas
    global_box = rank_header.find('div', class_='wa-rank-list__item wa-rank-list__item--global')
    country_box = rank_header.find('div', class_='wa-rank-list__item wa-rank-list__item--country')
    category_box = rank_header.find('div', class_='wa-rank-list__item wa-rank-list__item--category')
    # Obtengo los valores de las cajas
    global_rank = global_box.find('p', class_='wa-rank-list__value').text
    country_rank = country_box.find('p', class_='wa-rank-list__value').text
    category_rank = category_box.find('p', class_='wa-rank-list__value').text

    #########################################
    # Analizo la informacion de rankeo
    #########################################
    # Encuentro la caja de de engagement
    engagement_box = page.find('div', class_='engagement-list')
    # Encuentro los elementos dentro de la caja
    engagement_elements = engagement_box.find_all('div', class_='engagement-list__item')
    # Para cada elemento, obtengo el dato asociado
    total_visits = engagement_elements[0].find('p', class_='engagement-list__item-value').text
    bounce_rate = engagement_elements[1].find('p', class_='engagement-list__item-value').text
    pages_per_visit = engagement_elements[2].find('p', class_='engagement-list__item-value').text
    avg_duration_visit = engagement_elements[3].find('p', class_='engagement-list__item-value').text

    #########################################
    # Armo el diccionario de datos
    #########################################
    web_data = {
        'global_rank': global_rank,
        'country_rank': country_rank,
        'category_rank': category_rank,
        'total_visits': total_visits,
        'bounce_rate': bounce_rate,
        'pages_per_visit': pages_per_visit,
        'avg_duration_visit': avg_duration_visit,
    }

    return web_data

def get_similarweb_url_list_fromtable(data_list):

    url_list = []
    for data in data_list:
        url_list.append(
            (BASE_URL + f"website/{data['domain']}/", data['domain'].replace('.','_'))
        )

    return url_list

if __name__ == '__main__':
    # Defino la URL base
    BASE_URL = 'https://www.similarweb.com/'

    # Creo el objeto de tipo driver
    # driver = Driver(browser="chrome")

    # # Obtengo la informacion de las webs mas vistas
    # filename = driver.scrap_url(BASE_URL + "top-websites/", 'top_websites', delay=20)

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

    for url in url_list:
        filename = f'html_{url[1]}.dat'
        web_info = get_similarweb_web_info(filename=filename)
        print(web_info)
