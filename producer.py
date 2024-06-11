import Geohash  # (pip install Geohash but also pip install python-geohash )
import pandas as pd
from OSGridConverter import grid2latlong
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import XSD
from termcolor import colored

import ies_functions as ies
from logger import TelicentLogger, TelicentLogLevel

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

iesUri = "http://ies.data.gov.uk/ontology/ies4#"

facility = URIRef(iesUri+"Facility")
radioMast = URIRef(iesUri+"RadioMast")
telExch = URIRef(iesUri+"TelephoneExchange")
connector = URIRef(iesUri+"Connector")
ict = URIRef(iesUri+"isConnectedTo")
hc = URIRef(iesUri+"hasCharacteristic")
assCrity = URIRef(iesUri+"AssessCriticality")
serStation = URIRef(iesUri+"ServiceStation")
fuelStore = URIRef(iesUri+"FuelStorageFacility")
lngStore = URIRef(iesUri+"LNGStorageFacility")
road = URIRef(iesUri+"Road")
railway = URIRef(iesUri+"Railway")
address = URIRef(iesUri+"Address")

gridArea = URIRef(iesUri+"MapGridArea")
gridRef = URIRef(iesUri+"OSGridReference")

carver = URIRef(iesUri+"CarverAssessment")

crit = URIRef(iesUri+"criticalityRating")


rdfsComment = URIRef("http://www.w3.org/2000/01/rdf-schema#comment")
telicentPrimary = URIRef("http://telicent.io/ontology/primaryName")

assetStartCol = 4 #The index of the first column that contains criticality data

logger = TelicentLogger("producer")


def inGridRef(assetUri,gr,graph):
    if not pd.isna(gr):
        grid = ies.instantiate(graph, gridArea,instance=URIRef("http://ordnancesurvey.co.uk/grid#"+gr.replace(" ","")))
        ref = ies.instantiate(graph, gridRef,instance=URIRef("http://ordnancesurvey.co.uk/gridRef#"+gr.replace(" ","")))
        ies.addToGraph(graph, assetUri, ies.il, grid)
        ies.addToGraph(graph, grid, ies.iib, ref)
        ies.addToGraph(graph, ref, ies.rv, Literal(gr))
        coordinate = grid2latlong(gr)
        ies.addIdentifier(graph,grid,coordinate.latitude,idClass=ies.latitude)
        ies.addIdentifier(graph,grid,coordinate.longitude,idClass=ies.longitude)

        return grid
    else:
        return None

def CreateAssetAssTypeHelper(assetNumber, assetName):
    assType = facility
    #comms stuff
    if assetNumber[0] == "V":
        assType = address
    if "communications mast" in assetName.lower():
        assType = radioMast
    elif "tv mast" in assetName.lower():
        assType = radioMast
    elif "telephone exchange" in assetName.lower():
        assType = telExch
    elif ("service station" in assetName.lower() or "garage" in assetName.lower()
          or "filling station" in assetName.lower()):
        assType = serStation
    elif ("fuels storage" in assetName.lower() or "fuel storage" in assetName.lower()
          or "fuel depot" in assetName.lower()):
        assType = fuelStore
    elif "lng stor" in assetName.lower() in assetName.lower():
        assType = lngStore
    elif assetName[0:4].lower() == "rail":
        assType = railway
    elif assetName[0:4].lower() == "road":
        assType = road

    return assType

def createAsset(assetNumber,assetName,gridRef,segments,graph,uriStub):
    assType = CreateAssetAssTypeHelper(assetNumber=assetNumber, assetName=assetName)
    ass = ies.instantiate(graph, assType, instance = URIRef(uriStub+assetNumber))
    ies.addIdentifier(graph,ass,assetNumber,idUri=URIRef(uriStub+assetNumber+"_ID"))
    ies.addName(graph,ass,assetName,nameUri=URIRef(uriStub+assetNumber+"_Name"))
    ies.addToGraph(graph, ass, telicentPrimary, Literal(assetName))
    if gridRef and gridRef != "" and not pd.isna(gridRef):
        _ = inGridRef(ass, gridRef,graph)
    else:
        ghDict = {}
        for row in segments.iterrows():
            segment=row[1]
            segUri = URIRef(uriStub+assetNumber+"_segment_"+str(segment["SegmentSerial"]).zfill(4))
            ies.instantiate(graph, assType, instance = segUri)
            ies.addToGraph(graph,segUri,ies.ipao,ass)
            gh1 = Geohash.encode(float(segment["fromLat"]),float(segment["fromLon"]))
            if gh1 in ghDict:
                geoPoint1 = ghDict[gh1]
            else:
                geoPoint1 = ies.createGeoPoint(graph,segment["fromLat"],segment["fromLon"])
                ghDict[gh1] = geoPoint1
            ies.addToGraph(graph,segUri,ict,geoPoint1)
            gh2 = Geohash.encode(float(segment["toLat"]),float(segment["toLon"]))
            if gh2 in ghDict:
                geoPoint2 = ghDict[gh2]
            else:
                geoPoint2 = ies.createGeoPoint(graph,segment["toLat"],segment["toLon"])
                ghDict[gh2] = geoPoint2
            ies.addToGraph(graph,segUri,ict,geoPoint2)


    return ass



