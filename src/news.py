from datetime import datetime, timedelta
from unidecode import unidecode
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import os

try:
    from src.utils import getHTTPResponse
except:
    from utils import getHTTPResponse

class New:
    def __init__(self, topic=''):
        self.new_id = 0
        self.title = ''
        self.topic = topic
        self.topic_id = 0
        self.newspaper = ''
        self.newspaper_id = 0
        self.url = ''
        self.publish_date = '00-00-00 00:00:00'
        self.antique = ''
        # Campos que no van en la base de datos
        self.html_content = ''

    def to_dicc(self):
        return {
            'new_id' : self.new_id,
            'title' : self.title,
            'topic' : self.topic,
            'topic_id' : self.topic_id,
            'newspaper' : self.newspaper,
            'newspaper_id' : self.newspaper_id,
            'url' : self.url,
            'publish_date' : self.publish_date,
            'antique' : self.antique,
        }

class GoogleNew(New):
    def __init__(self, topic=''):
        super().__init__(topic=topic)

    def fetch_data(self):

        try:
            self.newspaper = self.html_content.find('div', class_='MgUUmf NUnG9d').text
            self.newspaper = unidecode( self.newspaper ) # Quito los acentos
            self.newspaper = self.newspaper.replace('\n','')
            self.newspaper = self.newspaper.replace('"', '')
            self.newspaper = self.newspaper.replace("'", '')
        except:
            self.newspaper = ''

        try:
            self.title = self.html_content.find('div', class_='n0jPhd ynAwRc MBeuO nDgy9d').text
            self.title = unidecode( self.title ) # Quito los acentos
            self.title = self.title.replace('\n','')
            self.title = self.title.replace('"', '')
            self.title = self.title.replace("'", '')
        except:
            self.title = self.html_content.find('div', class_='n0jPhd ynAwRc tNxQIb nDgy9d').text

        try:
            self.antique = self.html_content.find('div', class_='OSrXXb rbYSKb LfVVr').text
        except:
            self.antique = self.html_content.find('div', class_='OSrXXb rbYSKb').text
        self.antique = unidecode( self.antique ) # Quito los acentos

        # Busco la URL de la noticia
        try:
            self.url = self.html_content.find('a').get('href')
        except:
            self.url = ''

        # Obtengo los datos de fecha
        self.get_google_date()

    def get_google_date(self):
        """ """
        # Reemplazar meses
        self.antique = self.antique.replace('ene',  'jan')
        self.antique = self.antique.replace('abr',  'apr')
        self.antique = self.antique.replace('ago',  'aug')
        self.antique = self.antique.replace('sept', 'sep')
        self.antique = self.antique.replace('dic',  'dec')

        # Validar que la cadena de texto sea válida
        if 'hace' not in self.antique:
            date_obj = datetime.strptime(self.antique, "%d %b %Y")
            date = date_obj.strftime("%d-%m-%Y")
            return f'{date} 12:00:00'

        # Obtener el número y la unidad de tiempo de la cadena
        cantidad, unidad = self.antique.split()[1:]
        cantidad = int(cantidad)

        # Obtener la fecha actual
        cdate = datetime.now()

        # Calcular la fecha de publicación restando la cantidad de tiempo adecuada
        if 'minuto' in unidad:
            date = cdate - timedelta(minutes=cantidad)
        elif 'hora' in unidad:
            date = cdate - timedelta(hours=cantidad)
        elif 'dia' in unidad:
            date = cdate - timedelta(days=cantidad)
        elif 'semana' in unidad:
            date = cdate - timedelta(days=cantidad * 7)  # Suponiendo 30 días por mes
        elif 'mes' in unidad:
            date = cdate - timedelta(days=cantidad * 30)  # Suponiendo 30 días por mes
        elif 'año' in unidad:
            date = cdate - timedelta(days=cantidad * 365)  # Suponiendo 365 días por año

        self.publish_date = '{} {}'.format(
            date.date().strftime("%d-%m-%Y"),
            date.time().strftime("%H:%M:%S.%f")[:-7]
            )

class GoogleSearch:
    def __init__(self, topics=[], enable_MP=True, verbose=True):
        self.topics = topics
        self.enable_MP = enable_MP
        self.verbose = verbose
        self.news_dicc = {}
        self.news = []

    def fetch_news(self):
        """ """
        #
        if self.topics == None:
            print('Se omitio la obtencion de noticias...')
            print('La lista de temas esta vacia')
            return {} # Devuelvo un diccionario vacio

        # Ejecuto el codigo en paralelo o serie
        if self.enable_MP is True:
            self.fetch_news_from_topic_MP()
        else:
            self.fetch_news_from_topic()

        return self.news_dicc

    def fetch_news_from_topic(self):
        """Obtencion de noticias de la forma serie"""
        # Obtengo las noticias para cada tematica
        for topic in self.topics:
            self.fetch_topic_news(topic=topic)

    def fetch_news_from_topic_MP(self, version=1):
        """Obtencion de noticias de la forma paralela"""
        # Defino el numero de threads que puede usar el procesador
        # UPor defecto voy a utilizar la mitad de los hilos
        # disponibles
        nthreads = max(1, os.cpu_count() // 2)

        ############################################################
        # Esta version espera que todos los procesos terminen
        # antes de continuar con la ejecucion del programa
        ############################################################
        if version == 1:
            # Creo una lista para almacenar los procesos
            threads = []

            # Completo el diccionario utilizando ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=nthreads) as executor:
                for topic in self.topics:
                    thread = executor.submit(self.fetch_topic_news, topic)
                    threads.append(thread)

            # Esperar a que todos los hilos finalicen
            for thread in threads:
                thread.result()

        ############################################################
        # Esta version NO espera que todos los procesos terminen
        # antes de continuar con la ejecucion del programa
        ############################################################
        elif version == 2:
            # Creo una lista para almacenar los procesos
            processes = []

            # Completo el diccionario utilizando Process
            for topic in self.topics:
                process = multiprocessing.Process(target=self.fetch_topic_news, args=(topic,))
                processes.append(process)
                process.start()

            # Esperar a que todos los procesos finalicen
            for process in processes:
                process.join()

    def fetch_topic_news(self, topic = 'Netflix'):
        """Obtener las noticias mas relevantes en Google sobre un tema dado"""

        print('- Looking news for topic:', topic)

        # Reemplazo los espacios por signos + para ejecutar la busqueda
        rtopic = topic.replace(' ','+')

        # Defino la URL
        url = f'https://www.google.com/search?q={rtopic}&tbm=nws'

        # Respuesta del servidor
        response = getHTTPResponse(url, headers = None)

        # Obtengo las noticias
        # Intento primero obtener la noticia con el href incluido
        # Si no lo encuentro, busco otra division mas abajo
        html_news = response.find_all('div', class_=['CA8QAA','SoaBEf','xCURGd'])
        if html_news is None:
            html_news = response.find_all('div', class_=['iRPxbe','g5wfEd'])

        # Muestro las noticias
        for k, html_new in enumerate(html_news):
            new = GoogleNew(topic=topic)
            new.html_content = html_new
            new.fetch_data()

            # Agrego la noticia
            self.news.append( new )