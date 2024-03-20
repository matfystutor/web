# You can use `find . -name '*.DS_Store' -type f -delete` if you operating
# system is a bitch and pollutes you folders


### Fremgangmåde til endeligt import. ###
# 1. På en frossen udgave af Billede mappen køres `import-gallery.py -c`. Det
# tager et par minutter.
#
# 2. På alle fejl der rapportes, tages der stilling til hvad der skal gøres.
# Eks. .m4v filer laves til .mp4, mærkelige filer eller mapper slettes eller
# billeder kopieres fra resized til orginale.
#
# 3. Når `import-gallery.py -c` kun rapportere fejl der ikke skal gøres noget
# ved, kan man slå `generateImageThumbnails` fra i tkweb/apps/gallery/models.py
# ved at udkommentere `@receiver(…)`. Derefter køres `import-gallery.py -s` for
# importere alle filerne til filsystement og databasen, men uden at genrere
# thumbnails.
#
# 4. Hvis det ikke giver anledning til fejl kan man slå
# `generateImageThumbnails` til igen og køre en endelig import med
# `import-gallery.py -s`. Det kommer sansynlig vis til at tage timer.
#
# 5. Gå på druk imens man venter.


import os
from os.path import join
import re
import argparse
import subprocess

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tkweb.settings.prod")

import django
from django.core.files import File
from django.core.exceptions import ValidationError
from django.utils.text import slugify
django.setup()
from mftutor.gallery.models import Album, BaseMedia, Image, GenericFile

parser = argparse.ArgumentParser(description="Delete all old Albums and Images. Transverses the rootdir and makes new Albums. With arguments it will also add Images.")
parser.add_argument('-c', "--check", action="store_true",
                    help="Add the image to the imagemodel. Does not save it. This checks if the model can handle the filetype")
parser.add_argument('-s', "--save", action="store_true",
                    help="Save the images in the database and generate thumbnails. Implies -c")
parser.add_argument('rootdir', help="The path to the 'Billeder' folder from the old webpage")

args = parser.parse_args()

rootdir = args.rootdir
skipped = []
missingFromResizedGlobal = []

replDict = {"_": " ",
       "ae": "æ",
       "AE": "Æ",
       "oe": "ø",
       "OE": "Ø",
       "aa": "å",
       "AA": "Å",}

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

# The slug for the files in the Albums in this list will be forced to be from
# the name instead of EXIF
slugOverwrite = ['11-0708/92-Loebesedler']
slugOverwrite = [os.path.join(rootdir, p) for p in slugOverwrite]

# Files in this list will be compaired with the resized folder, but not
# imported afterwards. This break links from the old URLs
deleteFiles = []
deleteFiles = [os.path.join(rootdir, p) for p in deleteFiles]

notPublicFiles = []

notPublicFiles = [os.path.join(rootdir, p) for p in notPublicFiles]

Album.objects.all().delete()

