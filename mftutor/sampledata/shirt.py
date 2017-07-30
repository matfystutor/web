import random

from ..tutor.models import TutorProfile, Tutor
from ..shirt.models import ShirtPreference, ShirtOption

def make_tshirt_options():
    c = frozenset(('M small', 'M medium', 'M large',
        'F small', 'F medium', 'F large'))

    c = c - frozenset(so.choice for so in ShirtOption.objects.filter(
        choice__in=c))

    for choice in c:
        ShirtOption(
                choice=choice,
                position=0,
                ).save()

def make_tshirt_preferences(response_fraction):
    tutors = TutorProfile.objects.filter(tutor__in=Tutor.members())
    chosen = ShirtPreference.objects.filter(profile__in=tutors)
    add_count = int(response_fraction * tutors.count() - chosen.count())
    options = [so.choice for so in ShirtOption.objects.all()]
    while add_count > 0:
        t = random.choice(tutors.filter(shirtpreference__isnull=True))
        so = ShirtPreference(profile=t, choice1=random.choice(options), choice2=random.choice(options))
        so.save()
        add_count = add_count - 1
