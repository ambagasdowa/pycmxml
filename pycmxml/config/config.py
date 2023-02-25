# change to more standar configuration file like yaml or ini
# === === === === ===
import os
from platformdirs import *
import configparser
# UIX
from rich import print
from rich.progress import track
from rich.progress import Progress

# this must be a function
xdir = user_config_dir('pycmxml')
config_name = '/config.ini'

sample = """
[DEFAULT]
    app = pycmxml
    author = Jesus Baizabal
    mail = baizabal.jesus@gmail.com
    url = baizabal.xyz
    github = https://github.com/ambagasdowa 
[db_connection]
    #Ip for the server 
    server: 127.0.0.1
    driver: ODBC Driver 17 for SQL Server
    database: db
    user: sa
    password: sa
[download_config]
    token: 5365d430-32dc-4f0a-8725-905aeb373c1b
    http_path: transportescp.xsa.com.mx:9050/?/descargasCfdi
    download_path: /tmp/
    dir_path: gst_xml/
    filename: cfdi_?.zip
[service_params]
    # can be [XML,PDF,ACUSE]
    representacion: XML
    #[0-100] defaults 50
    pageSize: 100
    # same as params default is ? that means:yesterday
    fecha: '2022-12-06:2022-12-12'
    #        fecha: '2022-12-06'
    #fechaInicial => yyy-mm-dd | ? take argument from command line
    fechaInicial: '?'
    fechaFinal: '?'
    serie: ''
    # int
    folioEspecifico: ''
    folioInicial: ''
    folioFinal: ''
    # 2d340db1-9c08-4c97-9ca8-676dc648094e
    uuid: ''
[apps]
    michelin=true
    cmex=true
[michelin]
    url: http://sasintegra.sascar.com.br/SasIntegra/SasIntegraWSService?wsdl
    # headers:{content-type: 'application/soap+xml'}
    headers: {content-type: 'text/xml'}
    xtension : xml
    # Add methods for request to WS 
    # and need to add the xml-template for the body of request
    methods : obterPacotePosicoes,obterVeiculos
 """


def create_config(args):
    # set a parameter for defaults:
    debug = args.debug

    if (os.path.exists(xdir)):
        if debug:
            print(f"path found ok {xdir}...")
    else:
        if debug:
            print(f"[red]No path {xdir} found now create it ...")
        os.mkdir(xdir)

    if os.path.isfile(f"{xdir}{config_name}"):
       # Replace File
        if debug:
            print(f"File found backing up and replace")
        create_file()
    else:
        # Create File
        create_file()


def create_file():
    try:
        with open(f"{xdir}{config_name}", 'w') as f:
            f.write(sample)
    except FileNotFoundError:
        print(f"The {xdir} directory does not exist")


def read_config():
    # parse file in config dir
    config = configparser.ConfigParser()
    config.read(f"{xdir}{config_name}")
    return config

# === === === === === === === ===  Config Section  === === === === === === === === #
