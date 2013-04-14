import datetime
from django import template

register = template.Library()

@register.filter
def add_day(dt):
    return dt + datetime.timedelta(1)


