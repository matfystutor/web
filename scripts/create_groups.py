# encoding: utf8


import os
import sys

import codecs

sys.stdin = codecs.getreader('utf8')(sys.stdin)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

from mftutor.tutor.models import TutorGroup

input_string = """
buret   Buret
cs	CS-Oplæg
eval	Evaluering
gruppeansvarlige	Gruppeansvarlige
hytte	Hytte
hoestfest	Høstfest
labfys	IFA-Labrundvisning
labnano	iNANO-labrundvisning
indkoeb	Indkøb og bus
korrektur	Korrektur
latech	LaTeCh Support
legedag	Legegruppen
parxafari	ParXafari
grise	Praktiske Grise
rkfw	RKFW og Rus2tursguide
rusrevy	Rusrevy
sol	SOL
sportsdag	Sportsdag
tutorfest	Tutorfest
tutorsmiley	Tutorsmiley
dattoe	TØ i rusdagene - datalogi
fystoe	TØ i rusdagene - fysik
nanotoe	TØ i rusdagene - nano
"""
year = 2025
qs = TutorGroup.objects.filter(year=year)
existing_handles = set(g.handle for g in qs)
for line in input_string.splitlines():
    handle, name = line.split('\t')
    if handle not in existing_handles:
        print(name)
        tg = TutorGroup(handle=handle, name=name, year=year)
        tg.save()

