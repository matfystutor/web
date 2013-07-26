from ..tutor.auth import user_rus_data, NotTutor

def rus_data(request):
    try:
        d = user_rus_data(request.user)
    except NotTutor:
        return {}
    return {'rus': d.rus, 'profile': d.profile}
