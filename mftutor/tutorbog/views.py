from django.shortcuts import redirect
from django.http import HttpResponseNotFound
from constance import config


def secret_view(request, secret):
    if not config.TUTORBOG_SECRET:
        raise RuntimeError('No tutorbog secret configured')

    if not config.TUTORBOG_SURVEY_URL:
        raise RuntimeError('No tutorbog survey url configured')

    if secret == config.TUTORBOG_SECRET:
        return redirect(config.TUTORBOG_SURVEY_URL)
    else:
        # Should probably be prettier
        return HttpResponseNotFound('Forkert løsning, prøv igen!', content_type='text/plain; charset=utf-8')
