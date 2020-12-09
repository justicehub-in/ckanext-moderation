import json
from flask.views import MethodView
from flask import request, jsonify
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.model as model
from ckan.common import _, g, request
import ckan.logic as logic
from ckanext.moderation.lib.utils import tag_string_to_list
from ckan.lib.search import SearchIndexError
from six import text_type


NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key
ValidationError = logic.ValidationError


class CreateAPIView(MethodView):

    def _prepare(self, data=None):

        context = {
            u'model': model,
            u'session': model.Session,
            u'user': g.user,
            u'auth_user_obj': g.userobj,
            u'save': True
        }
        try:
            check_access(u'package_create', context)
        except NotAuthorized:
            return jsonify({'success': False, 'error': {'message': 'Not Authorized'}}), 401
        return context

    def post(self, package_type):
        # The staged add dataset used the new functionality when the dataset is
        # partially created so we need to know if we actually are updating or
        # this is a real new.
        context = self._prepare()
        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
            )
        except dict_fns.DataError:
            return jsonify({'success': False, 'error': {'message': _(u'Integrity Error')}}), 400
        try:
            context[u'allow_partial_update'] = True
            if u'tag_string' in data_dict:
                data_dict[u'tags'] = tag_string_to_list(
                    data_dict[u'tag_string']
                )
            if data_dict.get(u'pkg_name'):
                # This is actually an update not a save
                data_dict[u'id'] = data_dict[u'pkg_name']
                del data_dict[u'pkg_name']
                # don't change the dataset state
                data_dict[u'state'] = u'draft'
                # this is actually an edit not a save
                pkg_dict = get_action(u'package_update')(
                    context, data_dict
                )

                return json.dumps(
                    {'success': True,
                     'message': 'Dataset: {id} is successfully updated'.format(id=pkg_dict[u'name'])}), 200
            data_dict[u'state'] = u'draft'
            context[u'allow_state_change'] = True

            data_dict[u'type'] = package_type
            context[u'message'] = data_dict.get(u'log_message', u'')
            pkg_dict = get_action(u'package_create')(context, data_dict)

            return jsonify({'success': True,
                            'message': 'Dataset: {id} is successfully created'.format(id=pkg_dict[u'name'])}), 201
        except NotAuthorized:
            return jsonify({'success': False,
                            'error': {'message': 'Not Authorized'}}), 401
        except NotFound as e:
            return jsonify({'success': False,
                            'error': {'message': 'Dataset not found'}}), 404
        except SearchIndexError as e:
            try:
                exc_str = text_type(repr(e.args))
            except Exception:  # We don't like bare excepts
                exc_str = text_type(str(e))
            return jsonify({'success': False,
                            'error': {'message': _(u'Unable to add package to search index.') + exc_str}
                            }), 500
        except ValidationError as e:
            return jsonify({'success': False,
                            'error': {'message': 'Validation Error'}}), 400
