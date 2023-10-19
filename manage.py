# Libraries from Python
import sys

# My modules
from src.db import Database
from src.test import Test
import src.youtube_scrap as yt
import src.sql as sql
import src.db_fetch as dbf
import src.environment as env

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
        if arg == '-test':
            subarg_1 = args[kk + 2] if kk + 2 < len(args) else None
            subarg_2 = args[kk + 3] if kk + 3 < len(args) else None

            # Armo la lista de tests disponibles
            t = Test(start_dir='./tests/')
            t.get_suite(pattern='test_*.py')
            t.generate_test_list()

            # Imprimo el mensaje de ayuda
            if subarg_1 == '-h':
                t.help(script_name, arg)

            # Listo los tests y puedo aplicar un filtro si quiero
            if subarg_1 == '-l':
                pattern = None if subarg_2 is None else subarg_2
                t.show_test_list(pattern = pattern)

            # Ejecuto alguno de los tests
            if subarg_1 == '-r':
                test_list = subarg_2.split('-')
                for test in test_list:
                    t.run(int(test))

        # Ejecuto el scraping
        if arg == '-runscrap':
            subarg_1 = args[kk + 2] if kk + 2 < len(args) else None
            subarg_2 = args[kk + 3] if kk + 3 < len(args) else None
            subarg_3 = args[kk + 4] if kk + 4 < len(args) else None
            subarg_4 = args[kk + 5] if kk + 5 < len(args) else None

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
                if ((subarg_3 == '-save_html') or
                    (subarg_4 == '-save_html')
                ):
                    video.save_html_content()

                # Agrego el registro a la base de datos si es requerido
                if ((subarg_3 == '-add') or
                    (subarg_4 == '-add')
                ):
                    with Database() as db:
                        db.insert_video_record(video.to_dicc())

            # Obtengo la informacion de un canal unico
            if subarg_1 == '-channel':
                if '.com' in subarg_2:
                    channel = yt.scrap_channel_w_url(subarg_2)
                else:
                    channel = yt.scrap_channel_w_id(subarg_2)
                channel.fetch_channel_data()

                # Guardo el contenido HTML si fuera necesario
                if subarg_3 == '-save_html':
                    channel.save_html_content()

                # Agrego el registro a la base de datos si es requerido
                if ((subarg_3 == '-add') or
                    (subarg_4 == '-add')
                ):
                    with Database() as db:
                        db.insert_channel_record(channel.to_dicc())

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

        if arg == '-db':
            subarg_1 = args[kk + 2] if kk + 2 < len(args) else None
            subarg_2 = args[kk + 3] if kk + 3 < len(args) else None
            subarg_3 = args[kk + 4] if kk + 4 < len(args) else None
            subarg_4 = args[kk + 5] if kk + 5 < len(args) else None

            if subarg_1 == '-get':
                with Database() as db:
                    db.process_data(op='select',type=subarg_2, sel=subarg_3, val=subarg_4)
            elif subarg_1 == '-del':
                with Database() as db:
                    db.process_data(op='del',type=subarg_2, sel=subarg_3, val=subarg_4)

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