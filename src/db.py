import sqlite3
import datetime
import csv
try:
    from src.utils import o_fmt_error
except:
    from utils import o_fmt_error

def handle_export_args(args):
    # Defino un nombre por defecto al modulo
    module_name = 'export'

    # Muestro el mensaje de ayuda
    if args.ayuda:
        pass

    # Exporto la base de datos a formato .csv
    elif args.tocsv:
        with Database() as db:
            db.export_table(ext='.csv')

    # Exporto la base de datos a formato Excel
    elif args.toexcel:
        with Database() as db:
            db.export_table(ext='.xlsx')

    # Mensaje de error por defecto
    else:
        print(f'Modulos {module_name}')
        print(f'\tSe ha producido un error al procesar el comando')
        print(f'\tPuede utilizar {module_name} -h para obtener ayuda')
    pass

class Database:

    def __init__(self, db_name='latinframe.db'):
        self.db_name = db_name

        # Open connection
        self.db_open()

        # Create tables
        self.create_video_tables()
        self.create_channel_tables()
        self.create_similarweb_tables()
        self.create_news_tables()

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()

    def db_open(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except:
            msg = f'Could not open Database connection for {self.db_name}'
            o_fmt_error('0003', msg, 'Class__Database')

    def db_close(self):
        try:
            self.conn.close()
        except:
            msg = f'Error while closing DB connection for {self.db_name}'
            o_fmt_error('0004', msg, 'Class__Database')

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

    #################################################################
    # Tablas de videos de Youtube
    #################################################################
    def create_video_tables(self):
        try:
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
        except:
            msg = f'Error while creating table:\n\n{query}\n\n'
            o_fmt_error('0005', msg, 'Class__Database')

        try:
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
        except:
            msg = f'Error while creating table:\n\n{query}\n\n'
            o_fmt_error('0006', msg, 'Class__Database')

    def insert_video_record(self, video_info):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
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
        except:
            msg = f'Error while updating/inserting records for query:\n\n{query}\n\n{params}\n\n'
            o_fmt_error('0007', msg, 'Class__Database')

        try:
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
        except:
            msg = f'Error while updating/inserting records for query:\n\n{query}\n\n{params}\n\n'
            o_fmt_error('0008', msg, 'Class__Database')

    #################################################################
    # Tablas de canales de Youtube
    #################################################################
    def create_channel_tables(self):
        try:
            query = '''
            CREATE TABLE IF NOT EXISTS CHANNEL (
                CHANNEL_ID TEXT PRIMARY KEY,
                CHANNEL_NAME TEXT,
                UPDATE_DATE DATE
            )
            '''
            self.exec(query)
        except:
            msg = f'Error while creating table:\n\n{query}\n\n'
            o_fmt_error('0015', msg, 'Class__Database')

        try:
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
        except:
            msg = f'Error while creating table:\n\n{query}\n\n'
            o_fmt_error('0016', msg, 'Class__Database')

    def insert_channel_record(self, channel_info):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
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
        except:
            msg = f'Error while updating/inserting records for query:\n\n{query}\n\n{params}\n\n'
            o_fmt_error('0009', msg, 'Class__Database')

        try:
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
        except:
            msg = f'Error while updating/inserting records for query:\n\n{query}\n\n{params}\n\n'
            o_fmt_error('0010', msg, 'Class__Database')

    #################################################################
    # Tablas de paginas de SimilarWeb
    #################################################################
    def create_similarweb_tables(self):
        try:
            query = '''
            CREATE TABLE IF NOT EXISTS SIMILARWEB_DOMAINS (
                DOMAIN_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                DOMAIN TEXT,
                COMPANY TEXT,
                YEAR_FOUNDER INTEGER,
                EMPLOYEES TEXT,
                HQ TEXT,
                ANNUAL_REVENUE TEXT,
                INDUSTRY TEXT,
                UPDATE_DATE DATE
            )
            '''
            self.exec(query)
        except:
            msg = f'Error while creating table:\n\n{query}\n\n'
            o_fmt_error('0017', msg, 'Class__Database')

        try:
            query = '''
            CREATE TABLE IF NOT EXISTS SIMILARWEB_RECORDS (
                RECORD_ID INTEGER PRIMARY KEY,
                DOMAIN_ID INTEGER,
                GLOBAL_RANK INTEGER,
                COUNTRY_RANK INTEGER,
                CATEGORY_RANK INTEGER,
                TOTAL_VISITS TEXT,
                BOUNCE_RATE INTEGER,
                PAGES_PER_VISIT NUMBER,
                AVG_DURATION_VISIT TEXT,
                UPDATE_DATE DATE
            )
            '''
            self.exec(query)
        except:
            msg = f'Error while creating table:\n\n{query}\n\n'
            o_fmt_error('0018', msg, 'Class__Database')

    def insert_similarweb_record(self, data):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            query = '''
            INSERT OR REPLACE INTO SIMILARWEB_DOMAINS (
                DOMAIN_ID, DOMAIN, COMPANY, YEAR_FOUNDER, EMPLOYEES, HQ, ANNUAL_REVENUE, INDUSTRY, UPDATE_DATE
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                data['domain_id'], data['domain'],
                data['company'], data['year_founder'], data['employees'],
                data['hq'], data['annual_revenue'], data['industry'],
                current_time
            )
            self.exec(query, params)
        except:
            msg = f'Error while updating/inserting records for query:\n\n{query}\n\n{params}\n\n'
            o_fmt_error('0011', msg, 'Class__Database')

        try:
            query = '''
            INSERT OR REPLACE INTO SIMILARWEB_RECORDS (
                DOMAIN_ID, GLOBAL_RANK, COUNTRY_RANK, CATEGORY_RANK, TOTAL_VISITS, BOUNCE_RATE, PAGES_PER_VISIT, AVG_DURATION_VISIT, UPDATE_DATE
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                data['domain_id'],
                data['global_rank'], data['country_rank'], data['category_rank'],
                data['total_visits'], data['bounce_rate'], data['pages_per_visit'],
                data['avg_duration_visit'],
                current_time
            )
            self.exec(query, params)
        except:
            msg = f'Error while updating/inserting records for query:\n\n{query}\n\n{params}\n\n'
            o_fmt_error('0012', msg, 'Class__Database')

    #################################################################
    # Tablas de noticias
    #################################################################
    def create_news_tables(self):
        try:
            query = '''
            CREATE TABLE IF NOT EXISTS NEWS (
                NEW_ID INTEGER PRIMARY KEY,
                TITLE TEXT,
                TOPIC_ID INTEGER,
                NEWSPAPER_ID INTEGER,
                URL TEXT,
                PUBLISH_DATE DATE,
                ANTIQUE TEXT,
                UPDATE_DATE DATE
            );
            '''
            self.exec(query)
        except:
            msg = f'Error while creating table:\n\n{query}\n\n'
            o_fmt_error('0019', msg, 'Class__Database')

        try:
            query = '''
            CREATE TABLE IF NOT EXISTS TOPICS (
                TOPIC_ID INTEGER PRIMARY KEY,
                TOPIC TEXT,
                TOPIC_NEWS INTEGER,
                UPDATE_DATE DATE
            );
            '''
            self.exec(query)
        except:
            msg = f'Error while creating table:\n\n{query}\n\n'
            o_fmt_error('0020', msg, 'Class__Database')

        try:
            query = '''
            CREATE TABLE IF NOT EXISTS NEWSPAPERS (
                NEWSPAPER_ID INTEGER PRIMARY KEY,
                NEWSPAPER TEXT,
                NEWS_COUNT INTEGER,
                UPDATE_DATE DATE
            );
            '''
            self.exec(query)
        except:
            msg = f'Error while creating table:\n\n{query}\n\n'
            o_fmt_error('0021', msg, 'Class__Database')

    def insert_news_record(self, data):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            query = '''
            INSERT OR REPLACE INTO NEWS (
                NEW_ID, TITLE, TOPIC_ID, NEWSPAPER_ID, URL, PUBLISH_DATE, ANTIQUE, UPDATE_DATE
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                data['new_id'], data['title'],
                data['topic_id'], data['newspaper_id'], data['url'],
                data['publish_date'], data['antique'],
                current_time
            )
            self.exec(query, params)
        except:
            msg = f'Error while updating/inserting records for query:\n\n{query}\n\n{params}\n\n'
            o_fmt_error('0013', msg, 'Class__Database')

        try:
            query = '''
            INSERT OR REPLACE INTO TOPICS (
                TOPIC_ID, TOPIC, TOPIC_NEWS, UPDATE_DATE
            ) VALUES (?, ?, ?, ?)
            '''
            params = (
                data['topic_id'], data['topic'], 1,
                current_time
            )
            self.exec(query, params)
        except:
            msg = f'Error while updating/inserting records for query:\n\n{query}\n\n{params}\n\n'
            o_fmt_error('0014', msg, 'Class__Database')

        try:
            query = '''
            INSERT OR REPLACE INTO NEWSPAPERS (
                NEWSPAPER_ID, NEWSPAPER, NEWS_COUNT, UPDATE_DATE
            ) VALUES (?, ?, ?, ?)
            '''
            params = (
                data['newspaper_id'], data['newspaper'], 1,
                current_time
            )
            self.exec(query, params)
        except:
            msg = f'Error while updating/inserting records for query:\n\n{query}\n\n{params}\n\n'
            o_fmt_error('0015', msg, 'Class__Database')

    #################################################################
    # Exportacion de tablas
    #################################################################
    def export_table(self, table_name='CHANNEL', path='results/db/', ext='.csv'):
        import pandas as pd

        table_names = [
            'VIDEO','VIDEO_RECORDS','CHANNEL','CHANNEL_RECORDS',
            'NEWS','NEWSPAPERS','SIMILARWEB_DOMAINS','SIMILARWEB_RECORDS','TOPICS',
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

    def process_data(self, op='select', type=None, sel='name', val='elxokas'):

        # Defino la consulta
        if type == 'video':
            if sel == 'id':
                query = f"SELECT * FROM VIDEO WHERE VIDEO_ID LIKE '%{val}%'"
            elif sel == 'name':
                query = f"SELECT * FROM VIDEO WHERE VIDEO_NAME LIKE '%{val}%'"
            elif sel == '-channelid':
                query = f"SELECT * FROM VIDEO WHERE CHANNEL_ID LIKE '%{val}%'"
            elif sel == '-channelname':
                query = f"SELECT * FROM VIDEO WHERE CHANNEL_ID = (SELECT CHANNEL_ID FROM CHANNEL WHERE CHANNEL_NAME LIKE '%{val}%')"
        elif type == 'channel':
            if sel == 'id':
                query = f"SELECT * FROM CHANNEL WHERE CHANNEL_ID LIKE '%{val}%'"
            elif sel == 'name':
                query = f"SELECT * FROM CHANNEL WHERE CHANNEL_NAME LIKE '%{val}%'"
        else:
            print('Opciones validas: {channel/video} {id/name} target')
            return

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