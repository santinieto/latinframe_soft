# Libraries from Python
from bs4 import BeautifulSoup
from pytube import YouTube
import re
import json
import requests
import os
from datetime import datetime
import multiprocessing

# Modules and functions
from src.utils import getHTTPResponse
from src.utils import get_time_len
from src.utils import cprint
from src.utils import o_fmt_error
from src.utils import get_formatted_date
from src.utils import StrNum2RealNum

# Define a function to fetch video data and put it into the shared dictionary
def fetch_video_data(id, videos_dicc, canal_instance=None):
    video = YoutubeVideo(id)  # Assuming YoutubeVideo is a class constructor
    video_data = video.fetch_data()  # Replace with your method to fetch data
    videos_dicc[id] = video_data

    if canal_instance is not None:
        canal_instance.add_video(video)

class YoutubeChannel:
    def __init__(self, id=None, html_content=None, input_dicc=None, enable_MP=True, debug=True):
        """ Constructor of class YoutubeChannel, it requires one of two options:
            - YoutubeChannel ID to look on Youtube
            - Scrap of HTML content to look the information
        """

        # Establezco los valores por defecto
        self.set_default()
        self.debug = debug
        self.enable_MP = enable_MP

        # Verifico si tengo un diccionario para cargar
        if input_dicc is not None:
            self.id = id
            self.html_content = html_content
            self.set_from_dicc(input_dicc)

        # Verifico si tengo un contenido HTML para cargar
        elif html_content is not None:
            self.html_content = html_content
            self.id = id
            self.get_id()

        # Verifico si tengo un ID para cargar
        elif id is not None:
            self.id = id
            self.html_content = html_content
            self.get_html_content()

        # Si no tengo nada largo un mensaje de error
        else:
            self.id = id
            self.html_content = html_content
            # Log error message
            msg = f'Could not create a YoutubeChannel object with giving an ID or HTML scrap. Data could not be collected'
            o_fmt_error('0001', msg, 'Class__YoutubeChannel')

    def set_from_dicc(self, input_dicc):
        self.id = input_dicc['channelID']
        self.channel_name = input_dicc['channelName']
        self.views = input_dicc['channelViews']
        self.nVideos = input_dicc['nVideos']
        self.subscribers = input_dicc['suscribers']
        self.daily_subs = input_dicc['dailySub']
        self.monthly_subs = input_dicc['monthlySub']

    def set_default(self):
        self.views = 0
        self.nVideos = 0
        self.subscribers = 0
        self.daily_subs = 0
        self.monthly_subs = 0
        self.video_ids_list = []
        self.videos = []
        self.subchannels = []

    def add_video(self, video):
        self.videos.append(video)

    def __str__(self):
        """Returns all fields on the class to be displayed into the screen/file."""

        ans  = f"- Youtube Channel ID: {self.id}\n"
        ans += f"- Youtube Channel name: {self.channel_name}\n"
        ans += f"- Youtube Channel views: {self.views}\n"
        ans += f"- Youtube Channel videos: {self.nVideos}\n"
        ans += f"- Youtube Channel subscribers: {self.subscribers}\n"
        ans += f"- Youtube Channel monthly subscribers: {self.monthly_subs}\n"
        ans += f"- Youtube Channel daily subscribers: {self.daily_subs}\n"
        ans += f"- Youtube Channel video IDs: {self.video_ids_list}\n"
        ans += f"- Youtube Channel subchannels: {self.subchannels}"
        return ans

    def to_dicc(self):
        return {
            'channelID': self.id,
            'channelName': self.channel_name,
            'views': self.views,
            'nVideos': self.nVideos,
            'subscribers': self.subscribers,
            'monthly_subs': self.monthly_subs,
            'daily_subs': self.daily_subs,
        }

    def get_html_content(self, url_type='id', ovr_id=None, scrap_url=None):
        """ Get the HTML scrap for the given channel.
            This method recives an URL template to scrap but it
            sets one if (scrap_url) is None.
            Here we can overwrite the channel ID if field (ovr_id) is not None
        """

        # Define a default URL to scrap
        if scrap_url is None:
            scrap_url = 'https://www.youtube.com/channel'

        # Obtengo la lista de videos
        if url_type == 'name':
            # URL del canal de YouTube
            scrap_url = 'https://www.youtube.com/@' + {self.channel_name}
        elif url_type == 'id':
            # URL del canal de YouTube
            scrap_url = 'https://www.youtube.com/channel/' + self.id
        elif url_type == 'url':
            # URL del canal de YouTube
            scrap_url = scrap_url

        # If the channel ID is being overwritten use this clause
        if ovr_id is not None:
            self.id = ovr_id

        # Get HTML content
        self.html_content = getHTTPResponse(scrap_url, responseType = 'text')

    def save_html_content(self):
        # Create file name
        date = get_formatted_date()
        filepath = os.path.join(os.environ.get("SOFT_RESULTS"), 'channels')
        filename = filepath + f'/html_channel_{self.id}_date_{date}.dat'
        # Save HTML content
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(self.html_content)

    def fetch_channel_data(self):
        """ Fetch the channel data from the HTML code loaded.
            It logs an error if the HTML is None.
        """
        if self.html_content is None:
            # Log error message
            msg = f'Could not fetch information for channel {self.id} without a HTML content loaded'
            o_fmt_error('0002', msg, 'Class__YoutubeChannel')
        else:
            # Fetch channel information
            self.fetch_channel_name()
            self.fetch_subchannels()
            self.fetch_channel_video_ids()
            self.fetch_channel_stats()
            # Debug
            if self.debug is True:
                cprint('')
                cprint('-' * 100)
                cprint(str(self))
                cprint('-' * 100)

    def _fetch_data_from_pattern(self, pattern, html, err_code, err_msg):
        """Get data from HTML content given a pattern"""
        try:
            return re.search(pattern, html).group(1)
        except Exception as e:
            # Log error message
            o_fmt_error(err_code, err_msg, 'Class__YoutubeChannel')
            # Return a None value
            return None

    def get_id(self, pattern=None):
        """Get channel ID using pattern"""

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'youtube\.com/channel/([A-Za-z0-9_-]+)' if pattern is None else pattern

        # Get the required information using the classic method
        err_code = '0003'
        err_msg = f'Could not fetch channel ID for pattern {pattern}'
        self.id = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )
        if self.id is not None:
            self.id = self.id.replace('/@','')

        # Try an alternative method
        if self.id is None:
            try:
                # Transform response to a BS object
                response = BeautifulSoup(self.html_content, 'html.parser')
                # Look of <link> element with attribute rel="canonical"
                elemento_link = response.find('link', rel='canonical')
                # Get the href value
                href = elemento_link.get('href')
                # Get the channel ID
                self.id = href.split('/')[-1]
            except:
                err_code = '0004'
                err_msg = f'Could not fetch channel ID for pattern {pattern} using the alternative method'
                o_fmt_error(err_code, err_msg, 'Class__YoutubeChannel')

        # Set a default title if everything above failed
        if self.id is None:
            self.id = "Unknown"

    def fetch_channel_name(self, pattern=None):
        """Get channel name using pattern"""
        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"canonicalBaseUrl":"(.*?)"' if pattern is None else pattern

        # Get the required information using the classic method
        err_code = '0005'
        err_msg = f'Could not fetch channel name for channel {self.id} for pattern {pattern}'
        self.channel_name = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )
        if self.channel_name is not None:
            self.channel_name = self.channel_name.replace('/@','')

        # Set a default title if everything above failed
        if self.channel_name is None:
            self.channel_name = "Unknown"

    def fetch_subchannels(self):

        url = f'https://www.youtube.com/channel/{self.id}/channels'
        tmp_html_content = getHTTPResponse(url, responseType='text')

        # Expresión regular para buscar browseEndpoint
        regex = r'"browseEndpoint":{[^{}]*?}'
        matches = re.findall(regex, tmp_html_content)

        # Procesar las coincidencias
        for match in matches:
            # Parsear el JSON encontrado en la coincidencia
            data = json.loads("{" + match + "}")

            # Verificar si el objeto tiene tanto 'browseId' como 'canonicalBaseUrl'
            if( ("browseId" in data["browseEndpoint"]) and
                ("canonicalBaseUrl" in data["browseEndpoint"])
            ):
                # Extraer el valor de 'browseId'
                browse_id = data["browseEndpoint"]["browseId"]

                # Extraer el valor de 'canonicalBaseUrl'
                canonical_base_url = data["browseEndpoint"]["canonicalBaseUrl"]

                # Agregar una tupla con los valores al resultado
                # Un canal no se agrega a si mismo como subcanal
                if browse_id != self.id:
                    self.subchannels.append((browse_id, canonical_base_url))

        # Elimino duplicados
        self.subchannels = list( set( self.subchannels ) )

    def fetch_channel_video_ids(self, pattern=None):
        """Get most recent videos list"""
        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"videoId":"(.*?)"' if pattern is None else pattern

        # Get the required information using the classic method
        try:
            self.video_ids_list = re.findall(pattern, self.html_content)
            self.video_ids_list = list(set(self.video_ids_list))
        except Exception as e:
            self.video_ids_list = None
            err_code = '0006'
            err_msg = f'Could not fetch channel video IDs for channel {self.id} for pattern {pattern}'
            o_fmt_error(err_code, err_msg, 'Class__YoutubeChannel')

        # Set a default title if everything above failed
        if self.video_ids_list is None:
            self.video_ids_list = []

    def fetch_channel_stats(self):
        """"""
        # Set the URL to scrap
        url = f'https://socialcounts.org/youtube-live-subscriber-count/{self.id}'

        # Obtain HTTP response
        response = getHTTPResponse(url)

        if response is False:
            # Manage error
            pass

        # Fetch subscribers
        try:
            self.subscribers = response.find(
                class_='jsx-b59614d5220954ed id_odometer__ofLL8 mainOdometer'
            ).text
        except:
            self.subscribers = 0

        # Fetch more data
        try:
            info = response.find_all(
                class_='id_main_profile__2xQ33 id_odometer2__u1xPo'
            )
        except:
            pass

        try:
            self.views = StrNum2RealNum(info[0].text.replace('Channel Views',''))
        except:
            self.views = 0
        try:
            self.nVideos = StrNum2RealNum(info[1].text.replace('Videos',''))
        except:
            self.nVideos = 0
        try:
            self.daily_subs = StrNum2RealNum(info[2].text.replace('Daily sub ',''))
        except:
            self.daily_subs = 0
        try:
            self.monthly_subs = StrNum2RealNum(info[3].text.replace('Monthly sub ',''))
        except:
            self.monthly_subs = 0

    def fetch_videos_data(self):
        """"""
        # Scrap vidoeos
        if self.enable_MP is True:
            # Define the number of threads
            # Use the half of the total trheads in the proccesor
            nthreads = max(1, os.cpu_count() // 2)

            # Initialice the procceses
            pool = multiprocessing.Pool(processes=nthreads)

            # Create video instances
            self.videos = pool.map(YoutubeVideo, self.video_ids_list)

            # Close pool
            pool.close()
            pool.join()
        else:
            pass
            # videosDicc = processVideos(recentVideos, channelName, channelID, verbose=False)

        for video in self.videos:
            video.channel_id = self.id
            video.channel_name = self.channel_name

    def get_videos_dicc(self):
        videos_dicc = {}
        for video in self.videos:
            videos_dicc[video.id] = video.to_dicc()
        return videos_dicc

class YoutubeVideo:
    def __init__(self, id=None, html_content=None, input_dicc=None, debug=True, en_html_save=True):
        """ Constructor of class YoutubeVideo, it requires one of two options:
            - Video ID to look on Youtube
            - Scrap of HTML content to look the information
        """

        # Establezco los valores por defecto
        self.set_default()
        self.debug = debug
        self.en_html_save = en_html_save

        # Verifico si tengo un diccionario para cargar
        if input_dicc is not None:
            self.id = id
            self.html_content = html_content
            self.set_from_dicc(input_dicc)

        # Verifico si tengo un contenido HTML para cargar
        elif html_content is not None:
            self.html_content = html_content
            self.id = id
            self.get_id()

        # Verifico si tengo un ID para cargar
        elif id is not None:
            self.id = id
            self.html_content = html_content
            self.get_html_content()

        # Si no tengo nada largo un mensaje de error
        else:
            self.id = id
            self.html_content = html_content
            # Log error message
            msg = f'Could not create a YoutubeVideo object with giving an ID or HTML scrap. Data could not be collected'
            o_fmt_error('0001', msg, 'Class__YoutubeVideo')

        if input_dicc is None:
            # Fetch data for every video
            self.fetch_data()

        # Debug
        if self.debug is True:
            cprint(f'Created YoutubeVideo object for ID: {self.id}')

    def set_default(self):
        # Set defaults values for the class variables
        self.id = ''
        self.html_content = ''
        self.channel_id = ''
        self.channel_name = ''
        self.title = "Unknown"
        self.views = 0
        self.likes = 0
        self.length = '00:00:00'
        self.comments_cnt = 0
        self.mvm = '00:00:00'
        self.tags = "None"
        self.publish_date = "00/00/00"
        self.process_success = True

    def __str__(self):
        """Returns all fields on the class to be displayed into the screen/file."""

        ans  = f"\t- Youtube Video ID: {self.id}\n"
        ans += f"\t- Youtube Video name: {self.title}\n"
        ans += f"\t- Youtube Channel ID: {self.channel_id}\n"
        ans += f"\t- Youtube Channel name: {self.channel_name}\n"
        ans += f"\t- Youtube Video views: {self.views}\n"
        ans += f"\t- Youtube Video likes: {self.likes}\n"
        ans += f"\t- Youtube Video length: {self.length}\n"
        ans += f"\t- Youtube Video comments: {self.comments_cnt}\n"
        ans += f"\t- Youtube Video MVM: {self.mvm}\n"
        ans += f"\t- Youtube Video Publish date: {self.publish_date}\n"
        ans += f"\t- Youtube Video tags: {self.tags}"
        return ans

    def to_dicc(self):
        return {
            'videoID': self.id,
            'videoName': self.title,
            'channelID': self.channel_id,
            'channelName': self.channel_name,
            'views': self.views,
            'videoLength': self.length,
            'mostViewedMoment': self.mvm,
            'likes': self.likes,
            'videoTags': self.tags,
            'publishDate': self.publish_date,
            'videoCommentsCount': self.comments_cnt,
        }

    def set_from_dicc(self, input_dicc):
        self.id = input_dicc['id']
        self.title = input_dicc['title']
        self.channel_id = input_dicc['channel_id']
        self.channel_name = input_dicc['channel_name']
        self.views = input_dicc['views']
        self.length = input_dicc['length']
        self.mvm = input_dicc['mvm']
        self.likes = input_dicc['likes']
        self.tags = input_dicc['tags']
        self.publish_date = input_dicc['publish_date']
        self.comments_cnt = input_dicc['comments_cnt']

    def get_id(self, pattern=None):
        """Get the ID for the video from the HTML content"""

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"videoId":"(.*?)"' if pattern is None else pattern

        # Get the required information using the classic method
        err_code = '0017'
        err_msg = f'Could not fetch ID for video. Pattern {pattern}'
        self.id = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )

        # Aca deberia haber otro intento de procesamiento
        if self.id is None:
            # Bajo la bandera de analisis correcto
            self.process_success = False

    def get_channel_id(self, pattern=None):
        """Get the YoutubeChannel ID for the video from the HTML content"""

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"channelId":"(.*?)"' if pattern is None else pattern

        # Get the required information using the classic method
        err_code = '0018'
        err_msg = f'Could not fetch YoutubeChannel ID for video. Pattern {pattern}'
        self.channel_id = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )

        # Aca deberia haber otro intento de procesamiento
        if self.channel_id is None:
            # Bajo la bandera de analisis correcto
            self.process_success = False

    def get_channel_name(self, pattern=None):
        """Get the YoutubeChannel name for the video from the HTML content"""

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"ownerChannelName":"(.*?)"' if pattern is None else pattern

        # Get the required information using the classic method
        err_code = '0019'
        err_msg = f'Could not fetch YoutubeChannel name for video. Pattern {pattern}'
        self.channel_name = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )

        # Aca deberia haber otro intento de procesamiento
        if self.channel_name is None:
            # Bajo la bandera de analisis correcto
            self.process_success = False

    def get_html_content(self, ovr_id=None, scrap_url=None):
        """ Get the HTML scrap for the given video.
            This method recives an URL template to scrap but it
            sets one if (scrap_url) is None.
            Here we can overwrite the video ID if field (ovr_id) is not None
        """

        # Define a default URL to scrap
        if scrap_url is None:
            scrap_url = 'https://www.youtube.com/watch?v='

        # If the video ID is being overwritten use this clause
        if ovr_id is not None:
            self.id = ovr_id

        # Get HTML content for the required URL
        self.html_content = getHTTPResponse(scrap_url + self.id, responseType = 'text')

    def save_html_content(self):
        # Debug
        if self.debug is True:
            cprint(f'\t- Saving HTML scrap for YoutubeVideo {self.id}')
        # Create file name
        date = get_formatted_date()
        filepath = os.path.join(os.environ.get("SOFT_RESULTS"), 'videos')
        filename = filepath + f'/html_video_{self.id}_date_{date}.dat'
        # Save HTML content
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(self.html_content)

    def fetch_data(self):
        """ Fetch the video data from the HTML code loaded.
            It logs an error if the HTML is None.
        """

        # Debug
        if self.debug is True:
            cprint(f'Fetching data for YoutubeVideo {self.id}... ')

        # Logs an error if no HTML content is loaded
        if self.html_content is None:
            # Log error message
            msg = f'Could not fetch information for video {self.id} without a HTML content loaded'
            o_fmt_error('0004', msg, 'Class__YoutubeVideo')
            # Debug
            if self.debug is True:
                cprint('ERROR!')
        else:
            # Fetch video information
            self.fetch_title()
            self.fetch_views()
            self.fetch_most_viewed_moment()
            self.fetch_video_date()
            self.fetch_video_likes()
            self.fetch_video_length()
            self.fetch_video_tags()
            self.get_video_comments_count()
            self.get_channel_id()
            self.get_channel_name()

            # Debug
            if self.debug is True:
                cprint('')
                cprint('-' * 100)
                cprint(str(self))
                cprint('-' * 100)

            # Guardar scrap HTML si algo salio mal
            if ((self.process_success is False) and
                (self.en_html_save is True)
               ):
                self.save_html_content()

    def _fetch_data_from_pattern(self, pattern, html, err_code, err_msg):
        """Get data from HTML content given a pattern"""
        try:
            return re.search(pattern, html).group(1)
        except Exception as e:
            # Log error message
            o_fmt_error(err_code, err_msg, 'Class__YoutubeVideo')
            # Return a None value
            return None

    def fetch_title(self, pattern=None):
        """ Function:
            Fetch the video title using a pattern over the HTML code loaded.
            It logs an error if the video title could no be fetched.

            Arguments:
            - pattern (optional)

            Notes:
            - This methods has a main algorithm and an alternative one
            - The video title is set to Unknown if everything fails.
        """

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"title":"(.*?)"' if pattern is None else pattern

        # Get the required information using the classic method
        err_code = '0002'
        err_msg = f'Could not fetch title for video {self.id} for pattern {pattern}'
        self.title = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )
        if self.title is not None:
            self.title = self.title.replace('/@','')

        # Try with an alternative method
        else:
            try:
                # Make an alternative URL to scrap
                url = f'https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={self.id}&format=json'
                # Get the new HTTP response
                response = requests.get(url)
                # Transform to a JSON data
                data = json.loads(response.text)
                # Get the video title
                self.title = data['title']
            except Exception as e:
                # Log error message
                msg = f'Could not fetch title for video {self.id} with error type {str(e)}'
                o_fmt_error('0003', msg, 'Class__YoutubeVideo')

        # Set a default title if everything above failed
        if self.title is None:
            self.title = "Unknown"
            # Se success flag to False
            self.process_success = False

    def fetch_views(self, pattern=None):
        """ Function:
            Fetch the amount of views using a pattern over the HTML code loaded.
            It logs an error if the video title could no be fetched.

            Arguments:
            - pattern (optional)

            Notes:
            - This methods has a main algorithm and an alternative one
            - The video views are set to 0 if everything fails.
        """

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"viewCount":"(.*?)"' if pattern is None else pattern

        # Try to get data using the pattern given
        err_code = '0005'
        err_msg = f'Could not fetch views for video {self.id} for pattern {pattern}'
        self.views = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )

        # Try with an alternative method
        if self.views == None:
            # Design a new URL
            url = f'https://www.youtube.com/watch?v={self.id}'
            # Obtengo la cantidad de reproducciones
            try:
                video = YouTube(url)
                self.views = video.views
            except Exception as e:
                o_fmt_error('0055', f'Could not fetch views for video {self.id}', 'Class_YoutubeVideo')

        # Set a default value if everything above failed
        if self.views == None:
            self.views = 0
            # Se success flag to False
            self.process_success = False
        else:
            self.views = int(self.views)

    def fetch_most_viewed_moment(self, pattern=None):
        """ Function:
            Fetch the most viewed moment (MVM) using a pattern over the HTML code loaded.
            It logs an error if the video title could no be fetched.

            Arguments:
            - pattern (optional)

            Notes:
            - The video MVM is set to 00:00:00 if everything fails.
        """

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"decorationTimeMillis":(.*?),' if pattern is None else pattern


        # Intento obtener el dato solicitado a partir de un patron
        # En el caso del conteo de comentarios, dado que algunos videos
        # no los tienen habilitados, no vamos a considerar error no
        # encontrarlos
        err_code = None
        err_msg = None
        miliseconds = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )
        if miliseconds is not None:
            len_seconds = float(miliseconds) / 1000.0
            self.mvm = get_time_len( len_seconds )
        else:
            self.mvm = None

        # Set a default value if everything above failed
        if self.mvm is None:
            self.mvm = '00:00:00'

    def fetch_video_date(self, pattern_1=None, pattern_2=None):
        """ Function:
            Fetch the publish date using a pattern over the HTML code loaded.
            It logs an error if the video title could no be fetched.

            Arguments:
            - pattern_1 (optional)
            - pattern_2 (optional)

            Notes:
            - This methods has a main algorithm and an alternative one
            - The video publish date is set to 00/00/00 if everything fails.
        """

        # If a custom pattern is given, use it, if not use a default one
        pattern_1 = r'"uploadDate":"(.*?)"' if pattern_1 is None else pattern_1
        pattern_2 = r'"publishDate":"(.*?)"' if pattern_2 is None else pattern_2

        # Try to get data using the pattern given
        err_code = '0007'
        err_msg = f'Could not fetch publish date for video {self.id} for pattern {pattern_1}'
        self.publish_date = self._fetch_data_from_pattern(
            pattern_1, self.html_content, err_code, err_msg
        )

        # Try with an alternative method
        if self.publish_date is None:
            err_code = '0008'
            err_msg = f'Could not fetch publish date for video {self.id} for pattern {pattern_2}'
            self.publish_date = self._fetch_data_from_pattern(
                pattern_2, self.html_content, err_code, err_msg
            )

        # Set a default value if everything above failed
        if self.publish_date is None:
            self.publish_date = "00/00/00"
            # Se success flag to False
            self.process_success = False
        else:
            try:
                # Convierte la cadena a un objeto datetime
                fecha_objeto = datetime.fromisoformat(self.publish_date)
                # Formatea la fecha en el nuevo formato
                self.publish_date = fecha_objeto.strftime("%Y-%m-%d %H:%M:%S")
            except:
                err_code = '0015'
                err_msg = f'Error trying to format date {self.publish_date}'
                o_fmt_error(err_code, err_msg, 'Class__YoutubeVideo')
                pass

    def fetch_video_likes(self, pattern=None):
        """ Function:
            Fetch the likes using a pattern over the HTML code loaded.
            It logs an error if the video title could no be fetched.

            Arguments:
            - pattern (optional)

            Notes:
            - This methods has a main algorithm and an alternative one
            - The video likes date are set to 0 if everything fails.
        """

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"likeCount":"(.*?)"' if pattern is None else pattern

        # Try to get data using the pattern given
        err_code = '0009'
        err_msg = f'Could not fetch likes for video {self.id} for pattern {pattern}'
        self.likes = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )

        # Alternative method
        # FIXME: UNDER TEST
        if self.likes is None:
            # Transform response to a BS object
            response = BeautifulSoup(self.html_content, 'html.parser')
            # Find elements <script>
            script_tags = response.find_all('script')
            # Find script that contains "likeCount"
            for script_tag in script_tags:
                # Transform to string
                script_text = script_tag.string
                #
                if script_text and '"likeCount":' in script_text:
                    try:
                        self.likes = int( re.search(pattern, script_text).group(1) )
                    except Exception as e:
                        self.likes = None

        # Set a default value if everything above failed
        if self.likes is None:
            self.likes = 0
            # Set success flag to False
            self.process_success = False
        else:
            self.likes = int(self.likes)

    def fetch_video_length(self, pattern=None):
        """ Function:
            Fetch the time length using a pattern over the HTML code loaded.
            It logs an error if the video title could no be fetched.

            Arguments:
            - pattern (optional)

            Notes:
            - The video time length date are set to 00:00:00 if everything fails.
        """

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"lengthSeconds":"(.*?)",' if pattern is None else pattern

        # Try to get data using the pattern given
        err_code = '0011'
        err_msg = f'Could not fetch time length for video {self.id} for pattern {pattern}'
        lenSeconds = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )
        if lenSeconds is not None:
            self.length = get_time_len( lenSeconds )
        else:
            self.length = None

        # Set a default value if everything above failed
        if self.length is None:
            self.length = '00:00:00'
            # Se success flag to False
            self.process_success = False

    def fetch_video_tags(self, pattern=None):
        """ Function:
            Fetch the tags using a pattern over the HTML code loaded.
            It logs an error if the video title could no be fetched.

            Arguments:
            - pattern (optional)

            Notes:
            - This methods has a main algorithm and an alternative one
            - The video tags date are set to None if everything fails.
        """

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"keywords":[ ]*\[(.*?)\]' if pattern is None else pattern

        # Try to get data using the pattern given
        err_code = '0012'
        err_msg = f'Could not fetch tags for video {self.id} for pattern {pattern}'
        self.tags = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )
        if self.tags is not None:
            self.tags = self.tags.replace(',','/')
            self.tags = self.tags.replace('\\n',' ')
            self.tags = self.tags.replace('"','')

        # Try an alternative method
        if self.tags is None:
            try:
                # Transform to a BeautifulSoup object
                soup = BeautifulSoup(self.html_content, 'html.parser')
                # Search for "meta" element with atribute "name" equals to "keywords"
                meta_element = soup.find('meta', attrs={'name': 'keywords'})
                self.tags = meta_element['content']
                self.tags = self.tags.replace(',','/')
                self.tags = self.tags.replace('\\n',' ')
                self.tags = self.tags.replace('"','')
            except Exception as e:
                self.tags = None
                # Log error message
                msg = f'Could not fetch tags for video {self.id} with error type {str(e)}'
                o_fmt_error('0013', msg, 'Class__YoutubeVideo')

        # Set a default value if everything above failed
        if self.tags is None:
            self.tags = "None"
            # Se success flag to False
            self.process_success = False

    def get_video_comments_count(self, pattern=None):
        """ Function:
            Fetch the comments count using a pattern over the HTML code loaded.
            It logs an error if the video title could no be fetched.

            Arguments:
            - pattern (optional)

            Notes:
            - This methods has a main algorithm and an alternative one
            - The video comments count date are set to 0 if everything fails.
        """

        # If a custom pattern is given, use it, if not use a default one
        pattern = r'"commentCount":[ ]*\{(.*?)\}' if pattern is None else pattern

        # Intento obtener el dato solicitado a partir de un patron
        # En el caso del conteo de comentarios, dado que algunos videos
        # no los tienen habilitados, no vamos a considerar error no
        # encontrarlos
        err_code = None
        err_msg = None
        comments_str = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )
        if comments_str is not None:
            try:
                comments_str = comments_str.replace(',','/')
                self.comments_cnt = re.search(r'"\w+":"(\d+)"', comments_str).group(1)
                self.comments_cnt = int(self.comments_cnt)
            except:
                err_code = None
                err_msg = None
                o_fmt_error(err_code, err_msg, 'Class__YoutubeVideo')

        # Set a default value if everything above failed
        if self.comments_cnt is None:
            self.comments_cnt = 0
        else:
            self.comments_cnt = int(self.comments_cnt)