# Used to transition old mysql db to new django app

use warnings;
use strict;

my $year = $ARGV[0] or die "Usage: $0 year";
my $MYSQL = 'mysql --defaults-extra-file=~/tutordb.cnf';
my $fromgroup = 'alle';

print <<PYTHON;
from activation.models import *
from tutor.models import *
from django.contrib.auth.models import User

def mk_tutor(first_name, last_name, email, street, city, phone, study, studentnumber, year=None):
    gender = 'm'
    try:
        tp = TutorProfile.objects.get(studentnumber=studentnumber)
        #tp.street = street
        #tp.city = city
        #tp.phone = phone
        #tp.study = study
        #tp.studentnumber = studentnumber
        #tp.save()
        #ta = ProfileActivation.objects.get(profile=tp)
        #ta.first_name = first_name
        #ta.last_name = last_name
        #ta.email = email
    except TutorProfile.DoesNotExist:
        tp = TutorProfile(street=street, city=city, phone=phone, study=study, studentnumber=studentnumber, gender=gender)
        tp.save()
        ta = ProfileActivation(profile=tp, first_name=first_name, last_name=last_name, email=email)
        ta.save()
    if year is not None:
        tu = Tutor(year=year, profile=tp)
        tu.save()
        return tu
    else:
        return None

groups = {}

def mk_group(handle, name, visible):
    try:
        return TutorGroup.objects.get(handle=handle)
    except TutorGroup.DoesNotExist:
        g = TutorGroup(handle=handle, name=name, visible=visible)
        g.save()
        return g

PYTHON

sub sql {
	return "echo '$_[0]' |
	$MYSQL |"
}

my $WHEREmailalias = " (mailalias NOT LIKE \"\%+\%\" AND mailalias NOT LIKE \"\%-\%\")";

open GROUPS, sql("SELECT mailalias, navn, visible FROM ${year}_groups WHERE $WHEREmailalias ORDER BY visible DESC, mailalias ASC");

my @groups = ();

<GROUPS>;
while (<GROUPS>) {
	my ($mailalias, $navn, $visible) = /([^\t]+)/g;
	if ($visible == 1) { $visible = 'True'; } else { $visible = 'False'; }
	print "tutorgroup_$mailalias = mk_group(handle='$mailalias', name='$navn', visible=$visible)\n";
        push @groups, $mailalias;
}
close GROUPS;

print "\n";

open TUTORS, sql("SELECT tutorid, navn, email, gade, postby, mobil, studret, aarskort FROM ${year}_tutors WHERE tutorid IN (SELECT tutorid FROM ${year}_tutorInGroup WHERE mailalias = \"$fromgroup\") ORDER BY tutorid ASC");
<TUTORS>;
while (<TUTORS>) {
	s/([\\'])/\\$1/g;
        s/\n//;
	my ($tutorid, $navn, $email, $gade, $postby, $mobil, $studret, $aarskort) = split /\t/;
	my ($first, $last) = ($navn =~ /([^ ]*) (.*)/);
        if ($email !~ /@/) {
            print "# XXX invalid email?\n";
        }
        if ($aarskort !~ /^\d+$/) {
            print "# XXX invalid student number?\n";
        }

        print "tu$tutorid = mk_tutor(street='$gade', city='$postby', phone='$mobil', study='$studret', studentnumber='$aarskort', email='$email', first_name='$first', last_name='$last')\n";
}
close TUTORS;

print "\n";

open TUTORGROUPS, sql("SELECT tutorid, mailalias FROM ${year}_tutorInGroup WHERE tutorid IN (SELECT tutorid FROM ${year}_tutorInGroup WHERE mailalias = \"$fromgroup\") AND $WHEREmailalias AND mailalias IN (SELECT mailalias FROM ${year}_groups) AND tutorid IN (SELECT tutorid FROM ${year}_tutors) ORDER BY mailalias ASC");
<TUTORGROUPS>;
while (<TUTORGROUPS>) {
	my ($tutorid, $mailalias) = /([^\t\n]+)/g;
	print "tu$tutorid.groups.add(tutorgroup_$mailalias)\n";
}
close TUTORGROUPS;

open RUSSES, sql("SELECT r.navn, r.email, r.gade, r.postby, r.telefon, c.navn, r.aarskort from ${year}_russes r, ${year}_rusClasses c where r.Hold_ID = c.Hold_ID and aarskort <> \"\" order by r.navn asc");
<RUSSES>;
while (<RUSSES>) {
	s/([\\'])/\\$1/g;
        s/\n//;
	my ($tutorid, $navn, $email, $gade, $postby, $mobil, $studret, $aarskort) = split /\t/;
	my ($first, $last) = ($navn =~ /([^ ]*) (.*)/);
        if ($email !~ /@/) {
            print "# XXX invalid email?\n";
        }
        if ($aarskort !~ /^\d+$/) {
            print "# XXX invalid student number?\n";
        }

        print "mk_tutor(street='$gade', city='$postby', phone='$mobil', study='$studret', studentnumber='$aarskort', email='$email', first_name='$first', last_name='$last')\n";
}
close RUSSES;
