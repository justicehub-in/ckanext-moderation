from flask import Blueprint
from ckanext.moderation.views.resource import CreateAPIView as ResourceCreateAPIView
from ckanext.moderation.views.dataset import CreateAPIView as DatasetCreateAPIView, StatusAPIView
from ckanext.moderation.views.dataset import read

dataset = Blueprint(
    u'dataset_api',
    __name__,
    url_prefix=u'/api/dataset',
    url_defaults={u'package_type': u'dataset'}
)

dataset.add_url_rule(u'/new', view_func=DatasetCreateAPIView.as_view(str(u'dataset_new')))
dataset.add_url_rule(u'/status', view_func=StatusAPIView.as_view(str(u'dataset_status')))
dataset.add_url_rule(u'/<id>', view_func=read)
dataset.add_url_rule(u'/<id>/resource/new', view_func=ResourceCreateAPIView.as_view(str(u'resource_new')))
