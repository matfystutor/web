"""
Client-side script that generates the same LaTeX as
mftutor.rusclass.views.TutorListView.generate_tex,
but using the Python modules 'requests' and 'microdata'
to retrieve the information from the website.

The script shows (render_to_string) how to render a Django template
without running django.setup().
"""
import json
import requests
import microdata

import django.template
import django.template.backends.django


def render_to_string(template_name, context):
    engine = django.template.backends.django.Engine()
    with open(template_name) as fp:
        template = django.template.Template(fp.read(), engine=engine)
    context = django.template.Context(context)
    return template.render(context)


def strip_prefix(s, p):
    if s and s.startswith(p):
        return s[len(p):]
    else:
        return s


def main():
    url = "http://matfystutor.dk/rus/holdtutorer/"
    r = requests.get(url)
    item, = microdata.get_items(r.text)

    year = item.year

    rusclass_list = []

    o = item.get_all('rusclass')
    for rusclass in o:
        tutors = []
        for tutor in rusclass.get_all("tutor"):
            name = tutor.name
            phone = strip_prefix(str(tutor.phone), "tel:")
            tutors.append({
                'name': name,
                'phone': phone,
            })

        rusclass_list.append({
            'name': rusclass.name,
            'tutors': tutors,
        })

    template_name = 'templates/rusclass/tutorhold.tex'
    context = {'rusclass_list': rusclass_list, 'year': year}
    print(render_to_string(template_name, context))


if __name__ == "__main__":
    main()
