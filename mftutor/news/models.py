from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.urlresolvers import reverse

class NewsPost(models.Model):
    GROUP_HANDLES = (
        ('alle', 'Tutorhjemmesidens forside'),
        ('rus', 'Rushjemmesidens forside'),
    )
    author = models.ForeignKey(User, verbose_name='Forfatter')
    title = models.CharField(max_length=200, verbose_name='Titel')
    posted = models.DateTimeField(verbose_name='Dato', default=lambda: datetime.date.today())
    body = models.TextField(verbose_name='Indhold')
    group_handle = models.CharField(max_length=20)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        p = self.posted
        return reverse('news', kwargs={'year':p.year, 'month':p.month, 'day':p.day, 'pk':self.pk})

    class Meta:
        verbose_name = 'nyhed'
        verbose_name_plural = verbose_name + 'er'
