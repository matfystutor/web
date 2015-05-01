from .models import NewsPost
from django.contrib import admin

def forfatter(post):
    return post.author.get_full_name()

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', forfatter, 'posted', 'year')
    search_fields = ('title', 'author__first_name', 'author__last_name', 'body', 'year')

admin.site.register(NewsPost, PostAdmin)
