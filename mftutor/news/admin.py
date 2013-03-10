from .models import NewsPost
from django.contrib import admin

def forfatter(post):
    return post.author.get_full_name()

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', forfatter, 'posted')
    search_fields = ('title', 'author__first_name', 'author__last_name', 'body')

admin.site.register(NewsPost, PostAdmin)
