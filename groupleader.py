"""
Read tab-separated (student number, real name) lines from standard input
and output any weird names or unknown student numbers,
and output for each tutor the set of groups,
and for each group the set of tutors.

Mathias Rav, February 2015.
"""



import os
import sys
import collections

import codecs
sys.stdin = codecs.getreader('utf8')(sys.stdin)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

from mftutor.tutor.models import *

lines = [line.strip().split('\t') for line in sys.stdin][1:]
studentnumbers = [line[0] for line in lines]

profiles = dict([
    (tp.studentnumber, tp)
    for tp in TutorProfile.objects.filter(studentnumber__in=studentnumbers)
])

def first_last(s):
    s = s.lower()
    return s.split(' ', 1)[0], s.rsplit(' ', 1)[-1]

print("Weird names:")
for studentnumber, name in lines:
    try:
        tp = profiles[studentnumber]
    except KeyError:
        continue

    if first_last(tp.name) != first_last(name):
        print("%-30s%-30s%s" % (studentnumber, tp.name, name))
print('')

print("Unknown studentnumbers:")
for studentnumber, name in lines:
    if studentnumber not in profiles.keys():
        print("Not found: %s %s" % (studentnumber, name))
        last = first_last(name)[1]
        print("Did you mean (by studentnumber): %s" %
              ', '.join('%s %s' % (tp.studentnumber, tp.name)
                        for tp in TutorProfile.objects.filter(
                            studentnumber__contains=studentnumber[-4:])))
        print("Did you mean (by last name): %s" %
              ', '.join('%s %s' % (tp.studentnumber, tp.name)
                        for tp in TutorProfile.objects.filter(
                            name__icontains=last)))
print('')

groups = collections.defaultdict(lambda: [])
tutor_years = {}
for studentnumber, name in sorted(lines, key=lambda x: x[1]):
    try:
        tp = profiles[studentnumber]
    except KeyError:
        continue

    tutor_years[studentnumber] = [tutor.year for tutor in tp.tutor_set.all()]
    gr = []
    for tutor in tp.tutor_set.all():
        for group in tutor.groups.all():
            if group.handle in 'alle best koor'.split() or not group.visible:
                continue
            try:
                gl = TutorGroupLeader.objects.get(tutor=tutor, group=group)
            except TutorGroupLeader.DoesNotExist:
                gl = None
            groups[group.name].append((tutor, gl))
            gr.append('%s%s (%s)' % ('*' if gl else '', group.name, tutor.year))
    if gr:
        print('%s: %s' % (name, ', '.join(gr)))
print('')

for name, members in sorted(groups.items(), key=lambda x: x[0]):
    tutors = collections.defaultdict(lambda: [])
    for tutor, gl in members:
        tutors[tutor.profile.studentnumber].append(
            '%s%s' %
            ('*' if gl else '', tutor.year))
    print('%s:' % (name,))
    for studentnumber, years in sorted(tutors.items(), key=lambda x: profiles[x[0]].name):
        name = profiles[studentnumber].name
        y = tutor_years[studentnumber]
        print('[%d] %s (%s)' % (len(y), name, ', '.join(years)))
    print('')
