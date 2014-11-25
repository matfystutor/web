import os
import os.path
import sys
import json
import time
import shutil
import tarfile
import datetime

from optparse import make_option
from django.core.management.base import BaseCommand

from mftutor.tutor.models import (
    TutorProfile, Tutor, Rus, RusClass,
    TutorGroup, TutorGroupLeader,
)
from mftutor.documents.models import Document
from mftutor.aliases.models import Alias


def get_timestamp(dt):
    if isinstance(dt, datetime.datetime):
        tz = dt.tzinfo
        epoch = dt - datetime.datetime(1970, 1, 1, tzinfo=tz)
    else:
        epoch = dt - datetime.date(1970, 1, 1)

    total_seconds = (epoch.seconds +
                     epoch.microseconds / 1e6 +
                     epoch.days * (3600 * 24))
    return total_seconds


class ProgressIndicator(object):
    def __init__(self, steps):
        self.steps = 0
        self.total = steps
        self.t0 = time.time()

    def step(self, line):
        self.steps += 1
        sys.stdout.write((u'\r\033[K[%4d/%4d] %s' %
                          (self.steps, self.total, line)).encode('utf8'))
        sys.stdout.flush()

    def done(self):
        elapsed = time.time() - self.t0
        print(u'\r\033[K[%4d/%4d] In %s' % (self.total, self.total, elapsed))


class Command(BaseCommand):
    can_import_settings = True
    option_list = BaseCommand.option_list + (
        make_option(
            '--filename',
            dest='filename',
            default='mftutorexport.json'),
    )

    def dump_basic(self, obj, keys):
        return dict((k, getattr(obj, k)) for k in keys)

    def dump_rusclass(self, rc):
        if rc is None:
            return None
        else:
            return self.dump_basic(
                rc, 'year handle internal_name official_name'.split())

    def dump_group(self, grp):
        return self.dump_basic(
            grp, 'handle name visible'.split())

    def dump_tutorprofile(self, tp):
        o = self.dump_basic(
            tp,
            'name street city phone email study studentnumber gender'.split()
        )

        o['tutor'] = []
        o['rus'] = []
        o['username'] = tp.user.username
        o['password'] = tp.user.password

        for tu in tp.tutor_set.all():
            early_termination = None
            if tu.early_termination:
                early_termination = {
                    'date': get_timestamp(tu.early_termination),
                    'reason': tu.early_termination_reason,
                }

            a = {
                'year': tu.year,
                'early_termination': early_termination,
                'rusclass': self.dump_rusclass(tu.rusclass),
                'groups': [
                    self.dump_group(gr)
                    for gr in sorted(tu.groups.all(), key=lambda o: o.handle)],
                'groupleader': [
                    self.dump_group(tgl.group)
                    for tgl in sorted(tu.tutorgroupleader_set.all(), key=lambda o: o.group.handle)],
            }
            o['tutor'].append(a)

        for rus in tp.rus_set.all():
            a = {
                'year': rus.year,
                'rusclass': self.dump_rusclass(rus.rusclass),
                'arrived': rus.arrived,
                'initial_rusclass': self.dump_rusclass(rus.initial_rusclass),
            }
            o['rus'].append(a)

        return o

    def dump_tutorprofiles(self, fp):
        qs = TutorProfile.objects.all().prefetch_related(
            'tutor_set__groups', 'rus_set__rusclass',
            'tutor_set__tutorgroupleader_set', 'user')
        pi = ProgressIndicator(qs.count())
        fp.write('[\n')
        comma = ''
        for i, tp in enumerate(qs):
            pi.step(tp.name)
            fp.write(comma)
            comma = ',\n'

            json.dump(self.dump_tutorprofile(tp), fp, indent=0)
        fp.write(']\n')
        pi.done()

    def add_pictures(self, dirname, fp):
        qs = TutorProfile.objects.exclude(picture='')
        pi = ProgressIndicator(qs.count())
        for tp in qs:
            pi.step(tp.picture.name)
            tp.picture.open()
            ti = fp.gettarinfo(fileobj=tp.picture.file)
            root, ext = os.path.splitext(tp.picture.file.name)
            ti.name = os.path.join(
                dirname, 'pictures', '%s%s' % (tp.studentnumber, ext))
            fp.addfile(ti, fileobj=tp.picture.file)
            tp.picture.close()
        pi.done()

    def dump_documents(self, fp):
        qs = Document.objects.all()
        pi = ProgressIndicator(qs.count())
        documents = []
        for doc in Document.objects.all():
            pi.step(doc.title)
            o = self.dump_basic(
                doc, 'title year type'.split())
            o['published'] = get_timestamp(doc.published)
            o['time_of_upload'] = get_timestamp(doc.time_of_upload)
            head, tail = os.path.split(doc.doc_file.name)
            o['doc_file'] = tail
            documents.append(o)
        json.dump(documents, fp, indent=0)
        pi.done()

    def add_documents(self, dirname, fp):
        qs = Document.objects.all()
        pi = ProgressIndicator(qs.count())
        for doc in Document.objects.all():
            pi.step(doc.doc_file.name)
            head, tail = os.path.split(doc.doc_file.name)
            doc.doc_file.open()
            ti = fp.gettarinfo(fileobj=doc.doc_file.file)
            ti.name = os.path.join(
                dirname, 'documents', str(doc.year), doc.type, tail)
            fp.addfile(ti, fileobj=doc.doc_file.file)
            doc.doc_file.close()
        pi.done()

    def dump_aliases(self, fp):
        aliases = [
            self.dump_basic(alias, 'source destination'.split())
            for alias in Aliases.objects.all()
        ]
        json.dump(aliases, fp, indent=0)

    def handle(self, filename, **kwargs):
        dirname = datetime.datetime.now().strftime('mftutor%Y%m%d%H%M%S')

        os.mkdir(dirname)

        with open(os.path.join(dirname, 'tutorprofiles.json'), 'w') as fp:
            self.dump_tutorprofiles(fp)

        with open(os.path.join(dirname, 'documents.json'), 'w') as fp:
            self.dump_documents(fp)

        with open(os.path.join(dirname, 'aliases.json'), 'w') as fp:
            self.dump_aliases(fp)

        if filename.endswith('gz'):
            mode = 'w:gz'
        elif filename.endswith('bz2'):
            mode = 'w:bz2'
        else:
            mode = 'w:'

        fp = tarfile.open(filename, mode)
        try:
            fp.add(os.path.join(dirname, 'tutorprofiles.json'))
            fp.add(os.path.join(dirname, 'documents.json'))
            self.add_pictures(dirname, fp)
            self.add_documents(dirname, fp)
        finally:
            fp.close()
        shutil.rmtree(dirname)
