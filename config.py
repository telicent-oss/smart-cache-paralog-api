from telicent_lib.config import Configurator

__license__ = """
Copyright (c) Telicent Ltd.

This software is licensed under the terms found in the LICENSE file of this resository. 
    http://www.apache.org/licenses/LICENSE-2.0

The above copyright notice and license conditions shall be included in all
copies or substantial portions of the Software.
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
