# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db import models, migrations


def set_news_year(apps, schema_editor):
    NewsPost = apps.get_model('news', 'NewsPost')

    for post in NewsPost.objects.all():
        if post.posted.date() >= datetime.date(post.posted.year, 11, 5):
            post.year = post.posted.year + 1
        else:
            post.year = post.posted.year
        post.save()


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_newspost_year'),
    ]

    operations = [
        migrations.RunPython(set_news_year),
    ]
