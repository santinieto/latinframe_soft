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

import datetime

def generate_domain_id():
    with Database() as db:
        # Quiero obtener ahora el maximo valor de IDs
        query = "select max(domain_id) from similarweb_domains"

        # El resultado es una lista de tuplas
        # Me quedo con el primer elemento
        result = [x[0] for x in db.select(query)]
        max_id = list(set(result))[0]

        # Le cargo el ID de dominio a la web
        domain_id = int(max_id) + 1
    return domain_id

def get_domain_id(domain = 'youtube.com'):
    with Database() as db:
        # Defino la consulta que tengo que realizar
        query = f"select domain_id from similarweb_domains where domain = '{domain}'"

        # Obtengo el resultado de busqueda
        query_res = db.select(query)

        # Si obtengo un resultado lo agrego
        if len(query_res) > 0:
            # El resultado es una lista de tuplas
            # Me quedo con el primer elemento
            result = [x[0] for x in db.select(query)]
            domain_id = int(list(set(result))[0])

        # Si no se encuentra el ID devuelvo None
        else:
            domain_id = None

    return domain_id

def del_web(domain=None, domain_id=None):
    # Me fijo si tengo que buscar el dominio
    if domain is not None:
        domain_id = get_domain_id(domain=domain)

    # Si no encontre el dominio en la base de datos y
    # el usuario no proporciona el ID de dominio
    # entonces no puedo hacer nada
    if domain_id is None:
        print('ERROR! Can not remove data with no information')

    # Armo las consultas SQL
    query_1 = f"select * from similarweb_domains where domain_id = {domain_id}"
    query_2 = f"select * from similarweb_records where domain_id = {domain_id}"

    # Abro la conexion con la base de datos
    with Database() as db:
        results_1 = db.select(query_1)
        results_2 = db.select(query_2)

    # Muestro los resultados en la tabla SIMILARWEB_DOMAINS
    print('- COINCIDENCIAS EN SIMILARWEB_DOMAINS:')
    if len(results_1) > 0:
        for res in results_1:
            print(F'\t{res}')
    else:
        print('\t NO RESULTS')

    # Separacion para que se vea todo mas claro
    print()

    # Muestro los resultados en la tabla SIMILARWEB_RECORDS
    print('- COINCIDENCIAS EN SIMILARWEB_RECORDS:')
    if len(results_2) > 0:
        for res in results_2:
            print(F'\t{res}')
    else:
        print('\t NO RESULTS')

    # Checkeo si tengo resultados para borrar y pido confirmacion de borrado
    if ((len(results_1) > 0) or
        (len(results_2) > 0)
    ):
        # Le pregunto al usuario si realmente va a borrar los registros
        ans = None
        while ans not in ['y','n']:
            ans = input('Confirm deleting above records? (y/n): ')

        # Borro definitivamente los registros
        if ans == 'y':
            query_1 = query_1.replace('select *','delete')
            query_2 = query_2.replace('select *','delete')
            # Abro la conexion con la base de datos
            with Database() as db:
                results_1 = db.select(query_1)
                results_2 = db.select(query_2)
        else:
            # No hago nada y salgo del programa
            return

def add_web(domain='youtube.com'):
    # Busco el dominio en la base de datos
    domain_id = get_domain_id(domain)

    # Si no lo encontro, genero uno
    if domain_id is None:
        print(f'No se encontro el dominio {domain} en la base de datos')
        domain_id = generate_domain_id()
        print(f'Se generara el nuevo dominio {domain_id}')

        # Defino la consulta para agregar un dato
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = f"insert into similarweb_domains (domain_id, domain, update_date) values (?,?,?)"
        params = (domain_id, domain, current_time)

        # Abro la base de datos y ejecuto la consulta
        with Database() as db:
            db.exec(query,params)

    else:
        print(f'El dominio {domain} ya se encuentra en la base de datos con ID {domain_id}')

    pass

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
                # Busco el dominio en la base de datos
                domain_id = get_domain_id(web_info.domain)

                # Si el dominio no se encontro, genero uno nuevo
                if domain_id is None:
                    domain_id = generate_domain_id()

                # Le cargo el ID de dominio a la web
                web_info.domain_id = domain_id
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