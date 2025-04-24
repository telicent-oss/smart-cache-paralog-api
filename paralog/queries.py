PREFIXES = """
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX ies: <http://ies.data.gov.uk/ontology/ies4#>
PREFIX telicent: <http://telicent.io/ontology/>
PREFIX geoplace: <https://www.geoplace.co.uk/addresses-streets/location-data/the-uprn#>
PREFIX data: <http://nationaldigitaltwin.gov.uk/data#>
PREFIX ies: <http://ies.data.gov.uk/ontology/ies4#>
PREFIX qudt: <http://qudt.org/2.1/schema/qudt/>
PREFIX ndt: <http://nationaldigitaltwin.gov.uk/ontology#>
PREFIX iesuncertainty: <http://ies.data.gov.uk/ontology/ies_uncertainty_proposal/v2.0#>
"""


async def get_all_assessments():
    return (
        PREFIXES
        + """
        SELECT ?uri ?name (COUNT(?asset) AS ?numberOfAssessedItems)
        WHERE {
            ?uri a ies:CarverAssessment .
            ?uri ies:hasName ?cAssNameObj .
            ?cAssNameObj ies:representationValue ?name .
            OPTIONAL {
                ?uri ies:assessed ?asset
            }
        }
        GROUP BY ?uri ?name
    """
    )


async def get_assets_by_assessment(assessment_uri: str, types: list[str] | None = None):
    if types is None:
        types = []
    if len(types) > 0:
        types_list = ", ".join([f"<{value}>" for value in types])
        types_str = "FILTER (?type IN (" + types_list + "))"
    else:
        types_str = ""
    return (
        PREFIXES
        + '''
        SELECT DISTINCT ?uri ?type ?lat ?lon (COUNT(?dependencyUri) AS ?dependentCount) (SUM(?criticalityRating) AS
        ?dependentCriticalitySum) (COUNT(?part) AS ?partCount)
        WHERE {
            BIND (URI("'''
        + assessment_uri
        + """") as ?assessment)
            BIND(0.0 as ?defaultCrit)
            ?assessment ies:assessed ?uri .
            ?uri rdf:type ?type .
            OPTIONAL {
                ?uri ies:inLocation ?loc .
                ?loc ies:isIdentifiedBy ?latObj .
                ?latObj a ies:Latitude .
                ?latObj ies:representationValue ?lat .
                ?loc ies:isIdentifiedBy ?lonObj .
                ?lonObj a ies:Longitude .
                ?lonObj ies:representationValue ?lon .
            }
            OPTIONAL {
                ?provider ies:isParticipationOf ?uri .
                ?provider ies:isParticipantIn ?dependencyUri .
                ?provider a ies:Provider .
                OPTIONAL {
                    ?dependencyUri ies:criticalityRating ?crit
                }

            }
            OPTIONAL {
                ?part ies:isPartOf ?uri .
            }
            BIND(COALESCE(?crit, ?defaultCrit) as ?criticalityRating)
            FILTER NOT EXISTS {
                ?uri a ies:Dependency
            }
            """
        + types_str
        + """
        }
        GROUP BY ?uri ?type ?lat ?lon
    """
    )


async def get_asset_types_by_assessment(assessment_uri):
    return (
            PREFIXES
            + '''
        SELECT ?uri (COUNT(?asset) AS ?assetCount)
        WHERE {
            BIND (URI("'''
            + assessment_uri
            + """") as ?assessment)
            ?assessment ies:assessed ?asset .
            ?asset rdf:type ?uri .
            NOT EXISTS {
                ?asset a ies:Dependency
            }
        }
        GROUP BY ?uri
    """
    )


