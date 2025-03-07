# vim:set fileencoding=utf-8:

from django.contrib.auth.forms import AuthenticationForm

from mftutor.settings import BODY_CLASS


def login_form(request):
    return {
        'login_form': AuthenticationForm(),
        'request_path': request.get_full_path(),
    }


def tutor_data(request):
    if request.tutor:
        return {'tutor': request.tutor, 'profile': request.tutorprofile}
    elif request.rus:
        return {'rus': request.rus, 'profile': request.tutorprofile}
    else:
        return {}


def settings(request):
    return {
        'BODY_CLASS': BODY_CLASS,
        'BURET': 'Buret™',
        'firstDate0Stormøde': '11',
        'secondDate0Stormøde': '12',
        'måned0Stormøde': 'februar',
        'årstal0Stormøde': '2025',
        'date1Stormøde': '26',
        'måned1Stormøde': 'februar',
        'årstal1Stormøde': '2025',
        'firstDateRusuge': '20',
        'middleDateRusuge': '22',
        'månedRusuge': 'august',
        'firstDateBurMobil': '5',
        'månedBurMobil': 'august',
        'secondDateBurMobil': '18',
        'thirdDateBurMobil': '21',
        'fourthDateBurMobil': '23',
        'fifthDateBurMobil': '26',
        'sixthDateBurMobil': '38',
        'firstDateRustur': '5',
        'månedRustur': 'september',
        'secondDateRustur': '7',
        'dateSportsdag': '19',
    }
