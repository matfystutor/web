import logging
import textwrap

from optparse import make_option
from django.core.management.base import BaseCommand
from ....settings import YEAR
from ...models import Handout
from ...views import get_lightbox_state
import time

class Command(BaseCommand):
    can_import_settings = True
    option_list = BaseCommand.option_list + (
            #make_option('--members',
            #    dest='members',
            #    default=40),
            #make_option('--activations',
            #    dest='activations',
            #    default=0.1),
            )

    def handle(self, **kwargs):
        def typeset(cell):
            if cell is None:
                color = ''
                reset = ''
                name = ''
            else:
                colors = dict(zip('red yellow green'.split(), '41;37 43;30 42;30'.split()))
                color = '\033[%s;1m' % colors.get(cell.color)
                reset = '\033[0m'
                name = cell.rusclass.internal_name
            return '%s %s %s ' % (color, (name + ' ').center(7), reset)

        colors = dict(zip('red yellow green'.split(), '41;37 43;30 42;30'.split()))

        prev_display = ''
        frog = (
            '   00   ',
            '  (--)  ',
            ' ( || ) ',
            ' ^^~~^^ ',
        )
        width = 6*10 - 1
        note_width = width - len(frog[0])

        while True:
            d = get_lightbox_state(YEAR)
            note_object = d['note']
            note = note_object.note
            color = note_object.color
            by_study = d['by_study']
            columns = [list(each['rusclasses']) for each in by_study]
            max_len = max(len(each) for each in columns)
            columns_padded = [column + max_len*[None] for column in columns]
            rows = [[column[i] for column in columns_padded]
                    for i in range(max_len)]
            init = '\033[2J\033[H'
            header = '\033[%s;1m   BURET   \033[0m' % colors.get(color)
            rows_printed = '\n'.join(''.join(typeset(cell) for cell in row)
                                     for row in rows)

            note = ''.join(
                '%s\n' % '\n'.join(textwrap.wrap(line, note_width))
                for line in note.splitlines())
            note_lines = list(note.splitlines()) + 4*['']
            note_lines = [line.ljust(note_width) for line in note_lines]
            for i, frog_line in enumerate(frog):
                note_lines[i] += '\033[%s;1m%s\033[0m' % (colors.get(color), frog_line)
            note_with_frog = '\n'.join(note_lines).rstrip('\n ')
            display = '%s%s\n%s\n\n%s' % (init, header, note_with_frog, rows_printed)
            if display != prev_display:
                print(display)
                prev_display = display
            time.sleep(5)
