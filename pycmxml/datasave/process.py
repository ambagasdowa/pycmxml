#!/bin/python3

#=== === === === === === === ===  NOTES Section  === === === === === === === === #

# TODO buiild as a package 

#=== === === === === === === ===  Import Section  === === === === === === === === #
import pyodbc
import urllib
import os
import sys
import subprocess

# importing element tree
# under the alias of ET
import xml.etree.ElementTree as ET

#UIX
from rich import print
from rich.progress import track
from rich.progress import Progress

from datetime import datetime,date,tzinfo, timedelta
import time

from pycfdi_transform import CFDI40SAXHandler
from pycfdi_transform.formatters.cfdi40.efisco_corp_cfdi40_formatter import EfiscoCorpCFDI40Formatter
from pycfdi_transform.formatters.cfdi40.cda_cfdi40_formatter import CDACFDI40Formatter

from re import split, sub
#Zip
import zipfile
#md5
import hashlib


# request libs
import requests
import json
from jinja2 import Environment, PackageLoader, select_autoescape


## Inner libs

import pycmxml.config.config as conf
import pycmxml.utils.utils as lib
#import connection.db as db
import pycmxml.datasave.save as dts





def parse(cursor,config,fecha):
# === === === === === === === ===  Main Section  === === === === === === === === #

    # I'm the important line
    cursor.fast_executemany = True

    print ("[violet]"+"Downloading files ..."+"[violet]")

    for i in track(range(1), description="Cleaning storing dir ..."):    time.sleep(1)  # Simulate work being done
    tmp_path = config['download_config']['download_path'] + config['download_config']['dir_path']

    clean_dir_files = subprocess.run(["rm", "-r",tmp_path], stdout=subprocess.DEVNULL)

    make_dir_files = subprocess.run(["mkdir", "-p",tmp_path+"pack",tmp_path+"unpack"], stdout=subprocess.DEVNULL)

    cmex_token =config['download_config']['token']

    http_path = config['download_config']['http_path'].replace('?',cmex_token)
    download_path = config['download_config']['download_path']
    dir_path =  config['download_config']['dir_path']
    filename = config['download_config']['filename'].replace('?', str(int(time.time()))
    )

    pack = download_path+dir_path+"pack/"
    unpack = download_path+dir_path+"unpack/"



    for i in track(range(1), description="Downloading xml files ..."):
        time.sleep(1)  # Simulate work being done


