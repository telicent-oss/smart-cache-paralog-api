# Telicent Paralog Server
# =======================

# A simple REST API for accessing IES data in Paralog

# Copyright (c) 2022-2024 Telicent Ltd.

import io
import json

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Had to put in a temporary model server (for the ontology) until we get the ontology API up and running
from rdflib import Graph
from rdflib.plugins.sparql.results.jsonresults import JSONResultSerializer

import queries
import utils
from config import ParalogConfig
from decode_token import AccessMiddleware
from jena import JenaConnector
from logger import TelicentLogger, TelicentLogLevel

__license__ = """
Copyright (c) Telicent Ltd.

This software is licensed under the terms found in the LICENSE file of this resository. 

The above copyright notice and license conditions shall be included in all
copies or substantial portions of the Software.
"""

graph = Graph()
graph.parse("./ies4.ttl")
graph.parse("./iesExtensions.ttl")


def ontQuery(queryString):
    results = graph.query(queryString)
    with io.StringIO() as f:
        JSONResultSerializer(results).serialize(f)
        return json.loads(f.getvalue())


config = ParalogConfig()

log_level = TelicentLogLevel.INFO
if config.debug:
    log_level = TelicentLogLevel.DEBUG

logger = TelicentLogger("paralog-api", level=log_level)

jena = JenaConnector(
    config.jena_url,
    config.jena_port,
    config.knowledge_dataset,
    protocol=config.jena_protocol,
    user=config.jena_user,
    pwd=config.jena_pwd,
)

app = FastAPI(
    title="Paralog Server",
    description="A REST API for getting CARVER-style data out of an IES triplestore",
)

access_middleware = AccessMiddleware(app=app, jwt_header=config.jwt_header, logger=logger,
                                     jwks_url=config.jwt_url, public_key_url=config.public_key_url)

@app.middleware("http")
async def add_custom_middleware(request: Request, call_next):
    """
    passes request object containing token header information into access middleware.
    """
    response = await access_middleware(request=request, call_next=call_next)
    return response


# Bit of data modelling to constrain the REST API, and also helps with swagger documentation.
# Assessment objects were used extensively in the early CARVER work for NDT.
# They're less important now, but there is still one in the dataset at least
class Assessment(BaseModel):
    uri: str
    name: str
    numberOfAssessedItems: int


# IesType is a simple object wrapper for returning a type (RDFS Class).
# Optionally includes a count of the number of instances and a list of the parent classes
class IesType(BaseModel):
    uri: str
    assetCount: int | None = None
    subClassOf: list[str] | None = None


# Wrapper object for ies:Person
class Person(BaseModel):
    uri: str
    name: str | None = None


# Wrapper for IES objects that are considered Assets (e.g. Facilities, Locations, etc.) in the assessment
class Asset(BaseModel):
    uri: str
    assetType: str
    name: str | None = None
    lat: float | None = None
    lon: float | None = None
    address: str | None = None
    desc: str | None = None
    osmID: str | None = None
    wikipediaPage: str | None = None
    webPage: str | None = None
    dependentCount: int | None = None
    dependentCriticalitySum: float | None = None


# Wrapper for reduced data about an Asset - used for providing high-level summaries -
# without hitting the database for all the information that would be returned as Asset
# A future version of the API should probably merge this with Asset (this was built for a demo only)
class AssetSummary(BaseModel):
    uri: str
    type: str
    lat: float | None = None
    lon: float | None = None
    dependentCount: int | None = None
    dependentCriticalitySum: float | None = None
    partCount: int | None = None


# A wrapper for IES State instances
class State(BaseModel):
    uri: str
    stateType: str
    start: str | None = None
    end: str | None = None
    inPeriod: str | None = None


# A wrapper for dependencies between a provider asset and a dependent asset
class Dependency(BaseModel):
    dependencyUri: str
    providerNode: str
    providerNodeType: str
    providerName: str | None = None
    dependentNode: str
    dependentNodeType: str
    dependentName: str | None = None
    criticalityRating: float | None = None
    osmID: str | None = None


class Segment(BaseModel):
    lat: list[str]
    lon: list[str]
    id: list[str]
    type: list[str]


class FloodArea(BaseModel):
    uri: str
    name: str
    polygon_uri: str


class FloodWatchArea(BaseModel):
    uri: str
    name: str
    polygon_uri: str
    flood_areas: list[FloodArea]


class Building(BaseModel):
    uri: str
    uprn: str
    types: list[str]
    lat: str
    lon: str
    epc_rating: str
    name: str


class FullBuilding(Building):
    postcode: str
    address: str
    sap_points: float


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Base root
@app.get("/")
async def root():
    return {"name": "Paralog Server"}


# Returns all the assessments
@app.get("/assessments", response_model=list[Assessment])
async def get_assessments(req: Request):
    headers = utils.get_headers(req.headers)
    query = queries.get_all_assessments()
    return utils.flatten_out(jena.get(query, headers))


