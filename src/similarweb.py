from bs4 import BeautifulSoup

# BASE_URL = 'https://www.similarweb.com/'
# TOP_URL = 'top-websites/'
# ARTS_URL = 'arts-and-entertainment/'

def get_similarweb_table(filepath=''):

    # Abro el archivo
    with open(filepath, 'r', encoding="utf-8") as file:
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

def get_similarweb_web_info(filepath='scraped_page.html'):

    #########################################
    # Abro el archivo
    #########################################
    with open(filepath, 'r', encoding="utf-8") as file:
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

if __name__ == '__main__':
    data = get_similarweb_table('scraped_page.html')
    print(data)

    data = get_similarweb_web_info('scraped_page.html')
    print(data)