#    print ("[blue] Downloading files for date [blue]: [red]"+fecha+"[red]")


    pageSize = config['service_params']['pageSize']
    representacion = config['service_params']['representacion']

    download_files = subprocess.run([ "https" , "--print=hb","--download" , http_path ,'representacion=='+representacion,'pageSize=='+pageSize,"fecha=="+fecha, "--output" , pack+filename ]) 

    try:
        with zipfile.ZipFile(pack+filename, 'r') as zip_ref:
            zip_ref.extractall(unpack)
    except zipfile.BadZipfile:
        print("[red] zip file : "+pack+filename+" from provider with errors , try again ...[red]")

    # One with have the files 
    def get_files(path):
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                yield file

    files = []
    for file in get_files(unpack):
        files.append(file)



    for i in track(range(1), description="unzipping and process files ..."):
        time.sleep(1)  # Simulate work being done
    print (files)



    #build the function from hir
    # initialize files_id for post treatment
    files_ids = []
    for filename in files:
        source = unpack + filename

    # Open,close, read file and calculate MD5 on its contents 
        with open(source, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            md5_returned = hashlib.md5(data).hexdigest()

        name, ext = os.path.splitext(filename)
        #uuid,doctype:FAC,idfac,Date,SomeCtrlnum
        split_data = str(name).split('_')

        save_file = (split_data[1]+'_'+split_data[2],split_data[0],md5_returned,datetime.now().isoformat(timespec='seconds'),'',1,
    )

        qry_md5 = "select [_md5sum] from sistemas.dbo.cmex_api_controls_files where [_md5sum] = ?"
        md5 = False
        cursor.execute(qry_md5,(md5_returned,))
        for row in cursor.fetchall():
            if(row[0] == md5_returned):
                md5 = True

        if(md5 != True):
            print("[blue] save file : "+str(source)+"[blue]")
            insert_file = 'insert into sistemas.dbo.cmex_api_controls_files \
            (labelname,_filename,_md5sum,created,modified,_status) values( \
            ?,?,?,?,?,? \
            )'
            for i in track(range(2), description="Saving to Complement data to database..."):
                time.sleep(1)  # Simulate work being done

            count = cursor.execute(insert_file, save_file)
            cursor.commit()

            # get last id from comprobante
            cursor.execute(
                "select IDENT_CURRENT('sistemas.dbo.cmex_api_controls_files') as id")

            cmex_api_controls_files_id = cursor.fetchone()[0]
            cursor.commit()
            files_ids.append(str(cmex_api_controls_files_id))
            print("[red]cmex_api_controls_files_id : "+str(cmex_api_controls_files_id)+"[red]")

    #params = cmex_api_controls_files_id , source

            # NOTE after set the source start with the parsing :
            # First get the general information
            # path xml que queremos transformar
            path_xml = source
            print("[blue] Start CartaPorte20 DATA  XTRACTION [blue]")
            tree = ET.parse(source)
            # getting the parent tag of
            # the xml document
            # root = tree.getroot()

            # https://docs.python.org/es/3.9/library/xml.etree.elementtree.html
            ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4',
                  'cartapore20': 'http://www.sat.gob.mx/CartaPorte20'}


            transformer = CFDI40SAXHandler()  # Cfdi 4.0
            # transformer = CFDI40SAXHandler().use_concepts_cfdi40()  # Cfdi 4.0
            cfdi_data = transformer.transform_from_file(path_xml)

            print("[blue] Start CFDI DATA XTRACTION [blue]")

            complements_items = ['version', 'serie', 'folio', 'fecha', 'no_certificado', 'subtotal', 'descuento', 'total', 'moneda', 'tipo_cambio', 'tipo_comprobante', 'metodo_pago', 'forma_pago',
                                 'condiciones_pago', 'exportacion', 'lugar_expedicion', 'sello', 'certificado']

            concepts = ['confirmacion', 'emisor', 'receptor',
                        'conceptos', 'impuestos', 'complementos', 'addendas']

            fields = ('cmex_api_controls_files_id',)
            save_complement = (cmex_api_controls_files_id, )

            # General info

            for ind, data in cfdi_data['cfdi40'].items():
                if ind in complements_items:
                    fields = fields + (ind,)
                    save_complement = save_complement + (data,)

            cmex_api_standings_id = 1
            cmex_api_parents_id = 1
            created = datetime.now().isoformat(timespec='seconds')
            modified = ''
            status = 1

            add_fields = ['cmex_api_standings_id',
                          'cmex_api_parents_id', 'created', 'modified', '_status']
            add_save = [cmex_api_standings_id, cmex_api_parents_id,
                        created, modified, status]

            for this_tuple in add_save:
                save_complement = save_complement + (this_tuple,)

            for this_fields in add_fields:
                fields = fields + (this_fields,)

            insert = "insert into sistemas.dbo.cmex_api_cfdi_comprobante(cmex_api_controls_files_id, version, serie, folio, fecha,no_certificado, subtotal, descuento, total, moneda,tipo_cambio, tipo_comprobante, metodo_pago, forma_pago ,condiciones_pago,exportacion, lugar_expedicion, sello, certificado ,cmex_api_standings_id,cmex_api_parents_id, created, modified, _status) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            # NOTE Working from hir
            for i in track(range(2), description="Saving to Complement data to database..."):
                time.sleep(1)  # Simulate work being done

            count = cursor.execute(insert, save_complement)
            cursor.commit()

            # get last id from comprobante
            cursor.execute(
                "select IDENT_CURRENT('sistemas.dbo.cmex_api_cfdi_comprobante') as id")
            comprobante_last_id = cursor.fetchone()[0]
            cursor.commit()
            #print("[red]"+str(comprobante_last_id)+"[red]")


            # === === === === === === === ===  Tfd11 === === === === === === === ===
            print("[blue] Start TFD11 DATA  XTRACTION [blue]")
            print(cfdi_data['tfd11'])

            tfd_elements = [
             'version'
           , 'no_certificado_sat'
           , 'uuid'
           , 'fecha_timbrado'
           , 'rfc_prov_cert'
           , 'sello_cfd'
           , 'sello_sat'
            ]
            save_tfd = (cmex_api_controls_files_id,)
            for indx,tfdata in cfdi_data['tfd11'][0].items():
                if indx in tfd_elements :
                    save_tfd = save_tfd + (tfdata,)

            for this_tuple in add_save:
                save_tfd = save_tfd + (this_tuple,)

            tfd_insert = 'insert into sistemas.dbo.cmex_api_cfdi_tfds ( \
                 cmex_api_controls_files_id \
                ,version \
                ,no_certificado_sat \
                ,uuid \
                ,fecha_timbrado \
                ,rfc_prov_cert \
                ,sello_cfd \
                ,sello_sat \
                ,cmex_api_standings_id \
                ,cmex_api_parents_id \
                ,created \
                ,modified \
                ,_status \
                ) values(?,?,?,?,?,?,?,?,?,?,?,?,?)'

            for i in track(range(2), description="Saving to TimbreFiscal data to database..."):
                time.sleep(1)  # Simulate work being done

            cursor.execute(tfd_insert,save_tfd)
            cursor.commit()

            # === === === === === === === ===  Tfd11 === === === === === === === ===


            element_qry = "insert into sistemas.dbo.cmex_api_cfdi_data( \
                            cmex_api_controls_files_id \
                            ,cmex_api_section_id \
                            ,cmex_api_tags_id \
                            ,value \
                            ,created \
                            ,modified \
                            ,_status \
                        ) values(?,?,?,?,?,?,?)"

            # === === === === === === === ===  Emisor === === === === === === === ===

            dts.indb(True,cfdi_data['cfdi40']['emisor'],cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=1,offset=0,step=0,namespace = 'emisor')

            # === === === === === === === ===  Receptor === === === === === === === ===

            dts.indb(True,cfdi_data['cfdi40']['receptor'],cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=2,offset=0,step=0,namespace = 'receptor')
            # === === === === === === === ===  Receptor === === === === === === === ===

            impuestos_element = "select id,cmex_api_tagname from sistemas.dbo.cmex_api_tags where cmex_api_section_id = ? and id in (11,12)"
            dts.indb(True,cfdi_data['cfdi40']['impuestos'],cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element=impuestos_element,init=4,offset=0,step=0,namespace = 'impuestos')


            # === === === === === === === ===  cartaporte === === === === === === === ===

            dts.indb(True,cfdi_data['cfdi40']['impuestos']['retenciones'][0],cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=5,offset=0,step=0,namespace = 'retenciones')

            # === === === === === === === ===  Traslados === === === === === === === ===
            # Retentions && tralations

            dts.indb(True,cfdi_data['cfdi40']['impuestos']['traslados'][0],cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=6,offset=0,step=0,namespace = 'traslados')

            # === === === === === === === ===  cartaporte === === === === === === === ===
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=7,offset=0,step=0,namespace = 'carta_porte')
            # === === === === === === === ===  ubicacion_origen === === === === === === === ===
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=8,offset=0,step=2,namespace = 'ubicacion')
            # === === === === === === === ===  Domicilio  === === === === === === === ===
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=9,offset=0,step=2,namespace = 'domicilio')
            # === === === === === === === ===  Mercancias  === === === === === === === ===
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=12,offset=0,step=0,namespace = 'mercancias')
            # === === === === === === === ===  Mercancia  === === === === === === === ===
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=13,offset=0,step=0,namespace = 'mercancia')
            # === === === === === === === ===  autotransporte  === === === === === === === ===
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=14,offset=0,step=0,namespace = 'autotransporte')
            # === === === === === === === ===  identificacion  === === === === === === === ===
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=15,offset=0,step=0,namespace = 'identificacion_vehicular')
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=16,offset=0,step=0,namespace = 'seguros')
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=17,offset=0,step=0,namespace = 'remolque')
            dts.indb(False,cfdi_data,cursor,tree,ns,cmex_api_controls_files_id,created,modified,status,element_qry,mod_element='',init=18,offset=0,step=0,namespace = 'tipos_figura')
            # === === === === === === === ===  TFD11  === === === === === === === ===

        else:
            print(" [gray] The file [gray] : [blue] "+str(filename)+"[blue] [red] is not process because already exists in the db owner [red]")

    if not files_ids:
        print("Nothing to save ...")
    else:
        ## TODO Run db Procedure for info treatments and pass the id's files  as params 
        print(files_ids)

