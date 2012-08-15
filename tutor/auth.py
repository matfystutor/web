from tutor.models import TutorProfile, Tutor
from django.http import HttpResponse
from django.template import RequestContext, loader

def user_tutor_data(user):
    if user is None or not user.is_authenticated():
        return {'err': 'failauth'}
    if not user.is_active:
        return {'err': 'djangoinactive'}
    try:
        profile = user.get_profile()
    except TutorProfile.DoesNotExist:
        return {'err': 'notutorprofile'}
    try:
        tut = Tutor.objects.get(profile=profile, year=2012)
    except Tutor.DoesNotExist:
        return {'err': 'notutoryear'}
    return {'err': None, 'data': {'tutorprofile': profile, 'tutor': tut}}

def tutorbest_required_error(request):
    t = loader.get_template('tutorbest_required.html')
    c = RequestContext(request)
    return HttpResponse(t.render(c), status=403)

def is_tutorbest(tutor):
    return tutor.profile.user.is_superuser or tutor.groups.filter(handle='best').count() > 0

# Decorator
def tutorbest_required(fn):
    def wrapper(request, *args, **kwargs):
        d = user_tutor_data(request.user)
        if d['err'] is not None or not is_tutorbest(d['data']['tutor']):
            return tutorbest_required_error(request)
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper
