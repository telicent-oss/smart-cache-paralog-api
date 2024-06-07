import json
import uuid

import Geohash  # (pip install Geohash but also pip install python-geohash )
from kafka import KafkaProducer
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD

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

#The URI namespaces we're going to be using
iesUri = "http://ies.data.gov.uk/ontology/ies4#"
ituUri = "http://itu.int"
imoUri = "http://imo.org"
iso8601Uri = "http://iso.org/iso8601#"
#this data URI can be changed to whatever you want:
dataUri = "http://ais.data.gov.uk/ais-ies-test#"
rdfsComment = URIRef("http://www.w3.org/2000/01/rdf-schema#comment")
telicentPrimary = URIRef("http://telicent.io/ontology/primaryName")

"""
Now create some uri objects for the key IES classes we're going to be using -
These are just in-memory reference data the python can use to easily instantiate our data
In production, we automate this from the schema, but that makes it quite hard to follow the code.
For this, I've itemised out each class we use so it should make more sense
"""
accountHolder = URIRef(iesUri+"AccountHolder")
address = URIRef(iesUri+"Address")
aircraft = URIRef(iesUri+"Aircraft")
airport = URIRef(iesUri+"Airport")
arrival = URIRef(iesUri+"Arrival")
assess = URIRef(iesUri+"Assess")
assessor = URIRef(iesUri+"Assessor")
assessProbability=URIRef(iesUri+"AssessProbability")
assessToBeRemoteChance=URIRef(iesUri+"AssessToBeRemoteChance")
assessToBeHighlyUnlikely=URIRef(iesUri+"AssessToBeHighlyUnlikely")
assessToBeUnlikely=URIRef(iesUri+"AssessToBeUnlikely")
assessToBeRealisticPossibility=URIRef(iesUri+"AssessToBeRealisticPossibility")
assessToBeLikelyOrProbably=URIRef(iesUri+"AssessToBeLikelyOrProbably")
assessToBeHighlyLikely=URIRef(iesUri+"AssessToBeHighlyLikely")
assessToBeAlmostCertain=URIRef(iesUri+"AssessToBeAlmostCertain")
attendance=URIRef(iesUri+"Attendance")
birthState = URIRef(iesUri+"BirthState")
boundingState = URIRef(iesUri+"BoundingState")
callsign=URIRef(iesUri+"Callsign")
carrier = URIRef(iesUri+"Carrier")
commsIdentifier = URIRef(iesUri+"CommunicationsIdentifier")
country = URIRef(iesUri+"Country")
deathState = URIRef(iesUri+"DeathState")
event = URIRef(iesUri+"Event")
eventParticipant = URIRef(iesUri+"EventParticipant")
financialAccount = URIRef(iesUri+"FinancialAccount")
firstLineOfAddress = URIRef(iesUri+"FirstLineOfAddress")
follow = URIRef(iesUri+"Follow")
follower = URIRef(iesUri+"Follower")
followed = URIRef(iesUri+"Followed")
geoIdentity = URIRef(iesUri+"GeoIdentity")
geoPoint = URIRef(iesUri+"GeoPoint")
givenName = URIRef(iesUri+"GivenName")
icaoCode = URIRef(iesUri+"ICAOCode")
identifier = URIRef(iesUri+"Identifier")
iso3166A3 = URIRef(iesUri+"ISO3166Alpha_3")
latitude = URIRef(iesUri+"Latitude")
locationTransponder = URIRef(iesUri+"LocationTransponder")
locationObservation = URIRef(iesUri+"LocationObservation")
longitude = URIRef(iesUri+"Longitude")
meeting = URIRef(iesUri+"Meeting")
meetingChair = URIRef(iesUri+"MeetingChair")
name = URIRef(iesUri+"Name")
namingScheme = URIRef(iesUri+"NamingScheme")
observation = URIRef(iesUri+"Observation")
observedLocation = URIRef(iesUri+"ObservedLocation")
observedTarget = URIRef(iesUri+"ObservedTarget")
organisation = URIRef(iesUri+"Organisation")
organisationName = URIRef(iesUri+"OrganisationName")
particularPeriod = URIRef(iesUri+"ParticularPeriod")
person = URIRef(iesUri+"Person")
personName = URIRef(iesUri+"PersonName")
personState = URIRef(iesUri+"PersonState")
placeName = URIRef(iesUri+"PlaceName")
port = URIRef(iesUri+"Port")
postalCode = URIRef(iesUri+"PostalCode")
possibleWorld = URIRef(iesUri+"PossibleWorld")
probabilityRepresentation = URIRef(iesUri+"ProbabilityRepresentation")
purchase = URIRef(iesUri+"Purchase")
regionOfCountry = URIRef(iesUri+"RegionOfCountry")
roadVehicle = URIRef(iesUri+"RoadVehicle")
sailing = URIRef(iesUri+"Sailing")
sendingAccount = URIRef(iesUri+"SendingAccount")
surname = URIRef(iesUri+"Surname")
system = URIRef(iesUri+"System")
unLocode=URIRef(iesUri+"UN_LOCODE")
vehicleIdentificationNumber = URIRef(iesUri+"VehicleIdentificationNumber")
vehicleName = URIRef(iesUri+"VehicleName")
vehicleState = URIRef(iesUri+"VehicleState")

