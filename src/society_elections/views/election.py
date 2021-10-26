from django.http import HttpRequest
from django.shortcuts import render
from django.utils import timezone

from .helpers import get_latest_election, get_template


def index_view(req: HttpRequest):
    # Get latest election
    election = get_latest_election()    
    now = timezone.now()
    if election.nominations_start <= now and election.nominations_end > now:
        election_period = 'nominations'
    elif election.voting_start <= now and election.voting_end > now:
        election_period = 'voting'
    elif election.nominations_end <= now and election.voting_start > now:
        election_period = 'interim'
    elif election.nominations_start > now:
        election_period = 'pre-nomination'
    elif not election.results_submitted:
        election_period = 'post-voting'
    else:
        election_period = 'end'

    return render(req, get_template('election_detail'), {
        'election': election,
        'election_period': election_period
    })
