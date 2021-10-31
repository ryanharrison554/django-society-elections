from django.http import HttpRequest
from django.shortcuts import render

from .helpers import get_latest_election, get_template


def index_view(req: HttpRequest):
    # Get latest election
    election = get_latest_election()    

    return render(req, get_template('election_detail'), {
        'election': election,
        'election_period': election.current_period
    })