#New stuff, not yet approved !
classOfMeasure = URIRef(iesUri+"ClassOfMeasure")
cooper = URIRef(iesUri+"CooperAtSea")
coopering = URIRef(iesUri+"CooperingAtSea")
epsgParams = [URIRef(iesUri+"EpsgParameter1"),URIRef(iesUri+"EpsgParameter2"),
              URIRef(iesUri+"EpsgParameter3"),URIRef(iesUri+"EpsgParameter4")]
epsgRep = URIRef(iesUri+"EpsgGeoPointRepresentation")
inRep = URIRef(iesUri+"inRepresentation")
measure = URIRef(iesUri+"Measure")
measurement = URIRef(iesUri+"Measurement")
measureValue = URIRef(iesUri+"MeasureValue")
phiaAssYard = URIRef(iesUri+"PhiaAssessmentYardStick")
primaryGivenName = URIRef(iesUri+"PrimaryGivenName") #Addition to IES, subClassOf GivenName
unitOfMeasure = URIRef(iesUri+"UnitOfMeasure")
vessel = URIRef(iesUri+"Vessel")
vehicleUsed = URIRef(iesUri+"VehicleUsed")

imoNS = URIRef(imoUri+"#imo-NamingScheme")


#Now the IES predicates (properties / relationships) we'll be using
apn = URIRef(iesUri+"associatedPersonName")
ass = URIRef(iesUri+"assessed")
eb = URIRef(iesUri+"employedBy")
ha = URIRef(iesUri+"holdsAccount")
hn = URIRef(iesUri+"hasName")
hr = URIRef(iesUri+"hasRepresentation")
hv = URIRef(iesUri+"hasValue")
ieo = URIRef(iesUri+"isEndOf")
iib = URIRef(iesUri+"isIdentifiedBy")
ins = URIRef(iesUri+"inScheme")
ip = URIRef(iesUri+"inPeriod")
ipao = URIRef(iesUri+"isPartOf")
ipi = URIRef(iesUri+"isParticipantIn")
ipo = URIRef(iesUri+"isParticipationOf")
ir = URIRef(iesUri+"inRepresentation")
iso = URIRef(iesUri+"isStartOf")
isto = URIRef(iesUri+"isStateOf")
isoP = URIRef(iesUri+"iso8601PeriodRepresentation")
kao = URIRef(iesUri+"knownAssociateOf")
mu = URIRef(iesUri+"measureUnit")
owns = URIRef(iesUri+"owns")
parentOf = URIRef(iesUri+"parentOf")
ri = URIRef(iesUri+"residesIn")
rv = URIRef(iesUri+"representationValue")
so = URIRef(iesUri+"schemeOwner")

#New stuff, not yet approved !
ec = URIRef(iesUri+"epsgCode")
il = URIRef(iesUri+"inLocation")
mc = URIRef(iesUri+"measureClass")
och = URIRef(iesUri+"observedCharacteristic")


mmsiNs = URIRef(ituUri+"#mmsi-NamingScheme") #Make a URI for the MMSI naming schema from the ITU's URI

