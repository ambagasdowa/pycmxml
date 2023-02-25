import pyodbc
# UIX
from rich import print
from rich.progress import track
from rich.progress import Progress

# import config
import pycmxml.config.config as conf


def connect(config):

    config = conf.read_config()

    try:
        cnxn = pyodbc.connect(
            'Trusted_Connection=no;DRIVER={'+config['db_connection']['driver']+'};SERVER='+config['db_connection']['server']+';DATABASE=' +
            config['db_connection']['database']+';UID=' +
            config['db_connection']['user']+';PWD=' +
            config['db_connection']['password']
        )
    except pyodbc.Error as e:
        # print("Error %d: %s" % (e.args[0], e.args[1]))
        print("Error {}: {}".format(e.args[0], e.args[1]))
        sys.exit(1)

    print("[blue]DB Connected...[blue]")

    return cnxn.cursor()
