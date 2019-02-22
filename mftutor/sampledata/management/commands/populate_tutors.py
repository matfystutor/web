from django.core.management.base import BaseCommand

from ...all import populate_all


class Command(BaseCommand):
    help = "Populates database with random tutors."
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('--members',
                            dest='members',
                            type=int,
                            default=40)

    def handle(self, members, **kwargs):
        populate_all(members)