def iesClass(className):
    return URIRef(iesUri+className)

def addComment(iesGraph,item,comment):
    addToGraph(iesGraph=iesGraph,subject=item,predicate=rdfsComment,obj=Literal(comment))

def addTelicentName(iesGraph,item,name):
    addToGraph(iesGraph=iesGraph,subject=item,predicate=telicentPrimary,obj=Literal(name))

def setDataUri(uri):
    global dataUri
    dataUri = uri

#delete all triples in the graph
def clearGraph(iesGraph):
    iesGraph.remove((None, None, None))

#clears the graph and adds all the boilerplate stuff
def initialiseGraph(iesGraph=None):
    if iesGraph is None:
        iesGraph = Graph()
    clearGraph(iesGraph=iesGraph)
    iesGraph.namespace_manager.bind('ies', iesUri)
    iesGraph.namespace_manager.bind('iso8601', iso8601Uri)
    iesGraph.namespace_manager.bind('data', dataUri)
    addNamingSchemes(iesGraph=iesGraph)
    return iesGraph

def getShortUri(graph,uri):
    if type(uri) is URIRef:
        id = uri
    else:
        id = URIRef(uri)
    return id.n3(graph.namespace_manager)

def parseJSONLD(iesGraph, rawJSON):
    # assume it's compressed JSON-LD, so flatten it !
    flattened = json.flatten(rawJSON)
    iesGraph.parse(data=json.dumps(flattened), format='json-ld')

def parseN3(iesGraph, n3):
    # assume it's compressed JSON-LD, so flatten it !
    iesGraph.parse(data=n3, format='n3')

def parseNT(iesGraph, nt):
    # assume it's compressed JSON-LD, so flatten it !
    iesGraph.parse(data=nt, format='nt')

#this kinda speaks for itself. Creates a random (UUID) URI based on the dataUri stub
def generateDataUri():
    return(URIRef(dataUri+str(uuid.uuid4())))

#Check to see if a triple is already in our graph
def inGraph(iesGraph,subject,predicate,obj):
    return (subject, predicate, obj) in iesGraph

#We use this function to check if we've already got this triple in the graph before creating it,
#rdflib should deal with this, but we've had a few issues, and this also helps a bit with performance
def addToGraph(iesGraph,subject,predicate,obj):
    if not inGraph(iesGraph=iesGraph,subject=subject, predicate=predicate, obj=obj):
        iesGraph.add((subject, predicate, obj))

#Convenience function to create an instance of a class
def instantiate(iesGraph,_class,instance=None):
    if not instance:
        #Make a uri based on the data stub...
        instance = generateDataUri()
    addToGraph(iesGraph=iesGraph,subject=instance,predicate=RDF.type,obj=_class)
    return(instance)

#Puts an item in a particular period
def putInPeriod(iesGraph,item,timeString,periodName=None):
    iso8601TimeString = timeString.replace(" ","T")
    #The time is encoded in the URI so we can resolve on unique periods,
    #This code assumes ISO8601 formatted timestamp...standards dear boy, standards !
    pp = URIRef(iso8601Uri+str(iso8601TimeString))
    addToGraph(iesGraph=iesGraph,subject=pp,predicate=isoP,obj=Literal(str(iso8601TimeString), datatype=XSD.string))
    instantiate(iesGraph=iesGraph,_class=particularPeriod,instance=pp)
    addToGraph(iesGraph=iesGraph,subject=item,predicate=ip,obj=pp)
    if periodName is not None:
        addToGraph(iesGraph=iesGraph,subject=pp,predicate=hn,obj=Literal(periodName))
    return pp


def addState(iesGraph,item,stateType,start=None,end=None,inLocation=None):
    st = instantiate(iesGraph=iesGraph, _class=stateType)
    addToGraph(iesGraph=iesGraph, subject=st, predicate=isto, obj=item)
    if start is not None:
        startsIn(iesGraph=iesGraph, item=st, timeString=start)
    if end is not None:
        startsIn(iesGraph=iesGraph, item=st, timeString=end)
    if inLocation is not None:
        addToGraph(iesGraph,st,il,inLocation)
    return st

#Asserts an item started in a particular period
def startsIn(iesGraph,item,timeString):
    timeString = timeString.replace(" ","T")
    bs = instantiate(iesGraph=iesGraph,_class=boundingState)
    addToGraph(iesGraph=iesGraph,subject=bs,predicate=iso,obj=item)
    putInPeriod(iesGraph=iesGraph,item=bs,timeString=timeString)

#Asserts an item ended in a particular period
def endsIn(iesGraph,item,timeString):
    timeString = timeString.replace(" ","T")
    bs = instantiate(iesGraph=iesGraph,_class=boundingState)
    addToGraph(iesGraph=iesGraph,subject=bs,predicate=ieo,obj=item)
    putInPeriod(iesGraph=iesGraph,item=bs,timeString=timeString)

def createGeoPoint(iesGraph,lat,lon):
    gh = Geohash.encode(float(lat),float(lon))
    gp = instantiate(iesGraph,geoPoint,instance=URIRef("http://geohash.org/"+str(gh)))
    addIdentifier(iesGraph, gp, lat, idUri=URIRef("http://geohash.org/"+str(gh)+"_LAT"), idClass=latitude)
    addIdentifier(iesGraph, gp, lon, idUri=URIRef("http://geohash.org/"+str(gh)+"_LON"), idClass=longitude)
    return gp

def addParticipant(iesGraph,event,participatingEntity,participationType=eventParticipant,start=None,end=None):
    part = instantiate(iesGraph, participationType)
    addToGraph(iesGraph, part, ipi, event)
    addToGraph(iesGraph, part, ipo, participatingEntity)
    if start:
        startsIn(iesGraph=iesGraph, item=part, timeString=start)
    if end:
        startsIn(iesGraph=iesGraph, item=part, timeString=end)
    return part


#addMeasure - creates a measure that's an instance of a given measureClass, adds its value and unit of measure
def addMeasure(iesGraph,measureClass,value,uom=None,instance=None):
    meas = instantiate(iesGraph=iesGraph,_class=measure,instance=instance)
    addToGraph(iesGraph=iesGraph,subject=meas,predicate=mc,obj=measureClass)
    measureVal = instantiate(iesGraph=iesGraph,_class=measureValue)
    addToGraph(iesGraph=iesGraph,subject=measureVal,predicate=rv,obj=Literal(value, datatype=XSD.string))
    addToGraph(iesGraph=iesGraph,subject=meas,predicate=hv,obj=measureVal)
    if uom:
        addToGraph(iesGraph=iesGraph,subject=measureVal,predicate=mu,obj=uom)
    return(meas)



#add boilerplate stuff
def addNamingSchemes(iesGraph):
    #Boiler plate stuff - creating the NamingScheme for mmsi:
    #Note that RDF lib prefers to be given URIRefs...it will also work with strings,
    #but we hit some snags and now always force a URIRef for subject predicate and object
    addToGraph(iesGraph=iesGraph,
               subject=mmsiNs, predicate=RDF.type, obj=namingScheme)
    #Hoisted by its own petard...or at least named by its own naming scheme
    addName(iesGraph=iesGraph,item=mmsiNs,
            nameString="MMSI",namingScheme=mmsiNs)
    #congrats, you just created your first IES triple. Woop Woop.
    #Now let's make the ITU the owner of the namingScheme
    instantiate(iesGraph=iesGraph, _class=organisation,instance=URIRef(ituUri))
    #Now add a name for the ITU organisation
    addName(iesGraph=iesGraph,item=URIRef(ituUri),nameString="International Telecommunications Union")
    #Make the ITU the owner of that naming scheme
    addToGraph(iesGraph=iesGraph,subject=mmsiNs,predicate=so,obj=URIRef(ituUri))

def addIdentifier(iesGraph,identifiedItem,idText,idUri=None,idClass=identifier,idRelType = iib,namingScheme=None):
    idUri = instantiate(iesGraph=iesGraph,_class=idClass,instance=idUri)
    addToGraph(iesGraph=iesGraph,subject=idUri,predicate=rv,obj=Literal(idText, datatype=XSD.string))
    addToGraph(iesGraph=iesGraph,subject=identifiedItem,predicate=idRelType,obj=idUri)
    if namingScheme:
        addToGraph(iesGraph=iesGraph,subject=idUri,predicate=ins,obj=namingScheme)

