from django.contrib.syndication.views import Feed
from .models import NewsPost

class NewsFeed(Feed):
    title = 'Mat/Fys-Tutorgruppen'
    link = '/news/'
    description = 'Forsidenyheder fra Mat/Fys-Tutorgruppens bestyrelse.'

    def items(self):
        return NewsPost.objects.order_by('-posted')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body

    def item_author_name(self, item):
        return item.author.get_full_name()
