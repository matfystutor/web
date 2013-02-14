import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mftutor.settings")
from tutormail.send import make_mails
make_mails()
