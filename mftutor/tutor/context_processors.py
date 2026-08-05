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
        'firstDate0Stormøde': '10',
        'secondDate0Stormøde': '11',
        'måned0Stormøde': 'februar',
        'årstal0Stormøde': '2026',
        'date1Stormøde': '25',
        'måned1Stormøde': 'februar',
        'årstal1Stormøde': '2026',
        'firstDateRusuge': '19',
        'middleDateRusuge': '21',
        'månedRusuge': 'august',
        'firstDateBurMobil': '3',
        'månedBurMobil': 'august',
        'secondDateBurMobil': '14',
        'thirdDateBurMobil': '19',
        'fourthDateBurMobil': '21',
        'fifthDateBurMobil': '24',
        'sixthDateBurMobil': '26',
        'firstDateRustur': '4',
        'månedRustur': 'september',
        'secondDateRustur': '6',
        'dateSportsdag': '25',
    }
