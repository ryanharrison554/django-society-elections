from django.conf import settings
from django.db import models


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
        editable=False,
        related_name='elections_created',
        related_query_name='election_created'
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
        editable=False,
        related_name='elections_finished',
        related_query_name='election_finished'
    )
    results_submitted_at = models.DateTimeField(
        blank=True,
        null=True,
        editable=False
    )

    def __str__(self):
        return self.admin_title

    class Meta:
        app_label = 'society_elections'
        ordering = ['-nominations_start', 'admin_title']
        get_latest_by = ['nominations_start']
