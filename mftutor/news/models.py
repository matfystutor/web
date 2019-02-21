from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class NewsPost(models.Model):
    GROUP_HANDLES = (
        ('alle', 'Tutorhjemmesidens forside'),
        ('rus', 'Rushjemmesidens forside'),
    )
    author = models.ForeignKey(User, models.CASCADE, verbose_name='Forfatter')
    title = models.CharField(max_length=200, verbose_name='Titel')
    posted = models.DateTimeField(verbose_name='Dato')
    body = models.TextField(verbose_name='Indhold')
    group_handle = models.CharField(max_length=20)
    year = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        p = self.posted
        base_name = 'news'
        if self.group_handle == 'rus':
            base_name = 'rus_nyheder'
        return reverse(base_name, kwargs={'year':p.year, 'month':p.month, 'day':p.day, 'pk':self.pk})

    class Meta:
        verbose_name = 'nyhed'
        verbose_name_plural = verbose_name + 'er'
