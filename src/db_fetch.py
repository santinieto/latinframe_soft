import os
import pandas as pd
import datetime
import shutil

from src.db import Database
from src.utils import cprint
from src.utils import get_formatted_date

def youtube_db_fetch():
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Obtengo el directorio actual
    home = os.getcwd()

    # Seteo variables de entorno
    os.environ["SOFT_UTILS"] = os.path.join(home, 'utils')

    # Obtengo la lista de canales que esta en el .csv
    utils_path = os.environ.get("SOFT_UTILS")
    csv_path = os.path.join(utils_path, "Youtube_channelIDs.csv")
    channels_df = pd.read_csv(csv_path).dropna().dropna(axis=1)
    csv_ids = channels_df['channelID'].to_list()

    # Abro la conexion con la base datos
    with Database() as db:
        # Obtengo todos los IDs presentes en la base de datos
        db_channel_ids = db.get_youtube_channel_ids(table_name = 'CHANNEL')
        db_channel_records_ids = db.get_youtube_channel_ids(table_name = 'CHANNEL_RECORDS')
        db_video_ids = db.get_youtube_channel_ids(table_name = 'VIDEO')

        # Combino todas las listas y me quedo con los que no esten en la tabla CHANNEL
        total_id_list = list(set(csv_ids + db_channel_ids + db_channel_records_ids + db_video_ids))
        to_add_list = [x for x in total_id_list if x not in db_channel_ids]

        # Agrego los canales faltantes
        for to_add_id in to_add_list:
            cprint(f'Adding {to_add_id} to DB.[CHANNEL]')
            query = '''
            INSERT OR REPLACE INTO CHANNEL (
                CHANNEL_ID, CHANNEL_NAME, UPDATE_DATE
            ) VALUES (?, ?, ?)
            '''
            params = (
                to_add_id,
                '<channel_name>',
                current_time
            )
            db.exec(query, params)

def sql_generate_db_backup():
    """
    Genero un backup de la base de datos anexandole la fecha
    y hora actual
    """

    date = get_formatted_date()

    # Abro la conexion con la base de datos
    with Database() as db:

        # Rutas de origen y destino
        bkp_filename = 'db_backups/' + db.db_name.replace('.db',f'_{date}.db')

        try:
            # Copia el archivo de la ruta de origen a la ruta de destino
            shutil.copy(db.db_name, bkp_filename)
            print(f"Archivo copiado de '{db.db_name}' a '{bkp_filename}'.")
        except FileNotFoundError:
            print("El archivo de origen no fue encontrado.")
        except shutil.SameFileError:
            print("El archivo de origen y destino son el mismo archivo.")
        except PermissionError:
            print("No tienes permisos para copiar el archivo.")
        except Exception as e:
            print(f"Ocurrió un error: {e}")
