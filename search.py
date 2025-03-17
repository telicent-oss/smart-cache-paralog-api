from time import sleep
from urllib.parse import quote_plus

import requests

from logger import TelicentLogLevel

__license__ = """
Copyright (c) Telicent Ltd.

This software is licensed under the terms found in the LICENSE file of this resository. 

The above copyright notice and license conditions shall be included in all
copies or substantial portions of the Software.
"""

CONNECTION_LIMIT = 60
class SearchEntities:
    def __init__(self, url, logger, jwt_header) -> None:
        self.url = url
        self.logger = logger
        self.jwt_header = jwt_header
        self.connect_count = 0
        # self.wait_for_healthy_search()


    def wait_for_healthy_search(self):
        if self.check_health():
            self.logger("SEARCH API", "Search API reported as healthy", level=TelicentLogLevel.INFO)
            self.connect_count = 0
            return
        else:
            self.connect_count = self.connect_count + 1

            self.logger("SEARCH API",
                        f"Search API reported as unhealthy, wait 2s and try again, {str(self.connect_count)} retries",
                        level=TelicentLogLevel.WARN)
            sleep(2)
            self.wait_for_healthy_search()

    def check_health(self):
        try:
            search = requests.get(f"{self.url}/healthz")
            if search.ok and "healthy" in search.json() and search.json()["healthy"]:
                return True

            self.logger("SEARCH API", f"Unhealthy reported with response: {search.json()}",
                        level=TelicentLogLevel.DEBUG)
            return False
        except Exception:
            self.logger("SEARCH API", "Error connecting to Search API, is it up?", level=TelicentLogLevel.ERROR)
            return False


    def search_entities(self, query, req):
        headers = {}
        if self.jwt_header is not None and self.jwt_header != "":
            headers[self.jwt_header] = req.headers[self.jwt_header]

        results = requests.get(f"{self.url}/typeahead?query={quote_plus(query)}&fields=*primaryName", headers=headers)

        if results.ok:
            documents = results.json()

            return documents['results']

    def retrieve_entity(self, uri, req):
        headers = {}
        if self.jwt_header is not None and self.jwt_header != "":
            headers[self.jwt_header] = req.headers[self.jwt_header]

        entity = requests.get(f"{self.url}/documents/{quote_plus(uri)}", headers=headers)

        if entity.ok:
            document = entity.json()
            return document
