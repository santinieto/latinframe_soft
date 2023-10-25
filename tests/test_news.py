import unittest
import pprint
from src.db import Database
from src.news_scrap import get_id

class TestNews(unittest.TestCase):

    def test_title_with_comma(self):
        new = {
            'new_id' : 999,
            'title' : "'30 monedas' (2x01): guadañas y drones en un espléndido arranque de la temporada 2 de la serie de HBO",
            'topic' : 'HBO Test',
            'topic_id' : 999,
            'newspaper' : 'Espinof',
            'newspaper_id' : 999,
            'url' : 'https://www.espinof.com/criticas/30-monedas-2x01-guadanas-drones-esplendido-arranque-temporada-2-serie-hbo',
            'publish_date' : '2023/10/24 12:00:00',
            'antique' : 'Hace un dia',
        }
        pprint.pprint(new)

        with Database() as db:
            db.insert_news_record( new )

    def test_get_id(self):
        # Creo una noticia de prueba
        new = {
            'new_id' : 999,
            'title' : "'30 monedas' (2x01): guadañas y drones en un espléndido arranque de la temporada 2 de la serie de HBO",
            'topic' : 'HBO Test',
            'topic_id' : 999,
            'newspaper' : 'Espinof',
            'newspaper_id' : 999,
            'url' : 'https://www.espinof.com/criticas/30-monedas-2x01-guadanas-drones-esplendido-arranque-temporada-2-serie-hbo',
            'publish_date' : '2023/10/24 12:00:00',
            'antique' : 'Hace un dia',
        }
        # La muestro en pantalla
        pprint.pprint(new)

        # La agrego a la base de datos
        with Database() as db:
            db.insert_news_record( new )

        # Otengo el ID
        id = get_id(
            id_field='new_id',
            table_name='news',
            search_field='title',
            target=new['title']
            )

        # Muestro en pantalla el resultado obtenido
        print('ID obtenido: {}'.format(id))

        # Comprueba si el resultado obtenido es igual al esperado
        self.assertEqual(id, new['new_id'])

if __name__ == '__main__':
    unittest.main()