async def get_dependencies_by_assessment(assessment_uri: str, types: list[str] | None = None):
    if types is None:
        types = []
    if len(types) > 0:
        types_list = ", ".join([f"<{value}>" for value in types])
        dep_types_str = "FILTER (?dependentNodeType IN (" + types_list + "))"
        prov_types_str = "FILTER (?providerNodeType IN (" + types_list + "))"
    else:
        dep_types_str = ""
        prov_types_str = ""

    return (
        PREFIXES
        + '''
        SELECT DISTINCT ?dependencyUri ?providerNode ?providerNodeType
        ?dependentNode ?dependentNodeType ?criticalityRating ?osmID
        WHERE {
            BIND (URI("'''
        + assessment_uri
        + """") as ?assessment)
            ?provider ies:isParticipationOf ?providerNode .
            ?providerNode a ?providerNodeType .
            ?provider ies:isParticipantIn ?dependencyUri .
            ?provider a ies:Provider .
            ?dependent ies:isParticipantIn ?dependencyUri .
            ?dependent a ies:Dependent .
            ?dependent ies:isParticipationOf  ?dependentNode .
            ?dependentNode a ?dependentNodeType .
            OPTIONAL {
                ?dependencyUri ies:criticalityRating ?criticalityRating
            }
            OPTIONAL {
                ?dependencyUri ies:isIdentifiedBy ?osmIDobj .
                ?osmIDobj a ies:OpenStreetmapIdentifier .
                ?osmIDobj ies:representationValue ?osmID .
            }
            """
        + dep_types_str
        + """
            """
        + prov_types_str
        + """
        }
        ORDER BY ?id
    """
    )


async def get_asset(asset_uri: str):
    return (
        PREFIXES
        + '''
        SELECT DISTINCT ?uri ?assetType ?name ?osmID ?lat ?lon ?desc ?wikipediaPage
        ?webPage ?address (COUNT(?dependencyUri) AS ?dependentCount) (SUM(?criticalityRating)
        AS ?dependentCriticalitySum)
        WHERE {
            BIND (URI("'''
        + asset_uri
        + """") as ?uri)
            ?uri a ?assetType
            OPTIONAL {
                ?uri ies:isIdentifiedBy ?osmIDobj .
                ?osmIDobj ies:representationValue ?osmID .
                ?osmIDobj a ies:OpenStreetmapIdentifier .
            }
            OPTIONAL {
                ?uri ies:inLocation ?loc .
                ?loc ies:isIdentifiedBy ?latObj .
                ?latObj a ies:Latitude .
                ?latObj ies:representationValue ?lat .
                ?loc ies:isIdentifiedBy ?lonObj .
                ?lonObj a ies:Longitude .
                ?lonObj ies:representationValue ?lon .
            }
            OPTIONAL {
                ?uri rdfs:comment ?desc
            }
            OPTIONAL {
                ?uri ies:isIdentifiedBy ?wikipediaObj .
                ?wikipediaObj a ies:WikipediaPage .
                ?wikipediaObj ies:representationValue ?wikipediaPage
            }
            OPTIONAL {
                ?uri ies:isIdentifiedBy ?webPageObj .
                ?webPageObj a ies:URL .
                ?webPageObj ies:representationValue ?webPage .
            }
            OPTIONAL {
                ?uri ies:hasName ?nameObj .
                ?nameObj ies:representationValue ?name
            }
            OPTIONAL {
                ?uri ies:isIdentifiedBy ?addrObj .
                ?addrObj a ies:LineOfAddress .
                ?addrObj ies:representationValue ?address
            }
            OPTIONAL {
                ?provider ies:isParticipationOf ?uri .
                ?provider ies:isParticipantIn ?dependencyUri .
                ?provider a ies:Provider .
                OPTIONAL {
                    ?dependencyUri ies:criticalityRating ?crit
                }

            }
            BIND(COALESCE(?crit, ?defaultCrit) as ?criticalityRating)
        }
        GROUP BY ?uri ?assetType ?name ?osmID ?lat ?lon ?desc ?wikipediaPage ?webPage ?address
    """
    )


