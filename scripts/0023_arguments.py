import argparse
import sys

# Nota 1: Si a un argumento le pongo action='store_true' entonces solo puedo
#         preguntar si el comando esta presente o no, nada mas. Si quiero guardar
#         un valor entonces no tengo que poner nada

if __name__ == '__main__':

    ##################################################################################
    # Generacion de comados
    ##################################################################################
    # Creo el parser principal
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Modulo general', dest='module')

    # Modulos
    scrap_parser = subparsers.add_parser('scrap', help='Modulo principal')
    test_parser = subparsers.add_parser('test', help='Modulo de pruebas')
    video_parser = subparsers.add_parser('video', help='Modulo de scrap de video')
    channel_parser = subparsers.add_parser('channel', help='Modulo de scrao de canal')
    sw_parser = subparsers.add_parser('sw', help='Modulo de scrap de SimilarWebs')
    sql_parser = subparsers.add_parser('sql', help='Modulo de comandos SQL')
    news_parser = subparsers.add_parser('news', help='Modulo de noticias')
    backup_parser = subparsers.add_parser('backup', help='Modulo de generacion de backups')

    # Modulo general
    scrap_parser.add_argument('-ay', '--ayuda', action='store_true', help='Mensaje de ayuda')
    scrap_parser.add_argument('-all', '--all', action='store_true', help='Scrapear todo')
    scrap_parser.add_argument('-yt', '--youtube', action='store_true', help='Scrapear YouTube')
    scrap_parser.add_argument('-nw', '--news', action='store_true', help='Scrapear noticias')
    scrap_parser.add_argument('-sw', '--similarweb', action='store_true', help='Scrapear SimilarWebs')

    # Modulo de tests
    test_parser.add_argument('-ay', '--ayuda', action='store_true', help='Mensaje de ayuda')
    test_parser.add_argument('-l', '--list', action='store_true', help='Listar tests')
    test_parser.add_argument('-r', '--run', type=int, nargs='*', help='Correr un lista de tests')

    # Modulo de videos
    video_parser.add_argument('-ay', '--ayuda', action='store_true', help='Mensaje de ayuda')
    video_parser.add_argument('-add', '--add', type=str, help='Agregar un video a la base de datos')
    video_parser.add_argument('-del', '--delete', type=str, help='Borrar un video de la base de datos')
    video_parser.add_argument('-save-html', '--save-html', action='store_true', help='Guardar contenido HTML del video')

    # Modulo de canales
    channel_parser.add_argument('-ay', '--ayuda', action='store_true', help='Mensaje de ayuda')
    channel_parser.add_argument('-add', '--add', type=str, help='Agregar un canal a la base de datos')
    channel_parser.add_argument('-del', '--delete', type=str, help='Borrar un canal de la base de datos')
    channel_parser.add_argument('-save-html', '--save-html', action='store_true', help='Guardar contenido HTML del canal')

    # Modulo de SimilarWebs
    sw_parser.add_argument('-ay', '--ayuda', action='store_true', help='Mensaje de ayuda')
    sw_parser.add_argument('-add', '--add', type=str, help='Agregar una web usando un dominio URL')
    sw_parser.add_argument('-del', '--delete', type=str, help='Borrar un dominio desde la base de datos')
    sw_parser.add_argument('-web', '--web', type=str, help='Scrapear una web')
    sw_parser.add_argument('-skip-scrap', '--skip-scrap', action='store_true', help='Mensaje de ayuda')

    # Modulo de comandos SQL
    sql_parser.add_argument('-ay', '--ayuda', action='store_true', help='Mensaje de ayuda')
    sql_parser.add_argument('-f', '--file', type=str, help='Ejecutar una consulta SQL leida desde un scrip')
    sql_parser.add_argument('-q', '--query', type=str, help='Ejecutar una consulta SQL obtenida desde teclado')
    sql_parser.add_argument('-get', '--get',    metavar=('TABLE_NAME','FIELD_NAME','TARGET'), type=str, nargs=3, help='Ejecutar un comando SELECT en la base de datos')
    sql_parser.add_argument('-sel', '--select', metavar=('TABLE_NAME','FIELD_NAME','TARGET'), type=str, nargs=3, help='Ejecutar un comando SELECT en la base de datos')
    sql_parser.add_argument('-del', '--delete', metavar=('TABLE_NAME','FIELD_NAME','TARGET'), type=str, nargs=3, help='Ejecutar un comando DELETE en la base de datos')

    ##################################################################################
    # Generacion de pruebas
    ##################################################################################
    # Leo los comandos de teclado
    args = parser.parse_args()

    # Modulo de tests
    if args.module == 'test':
        if args.ayuda:
            test_parser.print_help()
        elif args.list:
            print('Tests - Listar los tests disponibles')
        elif args.run:
            print('Tests - Ejecutar los siguientes tests: {}'.format(args.run))
        else:
            test_parser.print_help()

    # Modulo de videos
    if args.module == 'video':
        if args.save_html:
            print('Video - Guardar contenido HTML del video')

        if args.ayuda:
            video_parser.print_help()
        elif args.add:
            print('Video - Agregar un video a la base de datos - {}'.format(args.add))
        elif args.delete:
            print('Video - Borrar un video a la base de datos - {}'.format(args.delete))
        else:
            video_parser.print_help()

    # Modulo de canales
    if args.module == 'channel':
        if args.save_html:
            print('Channel - Guardar contenido HTML del video')

        if args.ayuda:
            video_parser.print_help()
        elif args.add:
            print('Channel - Agregar un video a la base de datos - {}'.format(args.add))
        elif args.delete:
            print('Channel - Borrar un video a la base de datos - {}'.format(args.delete))
        else:
            video_parser.print_help()

    # Modulo de SimilarWeb
    if args.module == 'sw':
        if args.skip_scrap:
            print('SimilarWebs - Guardar contenido HTML del video')

        if args.ayuda:
            sw_parser.print_help()
        elif args.add:
            print('SimilarWebs - Agregar una web a la base de datos - {}'.format(args.add))
        elif args.delete:
            print('SimilarWebs - Borrar una web a la base de datos - {}'.format(args.delete))
        elif args.web:
            print('SimilarWebs - Obtener datos de una web - {}'.format(args.web))
        else:
            sw_parser.print_help()

    # Modulo de comandos SQL
    if args.module == 'sql':
        if args.ayuda:
            sql_parser.print_help()
        if args.file:
            print('SQL - Ejecutar un comando SQL desde un archivo - {}'.format(args.file))
        if args.query:
            print('SQL - Ejecutar un comando SQL desde consola - {}'.format(args.query))
        if args.get:
            print('SQL - Obtener datos desde la base da tos - {}'.format(args.get))
        if args.select:
            print('SQL - Obtener datos desde la base da tos - {}'.format(args.select))
        if args.delete:
            print('SQL - Borrar datos desde la base da tos - {}'.format(args.delete))

    # Modulo de noticias
    if args.module == 'news':
        pass

    # Modulo de generacion de backups
    if args.module == 'backup':
        pass
