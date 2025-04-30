# Smart Cache Paralog API

A REST API for getting CARVER-style data out of an IES triplestore.

The types of query that are required for apps like Paralog/CARVER don't really lend themselves well to GraphQL. The Paralog developers need a simple REST api to work with. This was originally written in NodeJS, but is now in Python so we can re-use maplib for writes back to CORE.

To get started, you need to use Python pip to install all the dependencies listed in the requirements.txt file. Once installed, you can then run the paralog_server.py file to start the API server on 4001 port. The swagger documentation (sparse) is at localhost:4001/docs

Note: if you're running the Telicent local deployment, you'll have to stop the paralog server container that it is running.

## Dependencies

- [Apache Jena](https://jena.apache.org/download/index.cgi)

## Usage

```shell
docker run -p 8000:8000 telicent/paralog-api`
``` 

When running in Docker it will be necessary to at least set the `JENA_URL` variable. Assuming Jena is running on the Docker
host:

```shell
docker run -e JENA_URL=host.docker.internal -p 8000:8000 --add-host=host.docker.internal:host-gateway telicent/paralog-api
 ```

Please note, additional environment variables will be required depending on how your Jena 

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
| JENA_PORT      | 3030      | Jena's host port            |
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


## Development

### Developmenmt Dependencies

- Jena available locally
- \>=Python 3.12

### Running Locally

1. Checkout the project code
2. Create and activate a virtual environment
```shell
python -m venv venv && . venv/bin/activate
```
2. Install the dependencies and set up the local environment:
```shell
./dev_setup.sh
```
3. Run FastAPI
```shell
fastapi run paralog/app.py
```

### .env

You may create a .env file to configure the application in your development environment. Paralog will automatically 
find and read configuration from this file.

### Building

To build the docker image you must first have a file called `sbom.json` at the route of your local project

```shell
touch sbom.json
```

You may then build the Docker image

```shell
docker build -t paralog-api . 
```
