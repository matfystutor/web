# vim: set fileencoding=utf8 :

from django.contrib import admin

from mftutor.tutor.models import (
    Tutor, TutorProfile, TutorGroup,
    BoardMember, RusClass, Rus)


class TutorInline(admin.TabularInline):
    model = Tutor


class TutorAdmin(admin.ModelAdmin):
    list_display = ('year', 'profile', 'is_tutorbest')
    list_display_links = ('profile',)
    list_filter = ('year',)
    search_fields = ['profile__name']
    filter_horizontal = ('groups',)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'studentnumber')
    inlines = [TutorInline]
    search_fields = ['name', 'studentnumber']


def make_visible(modeladmin, request, queryset):
    queryset.update(visible=True)
make_visible.short_description = 'Gør synlig'


def make_invisible(modeladmin, request, queryset):
    queryset.update(visible=False)
make_invisible.short_description = 'Gør ikke synlig'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'handle', 'visible', 'year')
    list_filter = ('visible', 'year')
    search_fields = ['name', 'handle']
    actions = [make_visible, make_invisible]


def board_full_name(bm):
    return bm.tutor.profile.get_full_name()
board_full_name.short_description = 'Navn'


def tutor_year(bm):
    return bm.tutor.year
tutor_year.short_description = 'År'
tutor_year.admin_order_field = 'tutor__year'


class BoardAdmin(admin.ModelAdmin):
    list_display = (board_full_name, tutor_year, 'title', 'position', 'short_title')
    list_filter = ('tutor__year',)
    search_fields = ['tutor__profile__name', 'title', 'short_title']
    list_editable = ('title', 'position', 'short_title')


class RusClassAdmin(admin.ModelAdmin):
    list_display = ('year', 'internal_name', 'official_name', 'handle')
    list_display_links = ('internal_name',)
    search_fields = ['internal_name', 'official_name', 'handle']


class RusAdmin(admin.ModelAdmin):
    list_display = ('profile', 'year', 'rusclass')
    search_fields = ['profile__name']


admin.site.register(Tutor, TutorAdmin)
admin.site.register(TutorProfile, ProfileAdmin)
admin.site.register(TutorGroup, GroupAdmin)
admin.site.register(BoardMember, BoardAdmin)
admin.site.register(RusClass, RusClassAdmin)
admin.site.register(Rus, RusAdmin)
