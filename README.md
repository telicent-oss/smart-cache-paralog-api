## Smart Cache Paralog API

A REST API for getting CARVER-style data out of an IES triplestore.

The types of query that are required for apps like Paralog/CARVER don't really lend themselves well to GraphQL. The Paralog developers need a simple REST api to work with. This was originally written in NodeJS, but is now in Python so we can re-use maplib for writes back to CORE.

To get started, you need to use Python pip to install all the dependencies listed in the requirements.txt file. Once installed, you can then run the paralog_server.py file to start the API server on 4001 port. The swagger documentation (sparse) is at localhost:4001/docs

Note: if you're running the Telicent local deployment, you'll have to stop the paralog server container that it is running.

## Usage
The API is best run in a containerzed environment. A DockerFile has been provided to help with this. To begin with, make sure you have the following environment variables set.

- JENA_URL (defaults to `localhost`)
- JENA_DATASET (defaults to `knowledge`)  
- JENA_PORT (defaults to `3000`)

After setting the environment variables; 

- In your terminal, navigate to the same directory that contains the DockerFile and run the command `docker build .`. This should build a docker image which you would use to run the API in a container.

- Run `docker run -p 4001:4001 <image:id>`. The containerized API should start running and be mapped to port 4001 your host PC.

## API
API paths are:


    GET:
    
    /                                           Hello World
    
    /docs                                       OpenAPI docs
    
    /assessments                                Return all the assessments in the database

    /assessments/asset-types                    Return all the asset types in the assessment - this is used to drive the checkboxes for the app
        ?assessment=<uri-of-the-assessment>

    /assessments/assets                         Return all the assets in the assessment, that are of the types specified in the query parameters
        ?assessment=<uri-of-the-assessment>
        ?types=<uri-of-asset-type> 1..many

    /assessments/dependencies                   Return all the dependencies in the assessment, that exist between assets of the types specified in the query parameters
        ?assessment=<uri-of-the-assessment>
        ?types=<uri-of-asset-type> 1..many

    /asset                                      Return all the info we have about the asset provided in the assetUri query parameter
        ?assetUri=<uri-of-asset>

    /asset/dependents                           Return all the assets that are dependent onthe asset provided in the assetUri query parameter
        ?assetUri=<uri-of-asset>

    /asset/providers                            Return all the assets that depend onthe asset provided in the assetUri query parameter
        ?assetUri=<uri-of-asset>

    /asset/residents                            Returns all the people who have lived at that address
        ?assetUri=<uri-of-asset>

    /asset/parts                                Returns all the parts of an asset (e.g. road segments)
        ?assetUri=<uri-of-asset>

    /asset/participations                       Returns all the events an asset participates in
        ?assetUri=<uri-of-asset>

    /assessments/assets?assessment=XX           Return all the assets covered by the assessments listed in the query params (1:many)
    
    /assessments/connections?assessment=XX      Return all the connections between assets covered by the assessments listed in the query params (1:many)
    
    /assets                                     Return all assets of a given type (NOT USED CURRENTLY)
        ?assetType=<uri-of-asset-type>

    /person/residences                          Return all the residences a person has lived in
        ?personUri=<uri of the person>

    /event/participants                         Returns all the assets that participate in an event
        ?eventUri=<uri-of-event>

    /ontology/class                             Return info about a class (in this case, what the parent classes are)
        ?classUri=<uri-of-the-asset-type>
    
    /flood-watch-areas                         Returns all flood watch areas with more specific flood areas

    /flood-watch-areas/polygon                  Returns geo json for each flood area polygon uri
        ?polygon_uri=<flood-area-polygon-uri>
