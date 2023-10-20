try:
    from src.driver import Driver
    from src.db import Database
    from src.similarweb import SimilarWebTopWebsitesTable
    from src.similarweb import SimilarWebWebsite
except:
    from driver import Driver
    from db import Database
    from similarweb import SimilarWebTopWebsitesTable
    from similarweb import SimilarWebWebsite

def scrap_similarweb(results_path='results/similarweb/', delay=10):
    """
    """

    # Defino la URL base
    SIMILARWEB_BASE_URL = 'https://www.similarweb.com/'

    # Creo el objeto de tipo driver
    driver = Driver(browser="chrome")

    # Obtengo la informacion de las webs mas vistas
    filename = driver.scrap_url(SIMILARWEB_BASE_URL + "top-websites/", 'top_websites', delay=delay)

    # Obtengo la lista de paginas mas vistas
    filename = f'{results_path}/{filename}'
    table = SimilarWebTopWebsitesTable(filename=filename)
    table.fetch_rows()
    url_list = table.get_url_list()

    # Obtengo el codigo HTML para esas paginas
    driver.scrap_url_list(url_list, delay=delay)

    # Cierro la pagina
    driver.close_driver()

    # Abro la conexion con la base de datos:
    with Database() as db:

        # Recorro la lista de URLs
        for url in url_list:

            # Armo el nombre del archivo a leer
            filename = f'{results_path}/html_{url[1]}.dat'

            # Obtengo la informacion a partir del contenido HTML
            web_info = SimilarWebWebsite(filename=filename)
            web_info.fetch_data()

            # Muestro el diccionario en pantalla
            print(web_info.to_dicc())

            # Agrego el registro a la tabla
            db.insert_similarweb_record(web_info.to_dicc())

if __name__ == '__main__':
    scrap_similarweb()