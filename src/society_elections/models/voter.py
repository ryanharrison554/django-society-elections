import uuid

from django.db import models

from ..apps import SocietyElectionsConfig
from .election import Election


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
        to=f'{SocietyElectionsConfig.name}.{Election.__name__}',
        on_delete=models.CASCADE,
        related_name='voters',
        related_query_name='voter'
    )
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
