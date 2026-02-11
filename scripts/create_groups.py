# encoding: utf8


import os
import sys

import codecs

sys.stdin = codecs.getreader('utf8')(sys.stdin)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

from mftutor.tutor.models import TutorGroup

input_string = """
gruppeansvarlige	Gruppeansvarlige
buret   Buret
cs	CS-Oplæg
eval	Evaluering
hytte	Hytte
hoestfest	Høstfest
indkoeb	Indkøb og bus
korrektur	Korrektur
labfys	IFA-Labrundvisning
labnano	iNANO-labrundvisning
latex	LaTeX-Git Support
web Web
legedag	Legegruppen
parxafari	ParXafari
grise	Praktiske Grise
rkfw	RKFW og Rus2tursguide
rusrevy	Rusrevy
tutorsmiley	Tutorsmiley
sol	SOL
sportsdag	Sportsdagsgruppen
tutorfest	Tutorfest
sangbog Sangbog
tutorbog    Tutorbog
"""
year = 2026
qs = TutorGroup.objects.filter(year=year)
existing_handles = set(g.handle for g in qs)
for line in input_string.splitlines():
    handle, name = line.split('\t')
    if handle not in existing_handles:
        print(name)
        tg = TutorGroup(handle=handle, name=name, year=year)
        tg.save()

