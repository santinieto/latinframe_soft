try:
    from src.driver import Driver
    from src.db import Database
    from src.similarweb import SimilarWebTopWebsitesTable
    from src.similarweb import SimilarWebWebsite
    from src.utils import cprint
    from src.utils import o_fmt_error
    from src.utils import SIMILARWEB_BASE_URL
    from src.utils import get_similarweb_url_tuple
    from src.utils import is_url_arg
except:
    from driver import Driver
    from db import Database
    from similarweb import SimilarWebTopWebsitesTable
    from similarweb import SimilarWebWebsite
    from utils import cprint
    from utils import o_fmt_error
    from utils import SIMILARWEB_BASE_URL
    from utils import get_similarweb_url_tuple
    from utils import is_url_arg

import datetime

def handle_similarweb_args(args):
    # Defino un nombre por defecto al modulo
    module_name = 'similarweb'

    # Obtengo el mensaje de ayuda
    if args.ayuda:
        scrap_similarweb_help()

    # Obtengo la informacion de una pagina web
    elif args.web:
        if is_url_arg(args.web):
            get_web(args.web)
        else:
            print('No es una URL')

    # Obtengo la informacion de los scraps que ya tengo
    elif args.obtain:
        scrap_similarweb(skip_scrap=True)

    # Agrego una web a la base de datos
    elif args.add:
        add_web(args.add)

    # Borro una web de la base de datos
    elif args.delete:
        if args.delete[0] == 'id':
            domain_id = int(args.delete[1])
            del_web(domain_id=domain_id)
        elif args.delete[0] == 'domain':
            del_web(domain=args.delete[1])

    # Mensaje de error por defecto
    else:
        print(f'Modulos {module_name}')
        print(f'\tSe ha producido un error al procesar el comando')
        print(f'\tPuede utilizar {module_name} -h para obtener ayuda')

def scrap_similarweb_help():
    print('Similarweb usage:')
    print('\tNULL\tExecute general Similarweb scrap')
    print('\t-help\tThis help message')
    print('\t-skip-scrap\tProcess scrapped pages')
    print('\t-web <domain>\tGet information for given domain')
    print('\t-add <domain>\tAdd web to DB for given domain')
    print('\t-del []\tDelete records from database')
    print('\t\t-id <domain_id>\tUsing an ID from database')
    print('\t\t-domain <domain>\tUsing a domain from database')

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
    # Devuelvo el ID de dominio
    return domain_id

def get_web(domain, results_path='results/similarweb/', delay=15):
    """
    """
    # Armo la URL
    url, alias = get_similarweb_url_tuple(domain)

    # Creo el objeto de tipo driver
    driver = Driver(browser="chrome")

    # Hago el scrap
    driver.scrap_url(url, alias, delay=delay)

    # Armo el nombre del archivo a leer
    filename = f'{results_path}/html_{url[1]}.dat'

    # Obtengo la informacion a partir del contenido HTML
    web_info = SimilarWebWebsite(filename=filename)
    web_info.fetch_data()

    # Busco el dominio en la base de datos
    domain_id = get_domain_id(web_info.domain)

    # Le cargo el ID de dominio a la web
    web_info.domain_id = domain_id

    # Mostrar datos de la pagina
    cprint('')
    cprint('-' * 100)
    cprint(str(web_info))
    cprint('-' * 100)

def del_web(domain=None, domain_id=None):
    # Me fijo si tengo que buscar el dominio
    if domain is not None:
        domain_id = get_domain_id(domain=domain)

    # Si no encontre el dominio en la base de datos y
    # el usuario no proporciona el ID de dominio
    # entonces no puedo hacer nada
    if domain_id is None:
        cprint('ERROR! Can not remove data with no information')

    # Armo las consultas SQL
    query_1 = f"select * from similarweb_domains where domain_id = {domain_id}"
    query_2 = f"select * from similarweb_records where domain_id = {domain_id}"

    # Abro la conexion con la base de datos
    with Database() as db:
        results_1 = db.select(query_1)
        results_2 = db.select(query_2)

    # Muestro los resultados en la tabla SIMILARWEB_DOMAINS
    print('- COINCIDENCIAS EN SIMILARWEB_DOMAINS:')
    if (results_1 is not None):
        if (len(results_1) > 0):
            for res in results_1:
                print(F'\t{res}')
        else:
            print('\t NO RESULTS')
    else:
        print('\t NO RESULTS')

    # Separacion para que se vea todo mas claro
    print()

    # Muestro los resultados en la tabla SIMILARWEB_RECORDS
    print('- COINCIDENCIAS EN SIMILARWEB_RECORDS:')
    if (results_2 is not None):
        if len(results_2) > 0:
            for res in results_2:
                print(F'\t{res}')
        else:
            print('\t NO RESULTS')
    else:
        print('\t NO RESULTS')

    if (results_1 is None):
        return
    if (results_2 is None):
        return

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

def scrap_similarweb(results_path='results/similarweb/', delay=10, skip_scrap=False):
    """
    """
    # Creo el objeto de tipo driver
    if skip_scrap is False:
        driver = Driver(browser="chrome")

    # Armo la lista de tablas que quiero
    tables_list = [
        # Format ('url','alias')
        ('top-websites/', 'top_websites'),
        ('top-websites/arts-and-entertainment/tv-movies-and-streaming/', 'streaming'),
    ]

    # Obtengo la informacion de las webs mas vistas
    filenames = []
    if skip_scrap is False:
        for table_config in tables_list:
            filenames.append( driver.scrap_url(SIMILARWEB_BASE_URL + table_config[0], table_config[1], delay=delay) )
    else:
        for table_config in tables_list:
            filenames.append( f'{results_path}/html_{table_config[1]}.dat' )

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
            url, alias = get_similarweb_url_tuple(domain)
            sub_url_list.append( (url,alias) )
        url_list.extend( sub_url_list )

        # Muestro la cantidad de dominios presentes en la base de datos
        cprint(f'- Se obtuvieron {len(sub_url_list)} dominios desde la base de datos')

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
    cprint('- Se va a obtener la informacion de {} paginas web'.format(len(url_list)))

    if skip_scrap is False:
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
            web_dicc = web_info.to_dicc()
            if (len(web_dicc['domain']) > 0):
                db.insert_similarweb_record(web_dicc)
            else:
                msg = f'Record not added to DB in scrap_similarweb() for file {filename}. Dicc:\n\n{web_dicc}\n\n'
                o_fmt_error('0100', msg, 'Function__scrap_similarweb')

if __name__ == '__main__':
    scrap_similarweb()