from .middleware import get_request
from .models import Revision
from .utils import obj_diff


def pre_save(instance, **kwargs):
    """
    Pre-save signal handler
    """
    model = kwargs["sender"]
    if not hasattr(instance, 'revision_info'):
        instance.revision_info = {}
    info = instance.revision_info

    try:
        original = model._default_manager.get(pk=instance.pk)
    except model.DoesNotExist:
        original = model()
    info['delta'] = obj_diff(instance, original)
    request = get_request()
    if request:
        if not info.get('editor'):
            info['editor'] = request.user
        if not info.get('editor_ip'):
            info['editor_ip'] = request.META.get("REMOTE_ADDR")
    if not hasattr(info, 'editor') or not getattr(info['editor'], 'pk', None):
        info['editor'] = None


def post_save(instance, **kwargs):
    """
    Post-save signal handler
    """
    info = getattr(instance, 'revision_info', {})
    if info:
        rev = Revision(**info)
        rev.content_object = instance
        rev.save()
