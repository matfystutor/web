from django import forms
from django.contrib.auth.models import User
from ..settings import TIDY_NEWS_HTML
from .models import NewsPost


class AuthorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = ('author', 'title', 'posted', 'body', 'group_handle')

    def __init__(self, **kwargs):
        year = kwargs.pop('year')
        super(NewsPostForm, self).__init__(**kwargs)
        author_field = self.fields['author']
        author_field.queryset = author_field.queryset.filter(
            tutorprofile__tutor__year__in=[year])

    author = AuthorModelChoiceField(
        label = 'Forfatter',
        empty_label = None,
        queryset = User.objects.filter(tutorprofile__tutor__groups__handle='best'))

    def clean_body(self):
        data = self.cleaned_data['body']

        if not TIDY_NEWS_HTML:
            return data

        from subprocess import Popen, PIPE
        p = Popen(
            ["tidy", "-utf8", "--bare", "yes",
                "--show-body-only", "yes", "-q",
                "--show-warnings", "no",
                "--enclose-block-text", "yes"],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            close_fds=True)

        p.stdin.write(data.encode('utf8'))
        p.stdin.close()
        tidied = p.stdout.read()
        errors = p.stderr.read()

        if errors:
            raise forms.ValidationError(errors)

        if not tidied:
            raise forms.ValidationError("Empty body")

        return tidied
