from django.contrib.auth.forms import AuthenticationForm
from tutor.models import TutorProfile
from tutor.auth import user_tutor_data

def login_form(request):
    return {'login_form': AuthenticationForm()}

def tutor_data(request):
    data = user_tutor_data(request.user)
    if data['err'] is not None:
        return {}
    return data['data']
