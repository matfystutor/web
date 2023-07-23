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
        'firstDate0Stormøde': '14',
        'secondDate0Stormøde': '15',
        'måned0Stormøde': 'februar',
        'årstal0Stormøde': '2023',
        'date1Stormøde': '1',
        'måned1Stormøde': 'marts',
        'årstal1Stormøde': '2023',
        'firstDateRusuge': '23',
        'månedRusuge': 'august',
        'firstDateBurMobil': '7',
        'månedBurMobil': 'august',
        'secondDateBurMobil': '22',
        'thirdDateBurMobil': '23',
        'fourthDateBurMobil': '25',
        'fifthDateBurMobil': '28',
        'sixthDateBurMobil': '30',
        'firstDateRustur': '8',
        'månedRustur': 'september',
        'secondDateRustur': '10',
        'dateSportsdag': '22',
    }
