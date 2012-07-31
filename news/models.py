from django.db import models
from django.contrib.auth.models import User

class NewsPost(models.Model):
    author = models.ForeignKey(User, verbose_name='Forfatter')
    title = models.CharField(max_length=200, verbose_name='Titel')
    body = models.TextField(verbose_name='Indhold')
    posted = models.DateTimeField(verbose_name='Dato')
