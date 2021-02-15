from flask import Blueprint
from ckanext.moderation.views.resource import CreateAPIView as ResourceCreateAPIView
from ckanext.moderation.views.dataset import CreateAPIView as DatasetCreateAPIView, StatusAPIView, DatasetUpdateAPIView
from ckanext.moderation.views.dataset import read

dataset = Blueprint(
    u'dataset_api',
    __name__,
    url_defaults={u'package_type': u'dataset'}
)

dataset.add_url_rule(u'/api/dataset/new', view_func=DatasetCreateAPIView.as_view(str(u'dataset_new')))
dataset.add_url_rule(u'/api/dataset/status', view_func=StatusAPIView.as_view(str(u'dataset_status')))
dataset.add_url_rule(u'/api/dataset/<id>', view_func=read)
dataset.add_url_rule(u'/api/dataset/<id>/resource/new', view_func=ResourceCreateAPIView.as_view(str(u'resource_new')))
dataset.add_url_rule(u'/dataset/<id>/edit', view_func=DatasetUpdateAPIView.as_view(str(u'dataset_update')))