#Add a name to an item, and optionally specify a particular type of name( from IES Model),
#and a naming scheme (of your own creation)
def addName(iesGraph,item,nameString,nameType=None,namingScheme=None,nameUri=None):
    if not nameType:
        nameType = name
    myName = instantiate(iesGraph=iesGraph,_class=nameType,instance=nameUri)
    if nameString:
        addToGraph(iesGraph=iesGraph,subject=myName,predicate=rv,obj=Literal(nameString, datatype=XSD.string))
    addToGraph(iesGraph=iesGraph,subject=item,predicate=hn,obj=myName)
    if namingScheme:
        addToGraph(iesGraph=iesGraph,subject=myName,predicate=ins,obj=namingScheme)
    return myName

def addPersonName(iesGraph,item,nameString,namingScheme=None,nameUri=None, surname=None,givenName=None):
    _ = addName(iesGraph,item,nameString,nameType=personName,namingScheme=namingScheme,nameUri=nameUri)

def createIdentifiedEntity(iesGraph,entityClass,idText,idClass=identifier,namingScheme=None,uri=None):
    if namingScheme==mmsiNs:
        if uri is None:
            uri = URIRef(dataUri+"MMSI_"+idText)
        idObj = URIRef(uri+"_MMSI_ID")
        addIdentifier(iesGraph,uri,idText,idUri=idObj,idClass=commsIdentifier,namingScheme=mmsiNs)
    else:
        if uri is None:
            uri = generateDataUri()
        addIdentifier(iesGraph,uri,idText,idClass=idClass,namingScheme=namingScheme)

    _ = instantiate(iesGraph,entityClass,uri)
    return(uri)

#This is used in both the following and track use cases.
def createLocationTransponder(iesGraph,mmsi):
    return createIdentifiedEntity(iesGraph=iesGraph,entityClass=locationTransponder,entityID=mmsi,namingScheme=mmsiNs)


#Instantiate an IES System class
def createSystem(iesGraph,sysName,instance=None):
    return instantiate(iesGraph=iesGraph,_class=system,instance=instance)

#Note probability must be a float between 0.0 and 1.0.
#items is a list of the things that are in the possible world

def assessPwProbabilityHelper(iesGraph, probability):
    if probability <= 0.05:
        myAss = instantiate(iesGraph,assessToBeRemoteChance)
    elif probability <=0.225: #Sigh...PHIA probs have gaps.
        myAss = instantiate(iesGraph,assessToBeHighlyUnlikely)
    elif probability <=0.375: #Sigh...PHIA probs have gaps.
        myAss = instantiate(iesGraph,assessToBeUnlikely)
    elif probability <=0.525: #Sigh...PHIA probs have gaps.
        myAss = instantiate(iesGraph,assessToBeRealisticPossibility)
    elif probability <=0.775: #Sigh...PHIA probs have gaps.
        myAss = instantiate(iesGraph,assessToBeLikelyOrProbably)
    elif probability <=0.925: #Sigh...PHIA probs have gaps.
        myAss = instantiate(iesGraph,assessToBeHighlyLikely)
    elif probability > 0.925: #Sigh...PHIA probs have gaps.
        myAss = instantiate(iesGraph,assessToBeAlmostCertain)

    return myAss

def assessPwProbability(iesGraph,items,assessorSystem,probability,usePHIA=False,assessDate=''):
    myPW = instantiate(iesGraph,possibleWorld)

    myAss = None
    if usePHIA is True:
        myAss = assessPwProbabilityHelper(iesGraph=iesGraph, probability=probability)

    if myAss is None:
        myAss = instantiate(iesGraph,assessProbability)

    addToGraph(iesGraph,myAss,ass,myPW)
    myProp = instantiate(iesGraph,probabilityRepresentation)
    addToGraph(iesGraph,myProp,rv,Literal(probability, datatype=XSD.float))
    addToGraph(iesGraph,myAss,hr,myProp)
    myAssessor = instantiate(iesGraph,assessor)
    addToGraph(iesGraph,myAssessor,ipi,myAss)
    addToGraph(iesGraph,myAssessor,ipo,assessorSystem)

    for item in items:
        addToGraph(iesGraph,item,ipao,myPW)

    if assessDate != '':
        putInPeriod(iesGraph,myAss,assessDate)


