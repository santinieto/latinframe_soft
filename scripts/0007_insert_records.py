import pandas as pd
import sys

sys.path.append(r'C:\Users\santi\OneDrive\Desktop\latinframe_soft')

from src.youtube import YoutubeVideo
from src.youtube import YoutubeChannel
from src.news import GoogleNew
from src.db import Database

def insert_video_records():
    # Cargo el CSV
    df = pd.read_csv(r'C:\Users\santi\soft\results\Youtube_Videos.csv')

    # Elimina las columnas 'Unnamed: 0', 'Unnamed: 0.1', y 'Unnamed: 0.2'
    columnas_a_eliminar = ['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.2']
    df = df.drop(columnas_a_eliminar, axis=1)

    # Cambio los nombres de los encabezados
    new_colummns = [
        'id','title','channel_id','channel_name','views',
        'length','mvm','likes','tags','publish_date',
        'comments_cnt','update_date',
    ]
    df.columns = new_colummns

    # Convierto el df a diccionario
    rows_dicc = df.to_dict(orient='records')

    # Obtengo la lista de videos disponibles
    query = "select video_id from video"
    with Database() as db:
        video_id_list = list(set([x[0] for x in db.select(query=query)]))

    # Recorro las filas
    with Database() as db:
        for kk,row in enumerate(rows_dicc):
            video = YoutubeVideo(input_dicc=row, debug=False)
            video_info = video.to_dicc()

            print('Inserting record {}/{} ...'.format(kk+1, len(rows_dicc)))

            # Inserto el registro en la lista historia
            query = '''
            INSERT INTO VIDEO_RECORDS (
                VIDEO_ID, VIEWS, MOST_VIEWED_MOMENT, LIKES, COMMENTS_COUNT, UPDATE_DATE
            ) VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (
                video_info['videoID'], video_info['views'], video_info['mostViewedMoment'],
                video_info['likes'], video_info['videoCommentsCount'],
                row['update_date']
            )
            db.exec(query, params)

            # Si no esta el ID en la tabla de videos lo agrego
            if video_info['videoID'] not in video_id_list:
                query = '''
                INSERT OR REPLACE INTO VIDEO (
                    VIDEO_ID, VIDEO_NAME, CHANNEL_ID, VIDEO_LEN, TAGS, PUBLISH_DATE, UPDATE_DATE
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
                params = (
                    video_info['videoID'], video_info['videoName'], video_info['channelID'],
                    video_info['videoLength'], video_info['videoTags'], video_info['publishDate'],
                    row['update_date']
                )
                db.exec(query, params)

def insert_channel_records():
    # Cargo el CSV
    df = pd.read_csv(r'C:\Users\santi\soft\results\Youtube_Channels.csv')

    # Elimina las columnas 'Unnamed: 0'
    columnas_a_eliminar = ['Unnamed: 0']
    df = df.drop(columnas_a_eliminar, axis=1)

    # Convierto el df a diccionario
    rows_dicc = df.to_dict(orient='records')

    # Obtengo la lista de videos disponibles
    query = "select channel_id from channel"
    with Database() as db:
        channel_id_list = list(set([x[0] for x in db.select(query=query)]))

    # Recorro las filas
    with Database() as db:
        for kk,row in enumerate(rows_dicc):
            channel = YoutubeChannel(input_dicc=row, debug=False)
            channel_info = channel.to_dicc()

            print('Inserting record {}/{} ...'.format(kk+1, len(rows_dicc)))

            # Inserto el registro en la lista historia
            query = '''
            INSERT INTO CHANNEL_RECORDS (
                CHANNEL_ID, VIDEOS_COUNT, SUBSCRIBERS, TOTAL_VIEWS, MONTHLY_SUBS, DAILY_SUBS, UPDATE_DATE
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                channel_info['channelID'], channel_info['nVideos'], channel_info['subscribers'], channel_info['views'],
                channel_info['monthly_subs'], channel_info['daily_subs'],
                '2023-08-11 12:00:00'
            )
            db.exec(query, params)

            # Si no esta el ID en la tabla de videos lo agrego
            if channel_info['channelID'] not in channel_id_list:
                query = '''
                INSERT OR REPLACE INTO CHANNEL (
                    CHANNEL_ID, CHANNEL_NAME, UPDATE_DATE
                ) VALUES (?, ?, ?)
                '''
                params = (
                    channel_info['channelID'], channel_info['channelName'],
                    '2023-08-11 12:00:00'
                )
                db.exec(query, params)

def insert_news_records():
    from src.news_scrap import get_id

    # Cargo el CSV
    df = pd.read_csv(r'C:\Users\santi\soft\results\GoogleNews.csv')

    # Elimina las columnas 'Unnamed: 0'
    columnas_a_eliminar = ['Unnamed: 0', 'Unnamed: 0.1']
    df = df.drop(columnas_a_eliminar, axis=1)

    # Cambio los nombres de los encabezados
    new_colummns = [
        'topic',
        'title',
        'newspaper',
        'antique',
        'publish_date',
        'publish_time',
        'update_date',
    ]
    df.columns = new_colummns

    # Convierto el df a diccionario
    rows_dicc = df.to_dict(orient='records')

    # Recorro las filas
    with Database() as db:
        for kk,row in enumerate(rows_dicc):

            print('Inserting record {}/{} ...'.format(kk+1, len(rows_dicc)))

            google_new = GoogleNew()
            google_new.topic = row['topic']
            google_new.title = row['title']
            google_new.newspaper = row['newspaper']
            google_new.antique = row['antique']
            google_new.publish_date = row['publish_date'] + ' ' + row['publish_time']

            google_new.new_id = get_id(
                id_field='new_id',
                table_name='news',
                search_field='title',
                target=google_new.title
                )

            google_new.topic_id = get_id(
                id_field='topic_id',
                table_name='topics',
                search_field='topic',
                target=google_new.topic
                )

            google_new.newspaper_id = get_id(
                id_field='newspaper_id',
                table_name='newspapers',
                search_field='newspaper',
                target=google_new.newspaper
                )

            data = google_new.to_dicc()

            query = '''
            INSERT OR REPLACE INTO NEWS (
                NEW_ID, TITLE, TOPIC_ID, NEWSPAPER_ID, URL, PUBLISH_DATE, ANTIQUE, UPDATE_DATE
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                data['new_id'], data['title'],
                data['topic_id'], data['newspaper_id'], data['url'],
                data['publish_date'], data['antique'],
                row['update_date']
            )
            db.exec(query, params)

            query = '''
            INSERT OR REPLACE INTO TOPICS (
                TOPIC_ID, TOPIC, TOPIC_NEWS, UPDATE_DATE
            ) VALUES (?, ?, ?, ?)
            '''
            params = (
                data['topic_id'], data['topic'], 1,
                row['update_date']
            )
            db.exec(query, params)

            query = '''
            INSERT OR REPLACE INTO NEWSPAPERS (
                NEWSPAPER_ID, NEWSPAPER, NEWS_COUNT, UPDATE_DATE
            ) VALUES (?, ?, ?, ?)
            '''
            params = (
                data['newspaper_id'], data['newspaper'], 1,
                row['update_date']
            )
            db.exec(query, params)

if __name__ == '__main__':
    # insert_video_records() # Done
    # insert_channel_records()
    # insert_news_records()