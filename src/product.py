import re

try:
    from src.utils import getHTTPResponse
    from src.utils import generateRandomUserAgent
except:
    from utils import getHTTPResponse
    from utils import generateRandomUserAgent

class Product:
    def __init__(self):
        self.id = None
        self.name = ''
        self.descrption = ''
        self.price = 0.0
        self.currency = ''
        self.rank = 0
        self.rating = 0.0
        self.rate_count = 0
        self.platform = ''
        self.store = ''
        self.most_selled = 0
        self.promoted = 0

        # Este no va en el diccionario
        self.html_content = ''

    def to_dicc(self):
        return {
            'id': self.id,
            'name': self.name,
            'descrption': self.descrption,
            'price': self.price,
            'currency': self.currency,
            'rank': self.rank,
            'rating': self.rating,
            'rate_count': self.rate_count,
            'platform': self.platform,
            'store': self.store,
            'most_selled': self.most_selled,
            'promoted': self.promoted,
        }

class MeLiProduct(Product):
    def __init__(self):
        # Inicio el constructor de la otra clase
        super().__init__()
        # Actualizo los parametros por defecto
        self.currency = 'ARS'
        self.platform = 'Mercado Libre'

    def fetch_data(self):
        self.fetch_name()
        self.fetch_price()
        self.fetch_store()
        self.fetch_rating()
        self.fetch_specials()

    def fetch_name(self):
        # Obtener el nombre del juguete
        try:
            self.name = self.html_content.find('h2', class_='ui-search-item__title').text.strip()
        except:
            self.name = 'Unknown toy'

    def fetch_price(self):
        # Obtener el precio del juguete
        try:
            self.price = self.html_content.find('span', class_=[
                'price-tag-fraction',
                'andes-money-amount__fraction',
            ]).text.strip()
            self.price = self.price.replace('.','')
            self.price = self.price.replace(',','.')
            self.price = float(self.price)
        except:
            self.price = 0

    def fetch_store(self):
        # Obtengo el vendedor del juguete
        try:
            self.store = self.html_content.find('p', class_='ui-search-official-store-label').text
            self.store = self.store.replace('por ','')
        except:
            self.store = '-'

    def fetch_rating(self):
        # Obtengo la calificacion del juguete
        try:
            rateBox   = self.html_content.find('span', class_='ui-search-reviews__ratings')
            # Cuento la cantidad de estrellas llenas
            fullStars = len( rateBox.find_all('svg', class_='ui-search-icon ui-search-icon--star ui-search-icon--star-full') )
            # Cuento la cantidad de estrellas a la mitad
            halfStars = len( rateBox.find_all('svg', class_='ui-search-icon ui-search-icon--star ui-search-icon--star-half') )
            self.rating = fullStars + halfStars * 0.5
        except:
            self.rating = 'Unknown'

        try:
            self.rate_count = self.html_content.find('span', class_='ui-search-reviews__amount').text[1:-1]
            self.rate_count = int(self.rate_count)
        except:
            self.rate_count = '-'

    def fetch_specials(self):
        # Obtengo datos de mas vendido o promocionado
        try:
            if self.html_content.find('div', class_='ui-search-item__highlight-label__container') is not None:
                self.most_selled = 1
            else:
                self.most_selled = 0
        except:
            self.most_selled = 0

        try:
            if self.html_content.find('span', class_='ui-search-item__pub-label ui-search-item__pub-label--blue') is not None:
                self.promoted = 1
            else:
                self.promoted = 0
        except:
            self.promoted = 0

class AmazonProduct(Product):
    def __init__(self):
        # Inicio el constructor de la otra clase
        super().__init__()
        # Actualizo los parametros por defecto
        self.currency = 'MX'
        self.platform = 'Amazon'

    def fetch_data(self):
        self.fetch_name()
        self.fetch_price()
        self.fetch_store()
        self.fetch_rating()
        self.fetch_specials()

    def fetch_name(self):
        # Obtener el nombre del juguete
        try:
            self.name = self.html_content.find('div', class_=[
                '_cDEzb_p13n-sc-css-line-clamp-3_g3dy1',
                '_cDEzb_p13n-sc-css-line-clamp-5_2l-dX',
            ]).text.strip()
        except:
            self.name = 'Unknown toy'

    def fetch_price(self):
        # Obtener el precio del juguete
        try:
            self.price = self.html_content.find('span', class_='_cDEzb_p13n-sc-price_3mJ9Z').text.strip()
            # Saco el punto del precio si lo tiene
            self.price = self.price.replace(',','')
            self.price = self.price.replace('$','')
            self.price = float(self.price)
        except:
            self.price = 0

    def fetch_store(self):
        # Obtengo el vendedor del juguete
        try:
            # NOTA: No se si Amazon te dice quien vende
            self.store = '-'
        except:
            self.store = '-'

    def fetch_rank(self):
        # Obtener la posición del juguete en la lista
        try:
            self.rank = self.html_content.find('span', class_='zg-bdg-text').text.strip()
        except:
            self.rank = 0

    def fetch_rating(self):
        # Obtener el calificacion del juguete
        try:
            # Me quedo con el div que tiene las estrellas
            rateBox = self.html_content.find('div', class_='a-icon-row')
            # Ese div deberia tener un elemento 'i' con varias clases
            classes = rateBox.find('i')['class']
            # Defino un valor por defecto
            self.rating = 'Unknown'
            # Recorro las clases que encontre
            for class_ in classes:
                # Nos quedamos con la clase que se parezca al patron
                # y nos fijamos las estrellas
                if 'a-star-small-' in class_:
                    rate = re.search(r'a-star-small-(\d+(\.\d+)?)', class_).group(1)
        except:
            self.rating = 'Unknown'

        try:
            # rateBox ya deberia haber estado definido de antes si todo salio bien
            self.rate_count = rateBox.find('span', class_='a-size-small').text
            self.rate_count = self.rate_count.replace(',','')
        except:
            self.rate_count = '-'

    def fetch_specials(self):
        # Obtengo datos de mas vendido o promocionado
        try:
            # NOTA: Creo que Amazon no te da esta informacion
            self.most_selled = 0
        except:
            self.most_selled = 0

        try:
            # NOTA: Creo que Amazon no te da esta informacion
            self.promoted = 0
        except:
            self.promoted = 0