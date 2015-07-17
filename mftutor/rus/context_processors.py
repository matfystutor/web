def rus_data(request):
    if request.rus:
        return {'rus': request.rus, 'profile': request.tutorprofile}
    else:
        return {}
