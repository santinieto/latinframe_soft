import os

def set_environment():
    # Get current directory
    home = os.getcwd()

    # Set environment variables
    os.environ["SOFT_HOME"] = home
    os.environ["SOFT_RESULTS"] = os.path.join(home, 'results')
    os.environ["SOFT_UTILS"] = os.path.join(home, 'utils')
    os.environ["SOFT_LOGS"] = os.path.join(home, 'logs')

def unset_environment():
    del os.environ["SOFT_HOME"]
    del os.environ["SOFT_RESULTS"]
    del os.environ["SOFT_UTILS"]
    del os.environ["SOFT_LOGS"]