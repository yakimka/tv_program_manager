*******************************
TV program manager for @baaaaat
*******************************

Description:
""""""""""""
This program allows you to import xml with TV program to the database and manage it.

For default program support only mysql database.

Supports only python3.

Install:
""""""""
* Move tv_program_manager.py in any folder
* Configure tv_program_manager.py
* pip install -r requirements.txt
* Use program

Configure:
""""""""""
Set environment variables:

* TV_PROGRAM_MANAGER_DB_NAME        - Database name
* TV_PROGRAM_MANAGER_DB_USER        - Database user
* TV_PROGRAM_MANAGER_DB_PASSWORD    - Database password

For example:
::

    export TV_PROGRAM_MANAGER_DB_NAME=tv_manager
    export TV_PROGRAM_MANAGER_DB_USER=tv_manager
    export TV_PROGRAM_MANAGER_DB_PASSWORD=password

Open tv_program_manager.py and change the settings as needed.
::

    DB_HOST = '127.0.0.1'               # Database host
    DB_PORT = 3306                      # Database port

    CHANNELS_TABLE_NAME = 'channels'    # Channels table name
    PROGRAMME_TABLE_NAME = 'pp'         # TV program table name

Database configuration:
"""""""""""""""""""""""
Table for channels:
===================

* name: VARCHAR(150)
* channel: VARCHAR(100) UNIQUE

Table for TV program:
=====================

* name: VARCHAR(150)
* date: DATE
* time: TIME
* timestart: INT(10)
* timestop: INT(10)
* channel: VARCHAR(100)
* UNIQUE index on name, date, time, channel

If you change the maximum length of the fields then also change it in tv_program_manager.py for models

SQL example:
============
::

    CREATE TABLE channels
    (
        name varchar(150),
        channel varchar(100)
    );
    CREATE UNIQUE INDEX channels_channel_uindex ON channels (channel);

    CREATE TABLE pp
    (
        name varchar(150),
        date date,
        time time,
        timestart int(10),
        timestop int(10),
        channel varchar(100)
    );
    CREATE UNIQUE INDEX pp_name_date_time_channel_uindex ON pp (name, date, time, channel);

Usage:
""""""
::

    $ ./tv_program_manager.py -h
    usage: tv_program_manager.py [-h] [--truncate-tables TABLES [TABLES ...]]
                                 [--delete-older N] [-f FILE] [-V]

    TV program manager for baat

    optional arguments:
      -h, --help            show this help message and exit
      --truncate-tables TABLES [TABLES ...]
                            Truncate tables
      --delete-older N      Delete records older then N days
      -f FILE, --file FILE  Import TV program from file
      -V, --version         Show version

    (c) yakimka 2018. Version 0.1


Truncate tables:
================
::

    $ ./tv_program_manager.py --truncate-tables channels pp

Where "channels" and "pp" are table names

Delete old TV program records
=============================
::

    $ ./tv_program_manager.py --delete-older 7

Where "7" is the number of days to save

Import TV program from xml file
===============================
::

    $ ./tv_program_manager.py -f ~/program.xml

Where "~/program.xml" is the file path

You also can combine this commands as you want:
===============================================
::

    $ ./tv_program_manager.py --delete-older 7 --truncate-tables channels -f ~/program.xml
    Successfully truncated "channels" table
    Import finished normally
    Successfully deleted 80078 records

