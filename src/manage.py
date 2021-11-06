#! /usr/bin/env python
import os
import sys

import django
from django.conf import settings

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
            'django.contrib.messages',
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'society_elections',
        ),
        MIDDLEWARE=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware'
        ),
        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],
        TIME_ZONE='UTC',
        USE_TZ=True,
        ROOT_URLCONF='urls',
        ALLOWED_HOSTS=['localhost'],
        SECRET_KEY='insecure'
    )
    django.setup()
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)