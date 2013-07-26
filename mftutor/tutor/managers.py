# vim:set fileencoding=utf-8:
from django.db import models
from ..settings import YEAR

class TutorProfileManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(TutorProfileManager, self).get_query_set().select_related('user')

class TutorManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(TutorManager, self).get_query_set().select_related('profile', 'profile__user')

class TutorMembers(TutorManager):
    def get_query_set(self):
        qs = super(TutorMembers, self).get_query_set()
        return qs.filter(year=YEAR, early_termination__isnull=True)

    def group(self, group):
        from .models import TutorGroup
        if isinstance(group, TutorGroup):
            return self.filter(groups=group)
        else:
            return self.filter(groups__handle__exact=group)

class VisibleTutorGroups(models.Manager):
    def get_query_set(self):
        qs = super(VisibleTutorGroups, self).get_query_set()
        return qs.filter(visible=True, tutor__year__in=[YEAR]).distinct()
