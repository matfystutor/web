# vim: set fileencoding=utf8:
import random
import sys
from django.contrib.auth.models import User
from ..tutor.models import TutorProfile, Tutor, TutorGroup
from .constants import FIRST_NAME, LAST_NAME, STREET, CITY, GROUP

def random_student_number(tutoryear):
    if random.random() < 0.005:
        # ASB-style student number
        return (chr(random.randint(ord('A'), ord('Z')))
                +chr(random.randint(ord('A'), ord('Z')))
                +str(random.randint(70000,99999)))

    year = int(tutoryear - round(random.expovariate(5)))

    if year < 1970:
        year = 1970

    if year < 2012:
        return str(year)+('%05d' % random.randint(0, 19999))
    else:
        return str(year)+('%04d' % random.randint(0, 9999))

def random_first_name():
    return random.choice(FIRST_NAME)

def random_last_name():
    name = random.choice(LAST_NAME)
    if random.random() < 0.1:
        name = name + u' ' + random.choice(LAST_NAME)
    if random.random() < 0.01:
        name = name + u' ' + random.choice(LAST_NAME)
    return name

def random_name():
    return random_first_name()+u' '+random_last_name()

def random_street():
    return random.choice(STREET) + u' ' + str(1+int(random.expovariate(0.1)))

def random_city():
    return random.choice(CITY)

def print_random_table():
    for x in range(100):
        sys.stdout.write(
                (u"%-40s %-10s %-40s %-20s\n" % (random_name(),
                    random_student_number(2013), random_street(), random_city()))
                .encode('utf8'))

def random_phone_number():
    return random.randint(20000000, 69999999)

def random_email(sn):
    return sn+random.choice(('@example.com', '@example.net', '@example.org',
        '@example.edu', '@matfystutor.local'))

def random_study():
    return random.choice((u'mat', u'fys', u'møk', u'nano', u'dat', u'it'))

def new_random_profile(year):
    sn = random_student_number(year)
    while TutorProfile.objects.filter(studentnumber__exact=sn).exists():
        sn = random_student_number()

    tp = TutorProfile(
            studentnumber=sn,
            street=random_street(),
            city=random_city(),
            phone=random_phone_number(),
            study=random_study(),
            )

    u = User(
            username=sn,
            email=random_email(sn),
            first_name=random_first_name(),
            last_name=random_last_name(),
            )
    u.save()
    tp.user = u
    tp.save()

    return tp

def get_group(handle, name):
    try:
        return TutorGroup.objects.get(handle__exact=handle)
    except TutorGroup.DoesNotExist:
        tg = TutorGroup(handle=handle, name=name, visible=True)
        tg.save()
        return tg

def new_random_tutor(year):
    tp = new_random_profile(year-1)
    tu = Tutor(
            profile=tp,
            year=year,
            )
    tu.save()
    tu.groups.add(get_group('alle', 'Alle tutorer'))
    tu.groups.add(get_group(*random.choice(GROUP)))
    tu.groups.add(get_group(*random.choice(GROUP)))
