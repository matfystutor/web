use warnings;
use strict;

my $year = $ARGV[0] or die "Usage: $0 year";
my $MYSQL = 'mysql --defaults-extra-file=~/tutordb.cnf';
my $fromgroup = 'best';

print <<PYTHON;
from tutor.models import *
from django.contrib.auth.models import User

def mk_profile(studentnumber, **kwargs):
    try:
        p = TutorProfile.objects.get(studentnumber=studentnumber)
        return p
    except TutorProfile.DoesNotExist:
        p = TutorProfile(studentnumber=studentnumber, **kwargs)
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

def mk_group(handle, name, visible):
    try:
        g = TutorGroup.objects.get(handle=handle)
    except TutorGroup.DoesNotExist:
        TutorGroup(handle=handle, name=name, visible=visible).save()

PYTHON

sub sql {
	return "echo '$_[0]' |
	$MYSQL |"
}

my $WHEREmailalias = " (mailalias NOT LIKE \"\%+\%\" AND mailalias NOT LIKE \"\%-\%\")";

open GROUPS, sql("SELECT mailalias, navn, visible FROM ${year}_groups WHERE $WHEREmailalias");

my @groups = ();

<GROUPS>;
while (<GROUPS>) {
	my ($mailalias, $navn, $visible) = /([^\t]+)/g;
	if ($visible == 1) { $visible = 'True'; } else { $visible = 'False'; }
	print "mk_group(handle='$mailalias', name='$navn', visible=$visible)\n";
        push @groups, $mailalias;
}
close GROUPS;

print "\n";

open TUTORS, sql("SELECT tutorid, navn, email, gade, postby, mobil, studret, aarskort FROM ${year}_tutors WHERE tutorid IN (SELECT tutorid FROM ${year}_tutorInGroup WHERE mailalias = \"$fromgroup\")");
<TUTORS>;
while (<TUTORS>) {
	s/([\\'])/\\$1/g;
	my ($tutorid, $navn, $email, $gade, $postby, $mobil, $studret, $aarskort) = split /[\t\n]+/;
	my ($first, $last) = ($navn =~ /([^ ]*) (.*)/);
	print "tp$tutorid = mk_profile(street='$gade', city='$postby', phone='$mobil', study='$studret', studentnumber='$aarskort', gender='m', activation_email='$email')\n";
	print "tu$tutorid = mk_tutor(profile=tp$tutorid, year=$year)\n";
}
close TUTORS;

print "\n";

for my $group (sort @groups) {
	print "tutorgroup_$group = TutorGroup.objects.get(handle='$group')\n";
}

print "\n";

open TUTORGROUPS, sql("SELECT tutorid, mailalias FROM ${year}_tutorInGroup WHERE tutorid IN (SELECT tutorid FROM ${year}_tutorInGroup WHERE mailalias = \"$fromgroup\") AND $WHEREmailalias");
<TUTORGROUPS>;
while (<TUTORGROUPS>) {
	my ($tutorid, $mailalias) = /([^\t\n]+)/g;
	print "tu$tutorid.groups.add(tutorgroup_$mailalias)\n";
}
close TUTORGROUPS;
