from __future__ import unicode_literals

from django.utils.functional import SimpleLazyObject

from mftutor import settings
from mftutor.tutor.models import TutorProfile, Tutor, Rus

def get_tutorprofile(request):
    if not request.user.id:
        return None
    try:
        return TutorProfile.objects.get(user_id=request.user.id)
    except TutorProfile.DoesNotExist:
        return None

def get_tutor(request):
    if not request.tutorprofile:
        return None
    try:
        return Tutor.objects.get(
            year=request.year, profile=request.tutorprofile)
    except Tutor.DoesNotExist:
        return None

def get_rus(request):
    if not request.tutorprofile:
        return None
    try:
        return Rus.objects.get(
            year=request.rusyear, profile=request.tutorprofile)
    except Rus.DoesNotExist:
        return None

class TutorMiddleware(object):
    def process_request(self, request):
        request.year = request.session.get('year', settings.YEAR)
        request.rusyear = request.session.get('rusyear',
                                              settings.RUSMAIL_YEAR)
        request.tutorprofile = SimpleLazyObject(
            lambda: get_tutorprofile(request))
        request.tutor = SimpleLazyObject(lambda: get_tutor(request))
        request.rus = SimpleLazyObject(lambda: get_rus(request))

    # def process_response(self, request, response):
    #     return response
