import uuid

from django.conf import settings
from django.db import models

from .apps import SocietyElectionsConfig


# Create your models here.
class Election(models.Model):
    f"""A first-past-the-post election
    
    An election is an event in two parts: nominations and voting. Nominations 
    run from a given time UTC to a given time UTC. During this time candidates 
    can nominate themselves for a given election position. Voting takes place 
    from a given time UTC (which must be after the end of nominations), to a 
    given time UTC. During this time, voters vote for candidates for positions.

    Voters will have a minimum and maximum number of votes that they can cast 
    for any given position, with the maximum number of votes generally 
    indicating how many positions are available for that given position.

    Attributes:
        title (str): Title of the election, displayed as the title of the pages
        admin_title (str): Title displayed only in the admin page, which 
            provides differentiation between annual elections
        description (str): Why the election is taking place
        created_by ({settings.AUTH_USER_MODEL}): Who created the election
        created_at (datetime): When the election was created
        nominations_start (datetime): When the nominations start
        nominations_end (datetime): When the nominations end
        voting_start (datetime): When the voting period starts
        voting_end (datetime): When the voting period ends,
        voter_email_domain_whitelist (str): An optional, newline delimited 
            whitelist of which email domains to allow voting from
        candidate_email_domain_whitelist (str): An optional, newline delimited 
            whitelist of which email domains to allow nominations from
        email_winners (bool): Whether or not to email the winners of an election
        email_losers (bool): Whether or not to email the losers of an election
        winner_message (str): The message to send successful candidates
        loser_message (str): The message to send unsuccessful candidates
        results_submitted (bool): Whether or not the results have been finalised
        results_submitted_by ({settings.AUTH_USER_MODEL}): Who finalised the 
            results
        results_submitted_at (datetime): When were the results finalised
        positions (object): one-to-many relation to ElectionPosition
    """
    title = models.CharField(
        max_length=100
    )
    admin_title = models.CharField(
        max_length=500,
        help_text='Title displayed only in the admin pages, which provides '
        'differentiation between e.g. annual elections'
    )
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        editable=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    nominations_start = models.DateTimeField(
        verbose_name='nominations start time'
    )
    nominations_end = models.DateTimeField(
        verbose_name='nominations end time'
    )
    voting_start = models.DateTimeField(
        verbose_name='voting period start time'
    )
    voting_end = models.DateTimeField(
        verbose_name='voting period end time'
    )
    voter_email_domain_whitelist = models.TextField(
        help_text='Newline-delimited list of email domains to accept when '
        'voters sign up to vote in the election',
        blank=True,
        null=True
    )
    candidate_email_domain_whitelist = models.TextField(
        help_text='Newline-delimited list of email domains to accept when '
        'candidates nominate themselves in the election'
    )
    email_winners = models.BooleanField(
        default=False
    )
    email_losers = models.BooleanField(
        default=False
    )
    verify_candidate_emails = models.BooleanField(
        default=False
    )
    winner_message = models.TextField(
        help_text='The message to send to successful candidates in an election.'
        ' Format the message by using {name} for the candidate name, {position}'
        ' for the title of the position, and {votes} for the number of votes '
        'they received',
        blank=True,
        null=True
    )
    loser_message = models.TextField(
        help_text='The message to send to unsuccessful candidates in an '
        'election. Format the message by using {name} for the candidate name, '
        '{position} for the title of the position, and {votes} for the number '
        'of votes they received',
        blank=True,
        null=True
    )
    candidate_verification_email = models.TextField(
        help_text='The message to send to candidates to verify their email in '
        'an election. Format the message by using {name} for the candidate '
        'name, {position} for the title of the position, and {verify_url} for '
        'the link to verify their email',
        blank=True,
        null=True
    )
    results_submitted = models.BooleanField(
        default=False,
        editable=False
    )
    results_submitted_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        editable=False
    )
    results_submitted_at = models.DateTimeField(
        blank=True,
        null=True,
        editable=False
    )

    def __str__(self):
        return self.admin_title


class Position(models.Model):
    """Reusable position that can be used in multiple elections
    
    The definition of a position simply defines a single position that can be 
    used in multiple elections, e.g. Chair. The Chair position can be included 
    in many elections

    Attributes:
        title (str): The title of the position, e.g. Chair, Treasurer
        admin_title (str): A verbose title, for if there are similar positions 
            which have the same name, but are mutually exclusive in their 
            jurisdiction. Use this if running elections for 2 different 
            societies. Only displayed on the admin pages.
        description (str): What the position entails, a job description
    """
    title = models.CharField(
        max_length=100
    )
    admin_title = models.CharField(
        max_length=500,
        help_text='Long title to give to position in admin pages to '
        'differentiate between similar roles that are mutually exclusive in '
        'their purpose, e.g. Chair for two different societies'
    )
    description = models.TextField()

    def __str__(self):
        return self.admin_title


