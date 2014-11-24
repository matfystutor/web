import sys
import json
import datetime

from optparse import make_option
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from mftutor.tutor.models import (
    TutorProfile, Tutor, Rus, RusClass,
    TutorGroup, TutorGroupLeader,
)


def from_timestamp(total_seconds):
    return datetime.datetime.fromtimestamp(total_seconds)


class Command(BaseCommand):
    can_import_settings = True
    option_list = BaseCommand.option_list + (
        make_option('--filename',
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
            rc = self.load_basic(RusClass, rcdata,
                            'handle official_name internal_name year'.split())
            rc.save()
            self.rusclasses[key] = rc
            return rc

    def load_tutorgroup(self, groupdata):
        key = groupdata['handle']
        try:
            return self.groups[key]
        except KeyError:
            tg = self.load_basic(TutorGroup, groupdata,
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
                tgl = TutorGroupLeader(tutor=tu, year=tu.year, group=gr)
                tgl.save()

        for rusdata in tpdata['rus']:
            rus = self.load_basic(Rus, rusdata, 'arrived year'.split())
            rus.profile = tp
            rus.rusclass = self.load_rusclass(rusdata['rusclass'])
            rus.initial_rusclass = self.load_rusclass(rusdata['initial_rusclass'])
            rus.save()

    def handle(self, *args, **kwargs):
        with open(kwargs.pop('filename')) as fp:
            data = json.load(fp)

        studentnumbers = [tp['studentnumber'] for tp in data]
        usernames = [tp['username'] for tp in data]

        chunksize = 500
        # Maps studentnumber to TutorProfile
        self.tutorprofiles = dict(
            (tp.studentnumber, tp)
            for chunk in range(int((len(studentnumbers) + chunksize - 1) / chunksize))
            for tp in TutorProfile.objects.filter(
                studentnumber__in=studentnumbers[chunk * chunksize : (chunk + 1) * chunksize])
        )

        # Maps username to User
        self.users = dict(
            (user.username, user)
            for chunk in range(int((len(usernames) + chunksize - 1) / chunksize))
            for tp in User.objects.filter(
                username__in=usernames[chunk * chunksize : (chunk + 1) * chunksize])
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
                    rusclass_keys.append((rusclass['year'], rusclass['handle']))
            for rusdata in tp['rus']:
                rusclass = rusdata['rusclass']
                if rusclass:
                    rusclass_keys.append((rusclass['year'], rusclass['handle']))

        rusclass_years = sorted(set(year for year, handle in rusclass_keys))
        rusclass_byyear = [
            (year, [handle for year_, handle in rusclass_keys if year == year_])
            for year in rusclass_years
        ]
        # Maps (year, handle) to RusClass
        self.rusclasses = dict(
            ((year, rusclass.handle), rusclass)
            for year, handles in rusclass_byyear
            for rusclass in RusClass.objects.filter(year=year, handle__in=handles)
        )

        count = len(data)

        loaded = skipped = 0
        for i, tpdata in enumerate(data):
            sys.stdout.write((u'\r\033[K[%4d+%4d/%4d] %s' %
                              (loaded, skipped, count, tpdata['name'])
                             ).encode('utf8'))
            sys.stdout.flush()

            if tpdata['studentnumber'] in self.tutorprofiles:
                skipped += 1
            else:
                self.tutorprofiles[tpdata['studentnumber']] = (
                    self.load_tutorprofile(tpdata))
                loaded += 1


        print('')
