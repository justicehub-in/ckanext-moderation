import logging
import ckanext.moderation.moderation_model as moderation_model
import click


log = logging.getLogger(__name__)


@click.group()
def moderation_table():
    """
    Perform commands to set up user_extra table
    """


@moderation_table.command(
    u'initdb',
    short_help=u'Initialize user_validation table'
)
def initdb():
    moderation_model.create_table()
    print("Successfully Created")


@moderation_table.command(
    u'cleandb',
    short_help=u'Delete user_extra table'
)
def cleandb():
    moderation_model.delete_table()
    print("Successfully Deleted")


@moderation_table.command(
    u'dropdb',
    short_help=u'Drop user_extra table'
)

def dropdb():
    moderation_model.drop_table()
    print("Successfully Dropped")
