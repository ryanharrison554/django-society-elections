from logging import getLogger

from django.contrib import admin
from django.utils.decorators import method_decorator

from ..decorators import log_model_admin_action
from ..models import ElectionPosition

logger = getLogger(__name__)


@admin.register(ElectionPosition)
@method_decorator(
    log_model_admin_action('save', ElectionPosition, logger),
    name='save_model'
)
@method_decorator(
    log_model_admin_action('delete', ElectionPosition, logger),
    name='delete_model'
)
class PositionAdmin(admin.ModelAdmin):
    """Defines how the ElectionPosition model is presented on the admin 
    interface
    """