class ElectionPosition(models.Model):
    """Specifies a position to allow candidates to run for in a given election

    Essentially implements a many-to-many relation, with some additional fields

    Attributes:
        position (Position): The position to include
        election (Election): Election the position is to be included in
        candidate_required (bool): Whether or not this position requires a 
            candidate in order for a successful election to take place
        allow_ron (bool): Allow voters to vote to "Re-open Nominations" when 
            voting for this position
        allow_abstain (bool): Allow votes to abstain from voting for a 
            candidate for this position
        positions_available (int): How many nominees can be successful in 
            applying for this position 
    """
    position = models.ForeignKey(
        to=f'{SocietyElectionsConfig.name}.Position',
        on_delete=models.CASCADE
    )
    election = models.ForeignKey(
        to=f'{SocietyElectionsConfig.name}.Election',
        on_delete=models.CASCADE,
        related_name='positions',
        related_query_name='position'
    )
    candidate_required = models.BooleanField(
        default=True,
        help_text='Whether or not at least one candidate is required in order '
        'to run this election'
    )
    allow_ron = models.BooleanField(
        default=True,
        help_text='Whether or not to include "Re-open Nominations" in the list '
        'of options for voters'
    )
    allow_abstain = models.BooleanField(
        default=True,
        help_text='Whether or not to allow voters to abstain from voting for '
        'this position'
    )
    positions_available = models.PositiveIntegerField(
        default=1,
        help_text='Number of available positions for this role'
    )

    def __str__(self):
        return f'{self.position.title} in {self.election.admin_title}'


class Candidate(models.Model):
    f"""Nominee for a given election position
    
    Attributes:
        position ({ElectionPosition.__name__}): The 
            {ElectionPosition.__name__} that the candidate is running for
        full_name (str): Name of the candidate
        email (str): Email address of the candidate, used to email them the 
            details of the election and whether or not they have won
        successful (bool): Whether or not the candidate was successful in their 
            nomination. Added so that results can be overridden in the case 
            where a candidate can only hold one position but won two
        nominated_at (datetime): When the candidate was nominated
    """
    position = models.ForeignKey(
        to=f'{SocietyElectionsConfig.name}.{ElectionPosition.__name__}',
        on_delete=models.CASCADE,
        related_name='candidates',
        related_query_name='candidate'
    )
    full_name = models.CharField(
        max_length=128
    )
    email = models.EmailField()
    successful = models.BooleanField(
        default=False,
        editable=False
    )
    nominated_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    def __str__(self):
        return f'{self.full_name} for {self.position.position}'


class Voter(models.Model):
    f"""Represents a voter in the database

    Data is anonymized as much as possible here, by creating a hash with a salt 
    of the email address that is used to signup. This prevents double voting 
    from occuring
    
    Attributes:
        id (UUID): Unique identifier for a voter in the database. A UUID is 
            used to prevent guessable voter IDs
        election ({Election.__name__}): The election the voter is signed up to
            vote in
        email_salt (bytes): Salt used when hashing a voter's email
        email_hash (bytes): The hash of the email combined with the salt
        verified (bool): Has the voter verified their email address
        registered_at (datetime): The time the voter registered
        verified_at (datetime): When the voter verified their email
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    election = models.ForeignKey(
        to=f'{SocietyElectionsConfig}.{Election.__name__}',
        on_delete=models.CASCADE,
        related_name='voters',
        related_query_name='voter'
    )
    email_salt = models.BinaryField()
    email_hash = models.BinaryField()
    verified = models.BooleanField(
        default=False,
        editable=False
    )
    registered_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        editable=False
    )

    def __str__(self):
        return str(self.id)


class Vote(models.Model):
    f"""Represents a vote from a voter for a particular election candidate (or 
    RON/Abstain

    Attributes:
        voter ({Voter.__name__}): Voter in the election
        candidate ({Candidate.__name__}): Candidate in the election
        position ({ElectionPosition.__name__}): The position being voted for
        ron (bool): Whether or not the voter voted to re-open nominations
        abstain (bool): Whether or not the voter voter to abstain
        vote_cast_at (datetime): Time the vote was cast
        vote_last_modified_at (datetime): Time the vote was last modified, 
            useful to understand if someone has changed their vote
    """
    voter = models.ForeignKey(
        to=f'{SocietyElectionsConfig.name}.{Voter.__name__}',
        on_delete=models.CASCADE,
        editable=False
    )
    candidate = models.ForeignKey(
        to=f'{SocietyElectionsConfig.name}.{Candidate.__name__}',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='votes',
        related_query_name='vote'
    )
    position = models.ForeignKey(
        to=f'{SocietyElectionsConfig.name}.{ElectionPosition.__name__}',
        on_delete=models.CASCADE,
        related_name='votes',
        related_query_name='vote',
        editable=False
    )
    ron = models.BooleanField(
        default=False,
        help_text='Vote to re-open the nominations for this position',
        verbose_name='re-open nominations'
    )
    abstain = models.BooleanField(
        default=False,
        help_text='Vote not to submit a vote for any candidate for this '
        'position'
    )
    vote_cast_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    vote_last_modified_at = models.DateTimeField(
        auto_now=True,
        editable=False
    )

    def __str__(self):
        return f'{self.voter} voting {self.candidate}'