# Returns all assets covered by the assessments. Assessments are provided as a list of query parameters
@app.get("/assessments/assets", response_model=list[AssetSummary])
async def get_assets_in_assessments(
    req: Request, assessment: str = Query(), types: list[str] = Query()#noqa
):
    headers = utils.get_headers(req.headers)
    query = queries.get_assets_by_assessment(assessment, types=types)
    return utils.flatten_out(jena.get(query, headers))

    # Returns all assets covered by the assessments. Assessments are provided as a list of query parameters


@app.get("/assessments/asset-types", response_model=list[IesType])
async def get_asset_types_in_assessments(
    req: Request, assessment: str = Query()
):
    headers = utils.get_headers(req.headers)
    query = queries.get_asset_types_by_assessment(assessment)
    return utils.flatten_out(jena.get(query, headers))


# Returns all assets covered by the assessments. Assessments are provided as a list of query parameters
@app.get("/assessments/dependencies", response_model=list[Dependency])
async def get_dependencies_in_assessment(
    req: Request, assessment: str = Query(), types: list[str] = Query() #noqa
):
    headers = utils.get_headers(req.headers)
    query = queries.get_dependencies_by_assessment(assessment, types=types)
    return utils.flatten_out(jena.get(query, headers))


# Returns all assets covered by the assessments. Assessments are provided as a list of query parameters
@app.get("/asset", response_model=Asset)
async def get_asset(req: Request, assetUri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_asset(assetUri)
    return utils.flatten_out(jena.get(query, headers), return_first_obj=True)


# Returns all assets that depend on this asset
@app.get("/asset/dependents", response_model=list[Dependency])
async def get_dependents_for_asset(req: Request, assetUri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_dependencies(assetUri, direction="dependents")
    return utils.flatten_out(jena.get(query, headers))


# Returns all assets that this asset is dependent on
@app.get("/asset/providers", response_model=list[Dependency])
async def get_providers_for_asset(req: Request, assetUri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_dependencies(assetUri, direction="providers")
    return utils.flatten_out(jena.get(query, headers))


@app.get("/asset/parts")
async def get_asset_parts(req: Request, assetUri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_asset_parts(assetUri)
    return utils.flatten_out(jena.get(query, headers))


@app.get("/asset/residents", response_model=list[Person])
async def get_residents(req: Request, assetUri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_residents(assetUri)
    return utils.flatten_out(jena.get(query, headers))


@app.get("/asset/participations", response_model=list)
async def get_participations(req: Request, assetUri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_participations(assetUri)
    return utils.flatten_out(jena.get(query, headers))


@app.get("/event/participants", response_model=list)
async def get_participants(req: Request, eventUri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_participants(eventUri)
    return utils.flatten_out(jena.get(query, headers))


@app.get("/person/residences", response_model=list[Asset])
async def get_residences(req: Request, personUri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_residence(personUri)
    return utils.flatten_out(jena.get(query, headers))


@app.get("/flood-watch-areas", response_model=list[FloodWatchArea])
async def get_flood_watch_areas(req: Request):
    headers = utils.get_headers(req.headers)
    query = queries.get_flood_areas()
    results = jena.get(query, headers)
    return utils.map_flood_areas(results)


@app.get("/flood-watch-areas/polygon")
async def get_flood_area_polygon(req: Request, polygon_uri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_flood_area_polygon(polygon_uri)
    results = jena.get(query, headers)

    if (
        results["results"]["bindings"] is None
        or len(results["results"]["bindings"]) == 0
    ):
        # handle missing uri -> throw error
        ret = None
        return ret
    geo_json = results["results"]["bindings"][0][results["head"]["vars"][0]]["value"]
    return json.loads(geo_json)


@app.get("/states")
async def get_states_for_parent(req: Request, parent_uri: str = Query()):
    headers = utils.get_headers(req.headers)
    query = queries.get_states(parent_uri)
    results = jena.get(query, headers)
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


# uri: str
# types: List[str]
# lat: str
# lon: str
# epc_rating: str
# sap_points: float
@app.get("/buildings", response_model=list[Building])
async def get_buildings(req: Request):
    headers = utils.get_headers(req.headers)
    query = queries.get_buildings()
    results = jena.get(query, headers)
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


@app.get("/buildings/{uprn}", response_model=FullBuilding)
async def get_building_details(uprn: str, req: Request):
    headers = utils.get_headers(req.headers)

    query = queries.get_building(uprn)
    results = jena.get(query, headers)

    if len(results["results"]["bindings"]) == 0:
        # throw error
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


# Temporary model / ontology stuff...


@app.get("/ontology/class")
async def get_class(classUri: str = Query()):
    query = (
        '''
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?uri ?superClass
    WHERE {
        BIND (URI("'''
        + classUri
        + """") as ?uri)
        ?uri rdfs:subClassOf ?superClass
    }
    """
    )
    results = utils.aggregate(ontQuery(query), "uri")
    return results


@app.get("/ontology/superclasses")
async def get_superclasses(classUris: list[str] = Query()): #noqa
    classUriStr = ", ".join([f"<{value}>" for value in classUris])
    query = (
        """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?uri ?superClass
    WHERE {
        ?uri rdfs:subClassOf ?superClass
        FILTER (?uri in ("""
        + classUriStr
        + """))
    }
    """
    )
    results = utils.aggregate(ontQuery(query), "uri")
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config.port)
