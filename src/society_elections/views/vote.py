import logging

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.http.response import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.utils import timezone
from ipware import get_client_ip

from ..models import AnonymousVoter, ElectionPosition, RegisteredVoter, Vote, Candidate
from .helpers import (get_latest_election, get_template,
                      is_request_authenticated)

logger = logging.getLogger(__name__)


def vote_view(req: HttpRequest) -> HttpResponse:
    """View to vote in an election

    The latest election is fetched. Voters are then verified, with 
    non-anonymized elections using UUID and anonymized elections using a 
    password.

    Once voters are verified, we present them with the vote page if they are 
    not submitting the votes, otherwise we verify they have submitted a vote 
    for all positions.

    Args:
        req (HttpRequest): Request sent by voter

    Returns:
        HttpResponse: Reponse sent to voter
    """
    election = get_latest_election()
    uuid = req.POST.get('uuid', req.GET.get('uuid'))
    password = req.POST.get('password')
    ip, _ = get_client_ip(req)
    try:
        authenticated = is_request_authenticated(election, req)
    except Http404:
        logger.info(f'Voter 404 not found: {uuid} "{election}" ({ip})')
        return render(req, get_template('voter_404'), {
            'uuid': uuid
        }, status=401)

    if not election.anonymous:
        voter = RegisteredVoter.objects.get(election=election, pk=uuid)
        if not authenticated:
            logger.warning(
                f'Voter 401 not authorized: {voter.email} "{election}" ({ip})'
            )
            return render(req, get_template('voter_not_verified'), {
                'voter': voter
            }, status=401)
    elif not authenticated: # and election.anonymous
        logger.warning(
            f'Voter 401 not registered: anonymous "{election}" ({ip})'
        )
        messages.add_message(req, messages.ERROR,
            'The password used was either incorrect, or your email has not '
            'yet been verified.'
        )
        return render(req, get_template('password_entry'), status=401)
    else:
        voter = None
        anon_voter = AnonymousVoter.objects.get(
            election=election, password=AnonymousVoter.hash_password(password)
        )

    # Voter verified
    context = {
        'election': election,
        'voter': voter,
        'password': password
    }

    # Voter has been verified, we can now check if we need to submit votes or 
    # just return voting page
    if req.method != 'POST' or req.POST.get('submit') is None:
        return render(req, get_template('vote'), context)
    
    # Method is POST and submit is present
    if election.anonymous:
        votes = Vote.objects.filter(anonymous_voter=anon_voter)
    else:
        votes = Vote.objects.filter(registered_voter=voter)

    positions = ElectionPosition.objects.filter(election=election)
    position_votes = {}
    voting_complete = True
    position: ElectionPosition
    for position in positions:
        position_votes[position] = votes.filter(position=position)
        if not position_votes[position].exists():
            messages.add_message(req, messages.WARNING, 
                'You have not yet submitted a vote for '
                f'{position.position.title}'
            )
            voting_complete = False
        
    if not voting_complete:
        if voter is None:
            voter = anon_voter
        logger.debug(
            f'Voting not finished: {voter} "{election}" ({ip})'
        )
        return render(req, get_template('vote'), context)
    else:
        if voter is None:
            voter = anon_voter
        logger.info(f'Votes submitted: {voter} "{election}" ({ip})')
        return redirect(reverse('vote_submitted'))


class VoteSubmittedView(TemplateView):
    """Called when votes have been submitted successfully"""

    def get_template_names(self):
        return [get_template('vote_submitted'),]


