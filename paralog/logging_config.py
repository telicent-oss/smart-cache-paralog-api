import os

from dotenv import load_dotenv

__license__ = """
Copyright (c) Telicent Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

load_dotenv()  # In case app imports before it loads

LOG_LEVEL = os.getenv('API_LOG_LEVEL', 'INFO')
LOG_STDOUT = os.getenv('API_LOG_STDOUT', 1)
LOG_FILE = os.getenv('API_LOG_FILE', 0)
LOG_FILE_PATH = os.getenv('API_LOG_FILE_PATH', 'barry.log')

handlers = []
if LOG_STDOUT == 1:
    handlers.append('stdout')
if LOG_FILE == 1:
    handlers.append('file')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
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
    },
    'loggers': {
        'paralog': {
            'handlers': handlers,
            'level': LOG_LEVEL,
            'propagate': False
        },
        'jena': {
            'handlers': handlers,
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
