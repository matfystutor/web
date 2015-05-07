# coding: utf-8

import re


def tutorpicture_upload_to(instance, filename):
    extension = re.sub(r'^.*\.', '', filename)
    return 'tutorpics/%s.%s' % (instance.studentnumber, extension)
