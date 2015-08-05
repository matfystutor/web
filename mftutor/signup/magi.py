from mftutor.signup.models import *
from mftutor.tutor.models import *

for a in TutorApplication.objects.all():
    try:
        qs = a.profile.tutor_set.get(year=2015).groups.all()
        qs = qs.exclude(handle__in='best gruppeansvarlige'.split())
        a.assigned_groups = qs
        a.accepted = True
    except Tutor.DoesNotExist:
        a.accepted = False
    a.save()

AssignedGroupLeader.objects.filter(group__year=2015).delete()
for a in TutorGroup.objects.filter(year=2015):
    if a.leader:
        AssignedGroupLeader(
            group=a, application=TutorApplication.objects.filter(profile__tutor=a.leader)[0]).save()

Tutor.objects.filter(year=2015).exclude(groups__handle='best').delete()
