#!/usr/bin/env python3

import argparse
import os
import sys
from collections import namedtuple
from datetime import date, datetime, timedelta
from xml.etree import ElementTree

import peewee
from peewee import (MySQLDatabase, Model, DateField, TimeField,
                    IntegerField, CharField)

VERSION = '0.2'

######################## CONFIG #########################
#########################################################
DB_NAME = os.getenv('TV_PROGRAM_MANAGER_DB_NAME')
DB_USER = os.getenv('TV_PROGRAM_MANAGER_DB_USER')
DB_PASSWORD = os.getenv('TV_PROGRAM_MANAGER_DB_PASSWORD')
DB_HOST = '127.0.0.1'
DB_PORT = 3306

CHANNELS_TABLE_NAME = 'channels'
PROGRAMME_TABLE_NAME = 'pp'
#########################################################
##################### END OF CONFIG #####################


TABLES_ALLOWED_TO_TRUNCATE = [CHANNELS_TABLE_NAME, PROGRAMME_TABLE_NAME]
_REGISTERED_MODELS = {}
db = MySQLDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD,
                   host=DB_HOST, port=DB_PORT)


def register_model(class_):
    _REGISTERED_MODELS[class_._meta.table_name] = class_
    return class_


class BaseModel(Model):
    class Meta:
        database = db


@register_model
class Channel(BaseModel):
    name = CharField(max_length=150)
    channel = CharField(unique=True, max_length=100)

    class Meta:
        db_table = CHANNELS_TABLE_NAME


@register_model
class Programme(BaseModel):
    name = CharField(max_length=150)
    date = DateField()
    time = TimeField()
    timestart = IntegerField()
    timestop = IntegerField()
    channel = CharField(max_length=100)

    class Meta:
        db_table = PROGRAMME_TABLE_NAME
        indexes = (
            (('name', 'date', 'time', 'channel'), True),
        )


TVProgramme = namedtuple('TVProgramme', 'channels programmes')


class TVProgrammeParser:
    def __init__(self, file):
        self.file = file

    def parse(self):
        channels = []
        programmes = []
        root = ElementTree.parse(self.file).getroot()
        for child in root:
            if child.tag == 'programme':
                programmes.append(self._parse_programme(child))
            elif child.tag == 'channel':
                channels.append(self._parse_channel(child))

        return TVProgramme(channels, programmes)

    def _parse_channel(self, element):
        data = self._parse_element(element)
        return dict(
            name=data['display-name']['text'][:Channel.name.max_length],
            channel=data['id'][:Channel.channel.max_length])

    def _parse_programme(self, element):
        data = self._parse_element(element)
        date = data['start']
        return dict(
            name=data['title']['text'][:Programme.name.max_length],
            date=date.date(),
            time=date.time(),
            timestart=int(date.timestamp()),
            timestop=int(data['stop'].timestamp()),
            channel=data['channel'][:Programme.channel.max_length])

    def _parse_element(self, element):
        data = {}
        data['tag'] = element.tag
        attrib = element.attrib.copy()
        if 'start' in attrib:
            attrib['start'] = self._parse_datetime(attrib['start'])
        if 'stop' in attrib:
            attrib['stop'] = self._parse_datetime(attrib['stop'])

        for atr_name, atr_val in attrib.items():
            data[atr_name] = atr_val

        for child in element:
            data[child.tag] = {
                'text': child.text,
                'attrib': child.attrib
            }

        return data

    def _parse_datetime(self, value):
        return datetime.strptime(value, '%Y%m%d%H%M%S %z')


def create_args_parser():
    def check_days_value(arg):
        try:
            value = int(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(
                'invalid int value: "{0}"'.format(arg))

        if value < 1:
            message = 'Expected > 0, got value = {}'.format(value)
            raise argparse.ArgumentTypeError(message)

        return value

    parser = argparse.ArgumentParser(
        description='TV program manager for baat',
        epilog='(c) yakimka 2018. Version {0}'.format(VERSION))
    parser.add_argument('--create-tables',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Create tables in database')
    parser.add_argument('--truncate-tables',
                        nargs='+',
                        choices=TABLES_ALLOWED_TO_TRUNCATE,
                        metavar='TABLES',
                        help='Truncate tables')
    parser.add_argument('--delete-older',
                        type=check_days_value,
                        metavar='N',
                        help='Delete records older then N days')
    parser.add_argument('-f', '--file',
                        type=argparse.FileType(),
                        metavar='FILE',
                        help='Import TV program from file')
    parser.add_argument('-V', '--version',
                        action='version',
                        help='Show version',
                        version=VERSION)

    return parser


def create_tables():
    Channel.create_table()
    Programme.create_table()


RecordsCount = namedtuple('RecordsCount', 'channels programmes')


def import_(file):
    channels, programmes = TVProgrammeParser(file).parse()
    Channel.replace_many(channels).execute()
    Programme.replace_many(programmes).execute()
    return RecordsCount(len(channels), len(programmes))


def truncate_tables(tables):
    for table in list(tables):
        model = _REGISTERED_MODELS.get(table)
        if model is not None:
            model.delete().execute()


def delete_old(days):
    date_ = date.today() - timedelta(days=days)
    return Programme.delete().where(Programme.date <= date_).execute()


if __name__ == '__main__':
    parser = create_args_parser()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    namespace = parser.parse_args(sys.argv[1:])
    try:
        if namespace.create_tables:
            create_tables()
        if namespace.truncate_tables:
            truncate_tables(namespace.truncate_tables)
            print('Successfully truncated {0} table(s)'.format(
                len(namespace.truncate_tables)))
        if namespace.file:
            import_(namespace.file)
            print('Import finished normally')
        if namespace.delete_older:
            del_cnt = delete_old(namespace.delete_older)
            print('Successfully deleted', del_cnt, 'records')
    except (peewee.OperationalError, peewee.InterfaceError) as e:
        print(str(e), 'Check your database credentials',
              file=sys.stderr,
              sep='\n')
        sys.exit(1)
