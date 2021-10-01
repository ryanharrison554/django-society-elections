from django.db import models

from ..apps import SocietyElectionsConfig
from .candidate import Candidate
from .electionposition import ElectionPosition
from .voter import Voter


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
