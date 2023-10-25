from src.utils import cprint
from src.utils import getHTTPResponse
from src.utils import is_url_arg
from src.youtube import YoutubeVideo
from src.youtube import YoutubeChannel
from src.db import Database

def scrap_youtube_help(script_name, arg):
    print('Usage:')
    print( '\t NULL : Execute all scraps')
    print( '\t -all : Execute all scraps')
    print( '\t -video <video_id/"url"> [] : Scrap a single video')
    print( '\t\t -save_html : Save HTML content (optional)')

def handle_video_args(args):
    # Defino un nombre por defecto al modulo
    module_name = 'video'

    # Mensaje de ayuda
    if args.ayuda:
        scrap_youtube_help()

    # Scrapeo un video con la ID
    elif args.id:
        if is_url_arg(args.id) == True:
            print('ID no valido')
        else:
            video = scrap_video_w_id(args.id)

    # Scrapero un video con la URL
    elif args.url:
        if is_url_arg(args.url) == True:
            video = scrap_video_w_url(args.url)
        else:
            print('URL no valida')

    # Mensaje de error por defecto
    else:
        print(f'Modulos {module_name}')
        print(f'\tSe ha producido un error al procesar el comando')
        print(f'\tPuede utilizar {module_name} -h para obtener ayuda')

    # Agregar el video a la base de datos
    if args.add:
        with Database() as db:
            db.insert_video_record(video.to_dicc())

    # Borrar el video a la base de datos
    elif args.delete:
        print('Video - Borrar un video a la base de datos - {}'.format(args.delete))
        print('Comming soon...')

    # Guardo el contenido HTML si fuera necesario
    if args.save_html:
        video.save_html_content()

def handle_channel_args(args):
    # Defino un nombre por defecto al modulo
    module_name = 'channel'

    # Mensaje de ayuda
    if args.ayuda:
        scrap_youtube_help()

    # Scrapeo un canal con la ID
    elif args.id:
        if is_url_arg(args.id) == True:
            print('ID no valido')
        else:
            channel = scrap_channel_w_id(args.id)
            channel.fetch_channel_data()

    # Scrapero un canal con la URL
    elif args.url:
        if is_url_arg(args.url) == True:
            channel = scrap_channel_w_url(args.url)
            channel.fetch_channel_data()
        else:
            print('URL no valida')

    # Mensaje de error por defecto
    else:
        print(f'Modulos {module_name}')
        print(f'\tSe ha producido un error al procesar el comando')
        print(f'\tPuede utilizar {module_name} -h para obtener ayuda')

    # Agregar el canal a la base de datos
    if args.add:
        with Database() as db:
            db.insert_channel_record(channel.to_dicc())

    # Borrar el canal a la base de datos
    elif args.delete:
        print('Channel - Borrar un video a la base de datos - {}'.format(args.delete))
        print('Comming soon...')

    # Guardo el contenido HTML si fuera necesario
    if args.save_html:
        channel.save_html_content()

def scrap_video_w_url(url):
    """
    Obtengo la informacion de un video de Youtube tomando como entrada una URL
    Ejemplos:
    $ python manage.py -runscrap -video "https://www.youtube.com/watch?v=55O5Gnwbp14&ab_channel=Acre" -save_html
    $ python manage.py -runscrap -video "https://www.youtube.com/watch?v=UAba5-enGOk&ab_channel=JUJALAG" -save_html -add
    $ python manage.py -runscrap -video "https://www.youtube.com/watch?v=GgjrAJQmMVA&ab_channel=RubiusZ" -add
    """
    html_content = getHTTPResponse(url, responseType = 'text')
    return YoutubeVideo(html_content=html_content)

def scrap_video_w_id(id):
    """
    Obtengo la informacion de un video de Youtube tomando como entrada una ID
    Ejemplo:
    $ python manage.py -runscrap -video 55O5Gnwbp14 -save_html
    """
    return YoutubeVideo(id=id, en_html_save=False)

def scrap_channel_w_url(url):
    """
    Obtengo la informacion de un Canal de Youtube tomando como entrada una ID
    Ejemplo:
    $ python manage.py -runscrap -channel "https://www.youtube.com/@elxokas" -save_html
    """
    html_content = getHTTPResponse(url, responseType = 'text')
    return YoutubeChannel(html_content=html_content)

def scrap_channel_w_id(id):
    """
    Obtengo la informacion de un Canal de Youtube tomando como entrada una ID
    Ejemplo:
    $ python manage.py -runscrap -channel UC9c4rND1mNP-XrWQjbFxp8g -save_html -add
    $ python manage.py -runscrap -channel UCFzGNDHEZ5-7d5UXxfHUcRg -save_html -add
    """
    return YoutubeChannel(id=id)

def scrap_youtube():
    """
    Ejemplo:
    python manage.py -runscrap -all
    python manage.py -runscrap
    """
    # Abro la conexion con la base de datos
    with Database() as db:

        # Obtengo la lista de IDs de los canales
        channel_ids = db.get_youtube_channel_ids()

        # Creo una lista vacia donde van a estar los objetos
        # del tipo Channel
        channels = []

        # Obtengo la informacion para cada canal
        for channel_id in channel_ids:
            cprint(f'- Fetching HTML content for channel {channel_id}')
            channels.append( YoutubeChannel(id=channel_id) )

        # Proceso cada canal individualmente
        for channel in channels:

            # Para cada canal, actualizo la informacion y guardo
            # el contenido HTML correspondiente
            channel.fetch_channel_data()
            channel.save_html_content()

            # Para ese canal en particular, obtengo todos los IDs
            # de video asociados que esten disponible en la base
            # de datos y los agrego para procesarlos
            query = 'SELECT VIDEO_ID FROM VIDEO WHERE CHANNEL_ID = ?'
            params = (channel.id,)
            db_ids = db.select(query, params)
            db_ids = [item[0] for item in db_ids]

            # Combino las listas
            total_id_list = channel.video_ids_list + db_ids
            channel.video_ids_list = list(set(total_id_list))

            # Obtengo la informacion mas reciente para cada objeto
            # del tipo Video
            channel.fetch_videos_data()

            # Guardo la informacion en la base de datos
            db.insert_channel_record(channel.to_dicc())

            # Obtengo el diccionario de videos
            videos_dicc = channel.get_videos_dicc()

            # Guardo la informacion para cada video
            # en la base de datos
            for key in videos_dicc.keys():
                db.insert_video_record(videos_dicc[key])