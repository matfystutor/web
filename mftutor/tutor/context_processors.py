# vim:set fileencoding=utf-8:
from django.contrib.auth.forms import AuthenticationForm
from ..settings import BODY_CLASS
from .models import TutorProfile
from .auth import user_tutor_data, NotTutor

def login_form(request):
    return {
            'login_form': AuthenticationForm(),
            'request_path': request.get_full_path(),
            }

def tutor_data(request):
    try:
        d = user_tutor_data(request.user)
    except NotTutor:
        return {}
    return {'tutor': d.tutor, 'profile': d.profile}

def settings(request):
    return {
            'BODY_CLASS': BODY_CLASS,
            'BURET': u'Buret™'
            }
