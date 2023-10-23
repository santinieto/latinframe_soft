# Importar librerias
from   bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import random
import json
import platform
import os

# Variables globables
HEADER = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
SIMILARWEB_BASE_URL = 'https://www.similarweb.com/'

# Funciones
def getHTTPResponse(url, headers = None, responseType = 'page', verbose = False, debug = False):
    """ Obtengo la respuesta HTML de una URL.
        Le puedo pasar headers a la funcion, si no le paso ninguno
        toma algunos por defecto.
        La funcion ya pasa el resultado HTML a un objeto de Beautiful Soup.
    """

    # Definimos los headers
    if headers == None:
        headers = {
            'user-agent' : HEADER
        }

    # Realizamos una solicitud a la página web
    response = requests.get(url, headers = headers)

    # Debug
    if debug is True:
        print('HTTP response:\n',response)

    # Analizamos el contenido HTML de la página web utilizando BeautifulSoup
    page = BeautifulSoup(response.content, 'html.parser')

    # Muestro los datos en pantalla
    if verbose is True:
        print('Ejecutando la funcion getHTTPResponse() ...')
        print('\t- URL:', url)
        print('\t- OK:', response.ok)
        print('\t- Cogido recibido:', response.status_code)
        print('')

    # Validation check
    if response.ok == True:
        if responseType == 'text':
            return response.text
        else:
            return page
    else:
        print('')
        print('\tERROR! Ocurrio un error inesperado al cargar la URL seleccionada')
        print('\t- URL:', url)
        print('\t- OK:', response.ok)
        print('\t- Cogido recibido:', response.status_code)
        print('')
        return False

# Obtengo el sistema operativo
def getOS():
    """Obtengo la version del sistema operativo que estoy usando"""

    # Obtengo la version del sistema operativo
    OSName = platform.system()

    # Devuelvo el nombre del sistema operativo
    return OSName

# Paso un numero en string a float
def StrNum2RealNum( text ):

    if 'u' in text:
        num = round( float( text.replace('u','') ) * 1e-6,  8 )
    elif 'm' in text:
        num = round( float( text.replace('m','') ) * 1e-3,  6 )
    elif 'k' in text:
        num = round( float( text.replace('k','') ) * 1e3,   2 )
    elif 'K' in text:
        num = round( float( text.replace('K','') ) * 1e3,   2 )
    elif 'M' in text:
        num = round( float( text.replace('M','') ) * 1e6,   2 )
    elif 'G' in text:
        num = round( float( text.replace('G','') ) * 1e9,   2 )
    elif 'T' in text:
        num = round( float( text.replace('T','') ) * 1e12,  2 )
    else:
        num = round( float( text) ,  2 )

    return num

def generateRandomUserAgent(usrAgentType = None):
    """ """

    # Verifico que tengo una tipologia seleccionada
    # sino, elijo una cualquiera
    if usrAgentType is None:
        usrAgentType = random.randint(0, 1)

    # Segun el estilo selecciono el modelo
    if usrAgentType == 0:
        param1    = random.randint(90, 128)
        userAgent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{param1}.0.0.0 Safari/537.36'
    elif usrAgentType == 1:
        param1    = random.randint(90, 128)
        userAgent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{param1}.0) Gecko/20100101 Firefox/{param1}.0'
    else:
        print('Error al generar un User Agent para el encabezado HTTP')

    return userAgent

def get_time_len(segundos = 0):
    try:
        # Validar que la entrada sea un número
        segundos = int(segundos)
        if segundos < 0:
            raise ValueError("Los segundos deben ser un valor positivo.")

        # Realizar los cálculos
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segundos = segundos % 60

        # Devolver el resultado en formato "HH:MM:SS"
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    except ValueError as e:
        print(f"Error: {e}")
        return "00:00:00"

def get_formatted_date():
    from datetime import datetime

    # Obtener la fecha y hora actual
    current_datetime    = datetime.now()
    formatted_date      = current_datetime.strftime("%Y%m%d_%H%M%S")

    return formatted_date

def getDirFiles(path, pattern=None):
    """Obtener los archivos dentro de un directorio.
       Ademas, se puede utilizar un patron para filtrar
       determinados archivos que nos interesen
    """

    # Obtengo los nombres de los archivos
    fileList = os.listdir(path)

    # Filtro los nombres si se requiere
    if pattern is not None:
        fileList = [x for x in fileList if pattern in x]

    # Devuelvo la lista filtrada
    return fileList

def getDateFromFilename(filename):
    """Función para obtener la fecha y hora de un nombre de archivo usando expresiones regulares"""

    # Expresion regular requerida
    pattern = r'(\d{8})_(\d{6})'

    # Aplico el patron
    res = re.search(pattern, filename)

    # Devuelvo el resultado buscado
    if res:
        return (res.group(1), res.group(2))
    else:
        return ('00000000', '000000')

def o_fmt_error(error_code=None, error_message=None, ref_code=None, filename=None):
    # Get current date
    import datetime
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Si no se provee un codigo o un mensaje de error abortar escritura
    if((error_code is None) or (error_message is None)):
        return
    # Open error log file
    if filename is None:
        filepath = os.environ.get("SOFT_LOGS")
        filename = (filepath if filepath is not None else 'logs') + "/error_log.txt"
    with open(filename, "a", encoding='utf-8') as error_log_file:
        # Add header to error log
        error_log_file.write("=" * 80 + "\n")
        error_log_file.write("=" * 20 + " " * 14 + "SYSTEM ERROR" + " " * 14 + "=" * 20 + "\n")
        error_log_file.write("=" * 80 + "\n")
        # Add date to error log
        error_log_file.write("\n")
        error_log_file.write(f"Date: {date}\n")
        error_log_file.write("\n")
        # Add user message to error log
        error_log_file.write(f"Error Message: {error_message}\n")
        # Add reference message to error log
        error_log_file.write("\n")
        error_log_file.write(f"Reference Code: {ref_code}-{error_code}\n")
        error_log_file.write("\n")
        #
        error_log_file.close()

def cprint(msg):
    # Get current date
    import datetime
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Open console log file
    filepath = os.environ.get("SOFT_LOGS")
    filename = filepath + "/console_log.txt"
    with open(filename, "a", encoding='utf-8') as console_log_file:
        print(msg)
        console_log_file.write(date + ': ' + msg + "\n")
        console_log_file.close()

def get_similarweb_url_tuple(domain):
    """"""
    try:
        url = f'{SIMILARWEB_BASE_URL}/website/{domain}/#overview'
        url = url.replace('//','/')
        alias = domain.replace('.','_')
        return url, alias
    except:
        msg = f'Could not get URL tuple for domain {domain}'
        o_fmt_error('0001', msg, 'Function__get_similarweb_url_tuple')
        return None, None

def is_url_arg(arg):
    if '.com' in arg:
        return True
    if 'https' in arg:
        return True
    else:
        return False
