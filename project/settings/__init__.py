import os

import environ
from split_settings.tools import include

if os.environ.get('DOCKER') == '1':
    env_file = 'config_docker.env'
else:
    env_file = 'config.env'  # to start django wed server outside the docker

ROOT_DIR = environ.Path(__file__) - 3
env = environ.Env()
env.read_env(str(ROOT_DIR.path(env_file)))

include(
    # Load environment settings
    'base/env.py',
    # Here we should have the order because of dependencies
    'base/paths.py',
    'base/apps.py',
    'base/middleware.py',
    'base/debug_toolbar.py',

    # Load all other settings
    'base/*.py',
)
