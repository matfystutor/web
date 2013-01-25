from django.contrib.auth.forms import AuthenticationForm
from tutor.models import TutorProfile
from tutor.auth import user_tutor_data, NotTutor
import mftutor.settings

def login_form(request):
    return {'login_form': AuthenticationForm()}

def tutor_data(request):
    try:
        d = user_tutor_data(request.user)
    except NotTutor:
        return {}
    return {'tutor': d.tutor, 'profile': d.profile}

def settings(request):
    return {'BODY_CLASS': mftutor.settings.BODY_CLASS}
