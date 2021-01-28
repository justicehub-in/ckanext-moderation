from ckanext.moderation import blueprint
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckanext.moderation.logic.validators as validators
import ckanext.moderation.moderation_model as moderation_model

import ckanext.moderation.actions.create as create

class ModerationPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IValidators)

    def get_validators(self):
        return {
            u'starts_with_b': validators.starts_with_b,
            u'scheming_multiple_choice_with_other': validators.scheming_multiple_choice_with_other
        }

    def update_config(self, config):
        tk.add_template_directory(config, 'templates')

    def get_helpers(self):
        return {}

    def is_fallback(self):
        return False

    def get_actions(self):
        return {
            'moderation_create': create.moderation_create
        }

    def configure(self, config):
        moderation_model.setup()

    def get_blueprint(self):
        return blueprint.dataset
