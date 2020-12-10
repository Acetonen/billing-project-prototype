INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'rest_framework',

    'django_extensions',
    'drf_yasg',
    'rest_framework_swagger',

    # Local
    'project.accounts.apps.AccountsConfig',
    'project.payments.apps.PaymentsConfig',
)
