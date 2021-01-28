from __future__ import print_function

import ckan.plugins as p
import ckanext.moderation.moderation_model as moderation_model


class ModerationCommand(p.toolkit.CkanCommand):
    """
    Usage:
        paster user_extra [initdb]
        Creates the table in db
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(ModerationCommand, self).__init__(name)

    def command(self):
        if not self.args or self.args[0] in ['-h', '--help', 'help'] or not len(self.args) in [1, 2]:
            print (self.usage)
            return

        cmd = self.args[0]
        self._load_config(load_site_user=False)
        if cmd == 'initdb':
            print ('Initializing Database...')
            self.initdb()
            print ('DONE Initializing Database...')
        elif cmd == 'cleandb':
            print ('Cleandb Database...')
            self.cleandb()
        else:
            print ('Error: command "{0}" not recognized'.format(cmd))
            print (self.usage)

    def initdb(self):
        """
        Create the table defined by model
        """
        moderation_model.create_table()

    def cleandb(self):
        """
        Delete information from table defined by model
        """
        moderation_model.delete_table()

    def dropdb(self):
        """
        Drop table defined by model
        """
        moderation_model.drop_table()
