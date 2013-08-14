from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

def a_tag(url, name, klass, autoescape):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    result = '<a href="%s" class="%s">%s</a>' % (esc(url), esc(klass), esc(name))
    return mark_safe(result)

@register.filter(needs_autoescape=True)
def rusclass_link(value, autoescape=None):
    return a_tag(
            reverse('browser_rusclass', kwargs={'year': value.year, 'handle': value.handle}),
            value.internal_name, '', autoescape)

@register.filter(needs_autoescape=True)
def profile_link(value, autoescape=None):
    if value.tutor_set.exists():
        klass = 'profile_tutor'
    else:
        klass = 'profile_nottutor'
    try:
        url = reverse('browser_profile', kwargs={'studentnumber': value.studentnumber})
        return a_tag(url, value.name, klass, autoescape)
    except NoReverseMatch:
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x
        return esc(value.name)

@register.filter(needs_autoescape=True)
def group_link(value, year, autoescape=None):
    try:
        url = reverse('browser_group', kwargs={'year': year, 'handle': value.handle})
        return a_tag(url, value.name, '', autoescape)
    except NoReverseMatch:
        if autoescape:
            esc = conditional_escape
        else:
            esc = lambda x: x
        return esc(value.name)
