import random
from typing import List

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from django import forms
from mftutor.gf.models import BallotLink
from mftutor.tutor.models import Tutor, TutorProfile


class BallotList(TemplateView):
    template_name = "mftutor/gf/ballot_list.html"

    def get_context_data(self, **kwargs):
        if self.request.tutor is None or self.request.tutor.profile is None:
            qs = BallotLink.objects.none()
        else:
            qs = BallotLink.objects.filter(profile=self.request.tutor.profile)
        return super().get_context_data(
            **kwargs,
            ballots=qs,
        )


class BallotUpdateForm(forms.Form):
    name = forms.CharField()
    domain = forms.CharField(required=False)
    urls = forms.CharField(widget=forms.Textarea, required=False)
    delete_existing = forms.BooleanField(required=False)


class BallotUpdate(FormView):
    template_name = "mftutor/gf/ballot_update.html"
    form_class = BallotUpdateForm

    def get_constituents(self) -> List[TutorProfile]:
        return [o.profile for o in Tutor.members()]

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            tutor_count=Tutor.members().count(),
            saved=bool(self.request.GET.get("saved")),
        )

    def form_valid(self, form) -> None:
        name = form.cleaned_data["name"]
        existing = BallotLink.objects.filter(name=name)
        tutors = self.get_constituents()
        domain = form.cleaned_data["domain"] or ""
        urls = [
            domain + u
            for u in form.cleaned_data["urls"].split()
        ]
        if urls and len(urls) < len(tutors):
            form.add_error("urls", "Indtast mindst %s links" % len(tutors))
            return self.form_invalid(form)
        if form.cleaned_data["delete_existing"]:
            existing.delete()
        elif not urls:
            form.add_error("urls", "Urls skal udfyldes")
            return self.form_invalid(form)
        random.shuffle(urls)
        ballots = [
            BallotLink(profile=p, url=u, name=name)
            for p, u in zip(tutors, urls)
        ]
        for o in ballots:
            o.save()
        return HttpResponseRedirect(reverse("ballot_update") + "?saved=1")
