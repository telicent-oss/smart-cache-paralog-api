# Smart Cache Paralog API

A REST API for getting CARVER-style data out of an IES triplestore.

The types of query that are required for apps like Paralog/CARVER don't really lend themselves well to GraphQL. The Paralog developers need a simple REST api to work with. This was originally written in NodeJS, but is now in Python so we can re-use maplib for writes back to CORE.

To get started, you need to use Python pip to install all the dependencies listed in the requirements.txt file. Once installed, you can then run the paralog_server.py file to start the API server on 4001 port. The swagger documentation (sparse) is at localhost:4001/docs

Note: if you're running the Telicent local deployment, you'll have to stop the paralog server container that it is running.

## Dependencies

- [Apache Jena](https://jena.apache.org/download/index.cgi)

## Usage

The API is best run in a containerised environment. A DockerFile has been provided to help with this. To begin with, make sure you have the following environment variables set.

- JENA_URL (defaults to `localhost`)
- JENA_DATASET (defaults to `knowledge`)  
- JENA_PORT (defaults to `3000`)

After setting the environment variables; 

- In your terminal, navigate to the same directory that contains the DockerFile and run the command `docker build .`. This should build a docker image which you would use to run the API in a container.

- Run `docker run -p 4001:4001 <image:id>`. The containerized API should start running and be mapped to port 4001 your host PC.

## Configuration

### API Configuration

General configuration for the API.

| Value               | Default       | Description                                                |
|---------------------|---------------|------------------------------------------------------------|
| API_ROOT_PATH       | None          | API request prefix, e.g. "/api/v1/"                        |
| API_OPENAPI_PATH    | /openapi.json | Where to serve the OpenAPI schema from (for the frontend)  |
| API_LOG_LEVEL       | INFO          | Log level                                                  |
| API_LOG_STDOUT      | 1             | Set to '1' to log to stdout, 0 to disable                  |
| API_LOG_FILE        | 0             | Set to '1' to log to a file, 0 to disable                  |
| API_LOG_FILE_PATH   | paralog.log   | Full path to the log file when API_LOG_FILE is set to 1    |


### Jena Configuration

Apache Jena must be running.

| Value          | Default   | Description                 |
|----------------|-----------|-----------------------------|
| JENA_URL       | localhost | Jena's host                 |
| JENA_PORT      | 3000      | Jena's host port            |
| JENA_DATASET   | knowledge | The Jena dataset to use     |
| JENA_PROTOCOL  | http      | Protocol to connect to Jena |
| JENA_USER      | None      | User to connect to Jena     |
| JENA_PASSWORD  | None      | Password to connect to Jena |


### Authentication Configuration

Paralog can evaluate JWT tokens to provide auth. A JWKS or public key end point must be configured, and the JWT header 
must be set in configuration.

| Value          | Default | Description                   |
|----------------|---------|-------------------------------|
| JWT_HEADER     | None    | The header containing the JTW |
| JWKS_URL       | None    | JWKS end-point                |
| PUBLIC_KEY_URL | None    | Public key end-point          |


Furthermore, authentication has its own logger, with additional attributes provided for monitoring.

#### paralog.decode_token

Extra logging attributes are:

method
: one of, "STARTUP" (for logs during start up) or "Authenticator", for logs generated during authentication

type
: one of, "GENERAL" for general messages, or "UNAUTHORIZED" when authorization fails. 
