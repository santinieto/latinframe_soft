import sys
import os

# Agrega el directorio actual al PYTHONPATH
sys.path.append( os.getcwd() )

# Agrego mis modulos
try:
    from src.db import Database
except:
    from db import Database

# Defino la URL base
SIMILARWEB_BASE_URL = 'https://www.similarweb.com/'

with Database() as db:

    # Consulta SQL
    query = "select domain from similarweb_domains"
    query_res = db.select(query)
    result = [x[0] for x in query_res]
    domains = list(set(result))

    url_list = []
    for domain in domains:
        url = (f'{SIMILARWEB_BASE_URL}/website/{domain}', domain.replace('.','_'))
        print(url)
