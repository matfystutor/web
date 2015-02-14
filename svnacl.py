"""
Output ACL file for the NFIT SVN repositories
managed by Michael Glad.

Mathias Rav, 2013.
"""
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mftutor.settings'

from mftutor.tutor.models import *

bookgroupset = {'csrusbog': 'rusbog', 'ifarusbog': 'rusbog', 'matrusbog': 'rusbog', 'sangbog': 'sangbog', 'sol': 'sol', 'tutorbog': 'tutorbog', 'latex': '', 'web': ''}
for k in bookgroupset.keys():
    print '# ADMIN: rav'
    print '[tutor:/'+bookgroupset[k]+']'
    print 'tutor = rw' 
    print 'rav = rw' 
    for tu in Tutor.objects.filter(year=2013, groups__handle__exact=k).select_related('profile__user', 'profile'):
        print tu.profile.user.email+u' = rw # '+tu.profile.studentnumber+u' '+tu.profile.get_full_name()+u' ('+(u', '.join(g.handle for g in tu.groups.all()))+u')'
    print
