from ckanext.moderation import blueprint
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class ModerationPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')

    def get_helpers(self):
        return {}

    def is_fallback(self):
        return False

    def get_blueprint(self):
        return blueprint.dataset
