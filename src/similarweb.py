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

if __name__ == '__main__':
    data = get_similarweb_table('scraped_page.html')
    print(data)