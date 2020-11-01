from django.db import models
from mftutor.tutor.models import TutorProfile


class BallotLink(models.Model):
    profile = models.ForeignKey(TutorProfile, models.CASCADE)
    name = models.CharField(max_length=50, db_index=True)
    url = models.TextField()
