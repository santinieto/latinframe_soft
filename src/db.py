import sqlite3
import datetime
import csv
from src.utils import o_fmt_error

class Database:

    def __init__(self, db_name='latinframe.db'):
        self.db_name = db_name

        # Open connection
        self.db_open()

        # Create tables
        self.create_video_tables()
        self.create_channel_tables()

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()

    def db_open(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def db_close(self):
        self.conn.close()

    def exec(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            # Log error message
            msg = f'Could not execute query:\n{query}\nParameters: {params}\nError: {str(e)}'
            o_fmt_error('0001', msg, 'Class__Database')

    def select(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            return result
        except sqlite3.Error as e:
            self.conn.rollback()
            # Log error message
            msg = f'Could not execute select:\n\n{query}\nError: {str(e)}'
            o_fmt_error('0002', msg, 'Class__Database')
            return None

    def add_column(self, table_name, column_name, column_type):
        query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        self.exec(query)

    def create_video_tables(self):
        query = '''
        CREATE TABLE IF NOT EXISTS VIDEO (
            VIDEO_ID TEXT PRIMARY KEY,
            VIDEO_NAME TEXT,
            CHANNEL_ID TEXT,
            VIDEO_LEN TEXT,
            TAGS TEXT,
            PUBLISH_DATE DATE,
            UPDATE_DATE DATE
        )
        '''
        self.exec(query)

        query = '''
        CREATE TABLE IF NOT EXISTS VIDEO_RECORDS (
            RECORD_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            VIDEO_ID TEXT,
            VIEWS INTEGER,
            MOST_VIEWED_MOMENT TEXT,
            LIKES INTEGER,
            COMMENTS_COUNT INTEGER,
            UPDATE_DATE DATE
        )
        '''
        self.exec(query)

    def insert_video_record(self, video_info):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = '''
        INSERT OR REPLACE INTO VIDEO (
            VIDEO_ID, VIDEO_NAME, CHANNEL_ID, VIDEO_LEN, TAGS, PUBLISH_DATE, UPDATE_DATE
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            video_info['videoID'], video_info['videoName'], video_info['channelID'],
            video_info['videoLength'], video_info['videoTags'], video_info['publishDate'],
            current_time
        )
        self.exec(query, params)

        query = '''
        INSERT INTO VIDEO_RECORDS (
            VIDEO_ID, VIEWS, MOST_VIEWED_MOMENT, LIKES, COMMENTS_COUNT, UPDATE_DATE
        ) VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (
            video_info['videoID'], video_info['views'], video_info['mostViewedMoment'],
            video_info['likes'], video_info['videoCommentsCount'],
            current_time
        )
        self.exec(query, params)

    def create_channel_tables(self):
        query = '''
        CREATE TABLE IF NOT EXISTS CHANNEL (
            CHANNEL_ID TEXT PRIMARY KEY,
            CHANNEL_NAME TEXT,
            UPDATE_DATE DATE
        )
        '''
        self.exec(query)

        query = '''
        CREATE TABLE IF NOT EXISTS CHANNEL_RECORDS (
            RECORD_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CHANNEL_ID TEXT,
            VIDEOS_COUNT INTEGER,
            SUBSCRIBERS INTEGER,
            TOTAL_VIEWS INTEGER,
            MONTHLY_SUBS INTEGER,
            DAILY_SUBS INTEGER,
            UPDATE_DATE DATE
        )
        '''
        self.exec(query)

    def insert_channel_record(self, channel_info):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = '''
        INSERT OR REPLACE INTO CHANNEL (
            CHANNEL_ID, CHANNEL_NAME, UPDATE_DATE
        ) VALUES (?, ?, ?)
        '''
        params = (
            channel_info['channelID'], channel_info['channelName'],
            current_time
        )
        self.exec(query, params)

        query = '''
        INSERT INTO CHANNEL_RECORDS (
            CHANNEL_ID, VIDEOS_COUNT, SUBSCRIBERS, TOTAL_VIEWS, MONTHLY_SUBS, DAILY_SUBS, UPDATE_DATE
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            channel_info['channelID'], channel_info['nVideos'], channel_info['subscribers'], channel_info['views'],
            channel_info['monthly_subs'], channel_info['daily_subs'],
            current_time
        )
        self.exec(query, params)

    def export_table(self, table_name='CHANNEL', path='results/db/', ext='.csv'):
        import pandas as pd

        table_names = [
            'VIDEO','VIDEO_RECORDS','CHANNEL','CHANNEL_RECORDS'
        ]

        for table_name in table_names:
            # Paso el nombre de la tabla a minusculas
            table_name = table_name.lower()

            # Nombre de la tabla a exportar
            query = f"SELECT * FROM {table_name}"

            # Obtengo los datos de la tabla
            df = pd.read_sql_query(query, self.conn)

            # Defino el tipo de exportacion
            if ext == '.csv':
                filename = f'{path}/{table_name}.csv'
                df.to_csv(filename, index=False)
            elif ext == '.xlsx':
                filename = f'{path}/{table_name}.xlsx'
                df.to_excel(filename, index=False)
            else:
                print('Formato no valido')
                return

            print(f"Data from the '{table_name}' table has been exported to '{filename}'.")

    #############################################################
    # Especific functions
    #############################################################
    def get_youtube_channel_ids(self, table_name = 'CHANNEL'):
        query = f'SELECT DISTINCT CHANNEL_ID FROM {table_name}'
        db_ids = self.select(query, ())
        db_ids = [item[0] for item in db_ids]
        return db_ids

    def get_data(self, op='select', type=None, sel='-name', val='elxokas'):

        # Defino la consulta
        if type == '-video':
            if sel == '-id':
                query = f"SELECT * FROM VIDEO WHERE VIDEO_ID LIKE '%{val}%'"
            elif sel == '-name':
                query = f"SELECT * FROM VIDEO WHERE VIDEO_NAME LIKE '%{val}%'"
        elif type == '-channel':
            if sel == '-id':
                query = f"SELECT * FROM CHANNEL WHERE CHANNEL_ID LIKE '%{val}%'"
            elif sel == '-name':
                query = f"SELECT * FROM CHANNEL WHERE CHANNEL_NAME LIKE '%{val}%'"

        # Muestro datos por pantalla
        print('\nExecuted query:\n')
        print(query)
        print()
        print('Results:')

        # Obtengo los restulados
        results = self.select(query, ())
        if ((results is None) or (results == [])):
            print('No results.')
            return
        else:
            for kk, result in enumerate(results):
                print(f'{kk}: {result}')

        if op == 'del':
            ans = None
            while ans not in ['y', 'n']:
                ans = input('\nWARNING! You are about to delete the results above\nContinue? (y/n): ').lower()
            if ans == 'y':
                del_query = query.replace('SELECT *', 'DELETE')
                results = self.select(del_query, ())
                print('Results deleted.')

if __name__ == '__main__':
    db = Database()

    # Add column
    db.add_column('CHANNEL_RECORDS', 'SUBSCRIBERS', 'INTEGER')