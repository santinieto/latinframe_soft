import unittest
from src.youtube import YoutubeChannel
from src.db import Database
from src.utils import getHTTPResponse

class TestChannel(unittest.TestCase):

    def test_create_channel_object(self):
        try:
            channel_obj = YoutubeChannel()
        except Exception as e:
            self.fail(f"Could not create Channel object.\n\tError value: {str(e)}")

    def test_channel_1(self):
        channel = YoutubeChannel(id='UCK1i2UviaXLUNrZlAFpw_jA')
        channel.fetch_channel_data()
        channel.fetch_videos_data()
        print(str(channel))

    def test_channel_2(self):
        channel = YoutubeChannel(id='UCu60hbJGH8nlCSFwfVe_wwA')
        channel.fetch_channel_data()
        print(str(channel))

    def test_channel_load_videos_ids(self):
        channel = YoutubeChannel(id='UCu60hbJGH8nlCSFwfVe_wwA')
        channel.fetch_channel_data()

        # Get channel videos ID from DB
        with Database() as db:
            query = 'SELECT VIDEO_ID FROM VIDEO WHERE CHANNEL_ID = ?'
            params = (channel.id,)
            db_ids = db.select(query, params)
            db_ids = [item[0] for item in db_ids]

        # Show scrapped videos and videos obtained from DB
        print('Scrapped videos:', len(channel.video_ids_list))
        print('Videos from DB:', len(db_ids))

        # Combine lists
        total_id_list = channel.video_ids_list + db_ids
        channel.video_ids_list = list(set(total_id_list))

        # Show final IDs list
        print('Final ID list len:', len(channel.video_ids_list))

    def test_channel_load_channel_ids(self):
        import os
        import pandas as pd

        # Get current directory
        home = os.getcwd()

        # Set environment variables
        os.environ["SOFT_UTILS"] = os.path.join(home, 'utils')

        # Load channels from CSV
        utils_path = os.environ.get("SOFT_UTILS")
        csv_path = os.path.join(utils_path, "Youtube_channelIDs.csv")
        channels_df = pd.read_csv(csv_path).dropna().dropna(axis=1)
        csv_ids = channels_df['channelID'].to_list()

        # Get channel IDs from DB
        with Database() as db:
            query = 'SELECT CHANNEL_ID FROM CHANNEL'
            db_ids = db.select(query, ())
            db_ids = [item[0] for item in db_ids]

        print('Channels from CSV:', len(channels_df))
        print('Channels from DB:', len(db_ids))

        # Combine lists
        total_id_list = list(set(csv_ids + db_ids))
        print('Total IDs count:', len(total_id_list))

    def test_get_channel_subchannels(self):
        import re

        url = 'https://www.youtube.com/@CoComelonEspanol/channels'
        html_content = getHTTPResponse(url, responseType='text')

        # Patrón regular para encontrar los argumentos de canonicalBaseUrl
        patron = r'canonicalBaseUrl":"/([^"]+)"'

        # Busca todas las coincidencias del patrón en el texto
        coincidencias = re.findall(patron, html_content)

        # Elimino los duplicados
        coincidencias = list( set( coincidencias ) )

        # Imprime los argumentos encontrados
        for argumento in coincidencias:
            print(argumento)

    def test_get_channel_subchannels_2(self):
        import re
        import json

        url = 'https://www.youtube.com/@CoComelonEspanol/channels'
        html_content = getHTTPResponse(url, responseType='text')

        # Expresión regular para buscar browseEndpoint
        regex = r'"browseEndpoint":{[^{}]*?}'
        matches = re.findall(regex, html_content)

        # Crear un diccionario para almacenar los resultados
        resultados = []

        # Procesar las coincidencias
        for match in matches:
            # Parsear el JSON encontrado en la coincidencia
            data = json.loads("{" + match + "}")

            # Verificar si el objeto tiene tanto 'browseId' como 'canonicalBaseUrl'
            if "browseId" in data["browseEndpoint"] and "canonicalBaseUrl" in data["browseEndpoint"]:
                # Extraer el valor de 'browseId'
                browse_id = data["browseEndpoint"]["browseId"]

                # Extraer el valor de 'canonicalBaseUrl'
                canonical_base_url = data["browseEndpoint"]["canonicalBaseUrl"]

                # Agregar una tupla con los valores al resultado
                resultados.append((browse_id, canonical_base_url))

        # Elimino duplicados
        resultados = list( set( resultados ) )

        # Imprimir el resultado
        print(resultados)

if __name__ == '__main__':
    unittest.main()