import os, sys

import django
import datetime as dt
import codecs
#sys.stdin = codecs.getreader('utf8')(sys.stdin)
#sys.stdout = codecs.getwriter('utf8')(sys.stdout)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mftutor.settings")
application = get_wsgi_application()

os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

from django.contrib.auth.models import User
from mftutor.tutor.models import TutorProfile

delete = False
accounts_to_delete = 0

for tutor_profile in TutorProfile.objects.all():
    last_login = tutor_profile.user.last_login
    if last_login is None:
        if delete:
            tutor_profile.user.delete()
            tutor_profile.delete()
        else:
            accounts_to_delete += 1
        continue

    delta_time = abs(last_login - dt.datetime.now(dt.timezone.utc))

    if delta_time.days >= 3*365 and delete:
        if delete:
            tutor_profile.user.delete()
            tutor_profile.delete()
        else:
            accounts_to_delete += 1

if not delete:
    print(accounts_to_delete)