async def get_dependencies(asset_uri: str, direction: str):
    if direction == "providers":
        bind_str = f'BIND (URI("{asset_uri}") as ?dependentNode)'
    else:
        bind_str = f'BIND (URI("{asset_uri}") as ?providerNode)'

    return (
        PREFIXES
        + """
        SELECT ?dependentNode ?dependentNodeType ?dependencyUri ?criticalityRating
        ?osmID ?providerNode ?providerNodeType ?dependentName ?providerName
        WHERE {
            """
        + bind_str
        + """
            ?provider ies:isParticipationOf ?providerNode .
            ?providerNode a ?providerNodeType .
            ?provider ies:isParticipantIn ?dependencyUri .
            ?provider a ies:Provider .
            ?dependent ies:isParticipantIn ?dependencyUri .
            ?dependent a ies:Dependent .
            ?dependent ies:isParticipationOf  ?dependentNode .
            ?dependentNode a ?dependentNodeType .
            OPTIONAL {
                ?dependencyUri ies:criticalityRating ?criticalityRating
            }
            OPTIONAL {
                ?dependencyUri ies:isIdentifiedBy ?osmIDobj .
                ?osmIDobj a ies:OpenStreetmapIdentifier .
                ?osmIDobj ies:representationValue ?osmID .
            }
            OPTIONAL {
                ?dependentNode <http://telicent.io/ontology/primaryName> ?dependentName .
            }
            OPTIONAL {
                ?providerNode <http://telicent.io/ontology/primaryName> ?providerName .
            }
        }
    """
    )


async def get_asset_parts(assetUri: str):
    return (
        PREFIXES
        + '''
        SELECT DISTINCT ?uri ?lat1 ?lon1 ?lat2 ?lon2 ?id ?type
        WHERE {
            BIND (URI("'''
        + assetUri
        + """") as ?assetUri)
            ?uri rdf:type ?type .
            ?uri ies:isPartOf ?assetUri.
            OPTIONAL {
                ?uri ies:isConnectedTo ?loc1 .
                ?loc1 ies:isIdentifiedBy ?latObj1 .
                ?latObj1 a ies:Latitude .
                ?latObj1 ies:representationValue ?lat1 .
                ?loc1 ies:isIdentifiedBy ?lonObj1 .
                ?lonObj1 a ies:Longitude .
                ?lonObj1 ies:representationValue ?lon1 .
                ?uri ies:isConnectedTo ?loc2 .
                ?loc2 ies:isIdentifiedBy ?latObj2 .
                ?latObj2 a ies:Latitude .
                ?latObj2 ies:representationValue ?lat2 .
                ?loc2 ies:isIdentifiedBy ?lonObj2 .
                ?lonObj2 a ies:Longitude .
                ?lonObj2 ies:representationValue ?lon2 .
            }
            FILTER (?loc1 != ?loc2)
    }
        ORDER BY ?uri
    """
    )

async def get_residents(asset_uri):
   return (
        PREFIXES
        + '''
        SELECT DISTINCT ?uri ?type ?name
        WHERE {
            BIND (URI("'''
        + asset_uri
        + """") as ?assetUri)
            ?residentState ies:isStateOf ?uri .
            ?residentState ies:residesIn ?assetUri .
            ?uri rdf:type ?type .
            OPTIONAL {
                ?uri ies:hasName ?perNameObj .
                ?perNameObj ies:representationValue ?name
            }
        }
        ORDER BY ?uri
    """
    )


async def get_participations(asset_uri):
    return (
        PREFIXES
        + '''
        SELECT DISTINCT ?participationType ?event ?eventType
        WHERE {
            BIND (URI("'''
        + asset_uri
        + """") as ?assetUri)
            ?participation ies:isParticipationOf ?assetUri .
            ?participation rdf:type ?participationType .
            ?participation ies:isParticipantIn ?event .
            ?event rdf:type ?eventType .
        }
        ORDER BY ?uri
    """
    )


async def get_participants(event_uri):
    return (
        PREFIXES
        + '''
        SELECT DISTINCT ?participationType ?asset ?assetType
        WHERE {
            BIND (URI("'''
        + event_uri
        + """") as ?event)
            ?participation ies:isParticipationOf ?asset .
            ?participation rdf:type ?participationType .
            ?participation ies:isParticipantIn ?event .
            ?asset rdf:type ?assetType .
        }
        ORDER BY ?uri
    """
    )


