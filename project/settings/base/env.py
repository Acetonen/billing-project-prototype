from project.settings import env

ALLOWED_HOSTS = env('ALLOWED_HOSTS', default=['*'])
BASE_URL = env('BASE_URL', default='')
DEBUG = env('DEBUG', default=False, cast=bool)
