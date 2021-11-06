"""Mocks a URL conf in a project with this app installed. 

Allows us to run tests with our URLs under the "society_elections" namespace
"""
from django.urls import include, path

urlpatterns = [
    path('', include('society_elections.urls'))
]