async def get_residence(person_uri: str):
    return (
        PREFIXES
        + '''
        SELECT DISTINCT ?uri ?assetType ?name ?osmID ?lat ?lon ?desc ?wikipediaPage ?webPage ?address
        WHERE {
            BIND (URI("'''
        + person_uri
        + """") as ?resident)
            ?residentState ies:isStateOf ?resident .
            ?residentState ies:residesIn ?uri .
            ?uri rdf:type ?assetType .
            OPTIONAL {
                ?uri ies:isIdentifiedBy ?osmIDobj .
                ?osmIDobj ies:representationValue ?osmID .
                ?osmIDobj a ies:OpenStreetmapIdentifier .
            }
            OPTIONAL {
                ?uri ies:inLocation ?loc .
                ?loc ies:isIdentifiedBy ?latObj .
                ?latObj a ies:Latitude .
                ?latObj ies:representationValue ?lat .
                ?loc ies:isIdentifiedBy ?lonObj .
                ?lonObj a ies:Longitude .
                ?lonObj ies:representationValue ?lon .
            }
            OPTIONAL {
                ?uri rdfs:comment ?desc
            }
            OPTIONAL {
                ?uri ies:isIdentifiedBy ?wikipediaObj .
                ?wikipediaObj a ies:WikipediaPage .
                ?wikipediaObj ies:representationValue ?wikipediaPage
            }
            OPTIONAL {
                ?uri ies:isIdentifiedBy ?webPageObj .
                ?webPageObj a ies:URL .
                ?webPageObj ies:representationValue ?webPage .
            }
            OPTIONAL {
                ?uri ies:hasName ?nameObj .
                ?nameObj ies:representationValue ?name
            }
            OPTIONAL {
                ?uri ies:isIdentifiedBy ?addrObj .
                ?addrObj a ies:LineOfAddress .
                ?addrObj ies:representationValue ?address
            }
        }
        ORDER BY ?residence
    """
    )


async def get_flood_areas():
    return (
        PREFIXES
        + """
        SELECT ?floodWatchArea ?floodWatchAreaName ?geoJsonUri ?floodArea ?floodAreaName ?faGeoJsonUri
        WHERE {
            ?floodWatchArea rdf:type <http://ies.data.gov.uk/ontology/ies4#FloodWatchArea> .
            ?floodWatchArea telicent:primaryName ?floodWatchAreaName .
            ?floodWatchArea ies:isRepresentedAs ?geoJsonUri .
            OPTIONAL {
                ?floodArea ies:inLocation ?floodWatchArea .
                ?floodArea telicent:primaryName ?floodAreaName .
                ?floodArea  ies:isRepresentedAs ?faGeoJsonUri .
            }
        }
    """
    )


async def get_flood_area_polygon(uri):
    return (
        PREFIXES
        + """
        SELECT ?geoJsonValue
        WHERE {
        <%s> ies:representationValue ?geoJsonValue .
        }
        """
        % uri
    )


async def get_states(uri):
    return (
        PREFIXES
        + """
        SELECT ?stateUri ?stateType ?starts ?ends ?inPeriod ?repType ?repValue
        WHERE {
            ?stateUri ies:isStateOf <%s>  .
            ?stateUri a ?stateType .
            OPTIONAL {
                ?stateUri ies:inPeriod ?pp .
                ?pp ies:iso8601PeriodRepresentation ?inPeriod .
            }
            OPTIONAL {
                ?startState ies:isStartOf ?stateUri .
                ?startState ies:inPeriod ?startPP .
                ?startPP ies:iso8601PeriodRepresentation ?starts .
            }
            OPTIONAL {
                ?endState ies:isEndOf ?stateUri .
                ?endState ies:inPeriod ?endPP .
                ?endPP ies:iso8601PeriodRepresentation ?ends .
            }
            OPTIONAL {
                ?stateUri ies:isRepresentedAs ?repObject .
                ?repObject rdf:type ?repType .
                ?repObject ies:representationValue ?repValue
            }
        }
        """
        % uri
    )


