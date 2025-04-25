import os

from dotenv import load_dotenv

__license__ = """
Copyright (c) Telicent Ltd.

This software is licensed under the terms found in the LICENSE file of this repository.

The above copyright notice and license conditions shall be included in all
copies or substantial portions of the Software.
"""

load_dotenv()  # In case app imports before it loads

LOG_LEVEL = os.getenv('API_LOG_LEVEL', 'INFO')
LOG_STDOUT = os.getenv('API_LOG_STDOUT', 1)
LOG_FILE = os.getenv('API_LOG_FILE', 0)
LOG_FILE_PATH = os.getenv('API_LOG_FILE_PATH', 'barry.log')

AUTH_LOG_STDOUT = os.getenv('AUTH_LOG_STDOUT', 1)
AUTH_LOG_FILE = os.getenv('AUTH_LOG_FILE', 0)
AUTH_LOG_FILE_PATH = os.getenv('AUTH_LOG_FILE_PATH', 'barry.log')

handlers = []
if LOG_STDOUT == 1:
    handlers.append('stdout')
if LOG_FILE == 1:
    handlers.append('file')

auth_handlers = []
if AUTH_LOG_STDOUT == 1:
    auth_handlers.append('auth_stdout')
if AUTH_LOG_FILE == 1:
    auth_handlers.append('auth_file')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'auth_with_extras': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "method": "%(method)s", '
                      '"type": "%(type)s", "message": "%(message)s"}'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOG_FILE_PATH,
            'formatter': 'simple'
        },
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'auth_file': {
            'class': 'logging.FileHandler',
            'filename': LOG_FILE_PATH,
            'formatter': 'auth_with_extras'
        },
        'auth_stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'auth_with_extras',
            'stream': 'ext://sys.stdout'
        },
    },
    'loggers': {
        'paralog.app': {
            'handlers': handlers,
            'level': LOG_LEVEL,
            'propagate': False
        },
        'paralog.jena': {
            'handlers': handlers,
            'level': LOG_LEVEL,
            'propagate': False
        },
        'paralog.decode_token': {
            'handlers': auth_handlers,
            'level': LOG_LEVEL,
            'propagate': False
        },
        'uvicorn.access': {
            'handlers': handlers,
            'level': LOG_LEVEL,
            'propagate': False
        },
        'uvicorn.error': {
            'handlers': handlers,
            'level': LOG_LEVEL,
            'propagate': False
        },
        'uvicorn.asgi': {
            'handlers': handlers,
            'level': LOG_LEVEL,
            'propagate': False
        },
    }
}
