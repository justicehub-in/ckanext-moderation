import hashlib
import json
import ckan.logic as logic
import ckanext.moderation.moderation_model as moderation_model

_check_access = logic.check_access


def moderation_create(context, data):
    package_id = data['package_id']
    status = data['status']
    user_id = data['user_id'] if 'user_id' in data else None
    # _check_access('user_create', context, None)
    model = context['model']
    mod_obj = moderation_model.ModerationModel(package_id, status, user_id)
    model.Session.add(mod_obj)
    model.Session.commit()
    return mod_obj.as_dict()


def error_message(error_summary):
    return json.dumps({'success': False, 'error': {'message': error_summary}})

