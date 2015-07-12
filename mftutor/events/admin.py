from .models import *
from django.contrib import admin
from django.forms.models import BaseInlineFormSet


class RSVPInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(RSVPInlineFormSet, self).__init__(*args, **kwargs)
        self.queryset = self.get_queryset().select_related('tutor__profile__user')


class RSVPInline(admin.TabularInline):
    model = EventParticipant
    formset = RSVPInlineFormSet

class EventAdmin(admin.ModelAdmin):
    inlines = [RSVPInline]
    date_hierarchy = 'start_date'
    fields = (('title', 'rsvp'), 'location', 'description', ('start_date', 'end_date'), ('start_time', 'end_time'))
    list_display = ('title', 'location', 'start_date', 'end_date', 'start_time', 'end_time', 'rsvp')
    search_fields = ('title', 'location', 'description')

def event_title(rsvp):
    return rsvp.event.title
event_title.short_description = 'Begivenhed'
event_title.admin_order_field = 'event'

class RSVPAdmin(admin.ModelAdmin):
    list_display = (event_title, 'tutor', 'status', 'notes')
    search_fields = ('tutor__profile__name', 'notes', 'event__title')

admin.site.register(Event, EventAdmin)
admin.site.register(EventParticipant, RSVPAdmin)
