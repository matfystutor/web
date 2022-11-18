# vim:set fileencoding=utf-8:
from django.contrib.syndication.views import Feed
from .models import Document

class MinutesFeed(Feed):
    title = 'Mat/Fys-Tutorforeningen - referater'
    link = '/document/referater/'
    description = 'Referater fra Mat/Fys-Tutorforeningens møder.'

    def items(self):
        qs = Document.objects.filter(type__exact='referater')
        return qs.order_by('-published')[:5]

    def item_title(self, item):
        return item.published.strftime('%Y-%m-%d')+' '+item.title

    def item_description(self, item):
        return self.item_title(item)

    def item_author_name(self, item):
        return "Mat/Fys-Tutorforeningen"
