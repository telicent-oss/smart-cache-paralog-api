from __future__ import annotations

import io
import json
import logging
import os
from logging import config as logging_config

import toml
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_healthchecks.api.router import HealthcheckRouter, Probe
from rdflib import Graph
from rdflib.plugins.sparql.results.jsonresults import JSONResultSerializer

from paralog import models, queries, utils
from paralog.__meta__ import DESCRIPTION, TITLE
from paralog.decode_token import AccessMiddleware
from paralog.jena import JenaConnector
from paralog.logging_config import LOGGING

__license__ = """
Copyright (c) Telicent Ltd.

This software is licensed under the terms found in the LICENSE file of this repository.

The above copyright notice and license conditions shall be included in all
copies or substantial portions of the Software.
"""

load_dotenv()


with open('./pyproject.toml') as f:
    toml_config = toml.load(f)


logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
if os.getenv('API_LOG_LEVEL') == 'DEBUG':
    logger.warning(
        'Log level is set to DEBUG. This log level is not suitable for production. '
        'Query results, headers and other sensitive data may be logged.'
    )


app = FastAPI(
    description=DESCRIPTION,
    title=TITLE,
    root_path=os.getenv("API_ROOT_PATH", ""),
    version=toml_config['project']['version'],
    openapi_url=os.getenv("API_OPENAPI_PATH", "/openapi.json")
)
app.include_router(
    HealthcheckRouter(
        Probe(name="availability", checks=[],),
        Probe(name="readiness", checks=[],),
    )
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
access_middleware = AccessMiddleware(
    app=app,
    jwt_header=os.getenv("JWT_HEADER"),
    jwks_url=os.getenv("JWKS_URL"),
    public_key_url=os.getenv("PUBLIC_KEY_URL")
)


@app.middleware("http")
async def add_custom_middleware(request: Request, call_next):
    """
    Passes request object containing token header information into access middleware.
    """
    response = await access_middleware(request=request, call_next=call_next)
    return response


jena = JenaConnector(
    os.getenv('JENA_HOST', 'localhost'),
    os.getenv('JENA_PORT', '3030'),
    os.getenv('JENA_DATASET', 'knowledge'),
    protocol=os.getenv('JENA_PROTOCOL', 'http'),
    user=os.getenv('JENA_USER', None),
    pwd=os.getenv('JENA_PASSWORD', None),
)


async def __get_query_with_headers_from_request(
    query: str,
    request: Request,
):
    headers = await utils.get_headers(request)

    logger.info('Sending query to Jena')
    logger.debug(f'Query: {query}')
    query_result = await jena.get(query, headers)
    logger.debug(f'Query result from Jena: {query_result}')
    return query_result


async def __get_query_with_headers_from_request_and_flatten(
    query: str,
    request: Request,
    return_first_obj: bool = False
):
    query_result = await __get_query_with_headers_from_request(query, request)
    logger.info('Flattening result')
    flattened_result = await utils.flatten_out(query_result, return_first_obj)
    logger.debug(f'flattened result: {flattened_result}')
    return flattened_result


async def __get_query_with_headers_from_request_and_map(
    query: str,
    request: Request
):
    query_result = await __get_query_with_headers_from_request(query, request)
    logger.info('Mapping result')
    mapped_result = await utils.map_flood_areas(query_result)
    logger.debug(f'mapped result: {mapped_result}')
    return mapped_result


@app.get("/assessments", response_model=list[models.Assessment])
async def get_assessments(request: Request):
    """
    Returns all assessments
    """
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_all_assessments(),
        request
    )


@app.get("/assessments/assets", response_model=list[models.AssetSummary])
async def get_assets_in_assessments(request: Request, assessment: str, types: list[str] = Query(default=[])):  # noqa
    """
    Returns all assets covered by the assessments. Assessments are provided
    as a list of query parameters
    """
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_assets_by_assessment(assessment, types),
        request
    )


@app.get("/assessments/asset-types", response_model=list[models.IesType])
async def get_asset_types_in_assessments(request: Request, assessment: str):
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_asset_types_by_assessment(assessment),
        request
    )


@app.get("/assessments/dependencies", response_model=list[models.Dependency])
async def get_dependencies_in_assessment(
    request: Request, assessment: str, types: list[str] = Query(default=[])  # noqa
):
    """
    Returns all assets covered by the assessments. Assessments are provided as a list of query parameters
    """
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_dependencies_by_assessment(assessment, types=types),
        request
    )


@app.get("/asset", response_model=models.Asset)
async def get_asset(request: Request, assetUri: str):
    """
    Returns all assets covered by the assessments. Assessments are provided as a list of query parameters.
    """
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_asset(assetUri),
        request,
        return_first_obj=True
    )


@app.get("/asset/dependents", response_model=models.Dependency)
async def get_dependents_for_asset(request: Request, assetUri: str):
    """
    Returns all assets that depend on this asset.
    """
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_dependencies(assetUri, direction="dependents"),
        request
    )


@app.get("/asset/providers", response_model=models.Dependency)
async def get_providers_for_asset(request: Request, assetUri: str):
    """
    Returns all assets that this asset is dependent on.
    """
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_dependencies(assetUri, direction="providers"),
        request
    )


