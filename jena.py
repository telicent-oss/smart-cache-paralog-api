from SPARQLWrapper import DIGEST, GET, JSON, POST, SPARQLWrapper


class JenaConnector:
    def __init__(self, host, port, dataset, protocol="http", user=None, pwd=None):
        self.url = f"{protocol}://{host}:{port}/{dataset}"

        self.user = user
        self.pwd = pwd

    def __create_sparql(self, endpoint, headers=None):
        if not headers:
            headers = {}
        sparql = SPARQLWrapper(self.url + "/" + endpoint)
        sparql.setHTTPAuth(DIGEST)
        if self.user is not None and self.pwd is not None:
            sparql.setCredentials(self.user, self.pwd)
        sparql.setReturnFormat(JSON)
        for name in headers:
            sparql.addCustomHttpHeader(name, headers[name])
        return sparql

    def get(self, query, headers=None):
        if not headers:
            headers = {}
        sparql = self.__create_sparql("query", headers)

        sparql.setMethod(GET)
        sparql.setQuery(query)
        return sparql.queryAndConvert()

    def post(self, update, headers=None):
        if not headers:
            headers = {}
        sparql = self.__create_sparql("update", headers)
        sparql.setMethod(POST)
        sparql.setQuery(update)
        return sparql.query()
