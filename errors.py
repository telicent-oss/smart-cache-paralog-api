__license__ = """
Copyright (c) Telicent Ltd.

This software is licensed under the terms found in the LICENSE file of this resository. 

The above copyright notice and license conditions shall be included in all
copies or substantial portions of the Software.
"""

class ConfigurationException(Exception):
    """Raised when a components requiring a configuration doesn't receive it

    Attributes:
        component -- component missing config
        config -- missing config
        message -- explanation of the error
    """

    def __init__(self, component, config, message="A component is missing the configuration it requires"):
        self.component = component
        self.config = config
        self.message = message
        super().__init__(self.message)
