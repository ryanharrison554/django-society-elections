from logging import getLogger

from django.contrib import admin
from django.http import HttpRequest

from ..forms import ElectionForm
from ..models import Election

logger = getLogger(__name__)


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    """Class defining how an Election model is presented in the admin interface

    Attributes:
    """
    date_hierarchy = 'nominations_start'
    form = ElectionForm


    def save_model(self, request: HttpRequest, obj: Election, *args, **kwargs):
        """Set request-specific data on the object before saving to database

        Args:
            request (HttpRequest): Request made when saving model
            obj (Election): Election object to save in database
        """
        if obj.pk is None:
            logger.info(f'{request.user} creating election "{obj}"')
            obj.created_by = request.user
        else:
            logger.info(f'{request.user} updating election "{obj}"')
        super().save_model(request, obj, *args, **kwargs)

