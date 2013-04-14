from django.conf import settings

def site(request):
    try:
        return {'SITE_URL': settings.SITE_URL}
    except AttributeError:
        return {}
