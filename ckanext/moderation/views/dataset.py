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


def read(package_type, id):
    context = {
        u'model': model,
        u'session': model.Session,
        u'user': g.user,
        u'for_view': True,
        u'auth_user_obj': g.userobj
    }
    data_dict = {u'id': id, u'include_tracking': True}
    activity_id = request.params.get(u'activity_id')

    # check if package exists
    try:
        pkg_dict = get_action(u'package_show')(context, data_dict)
        pkg = context[u'package']
    except (NotFound, NotAuthorized):
        return jsonify(
            {'success': False,
             'message': 'Dataset: {id} not found'.format(id=id)}), 404

    g.pkg_dict = pkg_dict
    g.pkg = pkg
    # NB templates should not use g.pkg, because it takes no account of
    # activity_id

    if activity_id:
        # view an 'old' version of the package, as recorded in the
        # activity stream
        try:
            activity = get_action(u'activity_show')(
                context, {u'id': activity_id, u'include_data': True})
        except NotFound:
            return jsonify(
                {'success': False,
                 'message': 'Activity not found'}), 404
        except NotAuthorized:
            return jsonify(
                {'success': False,
                 'message': 'Not Authorized'}), 403
        current_pkg = pkg_dict
        try:
            pkg_dict = activity[u'data'][u'package']
        except KeyError:
            return jsonify(
                {'success': False,
                 'message': 'Dataset: {id} not found'.format(id=id)}), 404
        if u'id' not in pkg_dict or u'resources' not in pkg_dict:
            return jsonify(
                {'success': False,
                 'message': 'Detail for given dataset activity not found'}), 404
        if pkg_dict[u'id'] != current_pkg[u'id']:

            # the activity is not for the package in the URL - don't allow
            # misleading URLs as could be malicious
            return jsonify(
                {'success': False,
                 'message': 'Activity not found'}), 404
        # The name is used lots in the template for links, so fix it to be
        # the current one. It's not displayed to the user anyway.
        pkg_dict[u'name'] = current_pkg[u'name']

        # Earlier versions of CKAN only stored the package table in the
        # activity, so add a placeholder for resources, or the template
        # will crash.
        pkg_dict.setdefault(u'resources', [])

    composite_repeating = ['links', 'publisher_contacts', 'region']
    for key in composite_repeating:
        if pkg_dict[key]:
            try:
                pkg_dict[key] = json.loads(pkg_dict[key])
            except:
                print('Not able to load')
    pkg_dict['source'] = pkg_dict['source'].split(",")
    return jsonify(pkg_dict), 200


class StatusAPIView(MethodView):

    def post(self, package_type):
        allowed_var = ['under-review', 'resubmission-required', 'rejected', 'active']
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': g.user,
            u'auth_user_obj': g.userobj,
            u'save': True
        }
        data_dict = request.get_json()
        if g.userobj.sysadmin and data_dict['state'] in allowed_var:
            # TODO: Pylons object get JSON
            try:
                pkg_dict = get_action(u'package_update')(
                    context, {'name': data_dict['name'], 'state': data_dict['state']}
                )
                return jsonify({'status': 'Successfully Updated'}), 200
            except:
                return jsonify({'status': 'Not found'}), 200
        else:
            return jsonify({'status': 'Not Authorized'}), 400


class CreateAPIView(MethodView):

    def post(self, package_type):
        # The staged add dataset used the new functionality when the dataset is
        # partially created so we need to know if we actually are updating or
        # this is a real new.
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
        try:
            data_dict = clean_dict(
                dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
            )
            # TODO: Check special character regex
            data_dict['name'] = data_dict['title'].lower().replace("  ", " ").replace(" ", "-")
            # TODO: Do give id in return
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

                return jsonify(
                    {'success': True,
                     'message': 'Dataset successfully updated',
                     'pkg_name': pkg_dict[u'name']}), 200
            # TODO: Should check by basestring
            if u'dataset_state' in data_dict and data_dict[u'dataset_state'] == 'active':
                data_dict[u'state'] = u'pending-review'
                if g.userobj.sysadmin:
                    data_dict[u'state'] = u'active'
            else:
                data_dict[u'state'] = u'draft'
            context[u'allow_state_change'] = True

            data_dict[u'type'] = package_type
            context[u'message'] = data_dict.get(u'log_message', u'')
            pkg_dict = get_action(u'package_create')(context, data_dict)

            mod_status = "SUBMITTED"
            if g.userobj.sysadmin:
                mod_status = "APPROVED"

            moderation = get_action('moderation_create')(context, {'package_id': pkg_dict[u'id'], 'status': mod_status})


            return jsonify({'success': True,
                            'message': 'Dataset successfully created',
                            'pkg_name': pkg_dict[u'name']}), 201
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
                            'error': {'message': 'Validation Error',
                                      'fields': e.error_dict}}), 400
