from logging import getLogger

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.decorators import method_decorator

from ..decorators import log_model_admin_action
from ..forms import CandidateAdminForm
from ..models import Candidate

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
        date_hierarchy (str): How Candidates are grouped by date
        form (django.forms.ModelForm): Which form to use for the model
    """
    form = CandidateAdminForm
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