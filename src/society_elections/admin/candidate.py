from logging import getLogger

from django.contrib import admin
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
