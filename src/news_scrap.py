
from datetime import datetime, timedelta
from unidecode import unidecode
import pprint

try:
    from src.db import Database
    from src.news import GoogleSearch
except:
    from db import Database
    from news import GoogleSearch

def get_id(id_field='news_id', table_name='news', search_field='title', target='youtube.com'):
    with Database() as db:
        # Defino la consulta que tengo que realizar
        query = "SELECT {} FROM {} WHERE {} = ?".format(
            id_field, table_name, search_field
            )
        params = (target,)

        # Obtengo el resultado de busqueda
        query_res = db.select(query, params)

        # Si obtengo un resultado lo proceso
        if ((query_res is not None) and
            (len(query_res) > 0)
        ):
            # El resultado es una lista de tuplas
            # Me quedo con el primer elemento
            result = [x[0] for x in query_res]
            id = int(list(set(result))[0])

        # Si no se encuentra el ID obtengo uno nuevo
        else:
            query = f"select max({id_field}) from {table_name}"

            # El resultado es una lista de tuplas
            # Me quedo con el primer elemento
            result = [x[0] for x in query_res]
            max_id = list(set(result))[0]

            # Ultimo check
            if max_id is None:
                id = 1
            else:
                # Genero el proximo ID
                id = int(max_id) + 1

    return id

def scrap_news(enable_MP=True):
    """Funcion para buscar noticias"""

    # Busco informacion de los canales de YouTube
    topics = []

    # Obtengo la lista de canales desde la base de datos
    with Database() as db:
        query = 'select channel_name from channel'
        results = db.select(query)
        channels = [x[0] for x in results]

        # Anexo los canales a la lista de temas
        topics.extend( channels )

    # Agrego algunos otros temas
    topics.append('peliculas infantiles')
    topics.append('amazon')
    topics.append('netflix')
    topics.append('hbo max')
    topics.append('pixar')
    topics.append('pixar elementos')
    topics.append('pixar elemental')

    # Ejecuto la funcion principal del scraper de Google
    gs = GoogleSearch(enable_MP=enable_MP, topics=topics)
    gs.fetch_news()

    # Recorro las noticias y les agrego los ID
    # Guardo los datos en la base de datos
    for new in gs.news:
        # select new_id from news where title = 'lalala'
        # select max(new_id) from news
        new.new_id = get_id(
            id_field='new_id',
            table_name='news',
            search_field='title',
            target=new.title
            )

        new.topic_id = get_id(
            id_field='topic_id',
            table_name='topics',
            search_field='topic',
            target=new.topic
            )

        new.newspaper_id = get_id(
            id_field='newspaper_id',
            table_name='newspapers',
            search_field='newspaper',
            target=new.newspaper
            )

        # Agrego la noticia a la base de datos
        with Database() as db:
            db.insert_news_record( new.to_dicc() )

    return gs.news

if __name__ == '__main__':
    news = scrap_news()

    # Muestro la lista de noticias obtenidas
    for new in news:
        pprint.pprint(new.to_dicc())