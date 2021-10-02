import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse

from ..apps import SocietyElectionsConfig
from .electionposition import ElectionPosition


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
    email_uuid = models.UUIDField(
        null=True,
        blank=True,
        editable=False
    ) # Only required if necessary to validate candidate email
    email_verified = models.BooleanField(
        default=False
    )


    def send_verification_email(self):
        """Send a verification email to the candidate
        
        Only send a verification email if this has been configured in the 
        election settings.
        """
        if self.position.election.verify_candidate_email:
            if self.email_uuid is None:
                raise ValueError(
                    'UUID has not yet been set, cannot send verification email'
                )
            send_mail(
                f'Verify Email for Nomination in {self.position.election}',
                self.position.election.candidate_verification_email.format(
                    name=self.full_name,
                    position=self.position.position,
                    verify_url=self.verify_url
                )
            )


    @property
    def verify_url(self) -> str:
        """str: URL to click to verify the email address of a candidate"""
        return (
            f'{settings.ROOT_URL}/'
            f'{reverse("candidate_verify", args=(self.email_uuid))}'
        )

    
    def save(self, *args, **kwargs):
        """Create a UUID for the verification email if required when saving for 
        the first time
        """
        if (
            self.email_uuid is None and
            self.position.election.verify_candidate_email
        ):
            self.email_uuid = uuid.uuid4()
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.full_name} for {self.position.position}'
