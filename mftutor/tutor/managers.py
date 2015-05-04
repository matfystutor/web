# vim:set fileencoding=utf-8:
from django.db import models
from ..settings import YEAR

class RusManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(RusManager, self).get_queryset().select_related('profile', 'rusclass', 'initial_rusclass')

class TutorProfileManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(TutorProfileManager, self).get_queryset()

class TutorManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(TutorManager, self).get_queryset().select_related('profile')

class TutorMembers(TutorManager):
    def get_queryset(self):
        qs = super(TutorMembers, self).get_queryset()
        return qs.filter(year=YEAR, early_termination__isnull=True)

    def group(self, group):
        from .models import TutorGroup
        if isinstance(group, TutorGroup):
            return self.filter(groups=group)
        else:
            return self.filter(groups__handle__exact=group)

class VisibleTutorGroups(models.Manager):
    def get_queryset(self):
        qs = super(VisibleTutorGroups, self).get_queryset()
        return qs.filter(visible=True, tutor__year__in=[YEAR]).distinct()


class RusClassManager(models.Manager):
    def create_from_official(self, year, official_name):
        """Translate (2015, "MA1") into a fresh RusClass object."""
        official_study = official_name[:2]
        number = official_name[2:]
        handle, internal_name = next(
            (handle, internal)
            for official, handle, internal in settings.RUSCLASS_BASE
            if official == official_study
        )
        handle = '%s%s' % (handle, number)
        internal_name = '%s %s' % (internal_name, number)
        return self.model(year=year, official_name=official_name,
                          handle=handle, internal_name=internal_name)
