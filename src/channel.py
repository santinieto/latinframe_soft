# Libraries from Python
import re
from bs4 import BeautifulSoup
import concurrent.futures
import multiprocessing
import os

# Modules and functions
from src.utils import cprint
from src.utils import o_fmt_error
from src.utils import StrNum2RealNum
from src.utils import getHTTPResponse
from src.utils import get_formatted_date
from .video import Video

# Define a function to fetch video data and put it into the shared dictionary
def fetch_video_data(id, videos_dicc, canal_instance=None):
    video = Video(id)  # Assuming Video is a class constructor
    video_data = video.fetch_data()  # Replace with your method to fetch data
    videos_dicc[id] = video_data

    if canal_instance is not None:
        canal_instance.add_video(video)

class Channel:
    def __init__(self, id=None, html_content=None, enable_MP=True, debug=True):
        """ Constructor of class Channel, it requires one of two options:
            - Channel ID to look on Youtube
            - Scrap of HTML content to look the information
        """

        # If neither the ID nor the HTML content was load
        # nothing can be processed and any information will be fetched
        # None on both fields will be set and an error will be logged
        if (id is None) and (html_content is None):
            self.id = id
            self.html_content = html_content
            # Log error message
            msg = f'Could not create a Channel object with giving an ID or HTML scrap. Data could not be collected'
            o_fmt_error('0001', msg, 'Class__Channel')

        # Case when the HTML is given but not the channel ID
        # The channel ID will be tried to be catched from HTML
        elif (id is None) and (html_content is not None):
            # Set the HTML content if one is given
            self.html_content = html_content
            # Get channel ID
            self.get_id()

        # Case when only the channel ID is given
        # The HTML code needs to be collected
        elif (id is not None) and (html_content is None):
            # Set the channel ID using input arguments
            self.id = id
            # If HTML content is not being set while construction,
            # get HTML content using id
            self.get_html_content()

        else:
            # Set both channel ID and HTML content using input arguments
            self.id = id
            self.html_content = html_content

        # Set defaults values for the class variables
        self.debug = debug
        self.enable_MP = enable_MP
        self.views = 0
        self.nVideos = 0
        self.subscribers = 0
        self.daily_subs = 0
        self.monthly_subs = 0
        self.video_ids_list = []
        self.videos = []

    def add_video(self, video):
        self.videos.append(video)

    def __str__(self):
        """Returns all fields on the class to be displayed into the screen/file."""

        ans  = f"- Channel ID: {self.id}\n"
        ans += f"- Channel name: {self.channel_name}\n"
        ans += f"- Channel views: {self.views}\n"
        ans += f"- Channel videos: {self.nVideos}\n"
        ans += f"- Channel subscribers: {self.subscribers}\n"
        ans += f"- Channel monthly subscribers: {self.monthly_subs}\n"
        ans += f"- Channel daily subscribers: {self.daily_subs}\n"
        ans += f"- Channel video IDs: {self.video_ids_list}"
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
            o_fmt_error('0002', msg, 'Class__Channel')
        else:
            # Fetch channel information
            self.fetch_channel_name()
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
            o_fmt_error(err_code, err_msg, 'Class__Channel')
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
                o_fmt_error(err_code, err_msg, 'Class__Channel')

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
            o_fmt_error(err_code, err_msg, 'Class__Channel')

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
            self.videos = pool.map(Video, self.video_ids_list)

            # Close pool
            pool.close()
            pool.join()

            # Save scraps
            pool = multiprocessing.Pool(processes=nthreads)
            pool.map(Video.save_html_content, self.videos)
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