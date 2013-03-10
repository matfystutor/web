from .models import *
from django.contrib import admin

class RSVPInline(admin.TabularInline):
    model = EventParticipant

class EventAdmin(admin.ModelAdmin):
    inlines = [RSVPInline]
    date_hierarchy = 'start_date'
    fields = (('title', 'rsvp'), 'description', ('start_date', 'end_date'), ('start_time', 'end_time'))
    list_display = ('title', 'start_date', 'end_date', 'start_time', 'end_time', 'rsvp')
    search_fields = ('title', 'description')

def event_title(rsvp):
    return rsvp.event.title
event_title.short_description = 'Begivenhed'
event_title.admin_order_field = 'event'

class RSVPAdmin(admin.ModelAdmin):
    list_display = (event_title, 'tutor', 'status', 'notes')
    search_fields = ('tutor__profile__user__first_name', 'tutor__profile__user__last_name', 'notes', 'event__title')

admin.site.register(Event, EventAdmin)
admin.site.register(EventParticipant, RSVPAdmin)
