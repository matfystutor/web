# vim:set fileencoding=utf-8:
from django.contrib.syndication.views import Feed
from .models import Document

class MinutesFeed(Feed):
    title = 'Mat/Fys-Tutorgruppen - referater'
    link = '/document/referater/'
    description = 'Referater fra Mat/Fys-Tutorgruppens møder.'

    def items(self):
        return Document.objects.filter(type__exact='referater').order_by('published')[:5]

    def item_title(self, item):
        return item.published.strftime(u'%Y-%m-%d')+u' '+item.title

    def item_description(self, item):
        return self.item_title(item)

    def item_author_name(self, item):
        return "Mat/Fys-Tutorgruppen"
