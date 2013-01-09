use warnings;
use strict;

print <<PYTHON;
from tutor.models import *
from django.contrib.auth.models import User

def mk_user(username, **kwargs):
    try:
        if username == '20103940':
            username = 'rav'
        u = User.objects.get(username=username)
        return u
    except User.DoesNotExist:
        u = User(username=username, **kwargs)
        u.set_password('tutor'+username)
        u.save()
        return u

def mk_profile(user, **kwargs):
    try:
        p = TutorProfile.objects.get(user=user)
        return p
    except TutorProfile.DoesNotExist:
        p = TutorProfile(user=user, **kwargs)
        p.save()
        return p

def mk_tutor(profile, year):
    try:
        t = Tutor.objects.get(profile=profile, year=year)
        return t
    except Tutor.DoesNotExist:
        t = Tutor(profile=profile, year=year)
        t.save()
        return t

PYTHON

my $year = 2012;
my $MYSQL = 'mysql --defaults-extra-file=~/tutordb.cnf';
my $fromgroup = 'best'; # 'alle'

sub sql {
	return "echo '$_[0]' |
	$MYSQL |"
}

open GROUPS, sql("SELECT mailalias, navn, visible FROM ${year}_groups");

my @groups = ();

<GROUPS>;
while (<GROUPS>) {
	my ($mailalias, $navn, $visible) = /([^\t]+)/g;
	if ($visible == 1) { $visible = 'True'; } else { $visible = 'False'; }
	print "TutorGroup(handle='$mailalias', name='$navn', visible=$visible).save()\n";
        push @groups, $mailalias;
}
close GROUPS;

open TUTORS, sql("SELECT tutorid, navn, email, gade, postby, mobil, studret, aarskort FROM ${year}_tutors WHERE tutorid IN (SELECT tutorid FROM ${year}_tutorInGroup WHERE mailalias = \"$fromgroup\")");
<TUTORS>;
while (<TUTORS>) {
	my ($tutorid, $navn, $email, $gade, $postby, $mobil, $studret, $aarskort) = /([^\t\n]+)/g;
	my ($first, $last) = ($navn =~ /([^ ]*) (.*)/);
	print "u$tutorid = mk_user(username='$aarskort', first_name='$first', last_name='$last',\n";
	print "	email='$email')\n";
	print "tp$tutorid = mk_profile(user=u$tutorid, street='$gade', city='$postby', phone='$mobil', study='$studret', studentnumber='$aarskort', gender='m')\n";
	print "tu$tutorid = mk_tutor(profile=tp$tutorid, year=$year)\n";
}
close TUTORS;


for my $group (sort @groups) {
	print "tutorgroup_$group = TutorGroup.objects.get(handle='$group')\n";
}


open TUTORGROUPS, sql("SELECT tutorid, mailalias FROM ${year}_tutorInGroup WHERE tutorid IN (SELECT tutorid FROM ${year}_tutorInGroup WHERE mailalias = \"$fromgroup\")");
<TUTORGROUPS>;
while (<TUTORGROUPS>) {
	my ($tutorid, $mailalias) = /([^\t\n]+)/g;
	print "tu$tutorid.groups.add(tutorgroup_$mailalias)\n";
}
close TUTORGROUPS;
