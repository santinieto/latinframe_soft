try:
    from src.product import *
    from src.utils import getHTTPResponse
    from src.utils import generateRandomUserAgent
    from src.db import Database
except:
    from product import *
    from utils import getHTTPResponse
    from utils import generateRandomUserAgent
    from db import Database

def save_html(filename, content):
    # Guardo el contenido HTML
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

def get_http_response(url, tries=10):
    # Pido la respuesta del servidor
    for k in range(tries):
        print('\tObteniendo datos para {}... Intento {}...'.format(url, k+1))
        page = getHTTPResponse(url,
                                headers = {
                                    'user-agent' : generateRandomUserAgent(),
                                },
                                debug = False)
        if page is not False:
            break
    if page is False:
        print('ERROR! No se pudieron obtener datos desde Amazon, se omitio la ejecucion')
        return None
    else:
        return page

def scrap_amazon_products(topics=[], tries=10):
    """
    """
    # Armo las URLs que voy a usar
    urls = search_urls_amazon(topics)

    # Defino una URL por defecto
    urls.append( 'https://www.amazon.com.mx/gp/bestsellers/toys/' )

    # Hago la busqueda para cada tema
    for url in urls:

        # Trato de obtener el contenido HTML
        page = get_http_response(url, tries)

        # Si hubo un error en la pagina doy nota de error
        if page is None:
            print(f'- Ocurrio un error al cargar la pagina {url}')
            return

        # Hago el scrap
        else:

            # Guardo el contenido HTML
            # save_html('amazon.html',page.prettify())

            # Encontrar los elementos relevantes que contienen la información de los juguetes más buscados
            toys = page.find_all('div', class_= [
                'a-cardui _cDEzb_grid-cell_1uMOS expandableGrid p13n-grid-content',
                # 'a-section a-spacing-base',
            ])

        # Iterar sobre los elementos encontrados y extraer la información deseada
        for k, toy in enumerate(toys):
            x = AmazonProduct()
            x.html_content = toy
            x.fetch_data()
            print(x.to_dicc())

def scrap_meli_products(topics=[], tries=10):
    """
    """
    # Armo las URLs que voy a usar
    urls = search_urls_meli(topics)

    # Defino una URL por defecto
    urls.append( 'https://listado.mercadolibre.com.ar/juguetes/' )

    # Hago la busqueda para cada tema
    for url in urls:

        # Trato de obtener el contenido HTML
        page = get_http_response(url, tries)

        # Si hubo un error en la pagina doy nota de error
        if page is None:
            print(f'- Ocurrio un error al cargar la pagina {url}')
            return

        # Guardo el contenido HTML
        # save_html('mercadolibre.html',page.prettify())

        # Encontrar los elementos relevantes que contienen la información de los juguetes más buscados
        toys = page.find_all('div', class_='ui-search-result__wrapper')

        # Iterar sobre los elementos encontrados y extraer la información deseada
        toys_dicc = []
        for k, toy in enumerate(toys):
            x = MeLiProduct()
            x.html_content = toy
            x.fetch_data()
            toys_dicc.append( x.to_dicc() )

        with Database() as db:
            for toy_dicc in toys_dicc:
                db.insert_product_record( toy_dicc )

def search_urls_amazon(topics=['toys'], tries=10):
    """
    """
    # Genero las URLs
    urls = []
    for topic in topics:
        url = 'https://www.amazon.com.mx/s?k={}/'.format( topic.replace(' ','+') )
        urls.append( url )
    return urls

def search_urls_meli(topics=['toys'], tries=10):
    """
    """
    # Genero las URLs
    urls = []
    for topic in topics:
        url = 'https://listado.mercadolibre.com.ar/{}/'.format( topic.replace(' ','-') )
        urls.append( url )
    return urls

if __name__ == '__main__':
    # Parametros
    tries = 10

    # Obtengo los productos de Amazon
    scrap_amazon_products(topics = [
        # 'toys', # NO FUNCIONAN
        # 'bestsellers toys and games', # NO FUNCIONAN
    ])

    # Obtengo los productos de Mercado Libre
    scrap_meli_products(topics = [
        'disney',
    ])

def get_meli_url(produc_id, product_name):
    return f'https://articulo.mercadolibre.com.ar/{produc_id}-{product_name}-_JM'
