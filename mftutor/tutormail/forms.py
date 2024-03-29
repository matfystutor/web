# encoding: utf-8

import django
from django.forms import Form, CharField, Textarea, TextInput, ValidationError, \
    ChoiceField, BooleanField
from mftutor.settings import STUDIES


class EmailForm(Form):
    # sender = CharField()
    # to = CharField(required=False)
    # cc = CharField(required=False)
    # bcc = CharField(required=False)

    only_me = BooleanField(required=False)

    send_study = BooleanField(required=False)

    send_institute = BooleanField(required=False)

    sender_name = CharField()
    sender_email = CharField(widget=TextInput(attrs={'placeholder':'mailalias'}))

    studies = ChoiceField(
        choices=[(x, x) for x in STUDIES],
        required=False
    )

    subject = CharField()

    text = CharField(widget=Textarea)

    wrapping = ChoiceField(
        choices=[(x, x) for x in 'lines paragraphs none'.split()],
    )

    institutes = ChoiceField(
        choices=[(x, x) for x in ['', 'Datalogi', 'IFA', 'IMF']],
        required=False
    )

    # def clean(self):
    #     cleaned_data = super(EmailForm, self).clean()
    #     to = cleaned_data.get('to')
    #     cc = cleaned_data.get('cc')
    #     bcc = cleaned_data.get('bcc')

    #     if not to and not cc and not bcc:
    #         msg = u"Du skal angive en modtager."
    #         if django.VERSION >= (1, 7):
    #             self.add_error('to', msg)
    #         else:
    #             raise ValidationError(msg)

    #     return cleaned_data