for yearFolder in os.listdir(rootdir):
    p = re.compile("^[0-9]{2}-[0-9]{4}$")
    if not p.match(yearFolder):
        skipped.append(os.path.join(rootdir, yearFolder))
        continue

    yearStr = yearFolder[3:5]
    if int(yearStr) > 50:
        yearStr = "19" + yearStr
    else:
        yearStr = "20" + yearStr
    #printi(0, yearStr)

    for eventFolder in os.listdir(os.path.join(rootdir, yearFolder)):
        p = re.compile("^[0-9]{2}-[\w\-]")
        if not p.match(eventFolder):
            skipped.append(os.path.join(rootdir, yearFolder, eventFolder))
            continue

        eventNo = eventFolder[:2]
        eventalbum = True
        if int(eventNo) > 85:
            eventalbum = False

        # The folders here will be renamed.
        if int(yearStr) == 2011 and eventFolder == '32-Brianfodring':
            eventStr = "Brianfodring 2"
        elif int(yearStr) == 2011 and eventFolder == '51-Brianfodring':
            eventStr = "Brianfodring 3"
        else:
            eventStr = eventFolder[3:]

        unSlugEventStr = replace_all(eventStr, replDict)

        album = Album()
        album.title = unSlugEventStr
        album.publish_date = None
        album.eventalbum = eventalbum
        album.gfyear = int(yearStr)
        album.slug = slugify(eventStr) # The old title should be a perfect
                                       # slug. We slugify() to be sure.
        album.oldFolder = os.path.join(yearFolder, eventFolder)
        album.save()

        orgiFilelist = []
        resizedFilelist = []

        for orgiOrFile in os.listdir(os.path.join(rootdir, yearFolder,
                                                  eventFolder)):
            if orgiOrFile in ("thumbs"):
                # We have a 'thumbs' folder, ignore
                continue

            elif orgiOrFile in ("Originale", 'originale', 'Oiginale',
                                'original', 'Originale-crop'):

                # We have a 'original' folder
                l = os.listdir(os.path.join(rootdir, yearFolder, eventFolder,
                                            orgiOrFile))
                orgiFilelist.extend([join(orgiOrFile, f) for f in l])

            elif os.path.basename(os.path.join(rootdir, yearFolder,
                                               eventFolder, orgiOrFile)):
                # We have a file
                resizedFilelist.append(orgiOrFile)

            else:
                # We have a strange folder
                skipped.append(os.path.join(rootdir, yearFolder,
                                            eventFolder, orgiOrFile))
        orgiFilelist.sort()
        resizedFilelist.sort()

        if not orgiFilelist and not resizedFilelist:
            # We have a empty album. Don't look further
            continue

        strippedOrgiFileList = [os.path.basename(f) for f in orgiFilelist]

        def diff(a, b):
            b_lower = set(x.lower() for x in b)
            return [x for x in a if x.lower() not in b_lower]

        missingFromResized = []
        missingFromOriginale= []

        d = diff(resizedFilelist, strippedOrgiFileList)
        for i in d:
            missingFromOriginale.append(i)

        d = diff(strippedOrgiFileList, resizedFilelist)
        for i in d:
            missingFromResized.append(i)


        filelist = []

        if not missingFromOriginale:
            # There is nothing missing from orginale
            for f in orgiFilelist:
                fullpath = os.path.join(rootdir, yearFolder, eventFolder, f)
                if os.path.isfile(fullpath):
                    filelist.append(fullpath)
                else:
                    skipped.append(fullpath)

            if missingFromResized:
                missingFromResizedGlobal.extend([os.path.join(rootdir, yearFolder, eventFolder,
                                                    f) for f in missingFromResized])

        elif not orgiFilelist:
            # There is no 'orginal' folder, use 'resized' folder
            for f in resizedFilelist:
                fullpath = os.path.join(rootdir, yearFolder, eventFolder, f)
                if os.path.isfile(fullpath):
                    filelist.append(fullpath)
                else:
                    skipped.append(fullpath)

        #printi(3, filelist)

        if not filelist:
            print("=== %s ===" % (os.path.join(rootdir, yearFolder, eventFolder)))
            print("orgiFilelist %s\n\n" % (orgiFilelist))
            print("resizedFilelist %s\n\n" % (resizedFilelist))
            print("missingFromOriginale %s\n\n" % (missingFromOriginale))
            print("missingFromResized %s\n\n" % (missingFromResized))

        else:
            if args.check or args.save:
                i = 0
                for filepath in filelist:
                    if filepath in deleteFiles:
                        continue

                    if os.path.splitext(os.path.basename(filepath))[0][0] == ".":
                        continue

                    op = open(filepath, "rb")
                    file = File(op)
                    ext = os.path.splitext(filepath)[1].lower()
                    if ext in (".png", ".gif", ".jpg", ".jpeg" ):
                        instance = Image(file=file, album=album)
                    elif ext in (".mp3"):
                        instance = GenericFile(file=file, album=album)
                        instance.type = BaseMedia.AUDIO
                    elif ext in (".mp4", ".m4v"):
                        tmpfilename = os.path.splitext(os.path.basename(filepath))[0] + '.mp4'
                        tmpfilepath = os.path.join('/tmp', tmpfilename)
                        ffargs = ['./ffmpeg-3.1.1-64bit-static/ffmpeg', '-y', '-i', filepath] + '-c copy -movflags +faststart'.split() + [tmpfilepath]
                        subprocess.check_call(ffargs)
                        op2 = open(tmpfilepath, "rb")
                        file2 = File(op2)
                        instance = GenericFile(originalFile=file, file=file2, album=album)
                        instance.type = BaseMedia.VIDEO
                    elif ext in (".avi", ".mov"):
                        tmpfilename = os.path.splitext(os.path.basename(filepath))[0] + '.mp4'
                        tmpfilepath = os.path.join('/tmp', tmpfilename)
                        ffargs = ['./ffmpeg-3.1.1-64bit-static/ffmpeg', '-y', '-i', filepath] + '-c:v libx264 -pix_fmt yuv420p -profile:v baseline -level 3.0 -movflags +faststart'.split() + [tmpfilepath]
                        subprocess.check_call(ffargs)
                        op2 = open(tmpfilepath, "rb")
                        file2 = File(op2)
                        instance = GenericFile(originalFile=file, file=file2, album=album)
                        instance.type = BaseMedia.VIDEO
                    elif ext in (".pdf", ".txt"):
                        instance = GenericFile(file=file, album=album)
                        instance.type = BaseMedia.OTHER
                    else:
                        skipped.append(filepath)
                        continue

                    if os.path.basename(filepath) in missingFromResized:
                        instance.visibility = BaseMedia.DISCARDED

                    if os.path.basename(filepath) in notPublicFiles:
                        instance.visibility = BaseMedia.DISCARDED

                    instance.forcedOrder = i
                    i += 1
                    try:
                        instance.full_clean()
                    except ValidationError as e:
                        print("=== %s ===" % (os.path.join(rootdir, yearFolder, eventFolder)))
                        print("file", file)
                        print("ValidationError", e)
                        print("")
                        continue

                    # overwrite some slugs
                    p = os.path.join(rootdir, yearFolder, eventFolder)
                    if p in slugOverwrite:
                        instance.slug = slugify(os.path.splitext(os.path.basename(file.name))[0])

                    if args.save:
                        instance.save() # This prints a newline

                    #Set album date from last image with a date.
                    if not instance.date == None:
                        album.publish_date = instance.date
        album.save()

print('Missing from resized / Not public images:')
for l in missingFromResizedGlobal:
    print("%s" % (l))

print('\n\nSkipped files:')
for l in skipped:
    print("%s" % (l))
