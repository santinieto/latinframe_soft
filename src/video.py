# Libraries from Python
from bs4 import BeautifulSoup
from pytube import YouTube
import re
import json
import requests
import os
from datetime import datetime

# Modules and functions
from src.utils import getHTTPResponse
from src.utils import get_time_len
from src.utils import cprint
from src.utils import o_fmt_error
from src.utils import get_formatted_date

class Video:
    def __init__(self, id=None, html_content=None, debug=True):
        """ Constructor of class Video, it requires one of two options:
            - Video ID to look on Youtube
            - Scrap of HTML content to look the information
        """

        # If neither the ID nor the HTML content was load
        # nothing can be processed and any information will be fetched
        # None on both fields will be set and an error will be logged
        if (id is None) and (html_content is None):
            self.id = id
            self.html_content = html_content
            # Log error message
            msg = f'Could not create a Video object with giving an ID or HTML scrap. Data could not be collected'
            o_fmt_error('0001', msg, 'Class__Video')

        # Case when the HTML is given but not the video ID
        # The video ID will be tried to be catched from HTML
        elif (id is None) and (html_content is not None):
            # Set the HTML content if it is given
            self.html_content = html_content
            # Get video ID
            # FIXME: Needs to be implemented
            self.get_id()

        # Case when only the video ID is given
        # The HTML code needs to be collected
        elif (id is not None) and (html_content is None):
            # Set the video ID using input arguments
            self.id = id
            # If HTML content is not being set while construction,
            # get HTML content using id
            self.get_html_content()

        else:
            # Set both video ID and HTML content using input arguments
            self.id = id
            self.html_content = html_content

        # Set defaults values for the class variables
        self.channel_id = ''
        self.channel_name = ''
        self.debug = debug
        self.title = "Unknown"
        self.views = 0
        self.likes = 0
        self.length = '00:00:00'
        self.comments_cnt = 0
        self.mvm = '00:00:00'
        self.tags = "None"
        self.publish_date = "00/00/00"

        # Debug
        if self.debug is True:
            cprint(f'Created Video object for ID: {self.id}')

        # Fetch data for every video
        self.fetch_data()

    def __str__(self):
        """Returns all fields on the class to be displayed into the screen/file."""

        ans  = f"\t- Video ID: {self.id}\n"
        ans += f"\t- Video name: {self.title}\n"
        ans += f"\t- Video views: {self.views}\n"
        ans += f"\t- Video likes: {self.likes}\n"
        ans += f"\t- Video length: {self.length}\n"
        ans += f"\t- Video comments: {self.comments_cnt}\n"
        ans += f"\t- Video MVM: {self.mvm}\n"
        ans += f"\t- Video Publish date: {self.publish_date}\n"
        ans += f"\t- Video tags: {self.tags}"
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

    def get_id(self):
        """Get the ID for the video from the HTML content"""
        pass

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
            cprint(f'\t- Saving HTML scrap for Video {self.id}')
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
            cprint(f'Fetching data for Video {self.id}... ')

        # Logs an error if no HTML content is loaded
        if self.html_content is None:
            # Log error message
            msg = f'Could not fetch information for video {self.id} without a HTML content loaded'
            o_fmt_error('0004', msg, 'Class__Video')
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
            o_fmt_error(err_code, err_msg, 'Class__Video')
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
                o_fmt_error('0003', msg, 'Class__Video')

        # Set a default title if everything above failed
        if self.title is None:
            self.title = "Unknown"

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
                o_fmt_error('0055', f'Could not fetch views for video {self.id}', 'Class_Video')

        # Set a default value if everything above failed
        if self.views == None:
            self.views = 0
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

        # Try to get data using the pattern given
        err_code = '0006'
        err_msg = f'Could not fetch most viewed moment for video {self.id} for pattern {pattern}'
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
        else:
            try:
                # Convierte la cadena a un objeto datetime
                fecha_objeto = datetime.fromisoformat(self.publish_date)
                # Formatea la fecha en el nuevo formato
                self.publish_date = fecha_objeto.strftime("%Y-%m-%d %H:%M:%S")
            except:
                err_code = '0015'
                err_msg = f'Error trying to format date {self.publish_date}'
                o_fmt_error(err_code, err_msg, 'Class__Video')
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
                o_fmt_error('0013', msg, 'Class__Video')

        # Set a default value if everything above failed
        if self.tags is None:
            self.tags = "None"

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

        # Try to get data using the pattern given
        err_code = '0014'
        err_msg = f'Could not fetch video comments count for video {self.id} for pattern {pattern}'
        comments_str = self._fetch_data_from_pattern(
            pattern, self.html_content, err_code, err_msg
        )
        if comments_str is not None:
            try:
                comments_str = comments_str.replace(',','/')
                self.comments_cnt = re.search(r'"\w+":"(\d+)"', comments_str).group(1)
                self.comments_cnt = int(self.comments_cnt)
            except:
                err_code = '0016'
                err_msg = f'Could not fetch video comments count for video {self.id} for pattern "\w+":"(\d+)"'
                o_fmt_error(err_code, err_msg, 'Class__Video')

        # Set a default value if everything above failed
        if self.comments_cnt is None:
            self.comments_cnt = 0
        else:
            self.comments_cnt = int(self.comments_cnt)