from flask.views import MethodView
from flask import request, jsonify
import ckan.model as model
from ckan.common import _, g, request
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns


NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key
ValidationError = logic.ValidationError


class EditView(MethodView):

    def post(self, package_type, id, resource_id):
        context = {
            u'model': model,
            u'session': model.Session,
            u'api_version': 3,
            u'for_edit': True,
            u'user': g.user,
            u'auth_user_obj': g.userobj
        }
        try:
            check_access(u'package_update', context, {u'id': id})
        except NotAuthorized:
            return jsonify({'success': False, 'error': {'message': 'Not Authorized to perform this action'}}), 401
        data = clean_dict(
            dict_fns.unflatten(tuplize_dict(parse_params(request.form)))
        )
        data.update(clean_dict(
            dict_fns.unflatten(tuplize_dict(parse_params(request.files)))
        ))

        # we don't want to include save as it is part of the form
        if 'save' in data:
            del data[u'save']

        data[u'package_id'] = id
        try:
            if resource_id:
                data[u'id'] = resource_id
                get_action(u'resource_update')(context, data)
            else:
                get_action(u'resource_create')(context, data)
        except ValidationError as e:
            error_summary = e.error_summary
            return jsonify({'success': False, 'error': {'message': error_summary}}), 400
        except NotAuthorized:
            return jsonify({'success': False, 'error': {'message': 'Not Authorized to perform this action'}}), 401

        return jsonify({'success': 'Resource has been updated successfully'}), 201


class DeleteView(MethodView):

    def post(self, package_type, id, resource_id):

        context = {
            u'model': model,
            u'session': model.Session,
            u'user': g.user,
            u'auth_user_obj': g.userobj
        }

        try:
            check_access(u'package_delete', context, {u'id': id})
        except NotAuthorized:
            return jsonify({'success': False, 'error': {'message': 'Not Authorized to perform this action'}}), 401

        try:
            get_action(u'resource_delete')(context, {u'id': resource_id})
            return jsonify({'success': True, 'error': {'message': 'Resource deleted successfully'}}), 200
        except NotAuthorized:
            return jsonify({'success': False, 'error': {'message': 'Not Authorized to perform this action'}}), 401
        except NotFound:
            return jsonify({'success': False, 'error': {'message': 'Resource not found'}}), 404


class CreateAPIView(MethodView):
    def post(self, package_type, id):
        files = request.files.to_dict()
        if len(files) > 1:
            return jsonify(
                {'success': False, 'error': {'message': 'You are not allowed to add more than 1 files at a time'}}), 400
        elif len(files) == 0 or 'upload' not in files:
            return jsonify(
                {'success': False, 'error': {'message': 'Missing files'}}
            ), 400

        data = {
            'upload': files['upload'],
            'name': request.form.get('name'),
            'description': request.form.get('description')
        }
        resource_id = request.form.get("id")

        context = {
            u'model': model,
            u'session': model.Session,
            u'user': g.user,
            u'auth_user_obj': g.userobj
        }

        data[u'package_id'] = id
        try:
            if resource_id:
                data[u'id'] = resource_id
                get_action(u'resource_update')(context, data)
            else:
                get_action(u'resource_create')(context, data)
        except ValidationError as e:
            error_summary = e.error_summary
            return jsonify({'success': False, 'error': {'message': error_summary}}), 400
        except NotAuthorized:
            return jsonify({'success': False, 'error': {'message': 'Not Authorized to perform this action'}}), 401
        except NotFound:
            return jsonify(
                {'success': False, 'error': {'message': 'The dataset {id} could not be found.'.format(id=id)}}), 404
        except:
            return jsonify(
                {'success': False, 'error': {'message': 'Exception error encountered'}}
            ), 500
        # XXX race condition if another user edits/deletes
        data_dict = get_action(u'package_show')(context, {u'id': id})
        get_action(u'package_update')(
            dict(context, allow_state_change=True),
            dict(data_dict)
        )
        return jsonify({'success': 'Resource has been created successfully'}), 201
