# Libraries from Python
import sys
import unittest

# My modules
from src.db import Database
import src.scrap_youtube as yt
import src.sql as sql
import src.db_fetch as dbf
import src.environment as env

# Functions
def execute_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='./tests/', pattern='test_*.py')
    # suite = loader.discover(start_dir='./tests/', pattern='test_channel.py')
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

# Funcion principal del programa
if __name__ == '__main__':
    # Preparo el entorno para operar
    env.set_environment()

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
                yt.scrap_youtube_help(script_name, arg)

            # Obtengo la informacion de un video unico
            if subarg_1 == '-video':
                if '.com' in subarg_2:
                    video = yt.scrap_video_w_url(subarg_2)
                else:
                    video = yt.scrap_video_w_id(subarg_2)

                # Guardo el contenido HTML si fuera necesario
                if subarg_3 == '-save_html':
                    video.save_html_content()

            # Ejecuto todo el scraper
            if ((subarg_1 == '-all') or
                (subarg_1 is None and subarg_2 is None)
               ):
                yt.scrap_youtube()

        if arg == '-sql':
            subarg_1 = args[kk + 2] if kk + 2 < len(args) else None
            subarg_2 = args[kk + 3] if kk + 3 < len(args) else None

            # Obtengo el mensaje de ayuda
            if subarg_1 == '-help':
                sql.sql_help(script_name, arg)

            # Verifico si tengo que leer un archivo
            # Cargo la consulta y la ejecuto
            if subarg_1 == '-file':
                query = sql.sql_get_query_fromfile(subarg_2)
                sql.sql_execute(query)

            # Ejecuto el comando SQL
            else:
                sql.sql_execute(subarg_1)

        if arg == '-fetch':
            print('Fetching DB...')
            dbf.youtube_db_fetch()

        if arg == '-export':
            subarg_1 = args[kk + 2] if kk + 2 < len(args) else None

            # Exporto todas las tablas de la base de datos
            # en formato ".csv"
            if subarg_1 == '-tocsv':
                with Database() as db:
                    db.export_table(ext='.csv')

            # Exporto todas las tablas de la base de datos
            # en formato ".xlsx"
            if subarg_1 == '-toexcel':
                with Database() as db:
                    db.export_table(ext='.xlsx')

        if arg == '-genbkp':
            dbf.sql_generate_db_backup()

    # Clear environment variables
    env.unset_environment()