from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import *

urlpatterns = [
    path('', login_required(AliasesView.as_view()), name='aliases'),
]
