# Libraries from Python
import sys

# My modules
import src.youtube_scrap as yt
import src.similarweb_scrap as sw
import src.news_scrap as nw
import src.product_scrap as prd
import src.environment as env
from src.arguments import get_parser_args
from src.arguments import process_parser_args
from src.mail import send_mail

# Scraper principal
def handle_scrap_args(args):
    # Defino un nombre por defecto al modulo
    module_name = 'scrap'

    # Obtengo el mensaje de ayuda
    if args.ayuda:
        pass

    # Scrapeo las noticias
    if args.all or args.news:
        nw.scrap_news()

    # Scrapeo Youtube
    if args.all or args.youtube:
        yt.scrap_youtube()

    # Scrapeo SimilarWeb
    if args.all or args.similarweb:
        sw.scrap_similarweb()

    # Scrapeo los jueuges
    if args.all or args.toys:
        prd.scrap_amazon_products()
        prd.scrap_meli_products()

    # Mando el correo si se requiere
    if args.send_mail:
        send_mail(filename='test.pdf')

    # Mensaje de error por defecto
    else:
        print(f'Modulos {module_name}')
        print(f'\tSe ha producido un error al procesar el comando')
        print(f'\tPuede utilizar {module_name} -h para obtener ayuda')

# Funcion principal del programa
if __name__ == '__main__':
    # Preparo el entorno para operar
    env.set_environment()

    # Proceso los argumentos
    parser, args = get_parser_args()

    # Verifico si tengo que correr el scraper principal
    if args.module == 'scrap':
        handle_scrap_args(args)
    else:
        process_parser_args(parser, args)

    # Clear environment variables
    env.unset_environment()

    # Salgo del programa con valor 0
    sys.exit(0)
