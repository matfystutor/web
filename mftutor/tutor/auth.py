from django.http import HttpResponse
from django.template import RequestContext, loader
import django.contrib.auth.backends
from ..settings import YEAR
from .models import TutorProfile, Tutor, Rus

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
        d.profile = user.get_profile()
    except TutorProfile.DoesNotExist:
        raise NotTutor('notutorprofile')
    return d

def user_tutor_data(user):
    d = user_profile_data(user)
    try:
        d.tutor = Tutor.objects.get(profile=d.profile, year=YEAR)
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
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return fn(request, *args, **kwargs)
        try:
            d = user_tutor_data(request.user)
        except NotTutor as e:
            return tutorbest_required_error(request)
        if not d.tutor.is_tutorbest():
            return tutorbest_required_error(request)
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

# Decorator
def tutor_required(fn):
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return fn(request, *args, **kwargs)
        try:
            d = user_tutor_data(request.user)
        except NotTutor as e:
            return tutor_required_error(request)
        if not d.tutor.is_member():
            return tutor_required_error(request)
        import inspect
        namedargs, varargs, varkw, defaults = inspect.getargspec(fn)
        if varkw is not None or 'tutor' in namedargs:
            kwargs['tutor'] = d.tutor
        if varkw is not None or 'profile' in namedargs:
            kwargs['profile'] = d.profile
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

# Decorator
def tutorbur_required(fn):
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return fn(request, *args, **kwargs)
        try:
            d = user_tutor_data(request.user)
        except NotTutor as e:
            return tutorbest_required_error(request)
        if not d.tutor.is_tutorbur():
            return tutorbest_required_error(request)
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
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
