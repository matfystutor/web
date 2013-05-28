from optparse import make_option
from django.core.management.base import BaseCommand
from ...all import populate_all

class Command(BaseCommand):
    can_import_settings = True
    option_list = BaseCommand.option_list + (
            make_option('--members',
                dest='members',
                default=40),
            make_option('--activations',
                dest='activations',
                default=0.1),
            )

    def handle(self, members, activations, **kwargs):
        populate_all(members, activations)