async def get_buildings():
    return (
        PREFIXES
        + """
SELECT
    ?name
    ?building
    ?uprn_id
    (GROUP_CONCAT(DISTINCT ?building_type; SEPARATOR=";") AS ?building_types)
    ?lat_literal
    ?lon_literal
    ?epc_rating
WHERE {
    ?building telicent:primaryName ?name .
    ?building ies:isIdentifiedBy ?uprn .
    ?uprn rdf:type geoplace:UniquePropertyReferenceNumber .
    ?uprn ies:representationValue ?uprn_id .

    ?building rdf:type ?building_type .
    ?building ies:inLocation ?geopoint .

    ?geopoint rdf:type ies:GeoPoint .

    ?geopoint ies:isIdentifiedBy ?lat .
    ?lat rdf:type ies:Latitude .
    ?lat ies:representationValue ?lat_literal .

    ?geopoint ies:isIdentifiedBy ?lon .
    ?lon rdf:type ies:Longitude .
    ?lon ies:representationValue ?lon_literal .

    ?state ies:isStateOf ?building .
    ?state a ?epc_rating .

}
GROUP BY
    ?name
    ?uprn_id
    ?building
    ?lat_literal
    ?lon_literal
    ?epc_rating
    """
    )


async def get_building(id):
    query = (
        "{p}"
        "SELECT "
        "?name "
        "({uri} as ?uprn_id) "
        "?building "
        '(GROUP_CONCAT(DISTINCT ?building_type; SEPARATOR="; ") AS ?building_types) '
        "?inspection_date_literal "
        "?epc_rating "
        "?sap_points "
        "?line_of_address_literal "
        "?postcode_literal "
        "?lat_literal "
        "?lon_literal "
        "WHERE {{"
        "?building telicent:primaryName ?name . "
        "?building ies:isIdentifiedBy ?uprn . "
        "?uprn ies:representationValue '{uri}' . "
        "?building rdf:type ?building_type. "
        "?building ies:inLocation ?address . "
        "?address ies:isIdentifiedBy ?postcode . "
        "?postcode rdf:type ies:PostalCode . "
        "?postcode ies:representationValue ?postcode_literal . "
        "?address ies:isIdentifiedBy ?line_of_address . "
        "?line_of_address rdf:type ies:FirstLineOfAddress . "
        "?line_of_address ies:representationValue ?line_of_address_literal . "
        "OPTIONAL {{"
        "?building ies:inLocation ?geopoint . "
        "?geopoint rdf:type ies:GeoPoint . "
        "?geopoint ies:isIdentifiedBy ?lat . "
        "?lat rdf:type ies:Latitude . "
        "?lat ies:representationValue ?lat_literal . "
        "?geopoint ies:isIdentifiedBy ?lon . "
        "?lon rdf:type ies:Longitude . "
        "?lon ies:representationValue ?lon_literal . "
        "}} "
        "?state ies:isStateOf ?building . "
        "?state ies:inPeriod ?inspection_date . "
        "?inspection_date ies:iso8601PeriodRepresentation ?inspection_date_literal . "
        "?state a ?epc_rating . "
        "?state ies:hasCharacteristic ?quantity . "
        "?quantity qudt:value ?sap_points . "
        "FILTER ("
        'regex(str(?epc_rating), "^http://gov.uk/government/organisations/department-for-levelling-up-housing-and-communities/ontology/epc#")'
        ")"
        "}}"
        "GROUP BY"
        "?name "
        "?building "
        "?inspection_date_literal "
        "?epc_rating "
        "?sap_points "
        "?line_of_address_literal "
        "?postcode_literal "
        "?lat_literal "
        "?lon_literal "
    )
    query = query.format(uri=id, p=PREFIXES)
    return query
