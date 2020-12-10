DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TEMPLATE_CONTEXT': True,
    'ENABLE_STACKTRACES': True,
    # 'SHOW_TOOLBAR_CALLBACK': lambda r: False,  # disables it
}

if DEBUG:
    # noinspection PyUnboundLocalVariable
    INSTALLED_APPS += 'debug_toolbar',

    # noinspection PyUnboundLocalVariable
    MIDDLEWARE += 'debug_toolbar.middleware.DebugToolbarMiddleware',

    INTERNAL_IPS = type(str('c'), (), {'__contains__': lambda *a: True})()
