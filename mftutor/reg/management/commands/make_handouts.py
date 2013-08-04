import logging
from optparse import make_option
from django.core.management.base import BaseCommand
from ....settings import YEAR
from ...models import Handout

class Command(BaseCommand):
    can_import_settings = True
    option_list = BaseCommand.option_list + (
            #make_option('--members',
            #    dest='members',
            #    default=40),
            #make_option('--activations',
            #    dest='activations',
            #    default=0.1),
            )

    def handle(self, **kwargs):
        names = frozenset([name for name, kind in Handout.PRESETS])
        existing = frozenset([h.name for h in Handout.objects.filter(name__in=names, year__exact=YEAR)])
        create = [Handout(name=name, kind=kind, year=YEAR)
                for name, kind in Handout.PRESETS
                if name not in existing]
        for h in create:
            logging.info("Create handout '%s'" % h.name)
            h.save()
