from src.db import Database

def sql_help(script_name, arg):
    print('Usage:')
    print(f'python {script_name} {arg} []')
    print( '\t "query" : Execute the given query')

def sql_get_query_fromfile(filename):
    """
    Verifico si tengo que leer un archivo
    Ejemplo
    $ python manage.py -sql -file sql/0015_query_1.sql
    """

    # Establezco un valor por defecto para la consulta
    query = ''

    # Trato de obtener la consulta a partir de un archivo
    try:
        with open(filename, "r") as archivo:
            # Lee todo el contenido del archivo y lo almacena en la cadena 'query'
            query = archivo.read()

        # Ahora 'query' contiene el contenido del archivo como una cadena
        # La muestro por pantalla si no hubo errores
        print("SQL query:\n\n" + query)

    # Defino los errores
    except FileNotFoundError:
        print(f"El archivo '{filename}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

    return query

def sql_execute(query):
    """
    Ejecuto una consulta SQL dada por el usuario teniendo en cuenta
    que si es del caracter SELECT entonces tengo que mostrar los datos
    resultado en pantalla.
    Ejemplo:
    $ python manage.py -sql "select * from channel;"
    """

    # Abro la conexion con la base de datos
    with Database() as db:

        # Obtengo la primer palabra
        fw = query.split()[0].lower()

        # Si es un SELECT tengo que mostrar los resultados
        # Ejemplo:
        # python manage.py -sql "SELECT CHANNEL_ID FROM CHANNEL"
        # python manage.py -sql "SELECT * FROM CHANNEL"
        # python manage.py -sql "select * from channel"
        if fw == 'select':
            results = db.select(query, ())
            for result in results:
                print(result)

        # Si es otro tipo de consulta la ejecuto directamente
        # Ejemplo
        # python manage.py -sql "update channel set channel_name = 'toycantando_edit' where channel_id = 'UC2xjgvWb9cx5F637XjsUNxw'"
        # python manage.py -sql "update channel set channel_name = 'toycantando' where channel_id = 'UC2xjgvWb9cx5F637XjsUNxw'"
        else:
            db.exec(query)