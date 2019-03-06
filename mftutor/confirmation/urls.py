from django.urls import path

from mftutor.tutor.auth import tutorbest_required
from .views import OwnConfirmationView, ConfirmationTableView, EditNoteView, ConfirmationCardView, ReminderEmailView

urlpatterns = [
    path('', OwnConfirmationView.as_view(), name='own_confirmation'),
    path('table/', tutorbest_required(ConfirmationTableView.as_view()), name='confirmation_table'),
    path('card/', tutorbest_required(ConfirmationCardView.as_view()), name='confirmation_card'),
    path('editnote/', EditNoteView.as_view(), name='confirmation_edit_note'),
    path('reminder/',
         tutorbest_required(ReminderEmailView.as_view()),
         name="confirmation_reminder"),
]