@app.get("/asset/parts")
async def get_asset_parts(request: Request, assetUri: str):
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_asset_parts(assetUri),
        request
    )


@app.get("/asset/residents", response_model=list[models.Person])
async def get_residents(request: Request, assetUri: str):
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_residents(assetUri),
        request
    )


@app.get("/asset/participations")
async def get_participations(request: Request, assetUri: str) -> list:
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_participations(assetUri),
        request
    )


@app.get("/event/participants")
async def get_participants(request: Request, eventUri: str) -> list:
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_participants(eventUri),
        request
    )


@app.get("/person/residences", response_model=list[models.Asset])
async def get_residences(request: Request, personUri: str):
    return await __get_query_with_headers_from_request_and_flatten(
        await queries.get_residence(personUri),
        request
    )


@app.get("/flood-watch-areas", response_model=list[models.FloodWatchArea])
async def get_flood_watch_areas(request: Request):
    return await __get_query_with_headers_from_request_and_map(
        await queries.get_flood_areas(),
        request
    )


@app.get("/flood-watch-areas/polygon")
async def get_flood_area_polygon(request: Request, polygon_uri: str):
    results = await __get_query_with_headers_from_request(
        await queries.get_flood_area_polygon(polygon_uri),
        request
    )
    if results["results"]["bindings"] is None or len(results["results"]["bindings"]) == 0:
        return None
    geo_json = results["results"]["bindings"][0][results["head"]["vars"][0]]["value"]
    return json.loads(geo_json)


@app.get("/states")
async def get_states_for_parent(request: Request, parent_uri: str):
    results = await __get_query_with_headers_from_request(
        await queries.get_states(parent_uri),
        request
    )
    states: dict = {}
    for st in results["results"]["bindings"]:
        if st["stateUri"]["value"] in states.keys():
            state = states[st["stateUri"]["value"]]
        else:
            state = {
                "end": "",
                "period": "",
                "start": "",
                "type": st["stateType"]["value"],
                "uri": st["stateUri"]["value"],
                "relations": [],
                "representations": [],
            }
            states[st["stateUri"]["value"]] = state
        if "inPeriod" in st.keys():
            state["period"] = st["inPeriod"]["value"]
        if "ends" in st.keys():
            state["end"] = st["ends"]["value"]
        if "starts" in st.keys():
            state["start"] = st["starts"]["value"]
        if "repType" in st.keys() and "repValue" in st.keys():
            rep = {st["repType"]["value"]: st["repValue"]["value"]}
            state["representations"].append(rep)

    return states


@app.get("/buildings", response_model=list[models.Building])
async def get_buildings(request: Request):
    results = await __get_query_with_headers_from_request(
        await queries.get_buildings(),
        request
    )
    buildings = []
    for st in results["results"]["bindings"]:
        building = {
            "uri": st["building"]["value"],
            "uprn": st["uprn_id"]["value"],
            "types": st["building_types"]["value"].split(";"),
            "lat": st["lat_literal"]["value"],
            "lon": st["lon_literal"]["value"],
            "epc_rating": st["epc_rating"]["value"],
            "name": st["name"]["value"],
        }
        buildings.append(building)

    return buildings


@app.get("/buildings/{uprn}", response_model=models.FullBuilding)
async def get_building_details(uprn: str, request: Request):
    results = await __get_query_with_headers_from_request(
        await queries.get_building(uprn),
        request
    )

    if len(results["results"]["bindings"]) == 0:
        return None
    st = results["results"]["bindings"][0]
    building = {
        "uri": st["building"]["value"],
        "uprn": st["uprn_id"]["value"],
        "types": st["building_types"]["value"].split(";"),
        "lat": st["lat_literal"]["value"],
        "lon": st["lon_literal"]["value"],
        "sap_points": float(st["sap_points"]["value"]),
        "epc_rating": st["epc_rating"]["value"],
        "postcode": st["postcode_literal"]["value"],
        "address": st["line_of_address_literal"]["value"],
        "name": st["name"]["value"],
    }
    return building


graph = Graph()
graph.parse("./paralog/ont/ies4.ttl")
graph.parse("./paralog/ont/iesExtensions.ttl")


async def __ont_query(query_string):
    results = graph.query(query_string)
    with io.StringIO() as f:
        JSONResultSerializer(results).serialize(f)
        return json.loads(f.getvalue())


@app.get("/ontology/class")
async def get_class(classUri: str):
    query = (
        '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?uri ?superClass
        WHERE {
            BIND (URI("''' + classUri + '''") as ?uri)
            ?uri rdfs:subClassOf ?superClass
        }
        '''
    )
    results = await utils.aggregate(await __ont_query(query), "uri")
    return results


@app.get("/ontology/superclasses")
async def get_superclasses(classUris: list[str] = Query()):  # noqa
    class_uri_str = ", ".join([f"<{value}>" for value in classUris])
    query = (
        '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?uri ?superClass
        WHERE {
            ?uri rdfs:subClassOf ?superClass
            FILTER (?uri in (''' + class_uri_str + '''))
        }
        '''
    )
    results = await utils.aggregate(await __ont_query(query), "uri")
    return results
