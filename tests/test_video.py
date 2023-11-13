import unittest
from src.youtube import YoutubeVideo
from src.utils import getHTTPResponse
import re

class TestVideo(unittest.TestCase):

    def test_create_video_object(self):
        try:
            video_obj = YoutubeVideo()
        except Exception as e:
            self.fail(f"Could not create Video object.\n\tError value: {str(e)}")

    def test_create_empty_video(self):
        video = YoutubeVideo()
        self.assertEqual(None, video.id, 'Error while checking Video object generation')
        self.assertEqual('Unknown', video.title, 'Error while checking Video object generation')

    def test_get_video_id(self):
        video_id = 'tNba_Da5sHk'
        video = YoutubeVideo(id=video_id)
        self.assertEqual(video_id, video.id, 'Error while checking Video ID generation')

    def test_video_belongs_to_playlist(self):
        url = 'https://www.youtube.com/watch?v=qY_qmvQ2rQ'
        html_content = getHTTPResponse(url, responseType='text')

        # print(f'- URL inicial: {url}')
        # print(f'- URL final: {response.url}')

        # # Verifica si hubo redirecciones
        # if response.history:
        #     print("URL redireccionada:")
        #     for resp in response.history:
        #         print(resp.url)

        # Guardo el contenido html
        with open('video.dat', 'w', encoding='utf-8') as archivo:
            archivo.write(html_content)

        # Patrón regular para encontrar la URL de la lista de reproducción
        # patron = r'playlist\?list=\w+'
        patron = r'"playlistId":"(PL[^"]+)"'

        # Buscar la coincidencia en la cadena
        resultado = re.search(patron, html_content)
        print

        # Comprobar si se encontró una coincidencia
        if resultado:
            url_lista_reproduccion = resultado.group(1)
            print("URL de la lista de reproducción:", url_lista_reproduccion)
        else:
            print("No se encontró una URL de lista de reproducción en la cadena.")

if __name__ == '__main__':
    unittest.main()