def addBirth(graph,being,dob,pob=None,periodName=None):
    birth = instantiate(graph, birthState, instance=URIRef(being.toPython()+"_BIRTH"))
    addToGraph(graph, birth, iso, being)
    if not dob:
        putInPeriod(graph, birth, dob,periodName=periodName)
    if not pob:
        addToGraph(graph,birth,il,pob)

def addDeath(graph,being,dod,pod=None,periodName=None):
    death = instantiate(graph, deathState, instance=URIRef(being.toPython()+"_DEATH"))
    addToGraph(graph, death, ieo, being)
    if not dod:
        putInPeriod(graph, death, dod,periodName=periodName)
    if not pod:
        addToGraph(graph,death,il,pod)


def createPerson(graph,uri=None,firstName="",lastName="",dob=None,pob=None,description=None,type_=person):
    if not uri:
        person = instantiate(graph, type_)
    else:
        person = instantiate(graph,type_,URIRef(uri))
    primaryName = lastName+" "+firstName
    if primaryName != " ":
        addToGraph(graph, person, telicentPrimary,Literal(primaryName))


    sName = instantiate(graph, surname, instance=URIRef(uri+"_SURNAME"))
    addToGraph(graph, sName, ir, name)
    addToGraph(graph, sName, rv, Literal(lastName))

    birth = instantiate(graph, birthState, instance=URIRef(uri+"_BIRTH"))
    addToGraph(graph, birth, iso, person)
    if dob:
        putInPeriod(graph, birth, dob)

    if pob:
        addToGraph(graph,birth,il,pob)

    if description:
        addToGraph(graph, person, rdfsComment, Literal(description))

    return person

def createEventParticipantHelper(graph, event, participant, defaultParticipationType):
    if "epType" in participant.keys():
        p = instantiate(graph,participant["epType"])
    else:
        p = instantiate(graph,defaultParticipationType)
    addToGraph(graph,p,ipi,event)
    if participant.get("uri"):
        if isinstance(participant["uri"], str):
            participant["uri"] = URIRef(participant["uri"])
            addToGraph(graph,p,ipo,participant["uri"])
    if participant.get("start"):
        startsIn(graph,p,participant["start"])
    if participant.get("end"):
        endsIn(graph,p,participant["end"])

#Create event
#As a minimum, this will just create an instance of ies:Event. If you set primartType, it'll create an instance of that
#To add participants, add an array of dictionaries, each of which looks like this:
#  {"uri":"http://TheUriOfTheParticipant","epType":"uri of the type of participation",
#"start":"2022-01-01...","end":"etc."}
# The participants can be sparse (even the URI...though that's not recommended)
def createEvent(graph,primaryType=event,participants=None,
                defaultParticipationType=eventParticipant,eventStart=None,eventEnd=None):
    if isinstance(primaryType, str):
        primaryType = URIRef(primaryType)
    event = instantiate(graph, primaryType)
    if eventStart is not None:
        startsIn(graph,event,eventStart)
    if eventEnd is not None:
        endsIn(graph,event,eventEnd)
    if participants:
        for participant in participants:
            _ = createEventParticipantHelper(graph=graph, event=event,
                                             participant=participant, defaultParticipationType=defaultParticipationType)
    return event

def saveRdf(graph,filename):
    graph.serialize(destination=filename, format='ttl')
    graph.remove((None, None, None)) #Clear the graph


def initialiseKafka(kHost):
    return KafkaProducer(bootstrap_servers=[kHost])

def sendToKafka(iesGraph,kProducer,kTopic):
    #NT = iesGraph.serialize(format='nt', indent=4).decode()
    #binNT = bytes(NT,"utf-8")
    #zipNT = zlib.compress(binNT)
    #kProducer.send(kTopic, value=zipNT)
    ttl = iesGraph.serialize(format='ttl', indent=4).decode()
    binTTL = bytes(ttl,"utf-8")
    kProducer.send(kTopic, value=binTTL)
