import logging

from django.core.management.base import BaseCommand

from mftutor.gallery.models import BaseMedia


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Slet billeder som er markeret "Slet"'

    def handle(self, *args, **options):
        qs = BaseMedia.objects.filter(visibility=BaseMedia.DELETE)
        n = qs.count()
        if n:
            ids = sorted(qs.values_list('id', flat=True))
            logger.info("Deleting %s BaseMedia objects with IDs %s",
                        n, ids)
            BaseMedia.objects.filter(id__in=ids).delete()
