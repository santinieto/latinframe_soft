try:
    from src.driver import Driver
    from src.db import Database
    from src.similarweb import SimilarWebTopWebsitesTable
    from src.similarweb import SimilarWebWebsite
    from src.utils import cprint
    from src.utils import o_fmt_error
except:
    from driver import Driver
    from db import Database
    from similarweb import SimilarWebTopWebsitesTable
    from similarweb import SimilarWebWebsite
    from utils import cprint
    from utils import o_fmt_error

def scrap_similarweb(results_path='results/similarweb/', delay=10):
    """
    """

    # Defino la URL base
    SIMILARWEB_BASE_URL = 'https://www.similarweb.com/'

    # Creo el objeto de tipo driver
    driver = Driver(browser="chrome")

    # Armo la lista de tablas que quiero
    tables_list = [
        # Format ('url','alias')
        ('top-websites/', 'top_websites'),
        ('top-websites/arts-and-entertainment/tv-movies-and-streaming/', 'streaming'),
    ]

    # Obtengo la informacion de las webs mas vistas
    filenames = []
    try:
        for table_config in tables_list:
            filenames.append( driver.scrap_url(SIMILARWEB_BASE_URL + table_config[0], table_config[1], delay=delay) )
    except:
        for table_config in tables_list:
            filenames.append( f'results/similarweb/html_{table_config[1]}.dat' )

    # Creo la lista total de paginas
    url_list = []

    # Obtengo la lista de dominios desde la base datos
    # Obtengo los dominios que ya tengo cargados
    with Database() as db:
        # Consulta SQL
        query = "select domain from similarweb_domains"
        query_res = db.select(query)
        result = [x[0] for x in query_res]
        domains = list(set(result))

        sub_url_list = []
        for domain in domains:
            # NOTA: CUIDADO CON CAMBIAR ESTO, REVISAR similarweb.py::SimilarWebTopWebsitesTable()
            url = (f'{SIMILARWEB_BASE_URL}/website/{domain}/', domain.replace('.','_'))
            sub_url_list.append( url )
        url_list.extend( sub_url_list )

        # Muestro la cantidad de dominios presentes en la base de datos
        print(f'- Se obtuvieron {len(sub_url_list)} dominios desde la base de datos')

    # Para cada top, obtengo la lista de dominios
    for filename in filenames:
        # Obtengo la lista de paginas mas vistas
        table = SimilarWebTopWebsitesTable(filename=filename)
        table.fetch_rows()
        sub_url_list = table.get_url_list()
        url_list.extend( sub_url_list )

    # Elimino repeticiones y paso todo a una lista
    url_list = list(set(url_list))

    # Muestro el total de paginas a scrapear
    print('- Se va a obtener la informacion de {} paginas web'.format(len(url_list)))

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

            # Mostrar datos de la pagina
            cprint('')
            cprint('-' * 100)
            cprint(str(web_info))
            cprint('-' * 100)

            # Agrego el registro a la tabla
            db.insert_similarweb_record(web_info.to_dicc())

if __name__ == '__main__':
    scrap_similarweb()