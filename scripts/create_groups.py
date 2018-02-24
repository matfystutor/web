# encoding: utf8


import os
import sys

import codecs

sys.stdin = codecs.getreader('utf8')(sys.stdin)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

from mftutor.tutor.models import TutorGroup

input_string = """arbejdstutor	Arbejdstutor
cslab	CS-labrundvisning
csdias	Dias - CS
ifadias	Dias - IFA
imfdias	Dias - IMF
eval	Evaluering
form	Formand
gruppeansvarlige	Gruppeansvarlige
guide	Guide
holdetstime	Holdets time
hytte	Hytte
hoestfest	Høstfest
ifalab	IFA-Labrundvisning
nanolab	iNANO-labrundvisning
inko	Indkøb
korrektur	Korrektur
latex	LaTeX
legebog	Legebog
lokale	Lokale
parxafari	ParXafari
grise	Praktiske Grise
rkfl3	RKFL^3
rkfw	RKFW
rus2turguide	Rus2Turs-guide
rusguide	Rusguide
rusteater	Rusteater
sangbog	Sangbog
sol	SOL
sponsor	Sponsor
sportsdag	Sportsdag
texmaster	TeX Master
tutorbog	Tutorbog
tutorfest	Tutorfest
tutorsmiley	Tutorsmiley
datalogitoe	TØ i rusdagene - datalogi
toefysik	TØ i rusdagene - fysik
toematoek	TØ i rusdagene - mat/øk
toemat	TØ i rusdagene - matematik
toenano	TØ i rusdagene - nano
web	Web
hacker	Wiki"""
year = 2017
qs = TutorGroup.objects.filter(year=year)
existing_handles = set(g.handle for g in qs)
for line in input_string.splitlines():
    handle, name = line.split('\t')
    if handle not in existing_handles:
        print(name)
        tg = TutorGroup(handle=handle, name=name, year=year)
        tg.save()