#    cursor.close()



def fetch_api(config, module,isJson):
    print(f"[blue]fetch the method[blue]")
    print(f"[red]testing templates ...[red]")

# JSON method
    #url = 'https://api.github.com/some/endpoint'
    #headers = {'user-agent': 'my-app/0.0.1'}
    #params = {'key':'value'}

    #response = requests.get(url, headers=headers,params=params)
    #print(response.text)
    #print(response.json())
    ## Getting dictionary
    #print(json.loads(response.text))
    ##Simulate the response
    #person_string = '{"name": "Bob", "languages": "English", "numbers": [2, 1.6, null]}'
    ## Getting dictionary
    #person_dict = json.loads(person_string)
    ## Pretty Printing JSON string back
    #print(json.dumps(person_dict, indent = 4, sort_keys=True))

    print(f"[red]JSON:[red][cyan] Printing ...[cyan]")
    print(config)
    print(config.app_section.michelin)
# XML method
    url=config.app_section[module].url
    headers=config.app_section[module].headers
    #headers = {'content-type': 'application/soap+xml'}
    # headers = {'content-type': 'text/xml'}

    # body = """<?xml version="1.0" encoding="UTF-8"?>
    #             <soapenv:Envelope
    #                 xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    #                 xmlns:ws="http://webservice.web.integracao.sascar.com.br/">
    #                     <soapenv:Header />
    #                     <soapenv:Body>
    #                             <ws:obterPacotePosicoes>
    #                                 <usuario>GST.GR</usuario>
    #                                 <senha>GRGST.2022</senha>
    #                                 <quantidade>3000</quantidade>
    #                             </ws:obterPacotePosicoes>
    #                     </soapenv:Body>
    #             </soapenv:Envelope>
    #         """

# Template('Hello {{ name }}!').stream(name='foo').dump('hello.html')

    env = Environment(
                        loader=PackageLoader('pycmxml', 'templates'),
                        autoescape=select_autoescape(
                                                        enabled_extensions=('html', 'xml','md'),
                                                        disabled_extensions=('txt'),
                                                        default_for_string=True,)
                    )

    file_ext = "xml"
    template_files = config.app_section[module].methods[file_ext]

    xfile = f"{module}/{template_files}.{file_ext}"
    #template = env.get_template('michelin/obterPacotePosicoes.xml')
    template = env.get_template(xfile)
    print(template)
    body = template.render()
    # print(body)
    response = requests.post(url,data=body,headers=headers)
    print(response.content)

    print(f"[red]End of request [red]")





