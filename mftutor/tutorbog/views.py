from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import HttpResponseNotFound


USERNAME = 'tutorbog_krydsord'


def secret_view(request, secret):
    user = User.objects.get(username=USERNAME)
    if user.check_password(secret):
        # Should be replaced by either:
        # * A redirect to the real survey, or
        # * A survey implemented on the website
        return redirect('https://example.org/')
    else:
        # Should probably be prettier
        return HttpResponseNotFound('Forkert løsning, prøv igen!', content_type='text/plain; charset=utf-8')
