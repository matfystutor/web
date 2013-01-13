from django.db import models
from django.contrib.auth.models import User
import datetime

class NewsPost(models.Model):
    author = models.ForeignKey(User, verbose_name='Forfatter')
    title = models.CharField(max_length=200, verbose_name='Titel')
    posted = models.DateTimeField(verbose_name='Dato', default=lambda: datetime.date.today())
    body = models.TextField(verbose_name='Indhold')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'nyhed'
        verbose_name_plural = verbose_name + 'er'
