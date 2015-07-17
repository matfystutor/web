import functools

from django.http import HttpResponse
from django.template import RequestContext, loader
import django.contrib.auth.backends

from mftutor.settings import YEAR, TUTORMAIL_YEAR
from mftutor.tutor.models import TutorProfile, Tutor, Rus


def rusclass_required_error(request):
    t = loader.get_template('rusclass_required.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), status=403)


def tutorbest_required_error(request):
    t = loader.get_template('tutorbest_required.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), status=403)


def tutor_required_error(request):
    t = loader.get_template('tutor_required.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), status=403)


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
