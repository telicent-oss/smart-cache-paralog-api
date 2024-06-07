from telicent_lib.config import Configurator

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

class ParalogConfig:
    def __init__(self):
        config = Configurator()
        self.debug = config.get(
            "DEBUG",
            default=False,
            description="Apply debug logging to the service",
            required_type=bool,
            converter=bool,
        )
        self.broker = config.get(
            "BOOTSTRAP_SERVERS",
            default="localhost:9092",
            description="Address of Core Kafka instance",
            required_type=str,
        )
        self.target_topic = config.get(
            "IES_TOPIC",
            default="knowledge",
            description="Knowledge topic name in Core",
            required_type=str,
        )
        self.jena_protocol = config.get(
            "JENA_PROTOCOL",
            default="http",
            description="Jena protocol",
            required_type=str,
        )
        self.jena_url = config.get(
            "JENA_URL",
            default="localhost",
            description="Jena host URL",
            required_type=str,
        )
        self.jena_port = config.get(
            "JENA_PORT",
            default=3030,
            description="Jena port",
            required_type=int,
            converter=int,
        )
        self.knowledge_dataset = config.get(
            "JENA_DATASET", default="knowledge", required_type=str
        )
        self.jena_user = config.get("JENA_USER")
        self.jena_pwd = config.get("JENA_PWD")
        self.port = config.get("PORT", default="4001", required_type=int, converter=int)
        self.jwt_header = config.get("JWT_HEADER")
        self.jwt_url = config.get("JWK_URL")
        self.public_key_url = config.get("PUBLIC_KEY_URL")
