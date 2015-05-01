# vim:set fileencoding=utf-8:

from django.contrib.auth.forms import AuthenticationForm

from mftutor.settings import BODY_CLASS
from mftutor.tutor.models import TutorProfile
from mftutor.tutor.auth import user_tutor_data, user_rus_data, NotTutor


def login_form(request):
    return {
        'login_form': AuthenticationForm(),
        'request_path': request.get_full_path(),
    }


def tutor_data(request):
    try:
        d = user_tutor_data(request.user)
        return {'tutor': d.tutor, 'profile': d.profile}
    except NotTutor:
        pass

    try:
        d = user_rus_data(request.user)
        return {'rus': d.rus, 'profile': d.profile}
    except NotTutor:
        pass

    return {}


def settings(request):
    return {
        'BODY_CLASS': BODY_CLASS,
        'BURET': u'Buret™',
    }
