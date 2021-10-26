"""Defines the settings for this package"""
from django.conf import settings

ROOT_URL = getattr(
    settings, 'SOCIETY_ELECTIONS_ROOT_URL', 'http://localhost:8000'
)