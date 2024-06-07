import json
import logging
from datetime import datetime
from enum import Enum

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


class TelicentLogLevel(Enum):
    DEBUG=0
    INFO=1
    WARN=2
    ERROR=3
    FATAL=4


class TelicentLogger:
    def __init__(self, name, level: TelicentLogLevel = TelicentLogLevel.INFO):
        self.name = name
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        loggingStreamHandler = logging.StreamHandler()
        self.logger.addHandler(loggingStreamHandler)

    def get_log_level(self):
        return self.level

    def __call__(self, method, message, level:TelicentLogLevel=TelicentLogLevel.DEBUG, type="GENERAL"):
        if level is TelicentLogLevel.DEBUG:
            self.logger.debug(self.format_log("DEBUG", method, message, type))
        elif level is TelicentLogLevel.INFO:
            self.logger.info(self.format_log("INFO", method, message, type))
        elif level is TelicentLogLevel.WARN:
            self.logger.warn(self.format_log("WARN", method, message, type))
        elif level is TelicentLogLevel.ERROR:
            self.logger.error(self.format_log("ERROR", method, message, type))
        elif level is TelicentLogLevel.FATAL:
            self.logger.fatal(self.format_log("FATAL", method, message, type))
    def format_log(self,level, method, message, type):
        return json.dumps({"level": "[%s]"%(level),"method": method,
                           "message": message, "type": type, "time": datetime.utcnow().isoformat()})

