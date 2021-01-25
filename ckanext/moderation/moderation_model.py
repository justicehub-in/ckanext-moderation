from __future__ import print_function

import sqlalchemy.orm as orm
import sqlalchemy.types as types
import logging
import ckan.model as model
from ckan.model.domain_object import DomainObject
from ckan.model import meta, extension
import ckan.model.types as _types

from sqlalchemy.schema import Table, Column, ForeignKey, Index

mapper = orm.mapper
log = logging.getLogger(__name__)

moderation_table = None


def setup():
    if moderation_table is None:
        define_moderation_table()
        log.debug('Moderation table defined in memory')

    create_table()


class ModerationModel(DomainObject):
    """
    Moderation Model information
    """

    def __init__(self, user_id, key, value):
        self.user_id = user_id
        self.key = key
        self.value = value

    @staticmethod
    def get(user_id, key):
        """

        :param user_id:
        :type user_id: str
        :param key:
        :type key: str
        :return:
        :rtype: UserExtra
        """
        query = meta.Session.query(ModerationModel)
        return query.filter_by(user_id=user_id, key=key).first()

    @staticmethod
    def get_by_user(user_id):
        """
        :param user_id:
        :type user_id: str
        :return:
        :rtype: list of UserExtra
        """
        query = meta.Session.query(ModerationModel).filter_by(user_id=user_id)
        result = query.all()
        return result

    @staticmethod
    def get_by_key( key):
        query = meta.Session.query(ModerationModel)
        return query.filter_by(key=key).all()

    @staticmethod
    def check_exists():
        return user_extra_table.exists()

    def as_dict(self):
        d = {k: v for k, v in vars(self).items() if not k.startswith('_')}
        return d


def define_moderation_table():
    global moderation_table
    moderation_table = Table('moderation', meta.metadata,
                             Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),
                             Column('user_id', types.UnicodeText, ForeignKey('user.id')),
                             Column('key', types.UnicodeText),
                             Column('value', types.UnicodeText),
                             )
    Index('user_id_key_idx', moderation_table.c.user_id, moderation_table.c.key, unique=True)
    mapper(ModerationModel, moderation_table, extension=[extension.PluginMapperExtension(), ])


# def _create_extra(key, value):
#    return ModerationModel(key=unicode(key), value=value)


def create_table():
    """
    Create user_extra table
    """
    if model.user_table.exists() and not moderation_table.exists():
        moderation_table.create()
        log.debug('Moderation table created')


def delete_table():
    """
    Delete information from user_extra table
    """
    print('Moderation trying to delete table...')
    if moderation_table.exists():
        print ('Moderation delete table...')
        moderation_table.delete()
        log.debug('Moderation table deleted')


def drop_table():
    """
    Drop user_extra table
    """
    print ('Moderation trying to drop table...')
    if moderation_table.exists():
        print ('Moderation drop table...')
        moderation_table.drop()
        log.debug('Moderation table dropped')
