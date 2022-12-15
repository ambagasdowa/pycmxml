---
title: "Python xml to database parser"
author: "baizabal.jesus@gmail.com"
extensions:
  - image_ueberzug
  - qrcode
  - render
styles:
  style: solarized-dark
  table:
    column_spacing: 15
  margin:
    top: 3
    bottom: 0
  padding:
    top: 3
    bottom: 3
---

# pycmxml

This is a small utility for download xml zipped from a repository and store in a database

# Install

```bash
git clone https://github.com/ambagasdowa/pycmxml.git
python3 -m pip install pycmxml
```
OR 
```bash
python3 -m pip install git+https://github.com/ambagasdowa/pycmxml.git
```
# Config

  mv config_sample.py config.py

 edit according to your needs 
```python
configuration = {
    "db_connection": {
        "server": "127.0.0.1",
        # Needs a previous odbc driver installed
        "driver": "ODBC Driver 17 for SQL Server",
        "database": "db",
        "user": "usr",
        "password": "pass",
    },
    "download_config": {
        "token": "some_random_char36",
        "http_path": "ws_url:port/?/file", # if needed <?> is replaced by <token>
        "download_path": "/tmp/",
        "dir_path": "xml/",
        "filename": "cfdi_?.zip", # if needed <?> is replaced by a random number
    },
    # This params are specified by the web service can be changed in https execution process
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

```

# Usage
  
  pycmxml --help

# Example

> dates : set the date for process files inputs can be --dates={[date:range] , [date0,date1] or [date]}  (default: yesterday)')

 get a range of dates 
```bash
  pycmxml --dates='2022-12-01:2022-12-15'
```

read from config.py
```bash
  pycmxml --config
```


# Todo

> Build functions for print messages and hide them
