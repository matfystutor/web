# coding: utf-8
from django.conf import global_settings

# Django settings for mftutor project.

DEBUG = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mftutor',
        'USER': 'mftutor',
        'PASSWORD': 'hunter2',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Copenhagen'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'da-DK'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'prodekanus/static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/upload/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'prodekanus/upload')

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'not.so.secret.right.now'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'mftutor/templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'mftutor.rus.context_processors.rus_data',
                'mftutor.tutor.context_processors.login_form',
                'mftutor.tutor.context_processors.tutor_data',
                'mftutor.tutor.context_processors.settings',
                'mftutor.events.context_processors.site',
                'django_su.context_processors.is_su',
                'constance.context_processors.config',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        }
    }
]

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mftutor.tutor.middleware.TutorMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'mftutor.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'mftutor.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django_su',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'constance',
    'constance.backends.database',

    'django_wysiwyg',
    'debug_toolbar',
    'sorl.thumbnail',

    'mftutor.tutor',
    'mftutor.news',
    'mftutor.events',
    'mftutor.aliases',
    'mftutor.browser',
    'mftutor.tutormail',
    'mftutor.page',
    'mftutor.shirt',
    'mftutor.confirmation',
    'mftutor.documents',
    'mftutor.sampledata',
    'mftutor.rus',
    'mftutor.reg',
    'mftutor.dump',
    'mftutor.rusclass',
    'mftutor.signup',
    'mftutor.groups',
    'mftutor.tutorbog',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTH_PROFILE_MODULE = 'tutor.TutorProfile'

LOGIN_REDIRECT_URL = "/"

LOGIN_URL = '/login/'

INTERNAL_IPS = ('127.0.0.1',)

BODY_CLASS = 'production'

# If True, use HTML Tidy to clean up news post HTML bodies.
TIDY_NEWS_HTML = False

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_su.backends.SuBackend',
)

SITE_URL = 'http://example.com'

CALENDAR_NAME = 'Calendar name'

CALENDAR_DESCRIPTION = 'Calendar description'

# Tuples (official_name, handle, internal_name).
# official_name is the two-letter prefix used by the faculty.
# handle is the lowercase ASCII prefix we use in the mail system.
# internal_name is the prefix we use in internal communications.
RUSCLASS_BASE = (
    ('MA', 'mat', 'Mat'),
    ('MØ', 'mok', 'Møk'),
    ('FY', 'fys', 'Fys'),
    ('NA', 'nano', 'Nano'),
    ('IT', 'it', 'It'),
    ('DA', 'dat', 'Dat'),
    ('DV', 'dav', 'Dav'),
)

# Prefix of email addresses going to tutors of a certain rusclass
# i.e. tutor+dat5 for the dat5 tutors -> use 'tutor+'
TUTORS_PREFIX = 'tutor+'

# Used by TutorProfile to set the default email if none is known.
DEFAULT_EMAIL_DOMAIN = 'post.au.dk'
DEFAULT_ASB_EMAIL_DOMAIN = 'stud.asb.dk'

PERSONAL_EMAIL_SENDER = 'Mat/Fys-Tutorgruppen <webfar@matfystutor.dk>'

# Email aliases that change with the GF in November
GF_GROUPS = ('best', 'koor', 'webfar', 'oekonomi', 'gris')

THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.dbm_kvstore.KVStore'
THUMBNAIL_DBM_FILE = '/home/mftutor/web/thumbnails/thumbnail_kvstore'

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'TUTORBOG_SECRET': ('', 'Svaret til krydsorden i tutorbogen'),
    'TUTORBOG_SURVEY_URL': ('', 'URL til tutorbog surveyen'),
    'ENABLE_CONFIRMATION': (False, 'Er tutorbekræftelser aktive?', bool),
}
