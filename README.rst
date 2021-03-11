======================
ckanext-moderation
======================

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!

CKAN Moderation module for datasets

ckanext-moderation consist of:

1. Custom API endpoint for CRUD operation over datasets and resources
2. Overwrite default actions and introduce custom moderation features

------------
Requirements
------------

Supports Python 2.7, tested with CKAN 2.8.4

------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-moderation:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Clone repository and install the ckanext-moderation requirements first by::

      pip install -r requirements.txt

3. Install extension into your virtual environment::

     python setup.py install

3. Add ``moderation`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


------------------------
Development Installation
------------------------

To install ckanext-moderation for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/justicehub-in/ckanext-moderation.git
    cd ckanext-moderation
    python setup.py develop

------------------------
Future of this plugin?
------------------------

Right now major modifications have been made for justicehub.in website and it's hard to generalize it for normal usage.
Few challenges are:

1. Creating moderation logic and overwriting with existing one
2. Overwrite and create both actions and API which can be used as an API + by default CKAN