@require_POST
def create_vote_ajax(req: HttpRequest) -> JsonResponse:
    """Create a new vote

    Creates a new vote for a given candidate in a given election. Validates 
    that the candidate is eligible to vote before validating that they are not 
    submitting a duplicate vote

    Args:
        req (HttpRequest): Request object

    Returns:
        JsonResponse: Repsonse to user indicating success and vote PK or 
            failure and error reason
    """
    election = get_latest_election()
    uuid = req.POST.get('uuid')
    password = req.POST.get('password')
    ip, _ = get_client_ip(req)
    candidate_pk = req.POST.get('candidate')
    position_pk = req.POST.get('position')
    ron = req.POST.get('ron') is not None
    abstain = req.POST.get('abstain') is not None
    try:
        authenticated = is_request_authenticated(election, req)
    except Http404:
        logger.info(f'Voter 404 not found: {uuid} "{election}" ({ip})')
        authenticated = False
    
    if not authenticated:
        logger.info(f'Voter not authorized: - "{election}" ({ip})')
        return JsonResponse({
            'error': 'Not authorized to Vote'
        }, status=401)

    try:
        position: ElectionPosition = get_object_or_404(
            ElectionPosition, election=election, pk=int(position_pk)
        )
    except (Http404, ValueError):
        return JsonResponse({
            'error': 'Position does not exist',
        }, status=404)

    # Check for bad request
    if (not position.allow_ron) and ron:
        return JsonResponse({
            'error': 'Cannot vote RON for this position'
        }, status=400)
    elif (not position.allow_abstain) and abstain:
        return JsonResponse({
            'error': 'Cannot abstain from voting for this position'
        }, status=400)
    elif (
        (ron and abstain) or
        (candidate_pk is not None and ron) or
        (candidate_pk is not None and abstain)
    ):
        return JsonResponse({
            'error': 'Can only vote for one of a candidate, RON or abstain'
        }, status=400)

    # Check candidate exists
    if abstain or ron:
        candidate = None
    else:
        try:
            candidate = get_object_or_404(
                Candidate, position__election=election, pk=int(candidate_pk)
            )
        except (Http404, ValueError):
            return JsonResponse({
                'error': 'Candidate does not exist'
            }, status=404)
    
    # Find clashing votes - change vote if positions available is only 1
    if election.anonymous:
        anon_voter = AnonymousVoter.objects.get(
            election=election, password=AnonymousVoter.hash_password(password)
        )
        reg_voter = None
        voter = anon_voter
    else:
        reg_voter = RegisteredVoter.objects.get(
            election=election, pk=uuid
        )
        anon_voter = None
        voter = reg_voter

    # Change existing vote if only one position available
    if position.positions_available == 1:
        try:
            existing_vote = get_object_or_404(
                Vote, registered_voter=reg_voter, 
                anonymous_voter=anon_voter,
                position=position
            )
        except Http404:
            logger.debug(f'Could not find existing vote for {position}')
        else:
            existing_vote.candidate = candidate
            existing_vote.abstain = abstain
            existing_vote.ron = ron
            existing_vote.vote_last_modified_at = timezone.now()
            logger.info(f'Vote updated: {voter} "{existing_vote}" ({ip})')
            existing_vote.save()
            return JsonResponse({
                'vote': str(existing_vote.pk)
            })
    else:
        existing_votes = Vote.objects.filter(
            position=position, 
            anonymous_voter=anon_voter,
            registered_voter=reg_voter
        )
        existing_votes_for_candidate = existing_votes.filter(
            candidate=candidate,
            abstain=abstain,
            ron=ron
        )
        if (
            existing_votes.count() >= position.positions_available or 
            existing_votes_for_candidate.exists()
        ):
            logger.warning(f'Excessive Voting: {voter} "{election}" ({ip})')
            return JsonResponse({
                'error': 'Already submitted votes for this position or '
                         'candidate'
            }, status=409) # 409 = Conflict
    
    # Can submit vote - no existing vote, or enough spaces left to vote
    new_vote = Vote(
        registered_voter=reg_voter,
        anonymous_voter=anon_voter,
        candidate=candidate,
        position=candidate.position,
        abstain=abstain,
        ron=ron
    )
    new_vote.save()
    logger.info(f'Vote created: {voter} "{new_vote}" ({ip})')
    return JsonResponse({
        'vote': str(new_vote.pk)
    })


@require_POST
def delete_vote_ajax(req: HttpRequest) -> JsonResponse:
    """Deletes a given vote from the database
    
    Args:
        req (HttpRequest): Request sent
    
    Returns:
        JsonResponse: Response indicating success or failure
    """
    election = get_latest_election()
    uuid = req.POST.get('uuid')
    password = req.POST.get('password')
    ip, _ = get_client_ip(req)
    vote_pk = req.POST.get('vote')

    try:
        authenticated = is_request_authenticated(election, req)
    except Http404:
        logger.info(f'Voter 404 not found: {uuid} "{election}" ({ip})')
        authenticated = False
    
    if not authenticated:
        logger.info(f'Voter not authorized: - "{election}" ({ip})')
        return JsonResponse({}, status=401)

    if election.anonymous:
        anon_voter = AnonymousVoter.objects.get(
            election=election, password=AnonymousVoter.hash_password(password)
        )
        reg_voter = None
        voter = anon_voter
    else:
        reg_voter = RegisteredVoter.objects.get(election=election, pk=uuid)
        anon_voter = None
        voter = reg_voter
    
    try:
        # This also checks we can delete a vote
        vote = get_object_or_404(
            Vote,
            registered_voter=reg_voter,
            anonymous_voter=anon_voter,
            pk=int(vote_pk)
        )
    except (Http404, ValueError):
        logger.warning(f'Voter cannot delete vote: {voter} "{vote_pk}" ({ip})')
        return JsonResponse({}, status=401)
    
    vote.delete()
    return JsonResponse({})
