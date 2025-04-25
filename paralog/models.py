from pydantic import BaseModel

__license__ = """
Copyright (c) Telicent Ltd.

This software is licensed under the terms found in the LICENSE file of this repository.

The above copyright notice and license conditions shall be included in all
copies or substantial portions of the Software.
"""


class Assessment(BaseModel):
    """
    Assessment objects were used extensively in the early CARVER work for NDT.
    They're less important now, but there is still one in the dataset at least
    """
    uri: str
    name: str
    numberOfAssessedItems: int


class AssetSummary(BaseModel):
    """
    #Wrapper for reduced data about an Asset - used for providing high-level summaries -
    without hitting the database for all the information that would be returned as Asset
    A future version of the API should probably merge this with Asset (this was built for a demo only)
    """
    uri: str
    type: str
    lat: float | None = None
    lon: float | None = None
    dependentCount: int | None = None
    dependentCriticalitySum: float | None = None
    partCount: int | None = None


class IesType(BaseModel):
    """
    IesType is a simple object wrapper for returning a type (RDFS Class).
    Optionally includes a count of the number of instances and a list of the parent classes
    """
    uri: str
    assetCount: int | None = None
    subClassOf: list[str] | None = None


class Dependency(BaseModel):
    """
    A wrapper for dependencies between a provider asset and a dependent asset.
    """
    dependencyUri: str
    providerNode: str
    providerNodeType: str
    providerName: str | None = None
    dependentNode: str
    dependentNodeType: str
    dependentName: str | None = None
    criticalityRating: float | None = None
    osmID: str | None = None


class Asset(BaseModel):
    """
    Wrapper for IES objects that are considered Assets (e.g. Facilities, Locations, etc.) in the assessment.
    """
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


class Person(BaseModel):
    """
    Wrapper object for ies:Person
    """
    uri: str
    name: str | None = None


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
