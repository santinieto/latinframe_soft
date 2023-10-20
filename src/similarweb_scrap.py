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

            # Obtengo el ID del canal
            try:
                # Defino la consulta que tengo que realizar
                query = f"select domain_id from similarweb_domains where domain = '{web_info.domain}'"

                # Obtengo el resultado de busqueda
                query_res = db.select(query)

                # Si obtengo un resultado lo agrego
                if len(query_res) > 0:
                    # El resultado es una lista de tuplas
                    # Me quedo con el primer elemento
                    result = [x[0] for x in db.select(query)]
                    domain_id = list(set(result))[0]

                    # Le cargo el ID de dominio a la web
                    web_info.domain_id = int(domain_id)

                # Sino, le establezco un nuevo ID al dominio
                else:
                    # Quiero obtener ahora el maximo valor de IDs
                    query = "select max(domain_id) from similarweb_domains"

                    # El resultado es una lista de tuplas
                    # Me quedo con el primer elemento
                    result = [x[0] for x in db.select(query)]
                    max_id = list(set(result))[0]

                    # Le cargo el ID de dominio a la web
                    web_info.domain_id = int(max_id) + 1
            except:
                pass

            # Muestro el diccionario en pantalla
            print(web_info.to_dicc())

            # Agrego el registro a la tabla
            db.insert_similarweb_record(web_info.to_dicc())

if __name__ == '__main__':
    scrap_similarweb()