import sys
import os

# Agrega el directorio actual al PYTHONPATH
sys.path.append( os.getcwd() )

# Importo mi modulo
from src.db import Database

# Ejecuto la rutina SQL
with Database() as db:
    domain = 'youtube.com  fasfasfa'

    # Defino la consulta que tengo que realizar
    query = f"select domain_id from similarweb_domains where domain = '{domain}'"

    # El resultado es una lista de tuplas
    # Me quedo con el primer elemento
    query_res = db.select(query)
    if len(query_res) > 0:
        result = [x[0] for x in query_res]
        domain_id = list(set(result))[0]

        # Muestro el resultado en pantalla
        print(domain_id)
    else:
        print('No results')

    # Quiero obtener ahora el maximo valor de IDs
    query = "select max(domain_id) from similarweb_domains"

    # El resultado es una lista de tuplas
    # Me quedo con el primer elemento
    result = [x[0] for x in db.select(query)]
    max_id = list(set(result))[0]

    # Muestro el resultado en pantalla
    print(max_id)