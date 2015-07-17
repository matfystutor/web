import os
import os.path
import re
import sys
import json
import time
import tarfile
import datetime

from optparse import make_option
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import django.core.files

from mftutor.tutor.models import (
    TutorProfile, Tutor, Rus, RusClass, TutorGroup,
)

from mftutor.documents.models import Document
from mftutor.aliases.models import Alias


def from_timestamp(total_seconds):
    return datetime.datetime.fromtimestamp(total_seconds)


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

    def load_basic(self, cls, obj, keys):
        data = {k: obj[k] for k in keys}
        return cls(**data)

    def load_rusclass(self, rcdata):
        if rcdata is None:
            return None

        key = (rcdata['year'], rcdata['handle'])
        try:
            return self.rusclasses[key]
        except KeyError:
            rc = self.load_basic(
                RusClass, rcdata,
                'handle official_name internal_name year'.split())
            rc.save()
            self.rusclasses[key] = rc
            return rc

    def load_tutorgroup(self, groupdata):
        key = groupdata['handle']
        try:
            return self.groups[key]
        except KeyError:
            tg = self.load_basic(
                TutorGroup, groupdata,
                'visible handle name'.split())
            tg.save()
            self.groups[key] = tg
            return tg

    def load_tutorprofile(self, tpdata):
        tp = self.load_basic(
            TutorProfile, tpdata,
            'name street city phone email study studentnumber gender'
            .split())

        try:
            user = self.users[tpdata['username']]
        except KeyError:
            user = self.load_basic(
                User, tpdata, 'username password'.split())
            try:
                user.first_name, user.last_name = tpdata['name'].split(' ', 1)
            except ValueError:
                user.first_name, user.last_name = tpdata['name'], ''
            user.save()

        tp.user = user
        tp.save()

        for tudata in tpdata['tutor']:
            tu = self.load_basic(Tutor, tudata, ['year'])
            tu.profile = tp
            tu.rusclass = self.load_rusclass(tudata['rusclass'])
            early_termination = tudata.get('early_termination')
            if early_termination is not None:
                tu.early_termination = (
                    from_timestamp(early_termination['date']))
                tu.early_termination_reason = early_termination['reason']
            tu.save()

            for groupdata in tudata['groups']:
                tu.groups.add(self.load_tutorgroup(groupdata))

            for groupdata in tudata['groupleader']:
                gr = self.load_tutorgroup(groupdata)
                gr.leader = tu
                gr.save()

        for rusdata in tpdata['rus']:
            rus = self.load_basic(Rus, rusdata, 'arrived year'.split())
            rus.profile = tp
            rus.rusclass = self.load_rusclass(rusdata['rusclass'])
            rus.initial_rusclass = self.load_rusclass(
                rusdata['initial_rusclass'])
            rus.save()

    def handle(self, *args, **kwargs):
        fp = tarfile.open(kwargs.pop('filename'), 'r')
        ti = fp.next()
        dirname = re.sub(r'/.*', '', ti.name)
        f = fp.extractfile('%s/tutorprofiles.json' % dirname)
        try:
            tutorprofiles = json.load(f)
        finally:
            f.close()
        self.load_tutorprofiles(tutorprofiles)

        f = fp.extractfile('%s/documents.json' % dirname)
        try:
            documents = json.load(f)
        finally:
            f.close()
        self.load_documents(documents)

        f = fp.extractfile('%s/aliases.json' % dirname)
        try:
            aliases = json.load(f)
        finally:
            f.close()
        self.load_aliases(aliases)

        members = fp.getmembers()
        pi = ProgressIndicator(len(members))
        skipped = loaded = 0
        for ti in members:
            pi.step(ti.name)
            if not ti.name.startswith('%s/' % dirname):
                continue
            name = ti.name[(len(dirname) + 1):]

            try:
                head, tail = name.split('/', 1)
            except ValueError:
                continue

            if head == 'pictures':
                self.load_picture(fp.extractfile(ti), tail)
                loaded += 1
            elif head == 'documents':
                self.load_document(fp.extractfile(ti), tail)
                loaded += 1
            else:
                skipped += 1
        pi.done()
        print("Skipped %d, loaded %d" % (skipped, loaded))

    def load_tutorprofiles(self, data):
        studentnumbers = [tp['studentnumber'] for tp in data]
        usernames = [tp['username'] for tp in data]

        chunksize = 500
        chunks = int((len(studentnumbers) + chunksize - 1) / chunksize)
        # Maps studentnumber to TutorProfile
        self.tutorprofiles = dict(
            (tp.studentnumber, tp)
            for chunk in range(chunks)
            for tp in TutorProfile.objects.filter(
                studentnumber__in=studentnumbers[
                    (chunk * chunksize):((chunk + 1) * chunksize)])
        )

        # Maps username to User
        chunks = int((len(usernames) + chunksize - 1) / chunksize)
        self.users = dict(
            (user.username, user)
            for chunk in range(chunks)
            for user in User.objects.filter(
                username__in=usernames[
                    (chunk * chunksize):((chunk + 1) * chunksize)])
        )

        group_keys = sorted(set(
            group['handle']
            for tp in data
            for tutor in tp['tutor']
            for groupset in [tutor['groups'], tutor['groupleader']]
            for group in groupset
        ))
        # Maps handle to TutorGroup
        self.groups = dict(
            (group.handle, group)
            for group in TutorGroup.objects.filter(handle__in=group_keys)
        )

        rusclass_keys = []
        for tp in data:
            for tudata in tp['tutor']:
                rusclass = tudata['rusclass']
                if rusclass:
                    rusclass_keys.append(
                        (rusclass['year'], rusclass['handle']))
            for rusdata in tp['rus']:
                rusclass = rusdata['rusclass']
                if rusclass:
                    rusclass_keys.append(
                        (rusclass['year'], rusclass['handle']))

        rusclass_years = sorted(set(year for year, handle in rusclass_keys))
        rusclass_byyear = [
            (year,
             [handle for year_, handle in rusclass_keys if year == year_])
            for year in rusclass_years
        ]
        # Maps (year, handle) to RusClass
        self.rusclasses = dict(
            ((year, rusclass.handle), rusclass)
            for year, handles in rusclass_byyear
            for rusclass in RusClass.objects.filter(
                year=year, handle__in=handles)
        )

        skipped = loaded = 0
        count = len(data)
        pi = ProgressIndicator(count)
        for i, tpdata in enumerate(data):
            pi.step(tpdata['name'])

            if tpdata['studentnumber'] in self.tutorprofiles:
                skipped += 1
            else:
                self.tutorprofiles[tpdata['studentnumber']] = (
                    self.load_tutorprofile(tpdata))
                loaded += 1
        pi.done()
        print("Skipped %d, loaded %d" % (skipped, loaded))

    def load_documents(self, documents):
        skipped = loaded = 0
        pi = ProgressIndicator(len(documents))
        for document in documents:
            pi.step(document['title'])
            doc = self.load_basic(
                Document, document, 'title year type'.split())
            doc.published = datetime.date.fromtimestamp(
                document['published'])
            doc.time_of_upload = datetime.datetime.fromtimestamp(
                document['time_of_upload'])
            doc.doc_file = doc.doc_upload_to(document['doc_file'])
            if Document.objects.filter(doc_file=doc.doc_file).exists():
                skipped += 1
            else:
                loaded += 1
                doc.save()
        pi.done()
        print("Skipped %d, loaded %d" % (skipped, loaded))

    def load_aliases(self, aliases):
        existing = set(
            (a.source, a.destination)
            for a in Alias.objects.all()
        )
        aliases = set(
            (a['source'], a['destination'])
            for a in aliases
        )
        new = aliases - existing
        pi = ProgressIndicator(len(new))
        for a in new:
            pi.step('%s -> %s' % a)
            Alias(source=a[0], destination=a[1]).save()
        pi.done()
        print("Loaded %d out of %d" % (len(new), len(aliases)))

    def load_picture(self, fp, filename):
        studentnumber, extension = os.path.splitext(filename)
        tp = TutorProfile.objects.get(studentnumber=studentnumber)
        tp.picture.save(filename, django.core.files.File(fp))

    def load_document(self, fp, path):
        year, type_, filename = path.split('/')
        doc = Document.objects.get(
            doc_file=Document(year=year, type=type_).doc_upload_to(filename))
        doc.doc_file.save(filename, django.core.files.File(fp))
