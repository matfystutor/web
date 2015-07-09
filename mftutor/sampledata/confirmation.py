import random
from ..tutor.models import Tutor
from ..confirmation.models import Confirmation
from .constants import RESITS
from .tutor import random_study, random_name

def random_priorities(study):
    studies = set()
    if random.random() > 0.1:
        studies.add(study)
    for x in range(int(random.randint(0,6))):
        studies.add(random_study())
    return u', '.join(studies)

def known_russes():
    russes = []
    for x in range(random.choice((0,0,0,0,0,0,0,1,1,2,3))):
        russes.append(random_name()+u', '+random_study())
    return u'\n'.join(russes)

def fill_out_confirmation(tutor):
    if Confirmation.objects.filter(tutor=tutor).exists():
        return

    c = Confirmation(tutor=tutor,
            study=tutor.profile.study,
            experience=str(random.choice((0,)*15 + (1,) * 10 + (2,) * 5 + (3,3,3,4))),
            resits=random.choice(RESITS),
            priorities=random_priorities(tutor.profile.study),
            firstaid=u'ja' if random.random() > 0.8 else u'nej',
            rusfriends=known_russes(),
            comment=u'bla bla' if random.random() > 0.9 else u'',
            )
    c.save()

def fill_out_confirmations(fraction):
    filled_out = Tutor.members().filter(confirmation__isnull=False)
    missing = Tutor.members().exclude(confirmation__isnull=False)
    new = int(fraction * Tutor.members().count()) - filled_out.count()
    for tutor in missing:
        if new <= 0:
            break
        fill_out_confirmation(tutor)
        new = new - 1
