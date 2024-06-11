
import jwt
import requests
from fastapi import Request
from fastapi.responses import JSONResponse
from jwt import PyJWKClient

from errors import ConfigurationException
from logger import TelicentLogLevel

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

auth_failed = {"ok": False, "message":"Authorization failed"}
class AccessMiddleware:
    '''
    Simple middleware to validate and decode tokens
    '''
    def __init__(self, app, jwt_header, logger, jwks_url=None, public_key_url=None):

        self.app = app
        self.jwks_url = jwks_url
        self.public_key_url = public_key_url
        if isinstance(self.public_key_url,str):
            self.public_key_url = self.public_key_url.strip("/")
        self.jwt_header = jwt_header
        self.logger = logger

        if not self.jwks_url and not self.public_key_url:
            self.logger(
                "STARTUP",
                "Both jwks_url and public_key_url are missing, starting paralog without auth",
                level=TelicentLogLevel.WARN,
            )

        if (self.jwks_url or self.public_key_url) and self.jwt_header:
            self.logger(
                "STARTUP",
                f"Configuring auth with using header {self.jwt_header}",
                level=TelicentLogLevel.DEBUG,
            )
            if not jwks_url and not public_key_url:
                self.logger(
                "STARTUP",
                "Both JWK_URL and config.public_key_url passed, JWK_URL takes preference",
                level=TelicentLogLevel.WARN,
                )
            if self.jwks_url:
                self.logger(
                    "STARTUP",
                    f"Auth configured with jwks endpoint {self.jwks_url}",
                    level=TelicentLogLevel.DEBUG,
                )
            if self.public_key_url:
                self.logger(
                    "STARTUP",
                    f"Auth configured with loadbalancer public key endpoint {self.public_key_url}",
                    level=TelicentLogLevel.DEBUG,
                )

            self.run_auth = True
        else:
            self.run_auth = False


    async def __call__(self, request: Request, call_next):

        if self.jwt_header not in request.headers:
            self.logger("Authenticator", "Unauthorized access: No required header: " + self.jwt_header,
                    level=TelicentLogLevel.INFO, type="UNAUTHORIZED")
            return JSONResponse(content={"message": f"missing auth header: {self.jwt_header}"}, status_code=400)
        encoded =  request.headers[self.jwt_header]

        if self.run_auth:
            try:
                token = self.validate_token(encoded)

                if token is None:
                    self.logger("Authenticator", "Unauthorized access: token not valid",
                        level=TelicentLogLevel.INFO, type="UNAUTHORIZED" )
                    return JSONResponse(content={"message": "unauthorised, invalid token"}, status_code=401)

            except (jwt.exceptions.InvalidTokenError, jwt.exceptions.PyJWKClientError):
                return JSONResponse(content={"message": "unauthorised, invalid token"}, status_code=401)

            except Exception:
                return JSONResponse(content={"message": "Internal Server Error"}, status_code=500)



        response = await call_next(request)

        return response


    def validate_token(self, token):
        try:
            headers = jwt.get_unverified_header(token)
            key = ""
            if self.jwks_url is not None:
                self.logger("Authenticator", "Validating token with jwks_url",
                            level=TelicentLogLevel.DEBUG, type="GENERAL" )
                jwks_client = PyJWKClient(self.jwks_url)
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                key = signing_key.key
            elif self.public_key_url is not None:
                self.logger("Authenticator", "Validating token with elb public key",
                            level=TelicentLogLevel.DEBUG, type="GENERAL" )
                public_key_ep = "{}{}".format(self.public_key_url, headers['kid'])
                req = requests.get(public_key_ep)
                key = req.text
            else:
                raise ConfigurationException("access_middleware", "jwks_url or public_key_url",
                                              "Token decoding requires either a jwks_url or public_key_url")
            data = jwt.decode(token, key, algorithms=[headers['alg']])

        except Exception as e:
            self.logger("Authenticator", "Exception validating token " + str(e),
                        level=TelicentLogLevel.INFO, type="UNAUTHORIZED" )
            raise e

        return data
