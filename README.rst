*******************************
TV program manager for @baaaaat
*******************************

Description:
""""""""""""
This program allows you to export xml with tv program to the database and manage it.

For default program use mysql database.

Supports only python3.

Install:
""""""""
* Move tv_program_manager.py in any folder
* Configure tv_program_manager.py
* pip install -r requirements.txt
* Use program

Configure:
""""""""""
Open tv_program_manager.py and change the settings as needed.
::

    DB_NAME = 'tv_manager'              # Database name
    DB_USER = 'tv_manager'              # Database user
    DB_PASSWORD = 'password'            # Database password
    DB_HOST = '127.0.0.1'               # Database host
    DB_PORT = 3306                      # Database port

    CHANNELS_TABLE_NAME = 'channels'    # Channels table name
    PROGRAMME_TABLE_NAME = 'pp'         # TV program table name

Usage:
""""""
::

    $ ./tv_program_manager.py -h
    usage: tv_program_manager.py [-h] [--truncate-tables TABLES [TABLES ...]]
                                 [--delete-older N] [-e FILE] [-V]

    TV program manager for baat

    optional arguments:
      -h, --help            show this help message and exit
      --truncate-tables TABLES [TABLES ...]
                            Truncate tables
      --delete-older N      Delete records older then N days
      -e FILE, --export FILE
                            Export TV program from file
      -V, --version         Show version

    (c) yakimka 2018. Version 0.1

Truncate tables:
================
::

    $ ./tv_program_manager.py --truncate-tables channels programs

Where "channels" and "programs" are table names

Delete old program records
==========================
::

    $ ./tv_program_manager.py --delete-older 7

Where "7" is the number of days to save

Export program from xml file
============================
::

    $ ./tv_program_manager.py -e ~/program.xml

Where "~/program.xml" is the file path

You also can combine this commands as you want:
===============================================
::

    $ ./tv_program_manager.py --delete-older 7 --truncate-tables channels -e ~/program.xml
    Successfully truncated "channels" table
    Export finished normally
    Successfully deleted 80078 records
