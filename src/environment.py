import os
import json
from src.utils import o_fmt_error

def set_environment():
    # Get current directory
    home = os.getcwd()

    # Set environment variables
    os.environ["SOFT_HOME"] = home
    os.environ["SOFT_RESULTS"] = os.path.join(home, 'results')
    os.environ["SOFT_UTILS"] = os.path.join(home, 'utils')
    os.environ["SOFT_LOGS"] = os.path.join(home, 'logs')

    # Leer las credenciales desde el archivo JSON
    try:
        credentials_file = os.environ["SOFT_UTILS"] + 'credentials.json'
        with open(credentials_file, 'r') as config_file:
            config = json.load(config_file)

        os.environ["EMAIL_ADRESS"] = config.get("email")
        os.environ["EMAIL_PASSWORD"] = config.get("password")
        os.environ["EMAIL_PLATFORM"] = config.get("platform")
    except Exception as e:
        os.environ["EMAIL_ADRESS"] = ''
        os.environ["EMAIL_PASSWORD"] = ''
        os.environ["EMAIL_PLATFORM"] = ''
        msg = f'Could not load environmnet variables.\nError: {e}'
        o_fmt_error('0001', msg, 'Function__set_environment')

def unset_environment():
    del os.environ["SOFT_HOME"]
    del os.environ["SOFT_RESULTS"]
    del os.environ["SOFT_UTILS"]
    del os.environ["SOFT_LOGS"]
    del os.environ["EMAIL_ADRESS"]
    del os.environ["EMAIL_PASSWORD"]
    del os.environ["EMAIL_PLATFORM"]