# Libraries from Python
import sys
import unittest
import os
import pandas as pd

# My modules
from src.channel import Channel
from src.video import Video
from src.db import Database
from src.db_fetch import *
from src.utils import cprint, getHTTPResponse

# Functions
def set_environment():
    # Get current directory
    home = os.getcwd()

    # Set environment variables
    os.environ["SOFT_HOME"] = home
    os.environ["SOFT_RESULTS"] = os.path.join(home, 'results')
    os.environ["SOFT_UTILS"] = os.path.join(home, 'utils')
    os.environ["SOFT_LOGS"] = os.path.join(home, 'logs')

def unset_environment():
    del os.environ["SOFT_HOME"]
    del os.environ["SOFT_RESULTS"]
    del os.environ["SOFT_UTILS"]
    del os.environ["SOFT_LOGS"]

def execute_db_fetch():
    cprint('Fetching DB...')
    youtube_db_fetch()

def execute_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='./tests/', pattern='test_*.py')
    # suite = loader.discover(start_dir='./tests/', pattern='test_channel.py')
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

def execute_scrap():
    # Open database connection
    with Database() as db:
        # Get channel IDs
        channel_ids = db.get_youtube_channel_ids()

        # Create Channel object list
        channels = []

        # Get dat for each channel
        for channel_id in channel_ids:
            print(f'Fetching HTML content for channel {channel_id}')
            channels.append( Channel(id=channel_id) )

        # Save CSVs
        # Obtain videos dicctionary
        # Update database
        for channel in channels:
            channel.fetch_channel_data()
            channel.save_html_content()

            # Get channel videos ID from DB
            query = 'SELECT VIDEO_ID FROM VIDEO WHERE CHANNEL_ID = ?'
            params = (channel.id,)
            db_ids = db.select(query, params)
            db_ids = [item[0] for item in db_ids]

            # Combine lists
            total_id_list = channel.video_ids_list + db_ids
            channel.video_ids_list = list(set(total_id_list))

            # Update videos data
            channel.fetch_videos_data()

            # Save channel data into database
            db.insert_channel_record(channel.to_dicc())

            # Obtain videos dicctionary
            videos_dicc = channel.get_videos_dicc()

            # Save video data into database
            for key in videos_dicc.keys():
                db.insert_video_record(videos_dicc[key])

def sql_execute(query):
    # Abro la conexion con la base de datos
    with Database() as db:
        # Obtengo la primer palabra
        fw = query.split()[0].lower()

        # Si es un SELECT tengo que mostrar los resultados
        # Ejemplo:
        # python manage.py -sql "SELECT CHANNEL_ID FROM CHANNEL"
        # python manage.py -sql "SELECT * FROM CHANNEL"
        # python manage.py -sql "select * from channel"
        if fw == 'select':
            results = db.select(query, ())
            for result in results:
                print(result)
        # Si es otro tipo de consulta la ejecuto directamente
        # Ejemplo
        # python manage.py -sql "update channel set channel_name = 'toycantando_edit' where channel_id = 'UC2xjgvWb9cx5F637XjsUNxw'"
        # python manage.py -sql "update channel set channel_name = 'toycantando' where channel_id = 'UC2xjgvWb9cx5F637XjsUNxw'"
        else:
            db.exec(query)

# Funcion principal del programa
if __name__ == '__main__':
    # Preparo el entorno para operar
    set_environment()

    # Obtengo los argumentos dados al programa
    args = sys.argv

    # Obtener el nombre del script
    script_name = args[0]

    # Recorrer los demas argumentos
    for kk, arg in enumerate(args[1:]):

        # Ejecuto los tests de los modulos
        if arg == '-runtest':
            execute_tests()

        # Ejecuto el scraping
        if arg == '-runscrap':
            subarg_1 = args[kk + 2] if kk + 2 < len(args) else None
            subarg_2 = args[kk + 3] if kk + 3 < len(args) else None
            subarg_3 = args[kk + 4] if kk + 4 < len(args) else None

            # Obtengo el mensaje de ayuda
            if subarg_1 == '-help':
                print('Usage:')
                print(f'python {script_name} {arg} []')
                print( '\t NULL : Execute all scraps')
                print( '\t -all : Execute all scraps')
                print( '\t -video <video_id/"url"> [] : Scrap a single video')
                print( '\t\t -save_html : Save HTML content (optional)')

            # Obtengo la informacion de un video unico
            if subarg_1 == '-video':

                # Verifico si el argumento de entrada es una URL
                # Ejemplo:
                # python manage.py -runscrap -video "https://www.youtube.com/watch?v=55O5Gnwbp14&ab_channel=Acre" -save_html
                if '.com' in subarg_2:
                    url = subarg_2
                    html_content = getHTTPResponse(url, responseType = 'text')
                    video = Video(html_content=html_content)

                # Sino, tomo al argumento de entrada como un ID
                # Ejemplo:
                # python manage.py -runscrap -video 55O5Gnwbp14 -save_html
                else:
                    video_id = subarg_2
                    video = Video(id=video_id, en_html_save=False)

                # Guardo el contenido HTML si fuera necesario
                if subarg_3 == '-save_html':
                    video.save_html_content()

            # Ejecuto todo el scraper
            # Ejemplo:
            # python manage.py -runscrap -all
            # python manage.py -runscrap
            if ((subarg_1 == '-all') or
                (subarg_1 is None and subarg_2 is None)
               ):
                execute_scrap()

        if arg == '-sql':
            subarg_1 = args[kk + 2] if kk + 2 < len(args) else None
            subarg_2 = args[kk + 3] if kk + 3 < len(args) else None

            # Obtengo el mensaje de ayuda
            if subarg_1 == '-help':
                print('Usage:')
                print(f'python {script_name} {arg} []')
                print( '\t "query" : Execute the given query')

            # Verifico si tengo que leer un archivo
            # Ejemplo
            # python manage.py -sql -file sql/0015_query_1.sql
            if subarg_1 == '-file':
                filename = subarg_2
                try:
                    with open(filename, "r") as archivo:
                        query = archivo.read()  # Lee todo el contenido del archivo y lo almacena en la cadena 'contenido'

                    # Ahora 'contenido' contiene el contenido del archivo como una cadena
                    print("SQL query:\n\n" + query)

                    # Ejecuto el comando
                    sql_execute(query)

                except FileNotFoundError:
                    print(f"El archivo '{filename}' no fue encontrado.")
                except Exception as e:
                    print(f"Ocurrió un error: {e}")

            # Ejecuto el comando SQL
            else:
                query = subarg_1
                sql_execute(query)

        if arg == '-fetch':
            execute_db_fetch()

    # Clear environment variables
    unset_environment()