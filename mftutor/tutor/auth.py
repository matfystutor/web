import functools

from django.template.response import TemplateResponse
import django.contrib.auth.backends
from django.views.generic import TemplateView


class TemplateResponseForbidden(TemplateResponse):
    status_code = 403

rusclass_required_error = TemplateView.as_view(
    response_class=TemplateResponseForbidden,
    template_name='rusclass_required.html')

tutorbest_required_error = TemplateView.as_view(
    response_class=TemplateResponseForbidden,
    template_name='tutorbest_required.html')

tutor_required_error = TemplateView.as_view(
    response_class=TemplateResponseForbidden,
    template_name='tutor_required.html')


# Decorator
def tutorbest_required(fn):
    @functools.wraps(fn)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return fn(request, *args, **kwargs)
        if not request.tutor:
            return tutorbest_required_error(request)
        if not request.tutor.is_tutorbest(year=request.year):
            return tutorbest_required_error(request)
        return fn(request, *args, **kwargs)

    return wrapper


# Decorator
def tutor_required(fn):
    @functools.wraps(fn)
    def wrapper(request, *args, **kwargs):
        if request.tutor:
            return fn(request, *args, **kwargs)
        elif request.user.is_superuser:
            return fn(request, *args, **kwargs)
        else:
            return tutor_required_error(request)

    return wrapper


# Decorator
def tutorbur_required(fn):
    @functools.wraps(fn)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return fn(request, *args, **kwargs)
        if not request.tutor:
            return tutorbest_required_error(request)
        elif not request.tutor.is_tutorbur():
            return tutorbest_required_error(request)
        else:
            return fn(request, *args, **kwargs)

    return wrapper


class SwitchUserBackend(django.contrib.auth.backends.ModelBackend):
    def authenticate(self, username, current_user):
        if not current_user.is_superuser:
            return None

        from django.contrib.auth.models import User

        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
