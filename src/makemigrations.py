#! /usr/bin/env python
import os

import django
from django.conf import settings
from django.core.management import call_command

if __name__ == '__main__':
    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'society_elections')
    )
    settings.configure(
        BASE_DIR=BASE_DIR,
        DEBUG=True,
        DATABASES={
            'default':{
                'ENGINE':'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        },
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'society_elections',
        ),
        TIME_ZONE='UTC',
        USE_TZ=True,
    )
    django.setup()
    
    call_command('makemigrations', 'society_elections')