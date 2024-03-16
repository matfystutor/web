import re
from django import forms
from mftutor.gallery.models import BaseMedia


class EditVisibilityForm(forms.Form):
    class Missing(Exception):
        pass

    def __init__(self, file_visibility, **kwargs):
        super(EditVisibilityForm, self).__init__(**kwargs)
        self.basemedias = []
        self.album_pks = set()
        for file in file_visibility:
            if isinstance(file, BaseMedia):
                pk = file.pk
                visibility = file.visibility
                album = file.album_id
            elif isinstance(file, tuple):
                pk, visibility, album = file
            else:
                raise TypeError(type(file))
            k = 'i%s' % pk
            self.album_pks.add(album)
            self.fields[k] = forms.ChoiceField(
                choices=BaseMedia.VISIBILITY,
                initial=visibility,
                widget=forms.RadioSelect)
            self.basemedias.append((pk, k))

    @classmethod
    def from_POST(cls, post_data):
        pattern = r'^i(\d+)$'
        pks = []
        for k, v in post_data.items():
            mo = re.match(pattern, k)
            if mo:
                pks.append(int(mo.group(1)))
        files = BaseMedia.objects.filter(pk__in=pks)
        files = list(files.values_list('pk', 'visibility', 'album_id'))
        found_pks = [f[0] for f in files]
        missing = set(pks) - set(found_pks)
        if missing:
            raise cls.Missing('Not found: %r' % (sorted(missing),))
        return cls(files, data=post_data)
