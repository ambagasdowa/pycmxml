# === === === === === === === ===  Config Section  === === === === === === === === #

configuration = {
    "db_connection": {
        "server": "10.8.0.235",
        "driver": "ODBC Driver 17 for SQL Server",
        "database": "sistemas",
        "user": "zam",
        "password": "lis",
    },
    "download_config": {
        "token": "5365d430-32dc-4f0a-8725-905aeb373c1b",
        "http_path": "transportescp.xsa.com.mx:9050/?/descargasCfdi",
        "download_path": "/tmp/",
        "dir_path": "gst_xml/",
        "filename": "cfdi_?.zip",
    },
    "service_params": {  # Partialy implemented ** Obligatorios e implementados
        "representacion": "XML",  # ** XML,PDF,ACUSE
        "pageSize": "100",  # ** [0-100] default 50
        # same as params, default is ? that means:yesterday
        "fecha": '2022-12-06:2022-12-12',
        #        "fecha": '2022-12-06',
        "fechaInicial": '?',  # yyyy-mm-dd
        "fechaFinal": '?',  # yyyy-mm-dd
        "serie": '',
        "folioEspecifico": '',  # int
        "folioInicial": '',  # int
        "folioFinal": '',  # int
        "uuid": '',  # 2d340db1-9c08-4c97-9ca8-676dc648094e
    }
}
