import sys
import os

# Agrega el directorio actual al PYTHONPATH
sys.path.append( os.getcwd() )

# Agrego mis modulos
try:
    from src.db import Database
except:
    from db import Database

# Abre el archivo en modo lectura (por defecto)
filename = "sql/0056_news_tables.sql"

try:
    with open(filename, "r") as archivo:
        content = archivo.read()  # Lee todo el contenido del archivo y lo almacena en la cadena 'contenido'

    # Separo las queries
    queries = content.split('\\')

    # Ejecuto la rutina SQL
    with Database() as db:
        for query in queries:
            print(query)
            print('-'*100)
            db.exec(query)

except FileNotFoundError:
    print(f"El archivo '{filename}' no fue encontrado.")
except Exception as e:
    print(f"Ocurrió un error: {e}")