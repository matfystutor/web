import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mftutor.settings")
from tutor.models import read_emails_loop
read_emails_loop()
