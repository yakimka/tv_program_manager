#!/usr/bin/env python3

import argparse
import sys
from datetime import date, datetime, timedelta
from xml.etree import ElementTree

from peewee import (MySQLDatabase, Model, DateField, TimeField,
                    IntegerField, CharField)

VERSION = '0.1'

##############
### CONFIG ###
DB_NAME = 'tv_manager'
DB_USER = 'tv_manager'
DB_PASSWORD = 'password'
DB_HOST = '127.0.0.1'
DB_PORT = 3306

CHANNELS_TABLE_NAME = 'channels'
PROGRAMME_TABLE_NAME = 'pp'
### END OF CONFIG ###
#####################


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


class TVProgrammeParser:
    def parse(self, file):
        channels = []
        programmes = []
        root = ElementTree.parse(file).getroot()
        for child in root:
            if child.tag == 'programme':
                programmes.append(self._parse_programme(child))
            elif child.tag == 'channel':
                channels.append(self._parse_channel(child))

        return channels, programmes

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
            raise argparse.ArgumentTypeError('invalid int value: "{0}"'.format(arg))

        if value < 1:
            message = 'Expected > 0, got value = {}'.format(value)
            raise argparse.ArgumentTypeError(message)

        return value

    parser = argparse.ArgumentParser(
        description='TV program manager for baat',
        epilog='(c) yakimka 2018. Version {0}'.format(VERSION))
    parser.add_argument('--truncate-tables', nargs='+',
                        choices=TABLES_ALLOWED_TO_TRUNCATE,
                        metavar='TABLES', help='Truncate tables')
    parser.add_argument('--delete-older', type=check_days_value, metavar='N',
                        help='Delete records older then N days')
    parser.add_argument('-f', '--file', type=argparse.FileType(), metavar='FILE',
                        help='Import TV program from file')
    parser.add_argument('-V', '--version',
                        action='version',
                        help='Show version',
                        version=VERSION)

    return parser


def import_(file):
    channels, programmes = TVProgrammeParser().parse(file)
    Channel.replace_many(channels).execute()
    Programme.replace_many(programmes).execute()
    print('Import finished normally')


def truncate_tables(tables):
    for table in tables:
        model = _REGISTERED_MODELS.get(table)
        if model is not None:
            model.delete().execute()
            print('Successfully truncated "{0}" table'.format(table))


def delete_old(days):
    date_ = date.today() - timedelta(days=days)
    del_cnt = Programme.delete().where(Programme.date <= date_).execute()
    print('Successfully deleted', del_cnt, 'records')


if __name__ == '__main__':
    parser = create_args_parser()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    namespace = parser.parse_args(sys.argv[1:])
    if namespace.truncate_tables:
        truncate_tables(namespace.truncate_tables)
    if namespace.file:
        import_(namespace.file)
    if namespace.delete_older:
        delete_old(namespace.delete_older)
