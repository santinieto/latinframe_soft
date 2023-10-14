import os
import pandas as pd
import datetime

from src.db import Database
from src.utils import cprint

def youtube_db_fetch():
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
        db_ids = db.get_youtube_channel_ids()

        # Combine lists
        total_id_list = list(set(csv_ids + db_ids))

        # Get list of IDs that are not in DB
        to_add_list = [x for x in total_id_list if x not in db_ids]

        # Add record to DB
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
