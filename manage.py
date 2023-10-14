# Libraries from Python
import sys
import unittest
import os
import pandas as pd

# My modules
from src.channel import Channel
from src.db import Database
from src.db_fetch import *
from src.utils import cprint

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
    # suite = loader.discover(start_dir='./tests/', pattern='test_*.py')
    suite = loader.discover(start_dir='./tests/', pattern='test_channel.py')
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

# Main function
if __name__ == '__main__':
    # Set environment
    set_environment()

    # Get access to the arguments
    args = sys.argv

    # Get script name
    script_name = args[0]

    # Get option
    opt_1 = args[1]

    if opt_1 == 'runtest':
        execute_tests()

    if opt_1 == 'runscrap':
        execute_scrap()

    if opt_1 == 'fetch':
        execute_db_fetch()

    # Clear environment variables
    unset_environment()