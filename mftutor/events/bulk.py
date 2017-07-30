import datetime
from mftutor.events.models import Event


def dump_date(d):
    return '%04d-%02d-%02d' % (d.year, d.month, d.day)


def dump_event(event):
    d1, d2 = event.start_date, event.end_date
    if d1 != d2:
        date = '%s:%s' % (dump_date(d1), dump_date(d2))
    else:
        date = dump_date(d1)

    t1, t2 = event.start_time, event.end_time
    if not t1:
        time = 'allday'
    elif t1 == t2:
        time = '%02d:%02d' % (t1.hour, t1.minute)
    else:
        time = '%02d:%02d-%02d:%02d' % (
            t1.hour, t1.minute, t2.hour, t2.minute)

    return '%s %s %s' % (date, time, event.title)


def dumps(events):
    return '\n'.join(dump_event(event) for event in events)


def parse_date(d):
    year, month, day = d.split('-')
    return datetime.date(
        year=int(year), month=int(month), day=int(day))


def parse_time(t):
    if t is None:
        return None
    hour, minute = t.split(':')
    return datetime.time(
        hour=int(hour), minute=int(minute))


def parse_event(line):
    date, time, title = line.split(None, 2)

    try:
        d1, d2 = date.split(':')
    except ValueError:
        d1 = d2 = date

    if time == 'allday':
        t1 = t2 = None
    else:
        try:
            t1, t2 = time.split('-')
        except ValueError:
            t1 = t2 = time

    if d1 > d2:
        raise ValueError("Start date is after end date")
    elif d1 == d2 and t1 is not None and t1 > t2:
        raise ValueError("Start time is after end time")

    return Event(
        title=title.strip(),
        start_date=parse_date(d1),
        end_date=parse_date(d2),
        start_time=parse_time(t1),
        end_time=parse_time(t2),
    )


def parse(data):
    events = []
    for i, line in enumerate(data.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(parse_event(line))
        except ValueError as e:
            raise ValueError("Could not parse line %d in input: %s"
                % (i + 1, e))
    return events
