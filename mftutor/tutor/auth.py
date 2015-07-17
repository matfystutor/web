import functools

from django.http import HttpResponse
from django.template import RequestContext, loader
import django.contrib.auth.backends

from mftutor.settings import YEAR, TUTORMAIL_YEAR
from mftutor.tutor.models import TutorProfile, Tutor, Rus


class NotTutor(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TutorData:
    pass


def user_profile_data(user):
    d = TutorData()
    if user is None or not user.is_authenticated():
        raise NotTutor('failauth')
    if not user.is_active:
        raise NotTutor('djangoinactive')
    try:
        d.profile = user.tutorprofile
    except TutorProfile.DoesNotExist:
        raise NotTutor('notutorprofile')
    return d


def user_tutor_data(user):
    d = user_profile_data(user)
    d.tutor = None
    try:
        d.tutor = Tutor.objects.get(year=YEAR, profile=d.profile)
    except Tutor.DoesNotExist:
        try:
            d.tutor = Tutor.objects.get(year=TUTORMAIL_YEAR, profile=d.profile)
        except Tutor.DoesNotExist:
            raise NotTutor('notutoryear')
    return d


def user_rus_data(user):
    d = user_profile_data(user)
    try:
        d.rus = Rus.objects.get(profile=d.profile, year=YEAR)
    except Rus.DoesNotExist:
        raise NotTutor('norusyear')
    return d


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
