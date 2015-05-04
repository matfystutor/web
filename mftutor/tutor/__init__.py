# coding: utf-8
def tutorpicture_upload_to(instance, filename):
    extension = re.sub(r'^.*\.', '', filename)
    return 'tutorpics/%s.%s' % (instance.studentnumber, extension)
