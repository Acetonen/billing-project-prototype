import os

MEDIA_URL = "/media/"
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, "staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_DIRS = (os.path.join(PROJECT_DIR, "static"),)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
