from logging import getLogger

from django.contrib import admin
from django.http import HttpRequest
from django.utils.decorators import method_decorator

from ..forms import ElectionForm
from ..models import Election
from .decorators import log_model_admin_action

logger = getLogger(__name__)


@admin.register(Election)
@method_decorator(
    log_model_admin_action('save', Election, logger),
    name='save_model'
)
@method_decorator(
    log_model_admin_action('delete', Election, logger),
    name='delete_model'
)
class ElectionAdmin(admin.ModelAdmin):
    """Class defining how an Election model is presented in the admin interface

    Attributes:
        list_display (tuple): Which fields should be shown in the table
        form (django.forms.ModelForm): Which form to use for the model
    """
    list_display = ('admin_title', 'nominations_start', 'voting_start')
    form = ElectionForm


    def save_model(self, request: HttpRequest, obj: Election, *args, **kwargs):
        """Set request-specific data on the object before saving to database

        Args:
            request (HttpRequest): Request made when saving model
            obj (Election): Election object to save in database
        """
        if obj.pk is None:
            obj.created_by = request.user
        super().save_model(request, obj, *args, **kwargs)

