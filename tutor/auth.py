from tutor.models import TutorProfile, Tutor
from django.http import HttpResponse
from django.template import RequestContext, loader
from mftutor import siteconfig

class NotTutor(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class TutorData:
    pass

def user_tutor_data(user):
    d = TutorData()
    if user is None or not user.is_authenticated():
        raise NotTutor('failauth')
    if not user.is_active:
        raise NotTutor('djangoinactive')
    try:
        d.profile = user.get_profile()
    except TutorProfile.DoesNotExist:
        raise NotTutor('notutorprofile')
    try:
        d.tutor = Tutor.objects.get(profile=d.profile, year=siteconfig.year)
    except Tutor.DoesNotExist:
        raise NotTutor('notutoryear')
    return d

def tutorbest_required_error(request):
    t = loader.get_template('tutorbest_required.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), status=403)

def is_tutorbest(tutor):
    return tutor.profile.user.is_superuser or tutor.groups.filter(handle='best').count() > 0

def tutor_required_error(request):
    t = loader.get_template('tutor_required.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), status=403)

def is_tutor(tutor):
    return tutor.profile.user.is_superuser or (tutor.groups.filter(handle='alle').count() > 0
            and tutor.early_termination is None)

# Decorator
def tutorbest_required(fn):
    def wrapper(request, *args, **kwargs):
        try:
            d = user_tutor_data(request.user)
        except NotTutor as e:
            return tutorbest_required_error(request)
        if not is_tutorbest(d.tutor):
            return tutorbest_required_error(request)
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

# Decorator
def tutor_required(fn):
    def wrapper(request, *args, **kwargs):
        try:
            d = user_tutor_data(request.user)
        except NotTutor as e:
            return tutor_required_error(request)
        if not is_tutor(d.tutor):
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
