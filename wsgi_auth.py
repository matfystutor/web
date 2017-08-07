"""
Script for Apache to check if user is logged in.

Used to restrict access to old gallery to authenticated users.

This script will be superseded when we finish the new gallery.

Based on http://openplm.org/svn/openPLM/trunk/openPLM/apache/access.wsgi
"""
import os
import sys


def here(x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

sys.path.append(here('venv/lib/python2.7/site-packages'))
sys.path.append(here('web'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

import django
from django import db
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user

from mftutor.tutor.models import TutorProfile, Tutor, Rus

django.setup()

# def check_password(environ, user, password):
#     db.reset_queries()
#     try:
#         try:
#             user = User.objects.get(username=user, is_active=True)
#         except User.DoesNotExist:
#             return None
#
#         if user.check_password(password):
#             return True
#         else:
#             return False
#     finally:
#         db.connection.close()


# def groups_for_user(environ, user):
#     db.reset_queries()
#     environ['wsgi.input'] = None
#     request = WSGIRequest(environ)
#     u = get_user(request)
#
#     # CURRENT_TUTOR = ['tutor', 'rus', 'current-tutor', 'current-rus']
#     PAST_TUTOR = ['tutor', 'rus']
#     # CURRENT_RUS = ['rus', 'current-rus']
#     PAST_RUS = ['rus']
#
#     try:
#         if u is None:
#             return []
#
#         try:
#             tp = TutorProfile.objects.get(user=u)
#         except TutorProfile.DoesNotExist:
#             return []
#
#         if Tutor.objects.filter(profile=tp).exists():
#             return PAST_TUTOR
#         elif Rus.objects.filter(profile=tp).exists():
#             return PAST_RUS
#         else:
#             return []
#     finally:
#         db.connection.close()


def allow_access(environ, host):
    db.reset_queries()
    environ['wsgi.input'] = None
    request = WSGIRequest(environ)
    SessionMiddleware().process_request(request)
    user = get_user(request)
    allowed = user.is_authenticated()
    db.connection.close()
    return allowed
