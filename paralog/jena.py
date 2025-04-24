import logging

from SPARQLWrapper import DIGEST, GET, JSON, POST, SPARQLWrapper

logger = logging.getLogger(__name__)


class JenaConnector:
    def __init__(self, host, port, dataset, protocol="http", user=None, pwd=None):
        self.url = f"{protocol}://{host}:{port}/{dataset}"
        self.user = user
        self.pwd = pwd

    async def __create_sparql(self, endpoint, headers: dict | None =None):
        if not headers:
            logger.debug('Headers not provided, setting to {}')
            headers = {}

        logger.info('Initialising SPARQLWrapper')
        sparql = SPARQLWrapper(self.url + "/" + endpoint)
        sparql.setHTTPAuth(DIGEST)

        if self.user is not None and self.pwd is not None:
            logger.info('Jena user and pwd provided, setting credentials')
            sparql.setCredentials(self.user, self.pwd)

        sparql.setReturnFormat(JSON)

        for name in headers:
            logger.debug(f'Adding header: {name}')
            sparql.addCustomHttpHeader(name, headers[name])

        return sparql

    async def get(self, query, headers: dict | None = None):
        logger.info('Jena getting query')
        logger.debug(f'Jena query: {query}')

        sparql = await self.__create_sparql("query", headers)

        logger.debug('Setting sparql method and query')
        sparql.setMethod(GET)
        sparql.setQuery(query)

        logger.debug('Running sparql query and convert')
        result = sparql.queryAndConvert()
        logger.debug(f'result: {result}')
        logger.info('Jena returning result')
        return result

    async def post(self, update, headers=None):
        if not headers:
            headers = {}
        sparql = await self.__create_sparql("update", headers)
        sparql.setMethod(POST)
        sparql.setQuery(update)
        return sparql.query()
