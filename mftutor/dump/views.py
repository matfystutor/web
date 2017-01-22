# vim: set fileencoding=utf8:
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View

from mftutor.tutor.models import Tutor, Rus, TutorGroup
from mftutor.events.models import EventParticipant


class DumpView(View):
    def access_field(self, base, current, name, path):
        parts = path.split('__') if path else ()
        o = current
        for i, p in enumerate(parts):
            o = getattr(o, p)
            if type(o).__name__ in ("RelatedManager", "ManyRelatedManager"):
                return ','.join(
                    self.access_field(
                        base,
                        oo,
                        name + '__' + p,
                        '__'.join(parts[i+1:]))
                    for oo in o.all())
        try:
            m = getattr(self, 'display_%s' % name)
        except AttributeError:
            pass
        else:
            o = m(o, base=base)
        return o

    def usage(self, s=None):
        return HttpResponseBadRequest(
            ("%s\n\n" % s if s else '') +
            'Available fields:\n' +
            ', '.join(self.available_fields.keys()) +
            '\n\n' +
            'Use display_fields=f1,f2 to set tab-separated output columns.\n' +
            'Use order_by=f1,f2 to set the output order.\n' +
            'Use format=tex&tex_name=bla to output lines like \\bla{f1}{f2}.\n',
            'text/plain; charset=utf8')

    def get(self, request):
        available_fields = self.available_fields
        params = dict(request.GET.items())
        try:
            display_fields = params.pop('display_fields').split(',')
        except KeyError:
            return self.usage('Missing param display_fields')
        available_display_fields = set(available_fields.keys())
        available_display_fields.add('n')
        if any(f not in available_display_fields for f in display_fields):
            return self.usage('Invalid display_fields')

        order_by = params.pop('order_by', None)
        if order_by is not None:
            if any(f not in available_fields for f in order_by.split(',')):
                return self.usage('Unknown key in order_by')
        download = params.pop('download', None)
        tex_name = params.pop('tex_name', self.tex_name)
        fmt = params.pop('format', 'tsv')
        try:
            formatter = getattr(self, 'format_%s' % (fmt,))
        except AttributeError:
            return self.usage('Unknown format %s' % (fmt,))

        if any(k not in available_fields for k in params):
            return self.usage('Unknown filter key')

        objects = self.get_objects(params)
        objects = self.handle_order_by(objects, order_by)

        rows = [
            [i+1 if k == 'n' else self.access_field(o, o, k, available_fields[k])
             for k in display_fields]
            for i, o in enumerate(objects)
        ]
        s = formatter(rows, tex_name=tex_name)
        response = HttpResponse(s)
        if download is not None:
            response['Content-Disposition'] = 'attachment; filename="dump.csv"'
            response['Content-Type'] = 'text/csv; charset=utf-8'
        else:
            response['Content-Type'] = 'text/plain; charset=utf-8'
        return response

    def get_objects(self, params):
        filter_kwargs = self.get_filter_kwargs(params)

        objects = self.get_queryset_base().filter(**filter_kwargs)
        return objects

    def get_queryset_base(self):
        return self.model.objects.all()

    def get_filter_kwargs(self, params):
        filter_kwargs = {}
        for k, v in params.items():
            try:
                filter_kwargs[self.available_fields[k]] = v
            except KeyError:
                return self.usage('Unknown key %s' % (k,))
        return filter_kwargs

    def handle_order_by(self, objects, order_by):
        if order_by:
            args = [
                self.available_fields[k]
                for k in order_by.split(',')
            ]
            objects = objects.order_by(*args)
        return objects

    def format_tsv(self, rows, **kwargs):
        return u''.join(u'%s\n' % u'\t'.join(map(unicode, r)) for r in rows)

    def format_tex(self, rows, tex_name, **kwargs):
        return u''.join(
            u'\\%s%s\n' %
            (tex_name, u''.join(u'{%s}' % x for x in r))
            for r in rows)


class TutorDumpView(DumpView):
    model = Tutor
    available_fields = {
        'year': 'year',
        'rusclass': 'rusclass',
        'study': 'profile__study',
        'name': 'profile__name',
        'phone': 'profile__phone',
        'email': 'profile__email',
        'studentnumber': 'profile__studentnumber',
        'street': 'profile__street',
        'city': 'profile__city',
        'groups': 'groups',
    }
    tex_name = 'tutor'

    def display_groups__groups(self, group, base, **kwargs):
        if group.leader == base:
            return '*%s' % group.handle
        else:
            return group.handle

    def get_queryset_base(self):
        return Tutor.objects.all()

    def get_filter_kwargs(self, params):
        gr = params.pop('group', None)
        filter_kwargs = super(TutorDumpView, self).get_filter_kwargs(params)
        if gr is not None:
            filter_kwargs['groups__name'] = gr
        return filter_kwargs


class RusDumpView(DumpView):
    model = Rus
    available_fields = {
        'year': 'year',
        'rusclass': 'rusclass',
        'name': 'profile__name',
        'phone': 'profile__phone',
        'email': 'profile__email',
        'studentnumber': 'profile__studentnumber',
        'arrived': 'arrived',
        'street': 'profile__street',
        'city': 'profile__city',
    }
    tex_name = 'rus'

    def display_arrived(self, v, **kwargs):
        return 'Ank' if v else ''


class EventsDumpView(DumpView):
    model = EventParticipant
    available_fields = {
        'event': 'event__pk',
        'name': 'tutor__profile__name',
        'status': 'status',
        'notes': 'notes',
    }
    tex_name = 'tutor'


class GroupsDumpView(DumpView):
    model = TutorGroup
    available_fields = {
        'name': 'name',
        'year': 'year',
        'leader': 'leader__profile__name',
        'handle': 'handle',
    }
    tex_name = 'group'
