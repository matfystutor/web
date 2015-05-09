from __future__ import unicode_literals

from django import forms


class SignupImportForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