def mapAssessments(graph,uriStub,assessmentList,parentName=None):
    for assessmentLetter in assessmentList:

        assessmentName = assessmentList[assessmentLetter]["name"]

        myAssessment = ies.instantiate(graph,carver,
                                       instance=URIRef(uriStub+assessmentName.replace(" ","_")+"_Assessment"))
        assessmentList[assessmentLetter]["uri"] = myAssessment
        ies.addName(graph,myAssessment,assessmentName,
                    nameUri=URIRef(uriStub+assessmentName.replace(" ","_")+"_Assessment_Name"))
        if parentName:
            parentAssessment = ies.instantiate(graph,carver,instance=URIRef(uriStub+parentName.replace(" ","_")))
            ies.addName(graph,parentAssessment,parentName,nameUri=URIRef(uriStub+parentName.replace(" ","_")+"_Name"))
            ies.addToGraph(graph, myAssessment, ies.ipao, parentAssessment)



def mapAssets(graph,uriStub,df,assessmentList,segments):
    asses = df["Asset Number"].to_list()
    for row in df.iterrows():
        rawAss=row[1]
        assUri = createAsset(rawAss[0],rawAss[1],rawAss[2],segments[segments["AssetID"]==rawAss[0]],graph,uriStub)
        assessObj=assessmentList[rawAss[0][0]]
        ies.addToGraph(graph,assessObj["uri"],ies.ass,assUri)

        for i,related in enumerate(asses):
            colNum = i+assetStartCol
            score = rawAss[colNum]
            if not pd.isna(score) and related > rawAss[0]:
                conn = ies.instantiate(graph, connector,instance=URIRef(uriStub+"connector_"+rawAss[0]+"_"+related))
                ies.addToGraph(graph, conn, ict, URIRef(uriStub+rawAss[0]))
                ies.addToGraph(graph, conn, ict, URIRef(uriStub+related))
                myAsses = ies.instantiate(graph, assCrity)
                ies.addToGraph(graph, myAsses, ies.ass, conn)
                try:
                    ies.addToGraph(graph, myAsses, crit, Literal(float(score),datatype=XSD.float))
                except Exception:
                    logger(method=mapAssets.__name__,
                           message=colored("ERROR: could not convert: "+str(score) + "[" + str(len(score))+
                                  "] to float for criticality score on connector_"+rawAss[0]+"_"+related,"red"),
                                  level=TelicentLogLevel.ERROR)



desc_secuirty_lookup = {
    "V": "deployed_organisation:NHS,nationality:GBR,clearance:TS",
    "E": "nationality:GBR,clearance:S",
    "T": "clearance:S"
}
def mapAssetDescriptions(graph,uriStub,df):
    for row in df.iterrows():

        assetRow = row[1]
        asset = URIRef(uriStub+assetRow[0])
        ies.addToGraph(graph, asset, rdfsComment, Literal(assetRow[1]))



def runData(uriStub):
    ies.setDataUri(uriStub)
    graph = Graph()
    assessments= {"T":{"name":"Transport"},"E":{"name":"Energy"},"W":{"name":"Water"},"F":{"name":"Fuel"},
                  "C":{"name":"Communications"},"M":{"name":"Medical"},"V":{"name":"Vulnerable People"}}

    tableDf = pd.read_csv("./iow_carver_with_vuln.csv")
    descriptionDf = pd.read_csv("./iow_descriptions.csv")


    #First of all, create an assessment for each one in our assessments dict.
    #Make each one a part of the IoW CARVER Assessment
    mapAssessments(graph,uriStub,assessments,parentName="IoW CARVER Assessment")

    roadSegmentsDF = pd.read_csv("./iow_road_segments.csv")
    #Now step through every asset and stream each on onto Kafka
    mapAssets(graph,uriStub,tableDf,assessments,roadSegmentsDF)

    mapAssetDescriptions(graph,uriStub,descriptionDf)

    graph.serialize(destination="assess.ttl")


runData("http://telicent.io/data#")
