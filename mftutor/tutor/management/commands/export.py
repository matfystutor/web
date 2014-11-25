import sys
import json
import datetime

from optparse import make_option
from django.core.management.base import BaseCommand

from mftutor.tutor.models import (
    TutorProfile, Tutor, Rus, RusClass,
    TutorGroup, TutorGroupLeader,
)


def get_timestamp(dt):
    tz = dt.tzinfo
    epoch = dt - datetime.datetime(1970, 1, 1, tzinfo=tz)
    total_seconds = (epoch.seconds +
                     epoch.microseconds / 1e6 +
                     epoch.days * (3600 * 24))
    return total_seconds


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

    def handle(self, filename, **kwargs):
        qs = TutorProfile.objects.all().select_related(
            'tutor__groups', 'rus__rusclass')
        count = qs.count()

        with open(filename, 'w') as fp:
            fp.write('[\n')
            comma = ''
            for i, tp in enumerate(qs):
                sys.stdout.write((u'\r\033[K[%4d/%4d] %s' %
                                  (i + 1, count, tp.name)).encode('utf8'))
                sys.stdout.flush()
                fp.write(comma)
                comma = ',\n'

                json.dump(self.dump_tutorprofile(tp), fp, indent=0)
            fp.write(']\n')
            print('')
