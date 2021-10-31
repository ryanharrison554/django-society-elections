from logging import getLogger

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.decorators import method_decorator

from ..forms import CandidateAdminForm
from ..models import Candidate
from .decorators import log_model_admin_action

logger = getLogger(__name__)


@admin.register(Candidate)
@method_decorator(
    log_model_admin_action('save', Candidate, logger),
    name='save_model'
)
@method_decorator(
    log_model_admin_action('delete', Candidate, logger),
    name='delete_model'
)
class CandidateAdmin(admin.ModelAdmin):
    """Class defining how an Candidate model is presented in the admin interface

    Attributes:
        list_display (tuple): What fields are shown on the tables
        form (django.forms.ModelForm): Which form to use for the model
        actions (list): Actions registered on the admin interface
    """
    form = CandidateAdminForm
    list_display = ('__str__', 'position_election', 'email_verified')
    actions = ['resend_verification_email_action']

    @admin.action(description='Resend verification emails')
    @method_decorator(log_model_admin_action(
        'resend verification email', Candidate, logger
    ))
    def resend_verification_email_action(
        self, request: HttpRequest, queryset: QuerySet
    ):
        """Regenerate UUID of selected candidates and resend email

        Args:
            request (HttpRequest): Request to server to perform action
            queryset (QuerySet): Set of objects to perform action on
        """
        candidate: Candidate
        for candidate in queryset:
            candidate.email_uuid = None
            candidate.save() # Regenerates UUID
            candidate.send_verification_email()

    @admin.display(description='Election')
    def position_election(self, obj: Candidate):
        return Candidate.position.election
