use warnings;
use strict;

my $year = 2012;
my $MYSQL = 'mysql --defaults-extra-file=~/tutordb.cnf';
my $fromgroup = 'web'; # 'alle'

print "from tutor.models import *\n";

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
#	| navn         | varchar(40)           | YES  |     | NULL    |                |
#	| gade         | varchar(60)           | YES  |     | NULL    |                |
#	| postby       | varchar(25)           | YES  |     | NULL    |                |
#	| mobil        | varchar(30)           | YES  |     | NULL    |                |
#	| email        | varchar(127)          | YES  |     | NULL    |                |
#	| studret      | varchar(30)           | YES  |     | NULL    |                |
#	| yat          | int(11)               | YES  |     | NULL    |                |
#	| fsy          | int(11)               | YES  |     | NULL    |                |
#	| password     | varchar(32)           | NO   |     |         |                |
#	| Hold_ID      | int(11)               | YES  |     | 0       |                |
#	| allemail     | tinyint(4)            | NO   |     | 1       |                |
#	| aarskort     | int(8)                | YES  |     | 0       |                |
#	| birthday     | date                  | YES  |     | NULL    |                |
#	| addGroupName | enum('y','n')         | NO   |     | n       |                |
#	| gender       | enum('male','female') | YES  | MUL | NULL    |                |
<TUTORS>;
while (<TUTORS>) {
	my ($tutorid, $navn, $email, $gade, $postby, $mobil, $studret, $aarskort) = /([^\t\n]+)/g;
	my ($first, $last) = ($navn =~ /([^ ]*) (.*)/);
	print "u$tutorid = User(username='$aarskort', first_name='$first', last_name='$last',\n";
	print "	email='$email')\n";
	print "u$tutorid.set_password('$aarskort')\nu$tutorid.save()\n";
	print "tp$tutorid = TutorProfile(user=u$tutorid, street='$gade', city='$postby', phone='$mobil', study='$studret', studentnumber='$aarskort', gender='m')\n";
	print "tp$tutorid.save()\n";
	print "tu$tutorid = Tutor(profile=tp$tutorid, year=$year)\ntu$tutorid.save()\n";
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
