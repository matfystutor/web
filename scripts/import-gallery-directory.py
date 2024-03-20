import os
import re
import sys
import argparse


NAME = dict(_=" ", ae="æ", AE="Æ", oe="ø", OE="Ø", aa="å", AA="Å")


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "mftutor.settings.prod")
    sys.path.append('/home/mftutor/.venv/lib/python3.5/site-packages')
    sys.path.append('/home/mftutor')

    import django
    django.setup()


def repl_name(s):
    return re.sub('|'.join(NAME.keys()),
                  lambda mo: NAME[mo.group(0)], s)


def get_paths(input_dir, exts=('jpg',)):
    known = []
    unknown = []
    for name in os.listdir(input_dir):
        name_lower = name.lower()
        if any(name_lower.endswith('.' + e) for e in exts):
            known.append(name)
        else:
            unknown.append(name)
    if unknown:
        print("Unknown file extension: %s" % (sorted(unknown),))
    paths = [os.path.join(input_dir, f) for f in known]
    return sorted(paths)


def album_from_args(input_dir, parser_error, args):
    from django.utils.text import slugify

    order = args.order  # possibly None
    dirname = os.path.basename(input_dir.rstrip('/'))
    if args.year is None:
        mo = re.match(r'^((?:19|20)\d\d)-(?:(\d\d)-)?(.*)$', dirname)
        if mo is None:
            parser_error("--year is required")
        year = int(mo.group(1))
        if mo.group(2) and order is None:
            order = int(mo.group(2))
        name = repl_name(mo.group(3))
    else:
        year = args.year
        name = dirname
    print(name, year, order)
    old_folder = '%02d-%02d%02d/%02d-%s' % (
        year - 1996,
        year % 100,
        (year+1) % 100,
        order,
        name,
    )

    return dict(
        title=name,
        publish_date=None,
        eventalbum=args.eventalbum,
        gfyear=year,
        slug=slugify(name),
        oldFolder=old_folder,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', type=int)
    parser.add_argument('-o', '--order', type=int)
    parser.add_argument('-m', '--type-misc', action='store_false',
                        dest='eventalbum')
    parser.add_argument('input_dirs', nargs='+')
    args = parser.parse_args()

    setup_django()

    albums_images = []
    for input_dir in args.input_dirs:
        album_data = album_from_args(input_dir, parser.error, args)
        paths = get_paths(input_dir)
        albums_images.append(make_objects(album_data, paths))
    for album, images in albums_images:
        save_and_set_date(album, images)


def make_objects(album_data, paths):
    from django.core.exceptions import ValidationError
    from django.core.files import File
    from mftutor.gallery.models import Album, Image
    album = Album(**album_data)
    images = []
    errors = []
    for i, path in enumerate(paths):
        fp = open(path, 'rb')
        fo = File(fp)
        instance = Image(
            file=fo, album=album,
            forcedOrder=i)
        try:
            instance.clean()
        except ValidationError as e:
            errors.append(e)
        else:
            images.append(instance)
    if errors:
        for m in ValidationError(errors).messages:
            print(m.code, m.params, m)
        raise SystemExit()
    return album, images


def save_and_set_date(album, images):
    album.save()
    for image in images:
        image.album = image.album  # update album_id
        image.save()
    dates = [image.date for image in images if image.date is not None]
    if dates:
        album.publish_date = max(dates)
        print("Set publish date to %s" % (album.publish_date,))
        album.save()
    else:
        print("No images have dates")


if __name__ == "__main__":
    main()
