from PIL.ExifTags import TAGS
from constance import config
from mftutor.settings.local import YEAR
from datetime import datetime
from django.utils.timezone import get_current_timezone
from django.utils.text import slugify as dslugify
from PIL import Image as PilImage
from unidecode import unidecode
import logging
import os

logger = logging.getLogger(__name__)

def slugify(string):
    return dslugify(unidecode(string))


def file_name(instance, path):
    filename = os.path.basename(path)
    sepFilename = os.path.splitext(filename)
    newFilename = slugify(sepFilename[0]) + sepFilename[1]
    gfyear = str(instance.album.gfyear)
    album_slug = instance.album.slug

    return '/'.join([gfyear, album_slug, newFilename])

def get_gfyear():
    return YEAR

def get_exif_date(filename):
    logger.debug('get_exif_date: called with filename: %s' % filename)
    try:
        image = PilImage.open(filename)
        info = image._getexif()
        if info is not None:
            exif = {}
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                exif[decoded] = value

            for t in ["Original", "Digitized", ""]:
                """
                Check the exif fields DateTimeOriginal, DateTimeDigitized and
                DateTime in that order. Return when the first is found.
                """
                if 'DateTime' + t in exif:
                    s = exif['DateTime' + t]
                    if type(s) is tuple:
                        s = str(s[0])
                    logger.debug('get_exif_date: found EXIF field DateTime%s. Parsed it as %s', t, s)

                    if 'SubsecTime' + t in exif:
                        ms = exif['SubsecTime' + t]
                        if type(ms) is tuple:
                            ms = str(ms[0])
                        logger.debug('get_exif_date: found EXIF field SubsecTime. Parsed it as %s', ms)
                    else:
                        ms = '0'

                    s += "." + ms

                    if any(str(n) in s for n in range(1,10)):
                        dt = datetime.strptime(s, '%Y:%m:%d %H:%M:%S.%f')
                        dt = dt.replace(tzinfo=get_current_timezone())

                        return dt

                    logger.debug('get_exif_date: the DateTime%s field only contained zeros. Trying next field', t)

    except AttributeError as e:
        logger.info('get_exif_date: could not get exif data. This file is properly not a jpg or tif. Returning None')
        return None

    except Exception as e:
        logger.warning('get_exif_date: An exception occurred in this slightly volatile function.', exc_info=True)

    logger.info('get_exif_date: could not get exif date. Returning None')
    return None
